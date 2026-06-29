// app/api/tasks/[id]/check/route.ts
// IFC 文件上传与审查 API - 纯数据库存储版

import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../../../backend/mongodb";
import { Resource } from "../../../../../backend/resource";
import mongoose from "mongoose";
import { rateLimit } from "../../../../lib/ratelimit";

// 强制动态渲染，避免缓存
export const dynamic = 'force-dynamic';

// Next.js 15 要求 params 必须是一个 Promise 类型
type ContextType = {
  params: Promise<{ id: string }>;
};

/**
 * POST /api/tasks/[id]/check
 * 上传 IFC 文件并触发审查
 *
 * 请求体: FormData { ifc: File }
 * 返回: { message: string, taskId: string }
 */
export async function POST(request: NextRequest, context: ContextType) {
  // 速率限制检查
  const isAllowed = await rateLimit(request);
  if (!isAllowed) {
    return NextResponse.json({ error: "Rate limit exceeded, please try again later" }, { status: 429 });
  }

  try {
    await dbConnect();

    // 解析 params
    const resolvedParams = await context.params;
    const taskId = resolvedParams.id;

    if (!taskId) {
      return NextResponse.json(
        { error: "Task ID missing" },
        { status: 400 }
      );
    }

    // Find task record - use atomic update to prevent race condition
    const task = await Resource.findOneAndUpdate(
      { _id: taskId, status: "completed", idsFileId: { $exists: true, $ne: null } },
      { $set: { _checkLock: Date.now() } }, // Temporary lock marker
      { new: true }
    );

    if (!task) {
      // Check what happened - task not found or status changed
      const currentTask = await Resource.findById(taskId);
      if (!currentTask) {
        return NextResponse.json(
          { error: "Task not found" },
          { status: 404 }
        );
      }
      if (currentTask.status !== "completed") {
        return NextResponse.json(
          { error: "Task status has changed, please refresh and try again", status: currentTask.status },
          { status: 409 } // Conflict
        );
      }
      if (!currentTask.idsFileId) {
        return NextResponse.json(
          { error: "IDS file does not exist, cannot proceed with review" },
          { status: 400 }
        );
      }
      return NextResponse.json(
        { error: "Task is being processed by another request" },
        { status: 409 }
      );
    }

    // Parse FormData
    const formData = await request.formData();
    const ifcFile = formData.get("ifc") as File | null;

    if (!ifcFile) {
      // Release lock
      await Resource.findByIdAndUpdate(taskId, { $unset: { _checkLock: 1 } });
      return NextResponse.json(
        { error: "Please upload IFC file" },
        { status: 400 }
      );
    }

    // Validate file type
    if (!ifcFile.name.toLowerCase().endsWith(".ifc")) {
      // Release lock
      await Resource.findByIdAndUpdate(taskId, { $unset: { _checkLock: 1 } });
      return NextResponse.json(
        { error: "Please upload .ifc format file" },
        { status: 400 }
      );
    }

    console.log(`[IFC Check] Processing task: ${taskId}`);
    console.log(`[IFC Check] IFC file: ${ifcFile.name}, size: ${ifcFile.size} bytes`);

    // Read file content
    const ifcBuffer = Buffer.from(await ifcFile.arrayBuffer());

    // Store to GridFS
    const db = mongoose.connection.db;
    if (!db) throw new Error("Database connection not available");
    const bucket = new mongoose.mongo.GridFSBucket(db, { bucketName: 'uploads' });

    const uploadStream = bucket.openUploadStream(ifcFile.name, {
      contentType: "application/x-step",
      metadata: {
        taskId: taskId,
        type: "ifc",
        originalName: ifcFile.name
      }
    });

    // Write file
    await new Promise<void>((resolve, reject) => {
      uploadStream.end(ifcBuffer);
      uploadStream.on('finish', () => resolve());
      uploadStream.on('error', (err) => reject(err));
    });

    const ifcFileId = uploadStream.id;
    console.log(`[IFC Check] IFC file stored in GridFS, ID: ${ifcFileId}`);

    // Update task record - set status to checking (atomic update with lock check)
    const updatedTask = await Resource.findOneAndUpdate(
      { _id: taskId, _checkLock: task._checkLock },
      {
        $set: {
          ifcFileId: ifcFileId,
          ifcFileName: ifcFile.name,
          ifcFileSize: ifcFile.size,
          status: "checking"
        },
        $unset: { _checkLock: 1 }
      },
      { new: true }
    );

    if (!updatedTask) {
      // Another request already processed - clean up uploaded file
      try {
        await bucket.delete(new mongoose.Types.ObjectId(ifcFileId));
      } catch (e) { /* ignore */ }
      return NextResponse.json(
        { error: "Task is being processed by another request, please try again" },
        { status: 409 }
      );
    }

    // 调用 Python 后端进行审查
    const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || "http://localhost:8000";

    console.log(`[IFC Check] 调用 Python 后端: ${PYTHON_BACKEND_URL}/check-ifc`);

    const checkResponse = await fetch(`${PYTHON_BACKEND_URL}/check-ifc`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        taskId: taskId,
        idsFileId: task.idsFileId.toString(),
        ifcFileId: ifcFileId.toString()
      })
    });

    if (!checkResponse.ok) {
      const errorData = await checkResponse.json().catch(() => ({ error: "Unknown error" }));
      console.error("[IFC Check] Python backend check error:", errorData);

      // 回滚状态
      await Resource.findByIdAndUpdate(taskId, {
        $set: {
          status: "check_failed",
          errorMessage: `Review service error: ${errorData.error || checkResponse.statusText}`
        }
      });

      return NextResponse.json(
        { error: "Review service call failed", details: errorData },
        { status: 500 }
      );
    }

    const checkResult = await checkResponse.json();
    console.log(`[IFC Check] 审查任务已提交:`, checkResult);

    return NextResponse.json({
      message: "IFC file uploaded, review started",
      taskId: taskId,
      ifcFileId: ifcFileId.toString(),
      status: "checking"
    });

  } catch (error) {
    console.error("IFC review upload failed:", error);
    return NextResponse.json(
      { error: "Internal server error", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}

/**
 * GET /api/tasks/[id]/check
 * 获取审查状态
 */
export async function GET(request: NextRequest, context: ContextType) {
  // 速率限制检查
  const isAllowed = await rateLimit(request);
  if (!isAllowed) {
    return NextResponse.json({ error: "Rate limit exceeded, please try again later" }, { status: 429 });
  }

  try {
    await dbConnect();

    const resolvedParams = await context.params;
    const taskId = resolvedParams.id;

    if (!taskId) {
      return NextResponse.json(
        { error: "Task ID missing" },
        { status: 400 }
      );
    }

    const task = await Resource.findById(taskId);

    if (!task) {
      return NextResponse.json(
        { error: "Task not found" },
        { status: 404 }
      );
    }

    return NextResponse.json({
      status: task.status,
      hasIFCFile: !!task.ifcFileId,
      ifcFileName: task.ifcFileName,
      hasReport: !!task.reportData,
      reportSummary: task.reportSummary,
      checkedAt: task.checkedAt,
      errorMessage: task.errorMessage
    });

  } catch (error) {
    console.error("Failed to get review status:", error);
    return NextResponse.json(
      { error: "Internal server error", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}

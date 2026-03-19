// app/api/tasks/[id]/check/route.ts
// IFC 文件上传与审查 API - 纯数据库存储版

import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../../../backend/mongodb";
import { Resource } from "../../../../../backend/resource";
import mongoose from "mongoose";

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
  try {
    await dbConnect();

    // 解析 params
    const resolvedParams = await context.params;
    const taskId = resolvedParams.id;

    if (!taskId) {
      return NextResponse.json(
        { error: "任务ID缺失" },
        { status: 400 }
      );
    }

    // 查找任务记录
    const task = await Resource.findById(taskId);

    if (!task) {
      return NextResponse.json(
        { error: "任务不存在" },
        { status: 404 }
      );
    }

    // 检查任务状态 - 只有 completed 状态才能进行审查
    if (task.status !== "completed") {
      return NextResponse.json(
        { error: "任务尚未完成 IDS 生成，无法进行审查", status: task.status },
        { status: 400 }
      );
    }

    // 检查是否有 IDS 文件
    if (!task.idsFileId) {
      return NextResponse.json(
        { error: "IDS 文件不存在，无法进行审查" },
        { status: 400 }
      );
    }

    // 解析 FormData
    const formData = await request.formData();
    const ifcFile = formData.get("ifc") as File | null;

    if (!ifcFile) {
      return NextResponse.json(
        { error: "请上传 IFC 文件" },
        { status: 400 }
      );
    }

    // 验证文件类型
    if (!ifcFile.name.toLowerCase().endsWith(".ifc")) {
      return NextResponse.json(
        { error: "请上传 .ifc 格式的文件" },
        { status: 400 }
      );
    }

    console.log(`[IFC Check] 开始处理任务: ${taskId}`);
    console.log(`[IFC Check] IFC 文件: ${ifcFile.name}, 大小: ${ifcFile.size} bytes`);

    // 读取文件内容
    const ifcBuffer = Buffer.from(await ifcFile.arrayBuffer());

    // 存储到 GridFS
    const db = mongoose.connection.db;
    const bucket = new mongoose.mongo.GridFSBucket(db, { bucketName: 'uploads' });

    const uploadStream = bucket.openUploadStream(ifcFile.name, {
      contentType: "application/x-step",
      metadata: {
        taskId: taskId,
        type: "ifc",
        originalName: ifcFile.name
      }
    });

    // 写入文件
    await new Promise<void>((resolve, reject) => {
      uploadStream.end(ifcBuffer);
      uploadStream.on('finish', () => resolve());
      uploadStream.on('error', (err) => reject(err));
    });

    const ifcFileId = uploadStream.id;
    console.log(`[IFC Check] IFC 文件已存储到 GridFS, ID: ${ifcFileId}`);

    // 更新任务记录 - 状态先设为 checking
    await Resource.findByIdAndUpdate(taskId, {
      $set: {
        ifcFileId: ifcFileId,
        ifcFileName: ifcFile.name,
        status: "checking"
      }
    });

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
          errorMessage: `审查服务错误: ${errorData.error || checkResponse.statusText}`
        }
      });

      return NextResponse.json(
        { error: "审查服务调用失败", details: errorData },
        { status: 500 }
      );
    }

    const checkResult = await checkResponse.json();
    console.log(`[IFC Check] 审查任务已提交:`, checkResult);

    return NextResponse.json({
      message: "IFC 文件上传成功，审查已开始",
      taskId: taskId,
      ifcFileId: ifcFileId.toString(),
      status: "checking"
    });

  } catch (error) {
    console.error("IFC 审查上传失败:", error);
    return NextResponse.json(
      { error: "服务器内部错误", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}

/**
 * GET /api/tasks/[id]/check
 * 获取审查状态
 */
export async function GET(request: NextRequest, context: ContextType) {
  try {
    await dbConnect();

    const resolvedParams = await context.params;
    const taskId = resolvedParams.id;

    if (!taskId) {
      return NextResponse.json(
        { error: "任务ID缺失" },
        { status: 400 }
      );
    }

    const task = await Resource.findById(taskId);

    if (!task) {
      return NextResponse.json(
        { error: "任务不存在" },
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
    console.error("获取审查状态失败:", error);
    return NextResponse.json(
      { error: "服务器内部错误", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}
import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../../backend/mongodb";
import { Resource } from "../../../../backend/resource";
import mongoose from "mongoose";
import { rateLimit } from "../../../lib/ratelimit";

// Next.js 15 要求 params 必须是一个 Promise 类型
type ContextType = {
  params: Promise<{ id: string }>;
};

// GET: 获取单个任务详情
export async function GET(
  request: NextRequest,
  context: ContextType
) {
  // 速率限制检查
  const isAllowed = await rateLimit(request);
  if (!isAllowed) {
    return NextResponse.json({ error: "Rate limit exceeded, please try again later" }, { status: 429 });
  }

  try {
    await dbConnect();

    // 必须使用 await 来解析 params
    const { id } = await context.params;
    const taskId = id;

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

    return NextResponse.json({ task });
  } catch (error) {
    console.error("Get task detail error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

// DELETE: 删除任务（包括 GridFS 中的文件）
export async function DELETE(
  request: NextRequest,
  context: ContextType
) {
  // 速率限制检查
  const isAllowed = await rateLimit(request);
  if (!isAllowed) {
    return NextResponse.json({ error: "Rate limit exceeded, please try again later" }, { status: 429 });
  }

  try {
    await dbConnect();

    const { id } = await context.params;
    const taskId = id;

    if (!taskId) {
      return NextResponse.json(
        { error: "Task ID missing" },
        { status: 400 }
      );
    }

    // 查找任务
    const task = await Resource.findById(taskId);

    if (!task) {
      return NextResponse.json(
        { error: "Task not found" },
        { status: 404 }
      );
    }

    // Delete files from GridFS
    const db = mongoose.connection.db;
    if (!db) throw new Error("Database connection not available");
    const bucket = new mongoose.mongo.GridFSBucket(db, { bucketName: 'uploads' });

    // 删除 IDS 文件
    if (task.idsFileId) {
      try {
        await bucket.delete(new mongoose.Types.ObjectId(task.idsFileId));
        console.log(`Deleted IDS file from GridFS: ${task.idsFileId}`);
      } catch (err) {
        console.log(`IDS file not found or already deleted: ${task.idsFileId}`);
      }
    }

    // 删除 IFC 文件
    if (task.ifcFileId) {
      try {
        await bucket.delete(new mongoose.Types.ObjectId(task.ifcFileId));
        console.log(`Deleted IFC file from GridFS: ${task.ifcFileId}`);
      } catch (err) {
        console.log(`IFC file not found or already deleted: ${task.ifcFileId}`);
      }
    }

    // 删除原始上传文件（如果有）
    if (task.fileId) {
      try {
        await bucket.delete(new mongoose.Types.ObjectId(task.fileId));
        console.log(`Deleted original file from GridFS: ${task.fileId}`);
      } catch (err) {
        console.log(`Original file not found or already deleted: ${task.fileId}`);
      }
    }

    // 删除数据库记录
    await Resource.findByIdAndDelete(taskId);

    return NextResponse.json({
      success: true,
      message: "Task deleted"
    });
  } catch (error) {
    console.error("Delete task error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
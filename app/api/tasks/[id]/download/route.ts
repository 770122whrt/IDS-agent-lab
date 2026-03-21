// app/api/tasks/[id]/download/route.ts
// IDS 文件下载 API - 从 GridFS 读取

import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../../../backend/mongodb";
import { Resource } from "../../../../../backend/resource";
import mongoose from "mongoose";
import { auth } from "../../../../lib/auth";
import { rateLimit } from "../../../../lib/ratelimit";

// 强制动态渲染，避免缓存
export const dynamic = 'force-dynamic';

// Next.js 15 要求 params 必须是一个 Promise 类型
type ContextType = {
  params: Promise<{ id: string }>;
};

export async function GET(request: NextRequest, context: ContextType) {
  // 速率限制检查
  const isAllowed = await rateLimit(request, "resource");
  if (!isAllowed) {
    return NextResponse.json({ error: "Rate limit exceeded, please try again later" }, { status: 429 });
  }

  try {
    // 从 session 获取当前登录用户
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session?.user?.id) {
      return NextResponse.json({ error: "Please login first" }, { status: 401 });
    }

    const currentUserId = session.user.id;

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

    // 查找任务记录
    const task = await Resource.findById(taskId);

    if (!task) {
      return NextResponse.json(
        { error: "Task not found" },
        { status: 404 }
      );
    }

    // 验证当前用户是否有权限下载该任务
    if (task.userId !== currentUserId) {
      return NextResponse.json({ error: "Not authorized to download this task" }, { status: 403 });
    }

    // 检查任务状态 - completed 或 checked 都可以下载
    if (!["completed", "checked"].includes(task.status)) {
      return NextResponse.json(
        { error: "Task not completed, cannot download", status: task.status },
        { status: 400 }
      );
    }

    // 检查是否有 IDS 文件 ID (GridFS)
    if (!task.idsFileId) {
      return NextResponse.json(
        { error: "IDS file does not exist" },
        { status: 404 }
      );
    }

    // Read file from GridFS
    const db = mongoose.connection.db;
    if (!db) throw new Error("Database connection not available");
    const bucket = new mongoose.mongo.GridFSBucket(db, { bucketName: 'uploads' });

    // 验证文件存在
    const files = await bucket.find({ _id: new mongoose.Types.ObjectId(task.idsFileId) }).toArray();
    if (files.length === 0) {
      return NextResponse.json(
        { error: "IDS file does not exist in database" },
        { status: 404 }
      );
    }

    const fileDoc = files[0];

    // 读取文件内容
    const downloadStream = bucket.openDownloadStream(new mongoose.Types.ObjectId(task.idsFileId));

    let fileContent: string;
    try {
      const chunks: Buffer[] = [];

      for await (const chunk of downloadStream) {
        chunks.push(chunk);
      }

      fileContent = Buffer.concat(chunks).toString('utf-8');
    } finally {
      // 显式关闭 GridFS 流，防止资源泄漏
      downloadStream.destroy();
    }

    // 生成下载文件名
    const baseName = task.originalname.replace(/\.[^/.]+$/, "") || `task_${taskId}`;
    const downloadFilename = `${baseName}.ids`;

    // 设置响应头
    const headers = new Headers();
    headers.set("Content-Type", "application/xml; charset=utf-8");
    headers.set(
      "Content-Disposition",
      `attachment; filename*=UTF-8''${encodeURIComponent(downloadFilename)}`
    );
    headers.set("Cache-Control", "no-cache, no-store, must-revalidate");

    // 返回文件内容
    return new NextResponse(fileContent, { headers });

  } catch (error) {
    console.error("IDS file download failed:", error);
    return NextResponse.json(
      { error: "Internal server error", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}
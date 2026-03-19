// app/api/tasks/[id]/download/route.ts
// IDS 文件下载 API - 从 GridFS 读取

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

export async function GET(request: NextRequest, context: ContextType) {
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

    // 检查任务状态 - completed 或 checked 都可以下载
    if (!["completed", "checked"].includes(task.status)) {
      return NextResponse.json(
        { error: "任务尚未完成，无法下载", status: task.status },
        { status: 400 }
      );
    }

    // 检查是否有 IDS 文件 ID (GridFS)
    if (!task.idsFileId) {
      return NextResponse.json(
        { error: "IDS 文件不存在" },
        { status: 404 }
      );
    }

    // 从 GridFS 读取文件
    const db = mongoose.connection.db;
    const bucket = new mongoose.mongo.GridFSBucket(db, { bucketName: 'uploads' });

    // 验证文件存在
    const files = await bucket.find({ _id: new mongoose.Types.ObjectId(task.idsFileId) }).toArray();
    if (files.length === 0) {
      return NextResponse.json(
        { error: "IDS 文件在数据库中不存在" },
        { status: 404 }
      );
    }

    const fileDoc = files[0];

    // 读取文件内容
    const downloadStream = bucket.openDownloadStream(new mongoose.Types.ObjectId(task.idsFileId));
    const chunks: Buffer[] = [];

    for await (const chunk of downloadStream) {
      chunks.push(chunk);
    }

    const fileContent = Buffer.concat(chunks).toString('utf-8');

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
    console.error("IDS 文件下载失败:", error);
    return NextResponse.json(
      { error: "服务器内部错误", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}
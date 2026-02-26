// app/api/tasks/[id]/download/route.ts
// IDS 文件下载 API

import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../../../backend/mongodb";
import { Resource } from "../../../../../backend/resource";
import { readFile, access } from "fs/promises";
import { constants } from "fs";

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

    // 检查任务状态
    if (task.status !== "completed") {
      return NextResponse.json(
        { error: "任务尚未完成，无法下载", status: task.status },
        { status: 400 }
      );
    }

    // 检查是否有 IDS 文件路径
    if (!task.idsFilePath) {
      return NextResponse.json(
        { error: "IDS 文件不存在" },
        { status: 404 }
      );
    }

    // 检查文件是否存在
    try {
      await access(task.idsFilePath, constants.F_OK);
    } catch {
      return NextResponse.json(
        { error: "IDS 文件在服务器上不存在", path: task.idsFilePath },
        { status: 404 }
      );
    }

    // 读取 IDS 文件
    const fileContent = await readFile(task.idsFilePath, "utf-8");

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
import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../../backend/mongodb";
import { Resource } from "../../../../backend/resource";
import { unlink, access } from "fs/promises";
import { constants } from "fs";

// Next.js 15 要求 params 必须是一个 Promise 类型
type ContextType = {
  params: Promise<{ id: string }>;
};

// GET: 获取单个任务详情
export async function GET(
  request: NextRequest,
  context: ContextType
) {
  try {
    await dbConnect();

    // 必须使用 await 来解析 params
    const { id } = await context.params;
    const taskId = id;

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

    return NextResponse.json({ task });
  } catch (error) {
    console.error("Get task detail error:", error);
    return NextResponse.json(
      { error: "服务器内部错误" },
      { status: 500 }
    );
  }
}

// DELETE: 删除任务（包括物理文件）
export async function DELETE(
  request: NextRequest,
  context: ContextType
) {
  try {
    await dbConnect();

    const { id } = await context.params;
    const taskId = id;

    if (!taskId) {
      return NextResponse.json(
        { error: "任务ID缺失" },
        { status: 400 }
      );
    }

    // 查找任务
    const task = await Resource.findById(taskId);

    if (!task) {
      return NextResponse.json(
        { error: "任务不存在" },
        { status: 404 }
      );
    }

    // 删除物理 IDS 文件（如果存在）
    if (task.idsFilePath) {
      try {
        await access(task.idsFilePath, constants.F_OK);
        await unlink(task.idsFilePath);
        console.log(`Deleted IDS file: ${task.idsFilePath}`);
      } catch (fileError) {
        // 文件不存在或删除失败，只记录日志，不阻止删除
        console.log(`IDS file not found or already deleted: ${task.idsFilePath}`);
      }
    }

    // 删除数据库记录
    await Resource.findByIdAndDelete(taskId);

    return NextResponse.json({
      success: true,
      message: "任务已删除"
    });
  } catch (error) {
    console.error("Delete task error:", error);
    return NextResponse.json(
      { error: "服务器内部错误" },
      { status: 500 }
    );
  }
}
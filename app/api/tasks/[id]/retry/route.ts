import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../../../backend/mongodb";
import { Resource } from "../../../../../backend/resource";

// Next.js 15 要求 params 必须是一个 Promise 类型
type ContextType = {
  params: Promise<{ id: string }>;
};

// POST: 重试失败的任务
export async function POST(
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

    // 检查任务状态
    if (task.status !== "failed") {
      return NextResponse.json(
        { error: "只有失败的任务才能重试" },
        { status: 400 }
      );
    }

    // 检查输入类型和内容
    if (task.input_type !== "text" || !task.inputText) {
      return NextResponse.json(
        { error: "任务类型不支持重试，请重新创建" },
        { status: 400 }
      );
    }

    // 重置状态为 pending，清除错误信息
    await Resource.findByIdAndUpdate(taskId, {
      $set: {
        status: "pending",
        errorMessage: null,
        idsFilePath: null,
      }
    });

    // 调用 Python 后端重新处理
    const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

    try {
      const response = await fetch(`${PYTHON_API_URL}/analyze-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resourceId: taskId,
          text: task.inputText,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Python service error on retry:", errorText);

        // 恢复失败状态
        await Resource.findByIdAndUpdate(taskId, {
          $set: {
            status: "failed",
            errorMessage: "重试失败: " + errorText,
          }
        });

        return NextResponse.json(
          { error: "重试失败，Python 服务调用失败" },
          { status: 500 }
        );
      }

      return NextResponse.json({
        success: true,
        message: "任务已重新提交处理",
        taskId: taskId
      });

    } catch (fetchError) {
      console.error("Failed to connect to Python service:", fetchError);

      // 恢复失败状态
      await Resource.findByIdAndUpdate(taskId, {
        $set: {
          status: "failed",
          errorMessage: "无法连接到 Python 分析服务",
        }
      });

      return NextResponse.json(
        { error: "无法连接到分析服务，请确保 Python 后端正在运行" },
        { status: 503 }
      );
    }

  } catch (error) {
    console.error("Retry task error:", error);
    return NextResponse.json(
      { error: "服务器内部错误" },
      { status: 500 }
    );
  }
}
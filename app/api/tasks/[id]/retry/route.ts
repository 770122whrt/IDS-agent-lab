import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../../../backend/mongodb";
import { Resource } from "../../../../../backend/resource";
import { rateLimit } from "../../../../lib/ratelimit";

// Next.js 15 要求 params 必须是一个 Promise 类型
type ContextType = {
  params: Promise<{ id: string }>;
};

// POST: Retry failed的任务
export async function POST(
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

    // 检查任务状态 - 支持 failed 和 check_failed
    if (task.status !== "failed" && task.status !== "check_failed") {
      return NextResponse.json(
        { error: "Only failed tasks can be retried" },
        { status: 400 }
      );
    }

    // 审查失败 (check_failed) 的重试逻辑 - 重置为 completed 状态，让用户重新上传 IFC
    if (task.status === "check_failed") {
      await Resource.findByIdAndUpdate(taskId, {
        $set: {
          status: "completed",
          errorMessage: null,
          ifcFileId: null,
          ifcFileName: null,
          reportData: null,
          reportSummary: null,
        }
      });

      return NextResponse.json({
        success: true,
        message: "Task reset to completed, please re-upload IFC file for review",
        taskId: taskId,
        retryType: "check_retry"
      });
    }

    // IDS 生成失败 (failed) 的重试逻辑 - 检查输入类型和内容
    if (task.input_type !== "text" || !task.inputText) {
      return NextResponse.json(
        { error: "Task type not supported for retry, please recreate" },
        { status: 400 }
      );
    }

    // 重置状态为 pending，清除错误信息
    await Resource.findByIdAndUpdate(taskId, {
      $set: {
        status: "pending",
        errorMessage: null,
        idsFileId: null,
        idsFileName: null,
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
            errorMessage: "Retry failed: " + errorText,
          }
        });

        return NextResponse.json(
          { error: "Retry failed, Python service call failed" },
          { status: 500 }
        );
      }

      return NextResponse.json({
        success: true,
        message: "Task re-submitted for processing",
        taskId: taskId,
        retryType: "ids_retry"
      });

    } catch (fetchError) {
      console.error("Failed to connect to Python service:", fetchError);

      // 恢复失败状态
      await Resource.findByIdAndUpdate(taskId, {
        $set: {
          status: "failed",
          errorMessage: "Cannot connect to Python analysis service",
        }
      });

      return NextResponse.json(
        { error: "Cannot connect to analysis service, ensure Python backend is running" },
        { status: 503 }
      );
    }

  } catch (error) {
    console.error("Retry task error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
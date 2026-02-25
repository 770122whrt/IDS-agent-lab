import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../backend/mongodb";
import { Resource } from "../../../backend/resource";

export async function POST(request: NextRequest) {
  try {
    await dbConnect();

    const { userId, text } = await request.json();

    if (!userId || !text) {
      return NextResponse.json(
        { error: "缺少必要参数: userId 或 text" },
        { status: 400 }
      );
    }

    // 1. 创建资源记录
    const newResource = await Resource.create({
      userId,
      originalname: `text_input_${Date.now()}`,
      mimetype: "text/plain",
      input_type: "text",
      inputText: text,
      status: "pending",
    });

    // 2. 调用 Python 后端进行分析
    const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

    try {
      const response = await fetch(`${PYTHON_API_URL}/analyze-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resourceId: newResource._id.toString(),
          text: text,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Python service error:", errorText);

        // 更新状态为失败
        await Resource.findByIdAndUpdate(newResource._id, {
          status: "failed",
          errorMessage: "Python服务调用失败: " + errorText,
        });

        return NextResponse.json(
          { error: "分析服务调用失败" },
          { status: 500 }
        );
      }

      return NextResponse.json({
        message: "文本分析任务已提交",
        resourceId: newResource._id.toString(),
      });
    } catch (fetchError) {
      console.error("Failed to connect to Python service:", fetchError);

      // 更新状态为失败
      await Resource.findByIdAndUpdate(newResource._id, {
        status: "failed",
        errorMessage: "无法连接到Python分析服务",
      });

      return NextResponse.json(
        { error: "无法连接到分析服务，请确保Python后端正在运行" },
        { status: 503 }
      );
    }
  } catch (error) {
    console.error("Analyze text route error:", error);
    return NextResponse.json(
      { error: "服务器内部错误" },
      { status: 500 }
    );
  }
}

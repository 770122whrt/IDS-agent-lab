import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../../backend/mongodb";
import { Resource } from "../../../../backend/resource";

// Next.js 15 要求 params 必须是一个 Promise 类型
type ContextType = {
  params: Promise<{ id: string }>;
};

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

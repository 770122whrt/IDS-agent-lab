import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../../backend/mongodb";
import { Resource } from "../../../../backend/resource";
import { rateLimit } from "../../../lib/ratelimit";

export async function POST(request: NextRequest) {
  // 速率限制检查
  const isAllowed = await rateLimit(request);
  if (!isAllowed) {
    return NextResponse.json({ error: "Rate limit exceeded, please try again later" }, { status: 429 });
  }

  try {
    // 1. 解析请求
    const { resourceId } = await request.json();
    if (!resourceId) {
      return NextResponse.json({ error: "Missing resourceId" }, { status: 400 });
    }

    // 2. 校验资源是否存在 (可选，也可以交给Python端校验)
    await dbConnect();
    const resource = await Resource.findById(resourceId);
    if (!resource) {
      return NextResponse.json({ error: "Resource not found" }, { status: 404 });
    }

    // 3. 呼叫 Python 服务
    // 如果你的 Python 和 Next.js 都在本地，用 localhost
    // 如果是用 Docker 部署，这里要改成容器名
    const PYTHON_API_URL = process.env.PYTHON_BACKEND_URL || process.env.PYTHON_API_URL || "http://localhost:8000";

    const response = await fetch(`${PYTHON_API_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resourceId }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Python service error:", errorText);
      return NextResponse.json({ error: "Failed to trigger analysis service" }, { status: 500 });
    }

    // 4. 成功返回
    return NextResponse.json({ message: "Analysis task submitted successfully" });

  } catch (error) {
    console.error("Analyze route error:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}

import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../../backend/mongodb";
//import { Resource } from "../../../../backend/resource";

export async function POST(request: NextRequest) {
  try {
    await dbConnect();
    const { resourceId } = await request.json();

    if (!resourceId) {
      return NextResponse.json({ error: "Missing resourceId" }, { status: 400 });
    }

    // 1. 调用 Python 服务
    // 假设 Python 服务跑在 localhost:8000
    const pythonServiceUrl = "http://localhost:8000/analyze";
    
    const pyRes = await fetch(pythonServiceUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resourceId }),
    });

    if (!pyRes.ok) {
        throw new Error("Failed to call Python service");
    }

    return NextResponse.json({ message: "Task submitted" });

  } catch (error) {
    console.error("Analysis trigger failed:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
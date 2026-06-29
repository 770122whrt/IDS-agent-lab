import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../backend/mongodb";
import { Resource } from "../../../backend/resource";
import { auth } from "../../lib/auth";
import { rateLimit } from "../../lib/ratelimit";

export async function POST(request: NextRequest) {
  // Rate limit check
  const isAllowed = await rateLimit(request);
  if (!isAllowed) {
    return NextResponse.json({ error: "Rate limit exceeded, please try again later" }, { status: 429 });
  }

  try {
    // Get current logged in user from session
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session?.user?.id) {
      return NextResponse.json({ error: "Not logged in, please login first" }, { status: 401 });
    }

    const userId = session.user.id;

    await dbConnect();

    const { text } = await request.json();

    if (!text) {
      return NextResponse.json(
        { error: "Missing required parameter: text" },
        { status: 400 }
      );
    }

    // 1. Create resource record
    const newResource = await Resource.create({
      userId,
      originalname: `text_input_${Date.now()}`,
      mimetype: "text/plain",
      input_type: "text",
      inputText: text,
      status: "pending",
    });

    // 2. Call Python backend for analysis
    const PYTHON_API_URL = process.env.PYTHON_BACKEND_URL || process.env.PYTHON_API_URL || "http://localhost:8000";

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

        // Update status to failed
        await Resource.findByIdAndUpdate(newResource._id, {
          status: "failed",
          errorMessage: "Python service call failed: " + errorText,
        });

        return NextResponse.json(
          { error: "Analysis service call failed" },
          { status: 500 }
        );
      }

      return NextResponse.json({
        message: "Text analysis task submitted",
        resourceId: newResource._id.toString(),
      });
    } catch (fetchError) {
      console.error("Failed to connect to Python service:", fetchError);

      // Update status to failed
      await Resource.findByIdAndUpdate(newResource._id, {
        status: "failed",
        errorMessage: "Cannot connect to Python analysis service",
      });

      return NextResponse.json(
        { error: "Cannot connect to analysis service, ensure Python backend is running" },
        { status: 503 }
      );
    }
  } catch (error) {
    console.error("Analyze text route error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

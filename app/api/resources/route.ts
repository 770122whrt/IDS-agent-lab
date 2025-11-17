import { NextRequest, NextResponse } from "next/server";
import { promises as fs } from "fs";
import path from "path";

const UPLOAD_DIR = path.join(process.cwd(), "uploads");

// 简单内存数据库模拟
let resources: Array<{
  id: string;
  userId: string;
  filename: string;
  originalname: string;
  uploadTime: string;
}> = [];

export async function POST(req: NextRequest) {
  const formData = await req.formData();
  const file = formData.get("file") as File;
  const userId = formData.get("userId") as string;
  if (!file || !userId) {
    return NextResponse.json({ error: "Missing file or userId" }, { status: 400 });
  }
  const arrayBuffer = await file.arrayBuffer();
  const buffer = Buffer.from(arrayBuffer);
  const filename = `${Date.now()}-${file.name}`;
  await fs.mkdir(UPLOAD_DIR, { recursive: true });
  await fs.writeFile(path.join(UPLOAD_DIR, filename), buffer);
  const meta = {
    id: filename,
    userId,
    filename,
    originalname: file.name,
    uploadTime: new Date().toISOString(),
  };
  resources.push(meta);
  return NextResponse.json({ success: true, meta });
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const userId = searchParams.get("userId");
  if (!userId) {
    return NextResponse.json({ error: "Missing userId" }, { status: 400 });
  }
  const userResources = resources.filter((r) => r.userId === userId);
  return NextResponse.json({ resources: userResources });
}

// app/api/resources/[id]/download/route.ts
import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../../../backend/mongodb";
import { Resource } from "../../../../../backend/resource";
import mongoose from "mongoose";
import { Readable } from "stream";
import { auth } from "../../../../lib/auth";
import { rateLimit } from "../../../../lib/ratelimit";


// 👇 修复问题1的潜在原因：强制动态渲染，告诉 Next.js 绝对不要缓存这个 GET 请求！
export const dynamic = 'force-dynamic';

// ---------------------------------------------------------
// GET 方法：通过 Resource 的 ID 下载对应的 GridFS 文件
// ---------------------------------------------------------
// ContextType 是 Next.js 提供的类型，用于获取路径参数 (params)

// 👇 修复问题2：Next.js 15 要求 params 必须是一个 Promise 类型
type ContextType = {
  params: Promise<{ id: string }>;
};

export async function GET(request: NextRequest, context: ContextType) {
  // 速率限制检查
  const isAllowed = await rateLimit(request, "resource");
  if (!isAllowed) {
    return NextResponse.json({ error: "Rate limit exceeded, please try again later" }, { status: 429 });
  }

  try {
    // 从 session 获取当前登录用户
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session?.user?.id) {
      return new NextResponse("请先登录", { status: 401 });
    }

    const currentUserId = session.user.id;

    // 0.连接database
    await dbConnect();
    const { params } = await context;

// 👇 修复问题2：必须使用 await 来解析 params
    const resolvedParams = await context.params;
    const resourceId = resolvedParams.id;
    if (!resourceId) {
      return new NextResponse("Resource ID is required", { status: 400 });
    }

    // 👇 修改点 1：解析 URL 上的查询参数 (e.g., ?type=result)
    const { searchParams } = new URL(request.url);
    const type = searchParams.get("type");

    // 2. 查找 Resource 记录，获取 GridFS 文件 ID
    // 为什么要查 Resource 表？因为 Resource 表记录了谁上传了哪个 GridFS 文件。
    const resource = await Resource.findById(resourceId);
    if (!resource) {
      return new NextResponse("Resource not found", { status: 404 });
    }

    // 验证当前用户是否有权限下载该文件
    if (resource.userId !== currentUserId) {
      return new NextResponse("无权下载此文件", { status: 403 });
    }


  // 👇 修改点 2：动态判断要下载的目标文件ID、文件名和 MIME 类型
    let targetFileId: mongoose.Types.ObjectId;
    let filename: string;
    let mimeType: string;

    if (type === "result") {
      // 当请求要求下载“结果”时
      if (!resource.resultFileId) {
        return new NextResponse("Analysis result not ready yet", { status: 404 });
      }
      targetFileId = resource.resultFileId; // 使用 Python 处理后存入的 resultFileId

      // 构造结果文件名，例如："原文件名(去后缀)_ids_result.json"
      const baseName = resource.originalname.replace(/\.[^/.]+$/, "");
      filename = `${baseName}_ids_result.json`;
      mimeType = "application/json"; // 结果是 JSON 格式
    } else {
      // 默认情况：下载用户最初上传的“原文件”
      targetFileId = resource.fileId;
      filename = resource.originalname;
      mimeType = resource.mimetype || "application/octet-stream";
    }



    // 3. Prepare GridFS Bucket
    const db = mongoose.connection.db;
    if (!db) throw new Error("Database connection not available");
    // Must use the same bucketName, otherwise the file cannot be found
    const bucket = new mongoose.mongo.GridFSBucket(db, {
      bucketName: "uploads",
    });

    // 4. 创建 GridFS 下载流
    // 为什么要用 fileId？因为这是文件在 GridFS 系统中被切片的唯一标识。
    const downloadStream = bucket.openDownloadStream(resource.fileId);

    // 5. 关键：将 Node.js Stream 转换为 Web Stream
    // Next.js (Edge/App Router) 倾向于使用 Web 标准的 ReadableStream。
    // Node.js Stream 需要适配。Readable.fromWeb(downloadStream) 可以实现这一转换。
    // 但是，直接将 Node Stream 传入 NextResponse 构造函数，Next.js 会自动处理转换。
    // Convert to Web Stream
    const webStream = Readable.toWeb(downloadStream);

    // 6. 设置响应头 (Response Headers)
    // 这是下载/预览的关键，告诉浏览器如何处理这个二进制流。
    const headers = new Headers();
    // Content-Type: 告诉浏览器文件类型 (如 image/jpeg, application/pdf)
    headers.set("Content-Type", resource.mimetype);
    // Content-Disposition: 决定浏览器行为
    // 'attachment' 会强制浏览器弹出下载对话框，或直接保存到默认下载目录。
    // 这解决了预览失败的问题，保证了文件的交付性。
    const dispositionType = 'attachment';
    // filename* 允许使用 UTF-8 编码的文件名
    headers.set(
      "Content-Disposition",
      `${dispositionType}; filename*=UTF-8''${encodeURIComponent(resource.originalname)}`
    );

    // 7. 返回流式响应
    // 为什么要用 NextResponse(body, ...)？
    // 这样做能够以流的方式发送数据。文件下载是边读边传，不会等整个文件加载到内存中再发送，
    // 极大地降低了服务器的内存占用，对于大文件至关重要。
    try {
      return new NextResponse(webStream as any, { headers });
    } finally {
      // 显式关闭 GridFS 流，防止资源泄漏
      downloadStream.destroy();
    }

  } catch (error) {
    console.error("File download failed:", error);
    return new NextResponse("File download failed", { status: 500 });
  }
}

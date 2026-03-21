// app/api/resources/route.ts
import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../backend/mongodb";
import { Resource } from "../../../backend/resource";

import mongoose from "mongoose";
import { Readable } from "stream";
import { auth } from "../../lib/auth";
import { rateLimit } from "../../lib/ratelimit";

// ---------------------------------------------------------
// 1. POST 方法：上传文件
// ---------------------------------------------------------
export async function POST(request: NextRequest) {
  // 速率限制检查
  const isAllowed = await rateLimit(request, "resource");
  if (!isAllowed) {
    return NextResponse.json({ error: "Rate limit exceeded, please try again later" }, { status: 429 });
  }

  try {
    // 1. 从 session 获取当前登录用户，而不是信任客户端参数
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session?.user?.id) {
      return NextResponse.json({ error: "Not logged in, please login first" }, { status: 401 });
    }

    const userId = session.user.id; // ✅ 使用服务端 session 中的用户 ID

    // 2. 确保数据库连接
    await dbConnect();
    
    // 2. 获取底层 MongoDB 数据库对象
    // 为什么要这么做？GridFS 是 MongoDB 原生驱动的功能，Mongoose 只是封装。
    // 我们需要拿到 raw db object 来创建 GridFSBucket。
    const db = mongoose.connection.db;
    if (!db) throw new Error("数据库连接异常");

    // 3. 解析 FormData（只获取文件，不获取 userId）
    const formData = await request.formData();
    const file = formData.get("file") as File | null;

    if (!file) {
      return NextResponse.json({ error: "Missing file parameter" }, { status: 400 });
    }

    // 4. 将文件转换为 Buffer
    // 注意：这里先把文件读入内存。对于极大文件(如 1GB+)，生产环境通常会用 stream pipe，
    // 但在 Next.js App Router 中处理 Web Stream 到 Node Stream 比较复杂，
    // 这里的 Buffer 方案对学习和几百 MB 的文件是安全的。
    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    // 5. 创建 GridFS 桶 (Bucket)
    // bucketName: 'uploads' 意味着文件会存到 uploads.files 和 uploads.chunks 两个集合里
    const bucket = new mongoose.mongo.GridFSBucket(db, {
      bucketName: 'uploads' 
    });

    // 6. 创建上传流并写入 GridFS
    // 这是一个 Promise 包装器，确保文件完全写完后再继续\
    // promise 会存在一个<mongoose.Types.ObjectId>的结果  resolve：”成功流完了，给你ID”  reject：等于说”管子爆了，报错”
    // 这是一个保险措施+获取ID的措施 重点在里面
    let uploadStream: mongoose.mongo.GridFSUploadStream | null = null;
    let readStream: NodeJS.ReadableStream | null = null;

    const fileId = await new Promise<mongoose.Types.ObjectId>((resolve, reject) => {
      // 创建一个写入流，文件名设为原始文件名 metadata为标签 为ID和类型
      uploadStream = bucket.openUploadStream(file.name, {
        metadata: { userId, contentType: file.type } // 把元数据也顺便存进 GridFS
      });

      // 将 Buffer 转为可读流，然后”管道”输送到 GridFS 的写入流
      readStream = Readable.from(buffer);

      readStream
        .pipe(uploadStream) // 把输入数据流接在进水口上
        .on('error', (error) => {
          // 确保出错时关闭流
          readStream?.destroy();
          uploadStream?.destroy();
          reject(error);
        })
        .on('finish', () => {
          // 写入完成，GridFS 会生成一个唯一的 _id
          // 我们需要把这个 ID 拿出来，存到我们要修改的 Resource 表里 回调给前面的promise -fileID
          resolve(uploadStream!.id as mongoose.Types.ObjectId);
        });
    });

    // 7. 在我们的 Resource 表中记录引用
    // 这里不再存 buffer，而是存 fileId
    const newResource = await Resource.create({
      userId,
      originalname: file.name,
      mimetype: file.type,
      fileId: fileId, // 👈 关键关联
    });

    return NextResponse.json(
      { message: "File uploaded successfully", resourceId: newResource._id },
      { status: 201 }
    );

  } catch (error) {
    console.error("GridFS upload failed:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

// ---------------------------------------------------------
// 2. GET 方法：获取当前用户的文件列表
// ---------------------------------------------------------
export async function GET(request: NextRequest) {
  // 速率限制检查
  const isAllowed = await rateLimit(request, "resource");
  if (!isAllowed) {
    return NextResponse.json({ error: "Rate limit exceeded, please try again later" }, { status: 429 });
  }

  try {
    // 1. 从 session 获取当前登录用户，而不是信任客户端参数
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session?.user?.id) {
      return NextResponse.json({ error: "Not logged in, please login first" }, { status: 401 });
    }

    const userId = session.user.id; // ✅ 使用服务端 session 中的用户 ID

    await dbConnect();

    // 2. 查询数据库
    // .find({ userId }) -> 找到该用户的所有文件
    // .sort({ uploadTime: -1 }) -> 按时间倒序排列（最新的在上面）
    const resources = await Resource.find({ userId })
      .sort({ uploadTime: -1 });

    // 3. 返回数据包裹
    return NextResponse.json({ resources });

  } catch (error) {
    console.error("Query failed:", error);
    return NextResponse.json({ error: "Failed to get list" }, { status: 500 });
  }
}
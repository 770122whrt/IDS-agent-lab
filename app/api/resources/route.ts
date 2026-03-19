// app/api/resources/route.ts
import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../backend/mongodb"; // 引入刚才修正过的数据库连接
import { Resource } from "../../../backend/resource"; // 引入刚才写的模型

import mongoose from "mongoose"; // 需要直接使用 mongoose 对象
import { Readable } from "stream"; // Node.js 原生流模块

// ---------------------------------------------------------
// 1. POST 方法：获取用户的文件列表
// ---------------------------------------------------------
export async function POST(request: NextRequest) {
  try {
    // 1. 确保数据库连接
    await dbConnect();
    
    // 2. 获取底层 MongoDB 数据库对象
    // 为什么要这么做？GridFS 是 MongoDB 原生驱动的功能，Mongoose 只是封装。
    // 我们需要拿到 raw db object 来创建 GridFSBucket。
    const db = mongoose.connection.db;
    if (!db) throw new Error("数据库连接异常");

    // 3. 解析 FormData
    const formData = await request.formData();
    const file = formData.get("file") as File | null;
    const userId = formData.get("userId") as string | null;

    if (!file || !userId) {
      return NextResponse.json({ error: "缺少参数" }, { status: 400 });
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
    // promise 会存在一个<mongoose.Types.ObjectId>的结果  resolve：“成功流完了，给你ID”  reject：等于说“管子爆了，报错”
    // 这是一个保险措施+获取ID的措施 重点在里面 
    const fileId = await new Promise<mongoose.Types.ObjectId>((resolve, reject) => {
      // 创建一个写入流，文件名设为原始文件名 metadata为标签 为ID和类型
      const uploadStream = bucket.openUploadStream(file.name, {
        metadata: { userId, contentType: file.type } // 把元数据也顺便存进 GridFS
      });

      // 将 Buffer 转为可读流，然后“管道”输送到 GridFS 的写入流
      const readStream = Readable.from(buffer);
      
      readStream
        .pipe(uploadStream) // 把输入数据流接在进水口上
        .on('error', (error) => reject(error)) //如果错误了 那么就触发reject
        .on('finish', () => {
          // 写入完成，GridFS 会生成一个唯一的 _id
          // 我们需要把这个 ID 拿出来，存到我们要修改的 Resource 表里 回调给前面的promise -fileID
          resolve(uploadStream.id as mongoose.Types.ObjectId);
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
      { message: "大文件上传成功", resourceId: newResource._id },
      { status: 201 }
    );

  } catch (error) {
    console.error("GridFS 上传失败:", error);
    return NextResponse.json(
      { error: "服务器内部错误" },
      { status: 500 }
    );
  }
}

// ---------------------------------------------------------
// 2. GET 方法：获取用户的文件列表
// ---------------------------------------------------------
export async function GET(request: NextRequest) {
  try {
    await dbConnect();

    // 1. 获取 URL 中的查询参数 ?userId=...
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get("userId");

    if (!userId) {
      return NextResponse.json({ error: "未提供用户ID" }, { status: 400 });
    }

    // 2. 查询数据库
    // .find({ userId }) -> 找到该用户的所有文件
    // .sort({ uploadTime: -1 }) -> 按时间倒序排列（最新的在上面）
    const resources = await Resource.find({ userId })
      .sort({ uploadTime: -1 });

    // 3. 返回数据包裹
    return NextResponse.json({ resources });

  } catch (error) {
    console.error("查询失败:", error);
    return NextResponse.json({ error: "获取列表失败" }, { status: 500 });
  }
}
// app/api/resources/route.ts
import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../backend/mongodb"; // 引入刚才修正过的数据库连接
import { Resource } from "../../../backend/resources"; // 引入刚才写的模型

// ---------------------------------------------------------
// 1. POST 方法：处理文件上传
// ---------------------------------------------------------
export async function POST(request: NextRequest) {
  try {
    // 1. 连接数据库
    await dbConnect();
    // 2. 解析前端传来的 FormData
    // Next.js App Router 提供了方便的 .formData() 方法
    const formData = await request.formData();
    
    // 获取字段（根据前端 append 的 key）
    const file = formData.get("file") as File | null;
    const userId = formData.get("userId") as string | null;

    // 3. 校验数据完整性
    if (!file || !userId) {
      return NextResponse.json(
        { error: "缺少文件或用户ID" },
        { status: 400 }
      );
    }

    // 4. 文件处理：将 Web File 对象转换为 Node.js Buffer
    // 数据库看不懂 File 对象，只能看懂二进制 Buffer
    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    // 5. 创建数据库记录
    const newResource = await Resource.create({
      userId,
      originalname: file.name,
      mimetype: file.type,
      buffer: buffer, // 把二进制数据存进去
    });

    // 6. 返回成功响应
    return NextResponse.json(
      { message: "上传成功", resourceId: newResource._id },
      { status: 201 }
    );

  } catch (error) {
    //提示出具体的错误内容
    console.error("上传失败:", error);
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
      .sort({ uploadTime: -1 })
      .select("-buffer");// .select("-buffer") -> ⚠️ 非常关键！ 列表页只需要文件名和 ID，不需要文件的具体二进制内容（buffer）。
    // 如果不加这一行，每次查询都会把几 MB 的文件内容全拉出来，网速会爆炸。

    // 3. 返回数据包裹
    return NextResponse.json({ resources });

  } catch (error) {
    console.error("查询失败:", error);
    return NextResponse.json({ error: "获取列表失败" }, { status: 500 });
  }
}
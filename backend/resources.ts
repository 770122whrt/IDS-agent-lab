// backend/Resource.ts
import { Schema, model, models } from 'mongoose';

const ResourceSchema = new Schema(
  {
    // 关联用户：存的是用户的 ID 字符串
    userId: { type: String, required: true },
    
    // 文件名：用于前端列表显示，例如 "resume.pdf"
    originalname: { type: String, required: true },
    
    // 文件类型：例如 "image/png"，浏览器预览时需要用到
    mimetype: { type: String, required: true },
    
    // 核心数据：将文件内容转为二进制 Buffer 存入数据库
    // 注意：MongoDB 单个文档最大限制 16MB，适合存头像、文档等小文件
    buffer: { type: Buffer, required: true },
    
    // 上传时间：默认当前时间
    uploadTime: { type: Date, default: Date.now },
  },
  { timestamps: true }
);

export const Resource = models?.Resource || model('Resource', ResourceSchema);
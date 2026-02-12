// backend/Resource.ts
import mongoose,{ Schema, model, models, Document } from 'mongoose';

export interface IResource extends Document {
  userId: string;
  originalname: string;
  mimetype: string;
  fileId: mongoose.Types.ObjectId; // 原始文件 ID
  uploadTime: Date;
  
  // 👇 新增字段
  status: 'pending' | 'processing' | 'completed' | 'failed'; // 任务状态
  resultFileId?: mongoose.Types.ObjectId; // 结果文件 ID (存放在 GridFS)
  errorMessage?: string; // 如果失败，记录错误信息
}

const ResourceSchema = new Schema<IResource>({
  userId: { type: String, required: true },
  originalname: { type: String, required: true },
  mimetype: { type: String, required: true },
  fileId: { type: Schema.Types.ObjectId, required: true },
  uploadTime: { type: Date, default: Date.now },
  
  // 👇 新增字段定义
  status: { 
    type: String, 
    enum: ['pending', 'processing', 'completed', 'failed'], 
    default: 'pending' 
  },
  resultFileId: { type: Schema.Types.ObjectId },
  errorMessage: { type: String }
});

// 防止重复定义模型
export const Resource = mongoose.models.Resource || mongoose.model<IResource>("Resource", ResourceSchema);
// backend/Resource.ts
import mongoose,{ Schema, model, models, Document } from 'mongoose';

export interface IResource extends Document {
  userId: string;
  originalname: string;
  mimetype: string;
  fileId?: mongoose.Types.ObjectId; // 原始文件 ID (文本输入时可选)
  uploadTime: Date;

  // 新增字段
  input_type: 'text' | 'ifc_file'; // 输入类型
  inputText?: string; // 原始文本内容（input_type为text时）
  status: 'pending' | 'processing' | 'pending_conversion' | 'completed' | 'failed'; // 任务状态
  resultJson?: object; // 结果JSON (直接存储，无需GridFS)
  idsFilePath?: string; // 生成的 .ids 文件物理路径
  errorMessage?: string; // 如果失败，记录错误信息
}

const ResourceSchema = new Schema<IResource>({
  userId: { type: String, required: true },
  originalname: { type: String, required: true },
  mimetype: { type: String, required: true },
  fileId: { type: Schema.Types.ObjectId }, // 文本输入时可选
  uploadTime: { type: Date, default: Date.now },

  // 新增字段定义
  input_type: {
    type: String,
    enum: ['text', 'ifc_file'],
    required: true
  },
  inputText: { type: String }, // 存储用户输入的文本
  status: {
    type: String,
    enum: ['pending', 'processing', 'pending_conversion', 'completed', 'failed'],
    default: 'pending'
  },
  resultJson: { type: Schema.Types.Mixed }, // 存储结果JSON对象
  idsFilePath: { type: String }, // 生成的 .ids 文件物理路径
  errorMessage: { type: String }
});

// 防止重复定义模型
export const Resource = mongoose.models.Resource || mongoose.model<IResource>("Resource", ResourceSchema);
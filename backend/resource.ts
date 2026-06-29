// backend/Resource.ts
import mongoose,{ Schema, model, models, Document } from 'mongoose';

export interface IResource extends Document {
  userId: string;
  originalname: string;
  mimetype: string;
  fileId?: mongoose.Types.ObjectId; // 原始文件 ID (文本输入时可选)
  uploadTime: Date;

  // 输入相关
  input_type: 'text' | 'ifc_file'; // 输入类型
  inputText?: string; // 原始文本内容（input_type为text时）

  // 任务状态
  status: 'pending' | 'processing' | 'pending_conversion' | 'completed' | 'checking' | 'checked' | 'check_failed' | 'failed';

  // IDS 生成相关 (存储在 GridFS 中)
  resultJson?: object; // Pipeline 生成的 JSON 结果
  idsFileId?: mongoose.Types.ObjectId; // IDS 文件在 GridFS 中的 ID
  idsFileName?: string; // IDS 文件名

  // IFC 审查相关 (存储在 GridFS 中)
  ifcFileId?: mongoose.Types.ObjectId; // IFC 文件在 GridFS 中的 ID
  ifcFileName?: string; // IFC 文件名

  // 审查报告 (直接存储 JSON)
  reportData?: object; // 完整的审查报告数据
  reportSummary?: {
    total_specs: number;
    passed_specs: number;
    failed_specs: number;
    total_failed_entities: number;
  };
  checkedAt?: Date; // 审查完成时间

  // 错误信息
  errorMessage?: string;
}

const ResourceSchema = new Schema<IResource>({
  userId: { type: String, required: true },
  originalname: { type: String, required: true },
  mimetype: { type: String, required: true },
  fileId: { type: Schema.Types.ObjectId }, // 文本输入时可选
  uploadTime: { type: Date, default: Date.now },

  // 输入相关
  input_type: {
    type: String,
    enum: ['text', 'ifc_file'],
    required: true
  },
  inputText: { type: String },

  // 任务状态
  status: {
    type: String,
    enum: ['pending', 'processing', 'pending_conversion', 'completed', 'checking', 'checked', 'check_failed', 'failed'],
    default: 'pending'
  },

  // IDS 生成相关 (GridFS 存储)
  resultJson: { type: Schema.Types.Mixed },
  idsFileId: { type: Schema.Types.ObjectId },
  idsFileName: { type: String },

  // IFC 审查相关 (GridFS 存储)
  ifcFileId: { type: Schema.Types.ObjectId },
  ifcFileName: { type: String },

  // 审查报告 (JSON 存储)
  reportData: { type: Schema.Types.Mixed },
  reportSummary: {
    total_specs: { type: Number },
    passed_specs: { type: Number },
    failed_specs: { type: Number },
    total_failed_entities: { type: Number }
  },
  checkedAt: { type: Date },

  // 错误信息
  errorMessage: { type: String }
});

// 防止重复定义模型
export const Resource = mongoose.models.Resource || mongoose.model<IResource>("Resource", ResourceSchema);

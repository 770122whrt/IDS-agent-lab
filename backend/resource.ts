// backend/Resource.ts
import { Schema, model, models } from 'mongoose';

const ResourceSchema = new Schema(
  {
    userId: { type: String, required: true },
    originalname: { type: String, required: true },
    mimetype: { type: String, required: true },
    
    // ✅ 新增 fileId 字段 删除buffer字段
    // 为什么要这么写？
    // 这个 ID 指向 GridFS 系统表(fs.files)里的那个文件。
    // 它是我们在应用层(Resource)和存储层(GridFS)之间的桥梁。
    fileId: { type: Schema.Types.ObjectId, required: true },
    
    uploadTime: { type: Date, default: Date.now },
  },
  { timestamps: true }
);

export const Resource = models?.Resource || model('Resource', ResourceSchema);
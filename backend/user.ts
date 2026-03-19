// Schema：to define the structure of documents in a collection
// model：to create and manage documents based on the schema
// models：to store all created models to avoid recompilation issues in serverless environments
import { Schema, model, models } from 'mongoose'

const UserSchema = new Schema(
  {
    // define the structure of the User document
    name: { type: String, required: true },
    email: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    image: { type: String, default: '' },
  },
  { timestamps: true }
)

// 核心修改：先检查 models 里有没有叫 'Users' 的，如果有就复用，没有才新建。
export const User = models?.Users || model('Users', UserSchema)


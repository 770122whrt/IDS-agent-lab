# Chapter 3 代码一致性检查报告

> 检查日期：2026/04/29
> 检查范围：`backend/package.json`、`ids-algo/requirements.txt`、`backend/src`结构、`ids-algo/c_knowledge_base_mapping`、MongoDB/GridFS 配置、`chapter_03_draft.md`

---

## 已验证的匹配项

- **Next.js**：`package.json` 依赖 `next: 15.3.2`，项目使用 App Router（`app/` 目录）。
- **TypeScript**：`package.json` 包含 `typescript: 5.7.3` 及类型定义包。
- **Tailwind CSS**：`package.json` 包含 `tailwindcss: ^3.4.0` 及相关插件。
- **FastAPI**：`ids-algo/requirements.txt` 包含 `fastapi>=0.109.0` 与 `uvicorn`。
- **ifcopenshell / ifctester**：均在 `requirements.txt` 中列出，且审查接口调用逻辑存在。
- **MongoDB**：`package.json` 包含 `mongoose` 与 `mongodb`，`backend/mongodb.ts` 实现连接。
- **GridFS**：`app/api/resources/route.ts` 与 `app/api/tasks/[id]/check/route.ts` 均使用 `mongoose.mongo.GridFSBucket` 存储 IFC/IDS 文件。
- **FAISS 向量检索**：`requirements.txt` 含 `faiss-cpu>=1.7.3`；`c_knowledge_base_mapping/vector_database/core/base.py` 直接基于 `faiss.IndexFlatIP` 实现向量库。
- **API 路由**：`app/api/` 下存在 `resources`、`tasks`、`auth`、`uploadthing` 等路由。
- **速率限制**：`app/lib/ratelimit.ts` 使用 `@upstash/ratelimit` 实现接口限流。

---

## 不匹配或夸大的声明

| 论文声明 | 实际代码情况 | 建议 |
|---|---|---|
| 前端"通过 **Axios** 库发起 HTTP 请求" | `package.json` **未引入 axios**，源码中无任何 `axios` 导入；前端使用原生 `fetch`。 | 改为"使用原生 `fetch` API"或补充引入 Axios。 |
| 用户认证"采用 **JWT 令牌机制**" | 实际使用 **`better-auth`**（Session Cookie + MongoDB Adapter），支持 OAuth（Google/GitHub）与邮箱密码登录；**无 JWT 相关代码**。 | 改为"基于 `better-auth` 的会话认证机制"，若需强调令牌可说明为 Session Token。 |
| 后端知识库"**LangChain** 框架...与 FAISS 向量数据库的集成" | `requirements.txt` **无 langchain**；源码中未导入 `langchain`；FAISS 与 `sentence-transformers` 均为**原生调用**。 | 删除 LangChain 描述，改为"基于 `sentence-transformers` 与 `faiss-cpu` 的原生向量检索实现"。 |

---

## 论文遗漏的重要实现细节

1. **UploadThing 文件托管**：`package.json` 包含 `uploadthing` 与 `@uploadthing/react`，并设有 `app/api/uploadthing` 路由；系统对部分文件（如图片）使用第三方 UploadThing 服务，而非全部存入 GridFS。
2. **认证库 better-auth**：论文未提及该库，也未提及 OAuth（Google/GitHub）登录与 Resend 邮件重置密码功能。
3. **Upstash Redis 限流**：`@upstash/ratelimit` + `@upstash/redis` 构成实际的安全防护层，论文在安全需求中仅泛谈"API 接口设置速率限制"，未指明技术实现。
4. **向量化模型 BGE-M3**：`vector_database/core/base.py` 默认使用 `BAAI/bge-m3` 嵌入模型，论文未说明具体模型选型。
5. **OpenAI API 直接调用**：`requirements.txt` 含 `openai>=2.8.1`，说明 LLM 调用大概率直接走 OpenAI SDK，而非通过 LangChain 封装。
6. **Next.js App Router**：论文仍使用"Next.js API Routes"这一偏 Pages Router 的表述，实际代码全部采用 App Router（`app/` 目录 + `route.ts`）。

---

## 修改建议

1. **3.2.2 / 3.3.1**：将"Axios"修正为"原生 `fetch` API"。
2. **3.2.2 / 3.2.3**：将"JWT 令牌机制"修正为"基于 `better-auth` 的会话认证（Session Cookie）"，并补充 OAuth 登录说明。
3. **3.3.2**：删除"LangChain"相关描述，补充 `sentence-transformers`、`faiss-cpu` 与 `BAAI/bge-m3` 模型选型依据。
4. **3.2.4 / 3.3.3**：在 GridFS 之外补充说明 UploadThing 用于部分文件上传，或统一描述为"MongoDB GridFS + UploadThing 混合存储"。
5. **3.1.2 安全性要求**：补充"基于 Upstash Redis 的速率限制"作为具体实现。
6. **术语统一**：将文中"Next.js API Routes"更新为"Next.js App Router API 端点"，以匹配项目实际结构。

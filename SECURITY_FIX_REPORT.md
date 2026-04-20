# 安全漏洞修复报告

> 生成日期：2026-03-19

---

## 一、问题概述

本次修复针对以下两个安全问题：

| 序号 | 问题描述 | 严重程度 |
|------|----------|----------|
| 1 | 密码重置功能未实现 | 中 |
| 2 | userId 信任客户端参数，可伪造 | 高 |

---

## 二、问题详情

### 1. 密码重置功能未实现

**文件位置**：`app/lib/auth.ts`

**问题说明**：
- `sendResetPassword` 函数仅为空实现，只打印日志
**原代码**：
```typescript
async sendResetPassword(data, request) {
  console.log("Password reset requested for:", data);
  // TODO: implement sending reset password email
},
```

---

### 2. userId 安全漏洞（IDOR）

**文件位置**：`app/api/resources/route.ts`

**问题说明**：
- 后端直接信任客户端传递的 `userId` 参数
- 攻击者可伪造任意用户 ID 来访问/上传文件

**原代码**：
```typescript
// POST 方法
const userId = formData.get("userId") as string | null;

// GET 方法
const userId = searchParams.get("userId");
```

---

## 三、修复方案

### 1. 密码重置功能

**修改文件**：`app/lib/auth.ts`

**修改内容**：
- 集成 Resend 邮件服务
- 添加环境变量验证
- 实现邮件发送逻辑

**新增代码**：
```typescript
import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

async sendResetPassword(data, request) {
  const resetUrl = `${NEXT_PUBLIC_APP_URL}/reset-password?token=${data.token}&email=${encodeURIComponent(data.email)}`;

  await resend.emails.send({
    from: "noreply@yourdomain.com",
    to: data.email,
    subject: "重置您的密码",
    html: `<p>点击链接重置密码：<a href="${resetUrl}">${resetUrl}</a></p>`
  });
},
```

**依赖安装**：
```bash
pnpm add resend
```

**环境变量**（.env）：
```
RESEND_API_KEY=re_xxx
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

### 2. userId 安全漏洞

#### 后端修复

**修改文件**：`app/api/resources/route.ts`

**修改内容**：
- 从 session 获取用户 ID，不再信任客户端输入
- 添加登录状态校验
- 移除客户端 userId 参数

**新增代码**：
```typescript
// 从 session 获取当前用户
const session = await auth.api.getSession({
  headers: request.headers,
});

if (!session?.user?.id) {
  return NextResponse.json({ error: "未登录，请先登录" }, { status: 401 });
}

const userId = session.user.id; // 使用服务端 session 中的用户 ID
```

#### 前端修复

**修改文件**：
- `app/ids_use/page.tsx`
- `app/tasks/page.tsx`

**修改内容**：
1. 移除 `formData.append("userId", ...)`
2. GET 请求移除 `?userId=xxx` 查询参数
3. 添加 `credentials: "include"` 确保发送 cookie
4. 使用 `session?.user?.id` 替代本地 userId 变量

---

## 四、环境变量配置

### .env.example

项目所需环境变量已更新至 `.env.example` 文件，请复制为本地 `.env` 并填入真实值：

```bash
# 复制命令（在项目根目录）
cp .env.example .env
```

#### 完整配置项：

```env
# ===================
# 应用基础配置
# ===================

# Node 环境
NEXT_PUBLIC_NODE_ENV=production

# 应用 URL（前端）
NEXT_PUBLIC_APP_URL=http://localhost:3000

# ===================
# 数据库
# ===================

# MongoDB 连接字符串
MONGODB_URI=mongodb://your-database-uri

# ===================
# 认证配置 (better-auth)
# ===================

# 用于加密 session 的密钥
BETTER_AUTH_SECRET=your-secret-key-here

# 应用基础 URL
BETTER_AUTH_URL=http://localhost:3000

# ===================
# OAuth 第三方登录
# ===================

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# ===================
# 邮件服务 (Resend)
# ===================

# Resend API Key（用于发送密码重置邮件）
RESEND_API_KEY=re_your-api-key-here

# ===================
# 文件上传 (UploadThing)
# ===================

UPLOADTHING_TOKEN=your-uploadthing-token-here
```

---

## 五、修改文件清单

| 文件路径 | 修改类型 |
|----------|----------|
| `app/lib/auth.ts` | 修改 |
| `app/api/resources/route.ts` | 修改 |
| `app/ids_use/page.tsx` | 修改 |
| `app/tasks/page.tsx` | 修改 |
| `package.json` | 修改（添加 resend 依赖） |

---

## 五、验证建议

### 1. 密码重置功能
- [ ] 访问忘记密码页面
- [ ] 输入注册邮箱
- [ ] 确认收到重置邮件
- [ ] 点击邮件中的链接能够重置密码

### 2. userId 安全漏洞
- [ ] 未登录状态下访问上传/列表接口返回 401
- [ ] 登录用户只能看到自己的文件
- [ ] 尝试伪造其他用户 ID 无法访问他人文件

---

## 六、总结

本次修复解决了两个重要的安全问题：

1. **密码重置功能**：通过集成 Resend 服务，实现了邮件发送功能
2. **IDOR 漏洞**：通过 session 验证，确保用户只能访问自己的资源

修复后，系统安全性得到显著提升。

---

# 安全漏洞修复报告（续）

> 生成日期：2026-03-20

---

## 一、本次修复概述

本次会话修复了以下安全问题：

| 序号 | 问题描述 | 严重程度 |
|------|----------|----------|
| 1 | 缺少安全响应头 (CSP 等) | 中 |
| 2 | 所有 API 无速率限制 | 高 |
| 3 | analyze-text 接口 userId 可伪造 | 高 |
| 4 | 文件/任务下载无权限验证 | 高 |
| 5 | GridFS 流未显式关闭 | 低 |

---

## 二、问题详情

### 1. 缺少安全响应头

**文件位置**：`next.config.mjs`

**问题说明**：
- 未配置 Content-Security-Policy (CSP)
- 未配置 X-Frame-Options
- 未配置 X-Content-Type-Options
- 容易受到 XSS、点击劫持等攻击

---

### 2. 所有 API 无速率限制

**文件位置**：所有 `app/api/**/route.ts` 文件

**问题说明**：
- 登录接口无防暴力破解限制
- 资源上传/下载无频率限制
- 攻击者可大量请求耗尽资源

**受影响的 API**：
- `/api/auth/*` - 登录/注册
- `/api/tasks/*` - 任务管理
- `/api/resources/*` - 文件操作
- `/api/analyze-*` - 分析功能

---

### 3. analyze-text 接口 userId 可伪造

**文件位置**：`app/api/analyze-text/route.ts`

**问题说明**：
- 与之前 resources 相同的 IDOR 漏洞
- 客户端可伪造任意 userId 创建分析任务

---

### 4. 文件/任务下载无权限验证

**文件位置**：
- `app/api/resources/[id]/download/route.ts`
- `app/api/tasks/[id]/download/route.ts`

**问题说明**：
- 任何登录用户可下载任意文件
- 未验证资源所有权

---

### 5. GridFS 流未显式关闭

**文件位置**：
- `app/api/resources/route.ts`
- `app/api/resources/[id]/download/route.ts`
- `app/api/tasks/[id]/download/route.ts`

**问题说明**：
- 流使用后未调用 `.destroy()`
- 可能导致资源泄漏

---

## 三、修复方案

### 1. 安全响应头

**修改文件**：`next.config.mjs`

```javascript
async headers() {
  return [
    {
      source: '/:path*',
      headers: [
        { key: 'Content-Security-Policy', value: "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://*.resend.com;" },
        { key: 'X-Frame-Options', value: 'DENY' },
        { key: 'X-Content-Type-Options', value: 'nosniff' },
        { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
      ],
    },
  ]
},
```

---

### 2. 速率限制

#### 2.1 安装依赖

```bash
pnpm add @upstash/ratelimit @upstash/redis
```

#### 2.2 创建速率限制辅助函数

**新增文件**：`app/lib/ratelimit.ts`

```typescript
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

// 通用速率限制器 - 10次/10秒
const通用速率限制 = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, "10 s"),
  prefix: "ratelimit:general",
});

// 登录相关速率限制 - 5次/1分钟
const登录速率限制 = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(5, "60 s"),
  prefix: "ratelimit:auth",
});

// 资源操作速率限制 - 20次/1分钟
const资源速率限制 = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(20, "60 s"),
  prefix: "ratelimit:resource",
});

export async function rateLimit(
  request: Request,
  type: "general" | "auth" | "resource" = "general"
) {
  const ip = request.headers.get("x-forwarded-for") || "unknown";
  const limiter = { general: 通用速率限制, auth: 登录速率限制, resource: 资源速率限制 }[type];
  const { success } = await limiter.limit(ip);
  return success;
}
```

#### 2.3 集成到各 API 路由

**修改的文件**：
- `app/api/resources/route.ts`
- `app/api/resources/[id]/download/route.ts`
- `app/api/resources/analyze/route.ts`
- `app/api/tasks/[id]/route.ts`
- `app/api/tasks/[id]/check/route.ts`
- `app/api/tasks/[id]/retry/route.ts`
- `app/api/tasks/[id]/download/route.ts`
- `app/api/analyze-text/route.ts`

**示例代码**：
```typescript
import { rateLimit } from "../../lib/ratelimit";

export async function POST(request: NextRequest) {
  // 速率限制检查
  const isAllowed = await rateLimit(request, "resource");
  if (!isAllowed) {
    return NextResponse.json({ error: "请求过于频繁，请稍后再试" }, { status: 429 });
  }
  // ... 正常逻辑
}
```

---

### 3. analyze-text 修复 userId 伪造

**修改文件**：`app/api/analyze-text/route.ts`

**修改内容**：
- 从 session 获取用户 ID
- 移除客户端传入的 userId 参数

```typescript
// 从 session 获取当前登录用户
const session = await auth.api.getSession({
  headers: request.headers,
});

if (!session?.user?.id) {
  return NextResponse.json({ error: "未登录，请先登录" }, { status: 401 });
}

const userId = session.user.id; // 使用服务端 session 中的用户 ID
```

---

### 4. 文件/任务下载权限验证

**修改文件**：
- `app/api/resources/[id]/download/route.ts`
- `app/api/tasks/[id]/download/route.ts`

**新增代码**：
```typescript
// 从 session 获取当前登录用户
const session = await auth.api.getSession({
  headers: request.headers,
});

if (!session?.user?.id) {
  return new NextResponse("请先登录", { status: 401 });
}

const currentUserId = session.user.id;

// ... 查询资源后验证所有权
if (resource.userId !== currentUserId) {
  return new NextResponse("无权下载此文件", { status: 403 });
}
```

---

### 5. GridFS 流显式关闭

**修改文件**：
- `app/api/resources/route.ts`
- `app/api/resources/[id]/download/route.ts`
- `app/api/tasks/[id]/download/route.ts`

**修复方式 - 下载流（try-finally）**：
```typescript
let fileContent: string;
try {
  const chunks: Buffer[] = [];
  for await (const chunk of downloadStream) {
    chunks.push(chunk);
  }
  fileContent = Buffer.concat(chunks).toString('utf-8');
} finally {
  downloadStream.destroy(); // 显式关闭
}
```

**修复方式 - 上传流（错误处理）**：
```typescript
readStream
  .pipe(uploadStream)
  .on('error', (error) => {
    readStream?.destroy();
    uploadStream?.destroy();
    reject(error);
  })
```

---

## 四、环境变量配置

### .env 新增配置

```env
# ===================
# 速率限制 (Upstash Redis)
# ===================

# Upstash Redis（用于 API 速率限制）
UPSTASH_REDIS_REST_URL=https://your-redis.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-redis-token-here
```

---

## 五、修改文件清单

| 文件路径 | 修改类型 |
|----------|----------|
| `next.config.mjs` | 修改（添加安全响应头） |
| `app/lib/ratelimit.ts` | 新增（速率限制辅助函数） |
| `package.json` | 修改（添加 @upstash/ratelimit 依赖） |
| `.env` | 修改（添加 Redis 配置） |
| `.env.example` | 修改（添加 Upstash 配置示例） |
| `app/api/resources/route.ts` | 修改（速率限制 + 流关闭） |
| `app/api/resources/[id]/download/route.ts` | 修改（速率限制 + 权限验证 + 流关闭） |
| `app/api/resources/analyze/route.ts` | 修改（速率限制） |
| `app/api/tasks/[id]/route.ts` | 修改（速率限制） |
| `app/api/tasks/[id]/check/route.ts` | 修改（速率限制） |
| `app/api/tasks/[id]/retry/route.ts` | 修改（速率限制） |
| `app/api/tasks/[id]/download/route.ts` | 修改（速率限制 + 权限验证 + 流关闭） |
| `app/api/analyze-text/route.ts` | 修改（速率限制 + userId 安全修复） |

---

## 六、验证建议

### 1. 安全响应头
- [ ] 使用浏览器开发者工具检查响应头
- [ ] 确认 CSP、X-Frame-Options 等头已设置

### 2. 速率限制
- [ ] 快速连续请求同一接口超过限制
- [ ] 确认返回 429 状态码

### 3. userId 安全修复
- [ ] 未登录状态访问接口返回 401
- [ ] 登录用户只能访问自己的资源

### 4. 下载权限验证
- [ ] 尝试访问其他用户的文件/任务
- [ ] 确认返回 403 禁止访问

### 5. GridFS 流关闭
- [ ] 多次上传/下载文件
- [ ] 检查 MongoDB 连接数是否正常

---

## 七、总结

本次修复显著提升了系统安全性：

1. **安全响应头**：防止 XSS、点击劫持等前端攻击
2. **速率限制**：防止暴力破解和 DDoS 攻击
3. **userId 安全**：确保用户只能操作自己的资源
4. **下载权限验证**：防止未授权访问
5. **资源管理**：防止 GridFS 流泄漏

所有修复已完成，系统安全性得到全面提升。

---

# 安全漏洞修复报告（续二）

> 生成日期：2026-03-21

---

## 一、本次修复概述

本次会话修复了以下安全问题：

| 序号 | 问题描述 | 严重程度 |
|------|----------|----------|
| 1 | 中英文混用错误信息 | 低 |
| 2 | 硬编码测试凭据 | 高 |
| 3 | mongoose.connection.db 缺少空值检查 | 中 |
| 4 | 状态更新存在竞态条件 | 中 |
| 5 | 缺少重置密码页面 | 中 |

---

## 二、问题详情

### 1. 中英文混用错误信息

**文件位置**：多个 API 路由文件

**问题说明**：
- API 错误信息中英文混用
- 影响前端日志解析和国际化为英文版本

**受影响的文件**：
- `app/api/analyze-text/route.ts`
- `app/api/tasks/[id]/route.ts`
- `app/api/resources/route.ts`
- `app/api/tasks/[id]/check/route.ts`
- `app/api/tasks/[id]/retry/route.ts`
- `app/api/resources/[id]/download/route.ts`
- `app/api/tasks/[id]/download/route.ts`
- `app/api/resources/analyze/route.ts`

---

### 2. 硬编码测试凭据

**文件位置**：
- `app/api/auth/[...all]/sign-in.ts`
- `app/api/auth/[...all]/sign-up.ts`

**问题说明**：
- 测试文件包含硬编码的测试邮箱和密码
- 生产环境可能误用这些凭据

**原代码**：
```typescript
// sign-in.ts
const email = "m@example.com";
const password = "123456";
const { data, error } = await authClient.signIn.email({
  email: "john.doe@example.com",
  password: "password1234",
});
```

---

### 3. mongoose.connection.db 缺少空值检查

**文件位置**：
- `app/api/tasks/[id]/route.ts`
- `app/api/tasks/[id]/check/route.ts`
- `app/api/resources/[id]/download/route.ts`
- `app/api/tasks/[id]/download/route.ts`

**问题说明**：
- 直接使用 `mongoose.connection.db` 而未检查空值
- 数据库连接未建立时会导致崩溃

**原代码**：
```typescript
const db = mongoose.connection.db;
const bucket = new mongoose.mongo.GridFSBucket(db, { bucketName: 'uploads' });
```

---

### 4. 状态更新存在竞态条件

**文件位置**：`app/api/tasks/[id]/check/route.ts`

**问题说明**：
- 两个用户同时对同一任务上传 IFC 文件
- 第二个请求会覆盖第一个请求的文件
- 没有使用事务或锁机制

**问题场景**：
```
用户A                    用户B                    数据库
  |                        |                        |
  |-- 检查 status=completed ---> OK                   |
  |-- 上传IFC, status=checking -->|                  |
  |                        |-- 检查 status=completed -> OK
  |                        |-- 上传IFC, status=checking ->|
  |                        |    (覆盖用户A的文件!)       |
```

---

### 5. 缺少重置密码页面

**文件位置**：无此页面

**问题说明**：
- 后端已实现密码重置邮件发送
- 但前端无 `/reset-password` 页面
- 用户无法完成密码重置流程

---

## 三、修复方案

### 1. 中英文混用错误信息修复

**修改内容**：将所有中文错误信息改为英文

| 原中文 | 修复后英文 |
|--------|------------|
| 请求过于频繁，请稍后再试 | Rate limit exceeded, please try again later |
| 未登录，请先登录 | Not logged in, please login first |
| 任务ID缺失 | Task ID missing |
| 任务不存在 | Task not found |
| 服务器内部错误 | Internal server error |
| 文件上传成功 | File uploaded successfully |
| 任务已删除 | Task deleted |

---

### 2. 硬编码测试凭据修复

**修改文件**：
- `app/api/auth/[...all]/sign-in.ts`
- `app/api/auth/[...all]/sign-up.ts`

**修改内容**：将实际登录代码替换为示例注释

```typescript
// sign-in.ts - 替换为示例注释
// Example usage (do not use in production):
// const { data, error } = await authClient.signIn.email({
//   email: "user@example.com",
//   password: "your-password",
//   callbackURL: "/dashboard",
//   rememberMe: false
// });

// For production, implement sign-in via the frontend form
```

---

### 3. mongoose.connection.db 空值检查

**修改文件**：
- `app/api/tasks/[id]/route.ts`
- `app/api/tasks/[id]/check/route.ts`
- `app/api/resources/[id]/download/route.ts`
- `app/api/tasks/[id]/download/route.ts`

**新增代码**：
```typescript
const db = mongoose.connection.db;
if (!db) throw new Error("Database connection not available");
const bucket = new mongoose.mongo.GridFSBucket(db, { bucketName: 'uploads' });
```

---

### 4. 竞态条件修复（分布式锁）

**修改文件**：`app/api/tasks/[id]/check/route.ts`

**修复方案**：使用原子性更新 + 临时锁标记

```typescript
// 使用 findOneAndUpdate 原子性检查并添加锁
const task = await Resource.findOneAndUpdate(
  { _id: taskId, status: "completed", idsFileId: { $exists: true, $ne: null } },
  { $set: { _checkLock: Date.now() } }, // 临时锁标记
  { new: true }
);

if (!task) {
  // 返回 409 Conflict
  return NextResponse.json(
    { error: "Task is being processed by another request" },
    { status: 409 }
  );
}

// ... 上传文件到 GridFS ...

// 使用锁验证后更新状态
const updatedTask = await Resource.findOneAndUpdate(
  { _id: taskId, _checkLock: task._checkLock },
  {
    $set: {
      ifcFileId: ifcFileId,
      ifcFileName: ifcFile.name,
      status: "checking"
    },
    $unset: { _checkLock: 1 }
  },
  { new: true }
);

if (!updatedTask) {
  // 清理已上传的文件
  await bucket.delete(new mongoose.Types.ObjectId(ifcFileId));
  return NextResponse.json(
    { error: "Task is being processed by another request, please try again" },
    { status: 409 }
  );
}
```

**返回状态码**：
| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 404 | 任务不存在 |
| 409 | 冲突 - 任务正在被其他请求处理 |
| 400 | 任务状态不对或参数错误 |

---

### 5. 重置密码页面创建

**新增文件**：`app/reset-password/page.tsx`

**页面功能**：
1. **步骤一**：请求重置邮件
   - 输入注册邮箱
   - 点击发送重置链接

2. **步骤二**：设置新密码（邮箱点击链接后）
   - 自动从 URL 获取 token 和 email
   - 输入新密码并确认
   - 提交完成重置

**修改文件**：
- `app/lib/auth-client.ts` - 导出 `resetPassword` 和 `sendResetPasswordEmail`
- `app/sign-in/page.tsx` - "Forgot password?" 链接指向 `/reset-password`

---

## 四、修改文件清单

| 文件路径 | 修改类型 |
|----------|----------|
| `app/api/analyze-text/route.ts` | 修改（错误信息英文） |
| `app/api/tasks/[id]/route.ts` | 修改（空值检查） |
| `app/api/resources/route.ts` | 修改（错误信息英文） |
| `app/api/tasks/[id]/check/route.ts` | 修改（空值检查 + 竞态条件） |
| `app/api/tasks/[id]/retry/route.ts` | 修改（错误信息英文） |
| `app/api/resources/[id]/download/route.ts` | 修改（空值检查） |
| `app/api/tasks/[id]/download/route.ts` | 修改（空值检查） |
| `app/api/resources/analyze/route.ts` | 修改（错误信息英文） |
| `app/api/auth/[...all]/sign-in.ts` | 修改（移除测试凭据） |
| `app/api/auth/[...all]/sign-up.ts` | 修改（移除测试凭据） |
| `app/reset-password/page.tsx` | 新增（重置密码页面） |
| `app/lib/auth-client.ts` | 修改（导出重置密码函数） |
| `app/sign-in/page.tsx` | 修改（链接修正 + 错误信息） |

---

## 五、验证建议

### 1. 中英文混用修复
- [ ] 所有 API 返回纯英文错误信息

### 2. 测试凭据清理
- [ ] 检查 sign-in.ts 和 sign-up.ts 不包含实际凭据

### 3. 空值检查
- [ ] 模拟数据库未连接场景
- [ ] 确认返回有意义的错误信息而非崩溃

### 4. 竞态条件
- [ ] 模拟两个用户同时上传 IFC 文件
- [ ] 确认第二个请求返回 409 冲突

### 5. 重置密码
- [ ] 访问 /reset-password 页面
- [ ] 输入邮箱请求重置
- [ ] 点击邮件链接设置新密码

---

## 六、总结

本次修复进一步提升了系统安全性：

1. **错误信息国际化**：统一使用英文，便于日志分析和国际化
2. **凭据安全**：移除硬编码测试凭据，防止误用
3. **空值检查**：防止数据库连接异常导致崩溃
4. **并发安全**：防止竞态条件导致数据覆盖
5. **功能完善**：补全密码重置功能

系统安全性已全面提升，所有已知问题已修复完成。
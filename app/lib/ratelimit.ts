import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

// 通用速率限制器 - 10次/10秒
const通用速率限制 = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, "10 s"),
  prefix: "ratelimit:general",
});

// 登录相关速率限制 - 5次/1分钟（防止暴力破解）
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

  const limiter = {
    general: 通用速率限制,
    auth: 登录速率限制,
    resource: 资源速率限制,
  }[type];

  const { success } = await limiter.limit(ip);

  return success;
}
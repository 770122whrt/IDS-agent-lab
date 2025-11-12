import { authClient } from "../../../lib/auth-client";

// 示例：先定义变量
const email = "user@example.com";
const password = "mypassword123";
const name = "Test User";
const image = "https://example.com/avatar.png";

try {
  const { data, error } = await authClient.signUp.email(
    {
      email,        // 用户邮箱
      password,     // 密码（至少8字符）
      name,         // 显示名
      image,        // 可选头像URL
      callbackURL: "/dashboard", // 邮箱验证后重定向
    },
    {
      onRequest: () => {
        console.log("⏳ 正在注册...");
      },
      onSuccess: (ctx) => {
        console.log("✅ 注册成功！");
        console.log(ctx.data);
        // 这里可以做跳转逻辑，比如 window.location.href = "/dashboard"
      },
      onError: (ctx) => {
        console.error("❌ 注册失败：", ctx.error.message);
      },
    }
  );

  // 如果你想手动使用 data/error：
  if (error) {
    console.error("注册出错:", error);
  } else {
    console.log("注册成功，返回数据:", data);
  }
} catch (err) {
  console.error("意外错误:", err);
}

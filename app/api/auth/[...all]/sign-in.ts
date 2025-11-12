import { authClient } from "../../../lib/auth-client";

const email = "m@example.com";
const password = "123456";

const { data, error } = await authClient.signIn.email({
  email,
  password,
  callbackURL: "/dashboard",
  rememberMe: false,
}, {});

// 使用返回结果
if (error) {
  console.error("登录失败:", error);
} else {
  console.log("登录成功:", data);
}

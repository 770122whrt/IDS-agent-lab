import { authClient } from "../../../lib/auth-client";

<<<<<<< HEAD
const { data, error } = await authClient.signUp.email({
        email: "john.doe@example.com",// user email address get from front
        password:"password1234", // user password -> min 8 characters by default get from front
        name: "John Doe", // user display name get from front
        //image:"https://example.com/image.png", // User image URL (optional)
        callbackURL: "/dashboard" // A URL to redirect to after the user verifies their email (optional)
    }, {
        onRequest: (ctx) => {
            //show loading
        },
        onSuccess: (ctx) => {
            //redirect to the dashboard or sign in page
        },
        onError: (ctx) => {
            // display the error message
            alert(ctx.error.message);
        },
});
=======
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
>>>>>>> origin/branch1

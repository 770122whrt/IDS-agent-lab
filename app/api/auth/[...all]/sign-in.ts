import { authClient } from "../../../lib/auth-client";

const email = "m@example.com";
const password = "123456";

const { data, error } = await authClient.signIn.email({
  email,
  password,
  callbackURL: "/dashboard",
  rememberMe: false,
}, {});

// use data and error as needed
if (error) {
  console.error("fail to sign in:", error);
} else {
  console.log("Sign in successful:", data);
}

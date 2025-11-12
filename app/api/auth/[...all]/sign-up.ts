import { authClient } from "../../../lib/auth-client";

// User details for sign-up
const email = "user@example.com";
const password = "mypassword123";
const name = "Test User";
const image = "https://example.com/avatar.png";

try {
  const { data, error } = await authClient.signUp.email(
    {
      email,        // 
      password,     // at least 6 characters
      name,         // 
      image,        // 
      callbackURL: "/dashboard", // redirect after sign-up
    },
    {
      onRequest: () => {
        console.log("Signing up...");
      },
      onSuccess: (ctx) => {
        console.log("Sign up successful!");
        console.log(ctx.data);
      },
      onError: (ctx) => {
        console.error("fail to sign up:", ctx.error.message);
      },
    }
  );

  if (error) {
    console.error("fail to sign up:", error);
  } else {
    console.log("Sign up successful, returned data:", data);
  }
} catch (err) {
  console.error("Unexpected error:", err);
}

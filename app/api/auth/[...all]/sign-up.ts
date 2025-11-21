import { email } from "better-auth";
import { authClient } from "../../../lib/auth-client";

<<<<<<< HEAD
const { data, error } = await authClient.signUp.email({
        email: email,// user email address get from front
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
// User details for sign-up
const email = "user@example.com";
const password = "mypassword123";
const name = "Test User";
const image = "https://example.com/avatar.png";

try {
  const { data, error } = await authClient.signUp.email(
    {
      email,        // 
      password,     // at least 8 characters
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
>>>>>>> c1de285f9d20cb790eb6f20d1109fbc45675668b

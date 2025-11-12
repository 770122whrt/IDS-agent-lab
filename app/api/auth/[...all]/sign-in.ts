import { authClient } from "../../../lib/auth-client";

const email = "m@example.com";
const password = "123456";

const { data, error } = await authClient.signIn.email({
<<<<<<< HEAD
        /**
         * The user email
         */
        email: "john.doe@example.com",
        /**
         * The user password
         */
        password:"password1234",
        /**
         * A URL to redirect to after the user verifies their email (optional)
         */
        callbackURL: "/dashboard",
        /**
         * remember the user session after the browser is closed. 
         * @default true
         */
        rememberMe: false
}, {
    //callbacks
})



await authClient.signIn.social({
    /**
     * The social provider ID
     * @example "github", "google", "apple"
     */
    provider: "github",
    /**
     * A URL to redirect after the user authenticates with the provider
     * @default "/"
     */
    callbackURL: "/dashboard", 
    /**
     * A URL to redirect if an error occurs during the sign in process
     */
    errorCallbackURL: "/error",
    /**
     * A URL to redirect if the user is newly registered
     */
    newUserCallbackURL: "/welcome",
    /**
     * disable the automatic redirect to the provider. 
     * @default false
     */
    disableRedirect: true,
});
=======
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
>>>>>>> origin/branch1

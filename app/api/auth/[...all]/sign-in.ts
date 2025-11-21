import { authClient } from "../../../lib/auth-client";

const email = "m@example.com";
const password = "123456";

const { data, error } = await authClient.signIn.email({
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

<<<<<<< HEAD


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
// use data and error as needed
if (error) {
  console.error("fail to sign in:", error);
} else {
  console.log("Sign in successful:", data);
}
>>>>>>> c1de285f9d20cb790eb6f20d1109fbc45675668b

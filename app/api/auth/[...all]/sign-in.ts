import { authClient } from "../../../lib/auth-client";
import { defaultLocale } from "@/i18n/config";

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
        callbackURL: `/${defaultLocale}/dashboard`,
        /**
         * remember the user session after the browser is closed. 
         * @default true
         */
        rememberMe: false
}, {
    //callbacks
})

// use data and error as needed
if (error) {
  console.error("fail to sign in:", error);
} else {
  console.log("Sign in successful:", data);
}

import { authClient } from "../../../lib/auth-client"; //import the auth client

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
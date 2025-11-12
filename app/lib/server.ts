import { auth } from "./auth"; // path to your Better Auth server instance
const response = await auth.api.signInEmail({
    body: {
        email:'11',
        password:'11'
    },
    asResponse: true // returns a response object instead of data
});


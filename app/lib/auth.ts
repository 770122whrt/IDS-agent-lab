import { betterAuth, BetterAuthAdvancedOptions, BetterAuthClientOptions } from "better-auth";
import { MongoClient } from "mongodb";
import { mongodbAdapter } from "better-auth/adapters/mongodb";

if (!process.env.MONGODB_URI) {
    throw new Error("MONGODB_URI environment variable is required");
}
const client = new MongoClient(process.env.MONGODB_URI);
await client.connect();
const db = client.db();

export const auth = betterAuth({
    database: mongodbAdapter(db, {client}),
    emailAndPassword: {
        enabled: true,
        autoSignIn: false,
        async sendResetPassword(data, request) {
            // Send an email to the user with a link to reset their password
        },
    },
    socialProviders: {
        google: {
            clientId: process.env.GOOGLE_CLIENT_ID!,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET!
        },
        github: {
            clientId: process.env.GITHUB_CLIENT_ID!,
            clientSecret: process.env.GITHUB_CLIENT_SECRET!
        }
    },

    /** if no database is provided, the user data will be stored in memory.
     * Make sure to provide a database to persist user data **/
});


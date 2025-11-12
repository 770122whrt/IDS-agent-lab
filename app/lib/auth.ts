import { betterAuth } from "better-auth";
import { MongoClient } from "mongodb";
import { mongodbAdapter } from "better-auth/adapters/mongodb";

const { 
  MONGODB_URI, 
  GOOGLE_CLIENT_ID, 
  GOOGLE_CLIENT_SECRET, 
  GITHUB_CLIENT_ID, 
  GITHUB_CLIENT_SECRET 
} = process.env;

if (!MONGODB_URI) {
  throw new Error("❌ MONGODB_URI environment variable is required");
}
if (!GOOGLE_CLIENT_ID || !GOOGLE_CLIENT_SECRET) {
  throw new Error("❌ Google OAuth credentials are missing");
}
if (!GITHUB_CLIENT_ID || !GITHUB_CLIENT_SECRET) {
  throw new Error("❌ GitHub OAuth credentials are missing");
}

const client = new MongoClient(MONGODB_URI);
await client.connect();
const db = client.db();

export const auth = betterAuth({
  database: mongodbAdapter(db, { client }),
  emailAndPassword: {
    enabled: true,
    autoSignIn: false,
    async sendResetPassword(data, request) {
      // TODO: implement sending password reset email
    },
  },
  socialProviders: {
    google: {
      clientId: GOOGLE_CLIENT_ID,
      clientSecret: GOOGLE_CLIENT_SECRET,
    },
    github: {
      clientId: GITHUB_CLIENT_ID,
      clientSecret: GITHUB_CLIENT_SECRET,
    },
  },
});

import { betterAuth } from "better-auth";
import { MongoClient } from "mongodb";
import { mongodbAdapter } from "better-auth/adapters/mongodb";

const {
  MONGODB_URI,
  GOOGLE_CLIENT_ID,
  GOOGLE_CLIENT_SECRET,
  GITHUB_CLIENT_ID,
  GITHUB_CLIENT_SECRET,
} = process.env;

if (!MONGODB_URI) throw new Error("❌ Missing MONGODB_URI");
if (!GOOGLE_CLIENT_ID || !GOOGLE_CLIENT_SECRET) throw new Error("❌ Missing Google OAuth credentials");
if (!GITHUB_CLIENT_ID || !GITHUB_CLIENT_SECRET) throw new Error("❌ Missing GitHub OAuth credentials");

const client = new MongoClient(MONGODB_URI);
await client.connect();
const db = client.db();

export const auth = betterAuth({
  database: mongodbAdapter(db, { client }),
  emailAndPassword: {
    enabled: true,
    autoSignIn: true, //auto sign in users after they sign up

    async sendResetPassword(data, request) {
      console.log("Password reset requested for:", data.email);
      // TODO: implement sending reset password email
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

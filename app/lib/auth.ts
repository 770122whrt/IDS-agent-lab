import { betterAuth, BetterAuthAdvancedOptions, BetterAuthClientOptions } from "better-auth";
import { MongoClient } from "mongodb";
import { mongodbAdapter } from "better-auth/adapters/mongodb";
import { Resend } from "resend";
import { defaultLocale } from "@/i18n/config";

const {
  MONGODB_URI,
  GOOGLE_CLIENT_ID,
  GOOGLE_CLIENT_SECRET,
  GITHUB_CLIENT_ID,
  GITHUB_CLIENT_SECRET,
  RESEND_API_KEY,
  NEXT_PUBLIC_APP_URL,
} = process.env;

if (!MONGODB_URI) throw new Error("❌ Missing MONGODB_URI");
if (!GOOGLE_CLIENT_ID || !GOOGLE_CLIENT_SECRET) throw new Error("❌ Missing Google OAuth credentials");
if (!GITHUB_CLIENT_ID || !GITHUB_CLIENT_SECRET) throw new Error("❌ Missing GitHub OAuth credentials");
if (!RESEND_API_KEY) throw new Error("❌ Missing RESEND_API_KEY");
if (!NEXT_PUBLIC_APP_URL) throw new Error("❌ Missing NEXT_PUBLIC_APP_URL");

const resend = new Resend(RESEND_API_KEY);

const client = new MongoClient(MONGODB_URI);
const db = client.db();

export const auth = betterAuth({
  database: mongodbAdapter(db, { client }),
  emailAndPassword: {
    enabled: true,
    autoSignIn: true, //auto sign in users after they sign up

    async sendResetPassword(data, request) {
      const email = data.user.email;
      const resetUrl = `${NEXT_PUBLIC_APP_URL}/${defaultLocale}/reset-password?token=${data.token}&email=${encodeURIComponent(email)}`;

      await resend.emails.send({
        from: "noreply@yourdomain.com",
        to: email,
        subject: "重置您的密码",
        html: `
          <h1>密码重置请求</h1>
          <p>您好，我们收到了您的密码重置请求。</p>
          <p>请点击以下链接重置您的密码：</p>
          <a href="${resetUrl}" style="display: inline-block; padding: 12px 24px; background-color: #0070f3; color: white; text-decoration: none; border-radius: 4px;">重置密码</a>
          <p>该链接将在 1 小时后过期。</p>
          <p>如果您没有请求重置密码，请忽略此邮件。</p>
        `
      });
      console.log("Password reset email sent to:", email);
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

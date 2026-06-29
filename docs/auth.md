# Authentication

The app uses Better Auth with MongoDB storage, email/password authentication, password reset email, and GitHub/Google OAuth providers.

## Required Variables

Set these variables in the Next.js environment:

```env
NEXT_PUBLIC_APP_URL=https://your-app.example.com
BETTER_AUTH_URL=https://your-app.example.com
BETTER_AUTH_SECRET=replace-with-a-strong-secret
MONGODB_URI=mongodb://...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
RESEND_API_KEY=...
```

`NEXT_PUBLIC_APP_URL` is used when generating password reset links. `BETTER_AUTH_URL` should match the deployed app origin.

## OAuth Callback Setup

Configure the OAuth applications with callback URLs under the deployed app origin. The Better Auth route is mounted at:

```text
/api/auth/[...all]
```

Use the same public origin in the provider console and the deployed environment variables.

## Password Reset Email

Password reset email is sent through Resend. The current sender is configured in `app/lib/auth.ts`. Before production, replace the placeholder sender domain with a verified Resend domain.

## Deployment Checklist

- Generate a strong `BETTER_AUTH_SECRET`.
- Set the same `MONGODB_URI` used by the rest of the app.
- Verify GitHub and Google OAuth credentials in the deployment environment.
- Verify the Resend API key and sender domain.
- Test sign up, sign in, OAuth sign in, and password reset after deployment.

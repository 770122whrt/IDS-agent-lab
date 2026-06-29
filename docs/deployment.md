# Deployment Guide

This guide covers the minimum deployment path for the IDS Agent application.

## Services

Deploy two services:

| Service | Entry Point | Default Port | Responsibility |
| --- | --- | --- | --- |
| Next.js app | `pnpm start` | `3000` | UI, authentication, uploads, task APIs, downloads. |
| Python API | `python ids-algo/server.py` | `8000` | IDS generation, text analysis, IFC checking. |

Both services must use the same `MONGODB_URI`.

## Required Environment Variables

Set these variables for the Next.js app:

```env
NEXT_PUBLIC_APP_URL=https://your-app.example.com
BETTER_AUTH_URL=https://your-app.example.com
BETTER_AUTH_SECRET=replace-with-a-strong-secret
MONGODB_URI=mongodb://...
PYTHON_BACKEND_URL=https://your-python-api.example.com
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
RESEND_API_KEY=...
UPLOADTHING_TOKEN=...
UPSTASH_REDIS_REST_URL=...
UPSTASH_REDIS_REST_TOKEN=...
```

Set these variables for the Python API:

```env
MONGODB_URI=mongodb://...
OPENROUTER_API_KEY=...
```

Keep real secrets in the deployment provider's secret manager. Do not commit runtime `.env` files.

## Build And Verify

From the repository root:

```bash
pnpm install
pnpm build
python -m compileall ids-algo ids_converter ifc_checker
```

From `ids-algo/`:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

Check the Python API:

```bash
curl http://localhost:8000/health
```

Then start the web app:

```bash
pnpm start
```

## Runtime Checks

After deployment, verify:

- Sign in and sign up pages load.
- OAuth providers redirect back to the deployed app URL.
- A text analysis request creates a resource and task.
- A file upload creates a resource and can be analyzed.
- IDS and report downloads work for completed tasks.
- IFC checking can call the Python `/check-ifc` endpoint.

## Operational Notes

- `PYTHON_BACKEND_URL` must be reachable from the Next.js server environment, not only from the user's browser.
- The Python service stores and reads task/resource state through MongoDB, so database connectivity is part of the health of both services.
- The app requires Resend configuration during module initialization because password reset email is part of auth setup.
- `next build` is configured to skip ESLint for deployment builds. Run lint separately before enforcing lint as a release gate.

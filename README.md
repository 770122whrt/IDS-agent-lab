# IDS Agent

IDS Agent is a web application for creating, managing, and checking IDS files. It combines a Next.js frontend/API layer with a Python FastAPI service that runs the IDS generation and IFC checking pipeline.

## What Is Included

- Next.js 15 application with dashboard, authentication, upload, task, and report pages.
- API routes for resources, task management, IDS download, IFC check triggering, and UploadThing integration.
- Python IDS pipeline in `ids-algo/`, including structured parsing, facet classification, knowledge-base mapping, constraint extraction, IDS building, and IFC checking.
- IDS converter utilities in `ids_converter/`.
- MongoDB-backed resource and task metadata storage.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `app/` | Next.js App Router pages and API routes. |
| `backend/` | MongoDB connection and Mongoose models. |
| `components/` | Shared UI components. |
| `i18n/` | English and Chinese UI messages. |
| `ids-algo/` | Python FastAPI service and IDS generation pipeline. |
| `ids_converter/` | IDS parsing, conversion, and template utilities. |
| `ifc_checker/` | IFC checking service integration. |
| `docs/` | Deployment and service configuration notes. |

## Requirements

- Node.js `^18.20.2` or `>=20.9.0`
- pnpm `^9` or `^10`
- Python 3.10 or newer
- MongoDB instance
- UploadThing token
- Resend API key
- Upstash Redis REST credentials
- GitHub and Google OAuth credentials

## Environment

Copy `.env.example` to `.env` and fill in real values:

```bash
cp .env.example .env
```

The most important variables are:

| Variable | Used By | Notes |
| --- | --- | --- |
| `NEXT_PUBLIC_APP_URL` | Next.js, Better Auth email links | Public application URL. |
| `BETTER_AUTH_URL` | Better Auth | Usually the same origin as `NEXT_PUBLIC_APP_URL`. |
| `BETTER_AUTH_SECRET` | Better Auth | Generate a strong secret before deployment. |
| `MONGODB_URI` | Next.js and Python service | Both services must point at the same database. |
| `PYTHON_BACKEND_URL` | Next.js API routes | URL of the FastAPI service, for example `http://localhost:8000`. |
| `UPLOADTHING_TOKEN` | UploadThing | Required for upload routes. |
| `RESEND_API_KEY` | Password reset email | Required by the auth module. |
| `UPSTASH_REDIS_REST_URL` / `UPSTASH_REDIS_REST_TOKEN` | Rate limiting | Required by `app/lib/ratelimit.ts`. |

Do not commit `.env`, `.env.local`, or `ids-algo/.env-pipeline`.

## Local Development

Install JavaScript dependencies:

```bash
pnpm install
```

Install Python dependencies:

```bash
cd ids-algo
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Start the Python service:

```bash
cd ids-algo
python server.py
```

Start the Next.js app in another terminal:

```bash
pnpm dev
```

Open `http://localhost:3000`.

## Production Build

Run the web build before deployment:

```bash
pnpm build
```

Run Python syntax validation:

```bash
python -m compileall ids-algo ids_converter ifc_checker
```

The production web server is started with:

```bash
pnpm start
```

The Python service must also be running and reachable from `PYTHON_BACKEND_URL`.

## Deployment Notes

- Deploy the Next.js app and Python FastAPI service as separate processes.
- Set the same `MONGODB_URI` in both services.
- Keep the Python service URL stable; Next.js API routes call `/analyze`, `/analyze-text`, and `/check-ifc`.
- Configure OAuth callback URLs in GitHub and Google to match the deployed app origin.
- Keep UploadThing, Resend, Upstash, and MongoDB credentials in the deployment platform's secret store.
- Build currently skips ESLint during `next build`; run lint separately when tightening code quality.

More detailed deployment notes are in [docs/deployment.md](docs/deployment.md).

## Related Docs

- [Deployment](docs/deployment.md)
- [Authentication](docs/auth.md)
- [Upload and Resource Flow](docs/upload.md)

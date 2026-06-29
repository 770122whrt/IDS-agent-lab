# Upload And Resource Flow

The app uses UploadThing for file uploads and MongoDB for resource/task metadata. Uploaded resources can be sent to the Python service for IDS analysis and IFC checking.

## Required Variables

Set these variables in the Next.js environment:

```env
UPLOADTHING_TOKEN=...
MONGODB_URI=mongodb://...
PYTHON_BACKEND_URL=https://your-python-api.example.com
```

Some routes also accept `PYTHON_API_URL` as a legacy fallback, but new deployments should use `PYTHON_BACKEND_URL`.

## Resource Lifecycle

1. The user uploads or submits content through the web app.
2. Next.js creates a resource record in MongoDB.
3. Analysis routes call the Python service:
   - `POST /analyze` for uploaded file analysis.
   - `POST /analyze-text` for text-based analysis.
   - `POST /check-ifc` for IFC checking.
4. The Python service updates MongoDB with task status and generated artifacts.
5. Next.js download routes stream generated IDS/report files back to the user.

## Important Routes

| Route | Purpose |
| --- | --- |
| `POST /api/resources` | Create a resource record. |
| `GET /api/resources` | List the current user's resources. |
| `POST /api/resources/analyze` | Start analysis for an uploaded resource. |
| `POST /api/analyze-text` | Start analysis from text input. |
| `GET /api/resources/[id]/download` | Download a generated resource artifact. |
| `POST /api/tasks/[id]/check` | Start IFC checking for a task. |
| `GET /api/tasks/[id]/download` | Download task output. |

## Deployment Checklist

- Confirm UploadThing token is configured in the Next.js service.
- Confirm `PYTHON_BACKEND_URL` is reachable from the server runtime.
- Confirm Next.js and Python services share the same `MONGODB_URI`.
- Upload a small test file and verify a resource record appears.
- Run a text analysis request and verify the task reaches a completed or failed terminal state.
- Download a generated IDS/report artifact from the task page.

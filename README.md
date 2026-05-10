# team-carebears

## Deploy Setup

This repo is prepared for:

- `frontend/` on `Vercel`
- `backend/` on `Render`

### Backend on Render

Use a Render Web Service with:

- Build command: `pip install -r backend/requirements.txt`
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

Set these backend env vars:

- `FIREBASE_MODE=true`
- `FIREBASE_PROJECT_ID=...`
- `FIREBASE_STORAGE_BUCKET=...`
- `FIREBASE_CREDENTIALS_JSON=...`
- `ANTHROPIC_API_KEY=...`
- `OPENAI_API_KEY=...`
- `WHISPER_MODE=api`
- `CORS_ALLOWED_ORIGINS=https://<your-vercel-domain>,http://localhost:3000,http://127.0.0.1:3000`

Notes:

- `GET /health` returns a simple healthcheck response for deploy verification.
- Hosted environments should prefer `FIREBASE_CREDENTIALS_JSON`.
- Local development can still use `FIREBASE_CREDENTIALS_PATH`.

### Frontend on Vercel

Create a Vercel project with `frontend/` as the root directory and set:

- `NEXT_PUBLIC_API_URL=https://<your-render-service>.onrender.com`

### Local Env Templates

- Backend template: [.env.example](/Users/sriyan/Documents/team-carebears/.env.example)
- Frontend template: [frontend/.env.example](/Users/sriyan/Documents/team-carebears/frontend/.env.example)

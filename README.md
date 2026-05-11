# Pulse

Pulse is a caregiving companion for families supporting a person with dementia. It helps caregivers capture daily observations, medication adherence, and spoken notes in a structured way, then turns those records into concise summaries that are easier to review before a doctor visit.

## Problem Statement

Family caregivers often notice small changes in mood, sleep, appetite, memory, behaviour, and medication routines, but those observations are usually scattered across memory, messages, paper notes, or rushed conversations. By the time a medical appointment happens, important details can be forgotten, dates may be unclear, and clinicians may not get the full picture.

Pulse addresses this by giving caregivers a lightweight way to record care events as they happen and convert them into visit-ready evidence.

## Solution

The app provides a mobile-first care logging workflow where caregivers can:

- Create a simple care profile for the caregiver and patient.
- Record ad-hoc voice observations and automatically transcribe them.
- Track daily wellbeing across sleep, appetite, and mood.
- Add and manage medications, including missed-dose context and voice notes.
- View previous voice notes and transcripts.
- Generate AI-assisted medical summaries for a selected date range.
- Produce summaries in English, Chinese, Malay, or Tamil.

The generated reports combine voice notes, daily wellbeing entries, and medication logs into a plain-language narrative, condensed bullet points with evidence references, and a list of items worth flagging to a doctor. The report assistant is designed to summarize caregiver observations without making clinical diagnoses.

## Tech Stack

### Frontend

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Hugeicons for UI icons
- Next.js rewrite proxy for backend API calls

### Backend

- FastAPI
- Python
- Pydantic and Pydantic Settings
- Uvicorn
- Firebase Admin SDK
- Firestore for app data
- Firebase Storage support
- OpenAI Whisper for audio transcription (Multilingual)
- Anthropic Claude for report generation

### Data and AI

- Firestore collections store patients, caregivers, voice notes, daily wellbeing entries, medications, and reports.
- OpenAI Whisper can run through the API or a local Whisper model.
- Claude generates structured JSON reports from an evidence bundle assembled by the backend.
- Mock mode is available for demo and development flows.

## Repository Structure

```text
backend/
  api/              FastAPI route modules
  models/           Internal data models
  repositories/     Firestore persistence layer
  schemas/          Request and response schemas
  services/         Business logic, transcription, reports, mock data
frontend/
  src/app/          Next.js app routes
  src/components/   Reusable UI components
  src/hooks/        Audio recording hook
  src/lib/          API client, language, and onboarding helpers
seed_data.py        Script for seeding demo data
```

## Key Features

- Voice-first capture: caregivers can record observations without typing long notes.
- Multilingual experience: the interface and report generation support English, Chinese, Malay, and Tamil.
- Daily wellbeing check-ins: structured inputs make it easier to notice trends over time.
- Medication tracking: medication records and related voice notes become part of the report evidence.
- AI report generation: selected care data is summarized into doctor-friendly notes.
- Deployment-ready setup: frontend is prepared for Vercel and backend for Render.

## Local Setup

### Backend

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Create a root `.env` file with the backend settings you need:

```env
FIREBASE_MODE=true
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FIREBASE_CREDENTIALS_JSON={}
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key
WHISPER_MODE=api
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Run the API:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```text
GET http://localhost:8000/health
```

### Frontend

Install dependencies:

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
API_PROXY_TARGET=http://127.0.0.1:8000
NEXT_PUBLIC_MOCK_MODE=false
NEXT_PUBLIC_MOCK_DATA_JSON=
```

Run the app:

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

## Environment Variables

### Backend

- `FIREBASE_MODE`: Enables Firestore-backed persistence.
- `FIREBASE_PROJECT_ID`: Firebase project ID.
- `FIREBASE_STORAGE_BUCKET`: Firebase Storage bucket name.
- `FIREBASE_CREDENTIALS_JSON`: Firebase service account JSON for hosted environments.
- `FIREBASE_CREDENTIALS_PATH`: Local path to a Firebase service account file.
- `ANTHROPIC_API_KEY`: Used for AI report generation.
- `OPENAI_API_KEY`: Used when `WHISPER_MODE=api`.
- `WHISPER_MODE`: `api` for OpenAI Whisper API or `local` for local Whisper.
- `WHISPER_MODEL`: Local Whisper model size when using local mode.
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed frontend origins.
- `MOCK_MODE`: Enables backend mock data responses.
- `MOCK_DATA_JSON`: JSON payload for mock data.

### Frontend

- `API_PROXY_TARGET`: Backend URL used by the Next.js proxy.
- `NEXT_PUBLIC_MOCK_MODE`: Enables frontend mock data mode.
- `NEXT_PUBLIC_MOCK_DATA_JSON`: JSON payload for frontend mock data.

## Deployment

### Backend on Render

Use a Render Web Service with:

```text
Build command: pip install -r backend/requirements.txt
Start command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Recommended backend environment variables:

```env
FIREBASE_MODE=true
FIREBASE_PROJECT_ID=...
FIREBASE_STORAGE_BUCKET=...
FIREBASE_CREDENTIALS_JSON=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
WHISPER_MODE=api
CORS_ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app,http://localhost:3000,http://127.0.0.1:3000
```

### Frontend on Vercel

Create a Vercel project with `frontend/` as the root directory.

Set:

```env
API_PROXY_TARGET=https://your-render-service.onrender.com
```

The frontend calls relative `/api/*` routes and relies on the Next.js rewrite proxy, so the browser does not need to call the Render backend directly.

## Notes

- Generated reports are summaries of caregiver-provided observations and are not medical diagnoses.
- Report audio playback is currently disabled in the backend.
- Firestore is the active persistence layer; the SQLAlchemy database module is kept only for compatibility with older code paths.

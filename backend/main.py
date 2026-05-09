from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, SessionLocal, Base
from .config import settings
from .services import transcription as transcription_service
from .seed import run_seed
from .routers import dashboard, voice_notes, medications, tracker, summary


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.WHISPER_MODE == "local":
        transcription_service.load_model()
    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()
    yield


logging.basicConfig(level=logging.INFO)

app = FastAPI(title="SilverPulse API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(voice_notes.router)
app.include_router(medications.router)
app.include_router(tracker.router)
app.include_router(summary.router)

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import dashboard, medications, summary, tracker, voice_notes
from .config import settings
from .database import Base, engine
from .services import transcription as transcription_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    if engine is not None:
        Base.metadata.create_all(bind=engine)
    if settings.WHISPER_MODE == "local":
        transcription_service.load_model()
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

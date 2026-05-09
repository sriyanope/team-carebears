from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import medications, voice_notes, daily_wellbeing, reports
from .config import settings
from .services import transcription as transcription_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.WHISPER_MODE == "local":
        transcription_service.load_model()
    yield


logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Pulse API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice_notes.router)
app.include_router(medications.router)
app.include_router(daily_wellbeing.router)
app.include_router(reports.router)

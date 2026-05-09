"""
Minimal stub kept for backwards compatibility with medication files (hands-off).
The app runs Firestore-only; db/engine are always None.
"""
from typing import Generator

from sqlalchemy.orm import DeclarativeBase

engine = None
SessionLocal = None


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    yield None

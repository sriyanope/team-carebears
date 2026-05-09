from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore

from .config import settings

_client: Optional[firestore.Client] = None


def get_firestore_client() -> firestore.Client:
    global _client
    if _client is not None:
        return _client
    if not settings.FIREBASE_PROJECT_ID:
        raise ValueError("FIREBASE_PROJECT_ID is required when FIREBASE_MODE is enabled")
    if not settings.FIREBASE_CREDENTIALS_PATH:
        raise ValueError("FIREBASE_CREDENTIALS_PATH is required when FIREBASE_MODE is enabled")
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {"projectId": settings.FIREBASE_PROJECT_ID})
    _client = firestore.client()
    return _client


def normalize_timestamp(value):
    if hasattr(value, "to_datetime"):
        return value.to_datetime()
    return value

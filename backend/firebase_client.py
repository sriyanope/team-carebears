import json
from typing import Optional
import threading

import firebase_admin
from firebase_admin import credentials, firestore, storage

from .config import settings

_client: Optional[firestore.Client] = None
_bucket = None
_firebase_init_lock = threading.Lock()


def _get_storage_bucket_name() -> str:
    if settings.FIREBASE_STORAGE_BUCKET:
        return settings.FIREBASE_STORAGE_BUCKET

    if settings.FIREBASE_PROJECT_ID:
        # Firebase Storage buckets are commonly project-id.appspot.com.
        # Do NOT default to project-id.firebasestorage.app unless Firebase console shows that exact bucket.
        return f"{settings.FIREBASE_PROJECT_ID}.appspot.com"

    raise ValueError(
        "FIREBASE_STORAGE_BUCKET or FIREBASE_PROJECT_ID is required when FIREBASE_MODE is enabled"
    )


def _get_firebase_credentials():
    raw_json = settings.FIREBASE_CREDENTIALS_JSON.strip()
    if raw_json:
        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            raise ValueError("FIREBASE_CREDENTIALS_JSON must be valid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("FIREBASE_CREDENTIALS_JSON must decode to a JSON object")
        return credentials.Certificate(payload)

    if settings.FIREBASE_CREDENTIALS_PATH:
        return credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)

    raise ValueError(
        "FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIALS_PATH is required when FIREBASE_MODE is enabled"
    )


def _get_or_init_firebase_app():
    try:
        return firebase_admin.get_app()
    except ValueError:
        pass

    with _firebase_init_lock:
        # Check again inside the lock in case another request initialized it
        # while this thread was waiting.
        try:
            return firebase_admin.get_app()
        except ValueError:
            pass

        if not settings.FIREBASE_PROJECT_ID:
            raise ValueError("FIREBASE_PROJECT_ID is required when FIREBASE_MODE is enabled")

        cred = _get_firebase_credentials()

        return firebase_admin.initialize_app(
            cred,
            {
                "projectId": settings.FIREBASE_PROJECT_ID,
                "storageBucket": _get_storage_bucket_name(),
            },
        )


def get_firestore_client() -> firestore.Client:
    global _client

    if _client is not None:
        return _client

    _get_or_init_firebase_app()
    _client = firestore.client()
    return _client


def get_storage_bucket():
    global _bucket

    if _bucket is not None:
        return _bucket

    app = _get_or_init_firebase_app()
    _bucket = storage.bucket(app=app)
    return _bucket


def normalize_timestamp(value):
    if hasattr(value, "to_datetime"):
        return value.to_datetime()
    return value

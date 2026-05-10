from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    DATABASE_URL: str = ""
    FIREBASE_MODE: bool = False
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_CREDENTIALS_PATH: str = ""
    FIREBASE_STORAGE_BUCKET: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    WHISPER_MODE: str = "local"
    WHISPER_MODEL: str = "base"
    MOCK_MODE: bool = False
    MOCK_DATA_JSON: str = ""


settings = Settings()

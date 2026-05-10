from pydantic_settings import BaseSettings, SettingsConfigDict


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    DATABASE_URL: str = ""
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    FIREBASE_MODE: bool = False
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_CREDENTIALS_PATH: str = ""
    FIREBASE_CREDENTIALS_JSON: str = ""
    FIREBASE_STORAGE_BUCKET: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    WHISPER_MODE: str = "local"
    WHISPER_MODEL: str = "base"
    MOCK_MODE: bool = False
    MOCK_DATA_JSON: str = ""

    def cors_allowed_origins_list(self) -> list[str]:
        return _split_csv(self.CORS_ALLOWED_ORIGINS)


settings = Settings()

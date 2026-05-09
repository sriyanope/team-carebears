from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "sqlite:///./silverpulse.db"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    WHISPER_MODE: str = "local"
    WHISPER_MODEL: str = "base"


settings = Settings()

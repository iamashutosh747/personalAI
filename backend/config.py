from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/config.py -> backend/ -> project root, where .env lives.
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    anthropic_api_key: str

    # Model IDs are configured here, never hard-coded in application logic.
    claude_model_main: str = "claude-sonnet-5"
    claude_model_utility: str = "claude-haiku-4-5"

    backend_port: int = 8000
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

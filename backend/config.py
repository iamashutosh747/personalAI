from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/config.py -> backend/ -> project root, where .env lives.
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    anthropic_api_key: str
    database_url: str
    voyage_api_key: str

    # Model IDs are configured here, never hard-coded in application logic.
    claude_model_main: str = "claude-sonnet-5"
    claude_model_utility: str = "claude-haiku-4-5"
    voyage_model: str = "voyage-3.5"
    voyage_embedding_dimension: int = 1024

    # How many long-term memories to inject into a chat request.
    memory_retrieval_top_k: int = 5

    backend_port: int = 8000
    environment: str = "development"

    # Temporary single-user placeholder until real auth (Phase 11).
    owner_email: str = "owner@example.com"

    # Cost control: cap how many past messages are sent to Claude per request.
    max_history_messages: int = 20

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

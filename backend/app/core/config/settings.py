from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "development"
    app_name: str = "RAGOps Platform"
    app_base_url: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000"
    log_level: str = "INFO"

    database_url: str = Field(
        default="postgresql+psycopg://ragops:ragops@localhost:5432/ragops",
    )
    vector_store_provider: str = "pgvector"
    vector_store_url: str = ""
    document_storage_path: str = "./data/documents"
    max_upload_mb: int = 10

    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.2"
    ollama_embedding_model: str = "nomic-embed-text"

    hosted_llm_provider: str = ""
    hosted_llm_model: str = ""
    hosted_embedding_model: str = ""
    openai_api_key: str = ""

    eval_enabled: bool = True
    eval_sample_set_path: str = "./demo-data/eval/sample_cases.json"
    eval_max_cases: int = 50

    chunk_size: int = 512
    chunk_overlap: int = 64
    default_top_k: int = 5
    context_token_budget: int = 4000
    insufficient_evidence_threshold: float = 0.35

    cors_origins: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def validate_required_settings() -> list[str]:
    settings = get_settings()
    missing: list[str] = []
    if not settings.database_url:
        missing.append("DATABASE_URL")
    if not settings.document_storage_path:
        missing.append("DOCUMENT_STORAGE_PATH")
    return missing

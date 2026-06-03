from fastapi import APIRouter

from app.api.schemas import RuntimeSettingsResponse
from app.core.config import get_settings
from app.domain.retrieval.models import RETRIEVAL_STRATEGIES

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/runtime", response_model=RuntimeSettingsResponse)
def runtime_settings() -> RuntimeSettingsResponse:
    settings = get_settings()
    return RuntimeSettingsResponse(
        app_env=settings.app_env,
        llm_provider="ollama" if not settings.hosted_llm_provider else settings.hosted_llm_provider,
        llm_model=settings.ollama_chat_model,
        embedding_model=settings.ollama_embedding_model,
        vector_store_provider=settings.vector_store_provider,
        max_upload_mb=settings.max_upload_mb,
        ollama_base_url=settings.ollama_base_url,
        eval_enabled=settings.eval_enabled,
        retrieval_strategies=RETRIEVAL_STRATEGIES,
    )

import time

import httpx

from app.core.config import get_settings
from app.core.errors.handlers import AppError
from app.providers.llm.base import LLMProvider, LLMResponse


class OllamaLLMProvider(LLMProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_chat_model

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(self, prompt: str, system: str | None = None) -> LLMResponse:
        url = f"{self._base_url}/api/generate"
        payload: dict = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                text = data.get("response", "").strip()
                latency_ms = (time.perf_counter() - start) * 1000
                return LLMResponse(
                    text=text,
                    model_provider=self.provider_name,
                    model_name=self._model,
                    latency_ms=latency_ms,
                )
        except httpx.HTTPError as exc:
            raise AppError(
                "LLM provider unavailable. Ensure Ollama is running.",
                code="llm_unavailable",
                status_code=503,
            ) from exc

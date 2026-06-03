import httpx

from app.core.config import get_settings
from app.core.errors.handlers import AppError
from app.providers.embeddings.base import EmbeddingProvider


class OllamaEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_embedding_model
        self._dim = 768

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimension(self) -> int:
        return self._dim

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        results = []
        for text in texts:
            results.append(await self.embed_query(text))
        return results

    async def embed_query(self, text: str) -> list[float]:
        url = f"{self._base_url}/api/embeddings"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    json={"model": self._model, "prompt": text},
                )
                response.raise_for_status()
                data = response.json()
                embedding = data.get("embedding", [])
                if not embedding:
                    raise AppError("Ollama returned empty embedding", code="embedding_error", status_code=502)
                self._dim = len(embedding)
                return embedding
        except httpx.HTTPError as exc:
            raise AppError(
                "Embedding provider unavailable. Ensure Ollama is running.",
                code="embedding_unavailable",
                status_code=503,
            ) from exc

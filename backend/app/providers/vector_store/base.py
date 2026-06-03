from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.retrieval.models import RetrievedChunk


class VectorStore(ABC):
    @abstractmethod
    async def upsert(
        self,
        chunk_id: UUID,
        embedding: list[float],
        model_name: str,
        dimension: int,
    ) -> None:
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: list[float],
        top_k: int,
        document_ids: list[UUID] | None = None,
        metadata_filters: dict | None = None,
    ) -> list[RetrievedChunk]:
        pass

    @abstractmethod
    async def delete_by_document(self, document_id: UUID) -> None:
        pass

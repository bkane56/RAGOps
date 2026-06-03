import time
from uuid import UUID

from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session

from app.domain.retrieval.models import RetrievedChunk, RetrievalRequest, RetrievalResult
from app.infrastructure.database.models import ChunkModel, DocumentModel
from app.providers.embeddings.base import EmbeddingProvider
from app.providers.vector_store.base import VectorStore
from app.services.reranking.service import RerankerService


class RetrievalStrategyBase:
    name = "base"

    def __init__(
        self,
        db: Session,
        embeddings: EmbeddingProvider,
        vector_store: VectorStore,
        reranker: RerankerService | None = None,
    ) -> None:
        self._db = db
        self._embeddings = embeddings
        self._vector_store = vector_store
        self._reranker = reranker

    async def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        raise NotImplementedError


class BasicVectorStrategy(RetrievalStrategyBase):
    name = "basic_vector"

    async def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        start = time.perf_counter()
        query_emb = await self._embeddings.embed_query(request.query_text)
        chunks = await self._vector_store.search(
            query_emb,
            request.top_k,
            request.document_ids,
            request.metadata_filters or None,
        )
        for c in chunks:
            c.strategy_name = self.name
        latency = (time.perf_counter() - start) * 1000
        return RetrievalResult(chunks=chunks, strategy_name=self.name, latency_ms=latency)


class MetadataFilteredVectorStrategy(BasicVectorStrategy):
    name = "metadata_filtered_vector"

    async def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        result = await super().retrieve(request)
        result.strategy_name = self.name
        for c in result.chunks:
            c.strategy_name = self.name
        return result


class HybridKeywordVectorStrategy(BasicVectorStrategy):
    name = "hybrid_keyword_vector"

    async def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        start = time.perf_counter()
        vector_result = await super().retrieve(request)
        keywords = [w for w in request.query_text.split() if len(w) > 3][:5]
        if keywords:
            pattern = "%" + "%".join(keywords[:3]) + "%"
            stmt = (
                select(ChunkModel, DocumentModel.filename)
                .join(DocumentModel, DocumentModel.id == ChunkModel.document_id)
                .where(DocumentModel.status == "ready")
                .where(or_(*[ChunkModel.text.ilike(f"%{kw}%") for kw in keywords[:3]]))
                .limit(request.top_k)
            )
            if request.document_ids:
                stmt = stmt.where(ChunkModel.document_id.in_(request.document_ids))
            rows = self._db.execute(stmt).all()
            seen = {c.chunk_id for c in vector_result.chunks}
            for row in rows:
                chunk, filename = row[0], row[1]
                if chunk.id in seen:
                    continue
                vector_result.chunks.append(
                    RetrievedChunk(
                        chunk_id=chunk.id,
                        document_id=chunk.document_id,
                        filename=filename,
                        chunk_text=chunk.text,
                        strategy_name=self.name,
                        page_number=chunk.page_number,
                        similarity_score=0.5,
                        token_estimate=chunk.token_estimate,
                    ),
                )
                seen.add(chunk.id)
            vector_result.chunks = vector_result.chunks[: request.top_k]
        vector_result.strategy_name = self.name
        vector_result.latency_ms = (time.perf_counter() - start) * 1000
        for c in vector_result.chunks:
            c.strategy_name = self.name
        return vector_result


class MultiQueryStrategy(BasicVectorStrategy):
    name = "multi_query"

    async def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        start = time.perf_counter()
        variants = [
            request.query_text,
            f"What is {request.query_text}",
            f"Explain {request.query_text}",
        ]
        merged: dict[UUID, RetrievedChunk] = {}
        for variant in variants[:3]:
            sub = RetrievalRequest(
                query_text=variant,
                strategy_name="basic_vector",
                top_k=request.top_k,
                document_ids=request.document_ids,
                metadata_filters=request.metadata_filters,
            )
            result = await super().retrieve(sub)
            for chunk in result.chunks:
                if chunk.chunk_id not in merged or (
                    chunk.similarity_score or 0
                ) > (merged[chunk.chunk_id].similarity_score or 0):
                    chunk.strategy_name = self.name
                    merged[chunk.chunk_id] = chunk
        chunks = sorted(
            merged.values(),
            key=lambda c: c.similarity_score or 0,
            reverse=True,
        )[: request.top_k]
        latency = (time.perf_counter() - start) * 1000
        return RetrievalResult(chunks=chunks, strategy_name=self.name, latency_ms=latency)


class RerankedStrategy(BasicVectorStrategy):
    name = "reranked"

    async def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        widened = RetrievalRequest(
            query_text=request.query_text,
            strategy_name="basic_vector",
            top_k=max(request.top_k * 2, 10),
            document_ids=request.document_ids,
            metadata_filters=request.metadata_filters,
        )
        result = await super().retrieve(widened)
        if self._reranker:
            result.chunks = await self._reranker.rerank(request.query_text, result.chunks)
            result.chunks = result.chunks[: request.top_k]
        result.strategy_name = self.name
        for c in result.chunks:
            c.strategy_name = self.name
        return result


STRATEGY_REGISTRY: dict[str, type[RetrievalStrategyBase]] = {
    "basic_vector": BasicVectorStrategy,
    "metadata_filtered_vector": MetadataFilteredVectorStrategy,
    "hybrid_keyword_vector": HybridKeywordVectorStrategy,
    "multi_query": MultiQueryStrategy,
    "reranked": RerankedStrategy,
}


def get_strategy(name: str, db: Session, embeddings: EmbeddingProvider, vector_store: VectorStore) -> RetrievalStrategyBase:
    from app.services.reranking.service import RerankerService

    cls = STRATEGY_REGISTRY.get(name, BasicVectorStrategy)
    reranker = RerankerService() if name == "reranked" else None
    return cls(db, embeddings, vector_store, reranker)

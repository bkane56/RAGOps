from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.retrieval.models import RetrievalRequest, RetrievedChunk
from app.services.retrieval.strategies import (
    BasicVectorStrategy,
    HybridKeywordVectorStrategy,
    MultiQueryStrategy,
    RerankedStrategy,
    get_strategy,
)


class MockEmbeddings:
    model_name = "mock"
    dimension = 4

    async def embed_query(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3, 0.4]


class MockVectorStore:
    async def search(self, query_embedding, top_k, document_ids=None, metadata_filters=None):
        return [
            RetrievedChunk(
                chunk_id=uuid4(),
                document_id=uuid4(),
                filename="test.md",
                chunk_text="RAG pipeline ingestion",
                strategy_name="basic_vector",
                similarity_score=0.9,
                token_estimate=10,
            ),
        ]

    async def upsert(self, *args, **kwargs):
        pass

    async def delete_by_document(self, document_id):
        pass


@pytest.mark.asyncio
async def test_basic_vector_strategy():
    db = MagicMock()
    strategy = BasicVectorStrategy(db, MockEmbeddings(), MockVectorStore())
    result = await strategy.retrieve(
        RetrievalRequest(query_text="RAG pipeline", strategy_name="basic_vector", top_k=3),
    )
    assert result.strategy_name == "basic_vector"
    assert len(result.chunks) == 1
    assert result.latency_ms >= 0


@pytest.mark.asyncio
async def test_multi_query_strategy():
    db = MagicMock()
    strategy = MultiQueryStrategy(db, MockEmbeddings(), MockVectorStore())
    result = await strategy.retrieve(
        RetrievalRequest(query_text="pipeline", strategy_name="multi_query", top_k=5),
    )
    assert result.strategy_name == "multi_query"


@pytest.mark.asyncio
async def test_reranked_strategy():
    db = MagicMock()
    strategy = RerankedStrategy(db, MockEmbeddings(), MockVectorStore(), reranker=MagicMock())
    strategy._reranker.rerank = AsyncMock(side_effect=lambda q, c: c)
    result = await strategy.retrieve(
        RetrievalRequest(query_text="RAG", strategy_name="reranked", top_k=3),
    )
    assert result.strategy_name == "reranked"


def test_get_strategy_registry():
    db = MagicMock()
    s = get_strategy("hybrid_keyword_vector", db, MockEmbeddings(), MockVectorStore())
    assert isinstance(s, HybridKeywordVectorStrategy)

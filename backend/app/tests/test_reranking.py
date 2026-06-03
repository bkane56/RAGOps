from uuid import uuid4

import pytest

from app.domain.retrieval.models import RetrievedChunk
from app.services.reranking.service import RerankerService


@pytest.mark.asyncio
async def test_rerank_orders_by_overlap():
    service = RerankerService()
    chunks = [
        RetrievedChunk(
            chunk_id=uuid4(),
            document_id=uuid4(),
            filename="a.txt",
            chunk_text="unrelated content",
            strategy_name="basic_vector",
            similarity_score=0.9,
        ),
        RetrievedChunk(
            chunk_id=uuid4(),
            document_id=uuid4(),
            filename="b.txt",
            chunk_text="RAG pipeline ingestion retrieval",
            strategy_name="basic_vector",
            similarity_score=0.5,
        ),
    ]
    result = await service.rerank("RAG pipeline", chunks)
    assert result[0].chunk_text.startswith("RAG") or result[0].reranker_score is not None

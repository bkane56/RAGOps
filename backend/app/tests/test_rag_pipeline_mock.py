from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.generation.models import CitationValidationResult, GeneratedAnswer
from app.domain.retrieval.models import RetrievalResult, RetrievedChunk
from app.services.rag_pipeline import RagPipelineService


@pytest.mark.asyncio
async def test_pipeline_insufficient_evidence_low_score():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()

    low_chunk = RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        filename="a.txt",
        chunk_text="text",
        strategy_name="basic_vector",
        similarity_score=0.1,
    )
    retrieval = RetrievalResult(chunks=[low_chunk], strategy_name="basic_vector", latency_ms=5.0)

    with patch.object(RagPipelineService, "__init__", lambda self, db: None):
        pipeline = RagPipelineService(db)
        pipeline._db = db
        pipeline._embeddings = MagicMock()
        pipeline._llm = MagicMock()
        pipeline._vector_store = MagicMock()
        pipeline._context = MagicMock()
        pipeline._generation = MagicMock()
        pipeline._citation = MagicMock()
        pipeline._embeddings = MagicMock()
        pipeline._vector_store = MagicMock()
        pipeline._settings = MagicMock(insufficient_evidence_threshold=0.35)

        with patch(
            "app.services.rag_pipeline.get_strategy",
            return_value=MagicMock(retrieve=AsyncMock(return_value=retrieval)),
        ):
            result = await pipeline.run("unknown question", "basic_vector", 5)

    assert result.answer.insufficient_evidence is True


@pytest.mark.asyncio
async def test_pipeline_with_generation():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()

    chunk = RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        filename="a.txt",
        chunk_text="RAG pipeline steps",
        strategy_name="basic_vector",
        similarity_score=0.9,
    )
    retrieval = RetrievalResult(chunks=[chunk], strategy_name="basic_vector", latency_ms=5.0)

    with patch.object(RagPipelineService, "__init__", lambda self, db: None):
        pipeline = RagPipelineService(db)
        pipeline._db = db
        pipeline._embeddings = MagicMock()
        pipeline._vector_store = MagicMock()
        pipeline._settings = MagicMock(insufficient_evidence_threshold=0.35)
        pipeline._context = MagicMock()
        pipeline._context.assemble.return_value = MagicMock(context_text="ctx", citation_map={"[1]": str(chunk.chunk_id)})
        pipeline._generation = MagicMock()
        pipeline._generation.generate = AsyncMock(
            return_value=GeneratedAnswer(
                text="Answer [1]",
                citations=[],
                model_provider="ollama",
                model_name="test",
                generation_latency_ms=10.0,
                insufficient_evidence=False,
            ),
        )
        pipeline._citation = MagicMock()
        pipeline._citation.validate.return_value = CitationValidationResult(
            coverage=1.0,
            status="valid",
            cited_chunk_ids=[chunk.chunk_id],
        )

        with patch(
            "app.services.rag_pipeline.get_strategy",
            return_value=MagicMock(retrieve=AsyncMock(return_value=retrieval)),
        ):
            result = await pipeline.run("What is RAG?", "basic_vector", 5)

    assert "Answer" in result.answer.text

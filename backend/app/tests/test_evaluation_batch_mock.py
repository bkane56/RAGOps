from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.evaluation.models import EvaluationCase, QueryMetrics
from app.domain.generation.models import GeneratedAnswer
from app.services.evaluation.service import EvaluationService
from app.services.rag_pipeline import RagPipelineResult


@pytest.mark.asyncio
async def test_run_batch_with_mock_pipeline():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock(side_effect=lambda obj: setattr(obj, "id", "run-id"))

    service = EvaluationService(db)
    service.load_cases = lambda: [
        EvaluationCase(
            question="test",
            expected_answer_summary="",
            category="no_supporting_evidence",
            expected_behavior="insufficient_evidence",
        ),
    ]

    metrics = QueryMetrics(
        answer_relevance=0,
        context_relevance=0,
        groundedness=0,
        citation_coverage=0,
        retrieval_latency_ms=1,
        generation_latency_ms=1,
        total_latency_ms=2,
        retrieved_chunk_count=0,
        cited_chunk_count=0,
        insufficient_evidence=True,
    )
    answer = GeneratedAnswer(
        text="insufficient",
        citations=[],
        model_provider="mock",
        model_name="mock",
        generation_latency_ms=1.0,
        insufficient_evidence=True,
    )
    from app.domain.generation.models import CitationValidationResult
    from app.domain.retrieval.models import RetrievalResult

    mock_pipeline_result = RagPipelineResult(
        query_id=MagicMock(),
        answer=answer,
        retrieval=RetrievalResult(chunks=[], strategy_name="basic_vector", latency_ms=1.0),
        validation=CitationValidationResult(coverage=0, status="insufficient_evidence", cited_chunk_ids=[]),
        metrics=metrics,
        evidence=[],
    )
    service._pipeline = MagicMock()
    service._pipeline.run = AsyncMock(return_value=mock_pipeline_result)

    result = await service.run_batch("basic_vector")
    assert result["case_count"] == 1
    assert result["pass_rate"] == 1.0

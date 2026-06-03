from app.domain.evaluation.models import EvaluationCase
from app.domain.generation.models import CitationValidationResult, GeneratedAnswer
from app.domain.retrieval.models import RetrievalResult, RetrievedChunk
from app.services.evaluation.metrics import compute_query_metrics
from app.services.evaluation.service import _aggregate_metrics, _evaluate_case, _default_cases


def test_compute_query_metrics():
    retrieval = RetrievalResult(chunks=[], strategy_name="basic_vector", latency_ms=10.0)
    answer = GeneratedAnswer(
        text="answer",
        citations=[],
        model_provider="ollama",
        model_name="test",
        generation_latency_ms=20.0,
        insufficient_evidence=False,
    )
    validation = CitationValidationResult(coverage=0.5, status="partial", cited_chunk_ids=[])
    metrics = compute_query_metrics(retrieval, answer, validation, 30.0)
    assert metrics.total_latency_ms == 30.0
    assert metrics.retrieval_latency_ms == 10.0


def test_evaluate_case_no_evidence():
    case = EvaluationCase(
        question="q",
        expected_answer_summary="",
        category="no_supporting_evidence",
    )
    from app.domain.evaluation.models import QueryMetrics

    metrics = QueryMetrics(
        answer_relevance=0,
        context_relevance=0,
        groundedness=0,
        citation_coverage=0,
        retrieval_latency_ms=0,
        generation_latency_ms=0,
        total_latency_ms=0,
        retrieved_chunk_count=0,
        cited_chunk_count=0,
        insufficient_evidence=True,
    )
    assert _evaluate_case(case, metrics, True) is True


def test_aggregate_metrics_empty():
    agg = _aggregate_metrics([], [])
    assert agg["case_count"] == 0


def test_default_cases():
    cases = _default_cases()
    assert len(cases) >= 2

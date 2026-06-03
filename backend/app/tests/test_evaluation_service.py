from pathlib import Path
from unittest.mock import MagicMock

from app.services.evaluation.service import EvaluationService, _default_cases, _evaluate_case
from app.domain.evaluation.models import EvaluationCase, QueryMetrics


def test_load_cases_from_repo_file():
    service = EvaluationService(MagicMock())
    cases = service.load_cases()
    assert len(cases) >= 2
    repo_file = Path(__file__).resolve().parents[4] / "demo-data/eval/sample_cases.json"
    if repo_file.exists():
        assert any("RAG pipeline" in c.question or "Mars" in c.question for c in cases)


def test_default_cases_fallback():
    cases = _default_cases()
    assert any(c.category == "no_supporting_evidence" for c in cases)


def test_evaluate_case_no_evidence_category():
    case = EvaluationCase(
        question="q",
        expected_answer_summary="",
        category="no_supporting_evidence",
    )
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

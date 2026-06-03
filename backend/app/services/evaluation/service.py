import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.domain.evaluation.models import EvaluationCase, EvaluationCaseResult, QueryMetrics
from app.domain.retrieval.models import RETRIEVAL_STRATEGIES
from app.infrastructure.database.models import EvaluationRunModel, RagQueryModel
from app.services.rag_pipeline import RagPipelineService


class EvaluationService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._settings = get_settings()
        self._pipeline = RagPipelineService(db)

    def load_cases(self) -> list[EvaluationCase]:
        path = Path(self._settings.eval_sample_set_path)
        if not path.is_absolute():
            repo_root = Path(__file__).resolve().parents[4]
            path = repo_root / path
        if not path.exists():
            return _default_cases()
        data = json.loads(path.read_text())
        cases = []
        for item in data[: self._settings.eval_max_cases]:
            cases.append(
                EvaluationCase(
                    question=item["question"],
                    expected_answer_summary=item.get("expected_answer_summary", ""),
                    expected_document_ids=item.get("expected_document_ids", []),
                    expected_behavior=item.get("expected_behavior", ""),
                    difficulty=item.get("difficulty", "medium"),
                    category=item.get("category", "direct_answer"),
                ),
            )
        return cases

    async def run_batch(self, strategy_name: str = "basic_vector") -> dict:
        cases = self.load_cases()
        results: list[EvaluationCaseResult] = []
        metrics_accum: list[QueryMetrics] = []

        for idx, case in enumerate(cases):
            try:
                result = await self._pipeline.run(case.question, strategy_name, top_k=5)
                passed = _evaluate_case(case, result.metrics, result.answer.insufficient_evidence)
                results.append(
                    EvaluationCaseResult(
                        case_index=idx,
                        question=case.question,
                        category=case.category,
                        passed=passed,
                        metrics=result.metrics,
                        failure_reason=None if passed else case.expected_behavior,
                    ),
                )
                metrics_accum.append(result.metrics)
            except Exception as exc:
                results.append(
                    EvaluationCaseResult(
                        case_index=idx,
                        question=case.question,
                        category=case.category,
                        passed=False,
                        metrics=QueryMetrics(
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
                        ),
                        failure_reason=str(exc)[:200],
                    ),
                )

        aggregate = _aggregate_metrics(metrics_accum, results)
        run = EvaluationRunModel(
            aggregate_metrics=aggregate,
            per_case_results=[
                {
                    "case_index": r.case_index,
                    "question": r.question,
                    "category": r.category,
                    "passed": r.passed,
                    "metrics": {
                        "answer_relevance": r.metrics.answer_relevance,
                        "context_relevance": r.metrics.context_relevance,
                        "groundedness": r.metrics.groundedness,
                        "citation_coverage": r.metrics.citation_coverage,
                        "insufficient_evidence": r.metrics.insufficient_evidence,
                    },
                    "failure_reason": r.failure_reason,
                }
                for r in results
            ],
        )
        self._db.add(run)
        self._db.commit()
        self._db.refresh(run)
        aggregate["run_id"] = str(run.id)
        return aggregate

    def list_runs(self, limit: int = 10) -> list[dict]:
        runs = self._db.scalars(
            select(EvaluationRunModel).order_by(EvaluationRunModel.created_at.desc()).limit(limit),
        ).all()
        return [
            {
                "id": str(r.id),
                "aggregate_metrics": r.aggregate_metrics,
                "created_at": r.created_at.isoformat(),
            }
            for r in runs
        ]

    def get_overview_stats(self) -> dict:
        from sqlalchemy import func

        from app.infrastructure.database.models import ChunkModel, DocumentModel

        doc_count = self._db.scalar(select(func.count()).select_from(DocumentModel)) or 0
        chunk_count = self._db.scalar(select(func.count()).select_from(ChunkModel)) or 0
        query_count = self._db.scalar(select(func.count()).select_from(RagQueryModel)) or 0
        runs = self.list_runs(1)
        latest_eval = runs[0]["aggregate_metrics"] if runs else {}
        return {
            "document_count": doc_count,
            "chunk_count": chunk_count,
            "query_count": query_count,
            "retrieval_strategies": RETRIEVAL_STRATEGIES,
            "latest_evaluation": latest_eval,
        }


def _evaluate_case(case: EvaluationCase, metrics: QueryMetrics, insufficient: bool) -> bool:
    if case.category == "no_supporting_evidence":
        return insufficient
    if case.category == "citation_required":
        return metrics.citation_coverage > 0 or insufficient
    return not insufficient or case.expected_behavior == "insufficient_evidence"


def _aggregate_metrics(metrics: list[QueryMetrics], results: list[EvaluationCaseResult]) -> dict:
    if not metrics:
        return {
            "case_count": 0,
            "pass_rate": 0,
            "avg_groundedness": 0,
            "avg_answer_relevance": 0,
            "avg_context_relevance": 0,
            "insufficient_evidence_rate": 0,
            "avg_citation_coverage": 0,
            "avg_total_latency_ms": 0,
            "failed_cases": [],
        }

    n = len(metrics)
    insufficient_count = sum(1 for m in metrics if m.insufficient_evidence)
    return {
        "case_count": len(results),
        "pass_rate": round(sum(1 for r in results if r.passed) / max(len(results), 1), 4),
        "avg_groundedness": round(sum(m.groundedness for m in metrics) / n, 4),
        "avg_answer_relevance": round(sum(m.answer_relevance for m in metrics) / n, 4),
        "avg_context_relevance": round(sum(m.context_relevance for m in metrics) / n, 4),
        "insufficient_evidence_rate": round(insufficient_count / n, 4),
        "avg_citation_coverage": round(sum(m.citation_coverage for m in metrics) / n, 4),
        "avg_total_latency_ms": round(sum(m.total_latency_ms for m in metrics) / n, 2),
        "failed_cases": [
            {"question": r.question, "reason": r.failure_reason}
            for r in results
            if not r.passed
        ],
    }


def _default_cases() -> list[EvaluationCase]:
    return [
        EvaluationCase(
            question="What is the RAG pipeline?",
            expected_answer_summary="Ingestion through retrieval and generation",
            category="direct_answer",
            difficulty="easy",
        ),
        EvaluationCase(
            question="What is the capital of Mars colony alpha?",
            expected_answer_summary="No evidence",
            category="no_supporting_evidence",
            expected_behavior="insufficient_evidence",
            difficulty="easy",
        ),
    ]

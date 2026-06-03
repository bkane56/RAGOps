from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.routes.ask import _to_evidence
from app.api.schemas import (
    CitationValidationResponse,
    CompareStrategiesRequest,
    CompareStrategiesResponse,
    QueryMetricsResponse,
    StrategyComparisonItem,
)
from app.domain.retrieval.models import RETRIEVAL_STRATEGIES
from app.infrastructure.database.session import get_db
from app.services.rag_pipeline import RagPipelineService

router = APIRouter(tags=["compare"])


@router.post("/compare-strategies", response_model=CompareStrategiesResponse)
async def compare_strategies(
    body: CompareStrategiesRequest,
    db: Session = Depends(get_db),
) -> CompareStrategiesResponse:
    pipeline = RagPipelineService(db)
    comparisons: list[StrategyComparisonItem] = []
    for name in body.strategies:
        if name not in RETRIEVAL_STRATEGIES:
            continue
        result = await pipeline.run(body.question, name, body.top_k, body.document_ids)
        comparisons.append(
            StrategyComparisonItem(
                strategy_name=name,
                answer=result.answer.text,
                insufficient_evidence=result.answer.insufficient_evidence,
                evidence=_to_evidence(result.evidence),
                metrics=QueryMetricsResponse(
                    answer_relevance=result.metrics.answer_relevance,
                    context_relevance=result.metrics.context_relevance,
                    groundedness=result.metrics.groundedness,
                    citation_coverage=result.metrics.citation_coverage,
                    retrieval_latency_ms=result.metrics.retrieval_latency_ms,
                    generation_latency_ms=result.metrics.generation_latency_ms,
                    total_latency_ms=result.metrics.total_latency_ms,
                    retrieved_chunk_count=result.metrics.retrieved_chunk_count,
                    cited_chunk_count=result.metrics.cited_chunk_count,
                    insufficient_evidence=result.metrics.insufficient_evidence,
                ),
                citation_validation=CitationValidationResponse(
                    coverage=result.validation.coverage,
                    status=result.validation.status,
                    unsupported_segments=result.validation.unsupported_segments,
                ),
            ),
        )
    return CompareStrategiesResponse(question=body.question, comparisons=comparisons)

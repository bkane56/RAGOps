from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import (
    AskRequest,
    AskResponse,
    CitationResponse,
    CitationValidationResponse,
    EvidenceChunkResponse,
    QueryMetricsResponse,
)
from app.infrastructure.database.session import get_db
from app.services.rag_pipeline import RagPipelineService

router = APIRouter(tags=["ask"])


def _to_evidence(chunks) -> list[EvidenceChunkResponse]:
    return [
        EvidenceChunkResponse(
            chunk_id=c.chunk_id,
            document_id=c.document_id,
            filename=c.filename,
            page_number=c.page_number,
            chunk_text=c.chunk_text,
            similarity_score=c.similarity_score,
            reranker_score=c.reranker_score,
            strategy_name=c.strategy_name,
            token_estimate=c.token_estimate,
            cited=c.cited,
        )
        for c in chunks
    ]


@router.post("/ask", response_model=AskResponse)
async def ask(body: AskRequest, db: Session = Depends(get_db)) -> AskResponse:
    pipeline = RagPipelineService(db)
    result = await pipeline.run(
        body.question,
        body.retrieval_strategy,
        body.top_k,
        body.document_ids,
    )
    return AskResponse(
        query_id=result.query_id,
        answer=result.answer.text,
        citations=[
            CitationResponse(chunk_id=c.chunk_id, label=c.label) for c in result.answer.citations
        ],
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
        model_provider=result.answer.model_provider,
        model_name=result.answer.model_name,
    )

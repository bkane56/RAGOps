from app.domain.evaluation.models import QueryMetrics
from app.domain.generation.models import CitationValidationResult, GeneratedAnswer
from app.domain.retrieval.models import RetrievalResult


def compute_query_metrics(
    retrieval: RetrievalResult,
    answer: GeneratedAnswer,
    validation: CitationValidationResult,
    total_latency_ms: float,
) -> QueryMetrics:
    avg_similarity = 0.0
    if retrieval.chunks:
        scores = [c.similarity_score or 0.0 for c in retrieval.chunks]
        avg_similarity = sum(scores) / len(scores)

    context_relevance = min(1.0, avg_similarity)
    answer_relevance = 0.0 if answer.insufficient_evidence else min(1.0, 0.5 + context_relevance * 0.5)
    groundedness = 0.0 if answer.insufficient_evidence else validation.coverage
    cited_count = len(validation.cited_chunk_ids)

    return QueryMetrics(
        answer_relevance=round(answer_relevance, 4),
        context_relevance=round(context_relevance, 4),
        groundedness=round(groundedness, 4),
        citation_coverage=round(validation.coverage, 4),
        retrieval_latency_ms=round(retrieval.latency_ms, 2),
        generation_latency_ms=round(answer.generation_latency_ms, 2),
        total_latency_ms=round(total_latency_ms, 2),
        retrieved_chunk_count=len(retrieval.chunks),
        cited_chunk_count=cited_count,
        insufficient_evidence=answer.insufficient_evidence,
    )

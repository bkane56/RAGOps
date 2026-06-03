from app.domain.retrieval.models import RetrievedChunk


class RerankerService:
    """Simple reranker using keyword overlap until a hosted reranker is configured."""

    async def rerank(self, query: str, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        query_terms = set(query.lower().split())

        def score(chunk: RetrievedChunk) -> float:
            text_terms = set(chunk.chunk_text.lower().split())
            overlap = len(query_terms & text_terms)
            base = chunk.similarity_score or 0.0
            rerank = overlap / max(len(query_terms), 1)
            chunk.reranker_score = rerank
            return base * 0.6 + rerank * 0.4

        return sorted(chunks, key=score, reverse=True)

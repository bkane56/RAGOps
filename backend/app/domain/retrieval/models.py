from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class RetrievedChunk:
    chunk_id: UUID
    document_id: UUID
    filename: str
    chunk_text: str
    strategy_name: str
    page_number: int | None = None
    similarity_score: float | None = None
    reranker_score: float | None = None
    token_estimate: int = 0
    cited: bool = False


@dataclass
class RetrievalResult:
    chunks: list[RetrievedChunk]
    strategy_name: str
    latency_ms: float


@dataclass
class RetrievalRequest:
    query_text: str
    strategy_name: str
    top_k: int = 5
    document_ids: list[UUID] | None = None
    metadata_filters: dict = field(default_factory=dict)


RETRIEVAL_STRATEGIES = [
    "basic_vector",
    "metadata_filtered_vector",
    "hybrid_keyword_vector",
    "multi_query",
    "reranked",
]

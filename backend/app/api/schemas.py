from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str


class HealthResponse(BaseModel):
    status: str
    app_name: str


class ReadyResponse(BaseModel):
    status: str
    database: str


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    file_type: str
    status: str
    content_hash: str | None
    chunk_count: int
    created_at: datetime
    error_message: str | None = None


class ChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    text: str
    page_number: int | None
    section_heading: str | None
    token_estimate: int
    chunking_strategy: str
    content_hash: str
    created_at: datetime | None = None


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    retrieval_strategy: str = "basic_vector"
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: list[UUID] | None = None


class CitationResponse(BaseModel):
    chunk_id: str
    label: str


class EvidenceChunkResponse(BaseModel):
    chunk_id: UUID
    document_id: UUID
    filename: str
    page_number: int | None
    chunk_text: str
    similarity_score: float | None
    reranker_score: float | None
    strategy_name: str
    token_estimate: int
    cited: bool


class QueryMetricsResponse(BaseModel):
    answer_relevance: float
    context_relevance: float
    groundedness: float
    citation_coverage: float
    retrieval_latency_ms: float
    generation_latency_ms: float
    total_latency_ms: float
    retrieved_chunk_count: int
    cited_chunk_count: int
    insufficient_evidence: bool


class CitationValidationResponse(BaseModel):
    coverage: float
    status: str
    unsupported_segments: list[str]


class AskResponse(BaseModel):
    query_id: UUID
    answer: str
    citations: list[CitationResponse]
    insufficient_evidence: bool
    evidence: list[EvidenceChunkResponse]
    metrics: QueryMetricsResponse
    citation_validation: CitationValidationResponse
    model_provider: str
    model_name: str


class CompareStrategiesRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    strategies: list[str] = Field(default_factory=lambda: ["basic_vector", "hybrid_keyword_vector"])
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: list[UUID] | None = None


class StrategyComparisonItem(BaseModel):
    strategy_name: str
    answer: str
    insufficient_evidence: bool
    evidence: list[EvidenceChunkResponse]
    metrics: QueryMetricsResponse
    citation_validation: CitationValidationResponse


class CompareStrategiesResponse(BaseModel):
    question: str
    comparisons: list[StrategyComparisonItem]


class RuntimeSettingsResponse(BaseModel):
    app_env: str
    llm_provider: str
    llm_model: str
    embedding_model: str
    vector_store_provider: str
    max_upload_mb: int
    ollama_base_url: str
    eval_enabled: bool
    retrieval_strategies: list[str]


class EvaluationRunRequest(BaseModel):
    strategy_name: str = "basic_vector"


class EvaluationRunResponse(BaseModel):
    run_id: str | None
    case_count: int
    pass_rate: float
    avg_groundedness: float
    avg_answer_relevance: float
    avg_context_relevance: float
    insufficient_evidence_rate: float
    avg_citation_coverage: float
    avg_total_latency_ms: float
    failed_cases: list[dict]


class OverviewResponse(BaseModel):
    document_count: int
    chunk_count: int
    query_count: int
    retrieval_strategies: list[str]
    latest_evaluation: dict

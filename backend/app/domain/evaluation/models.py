from dataclasses import dataclass, field


@dataclass
class QueryMetrics:
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


@dataclass
class EvaluationCase:
    question: str
    expected_answer_summary: str
    expected_document_ids: list[str] = field(default_factory=list)
    expected_behavior: str = ""
    difficulty: str = "medium"
    category: str = "direct_answer"


@dataclass
class EvaluationCaseResult:
    case_index: int
    question: str
    category: str
    passed: bool
    metrics: QueryMetrics
    failure_reason: str | None = None

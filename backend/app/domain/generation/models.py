from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class CitationRef:
    chunk_id: str
    label: str


@dataclass
class AssembledContext:
    chunks: list
    context_text: str
    citation_map: dict[str, str] = field(default_factory=dict)


@dataclass
class GeneratedAnswer:
    text: str
    citations: list[CitationRef]
    model_provider: str
    model_name: str
    generation_latency_ms: float
    insufficient_evidence: bool = False


@dataclass
class CitationValidationResult:
    coverage: float
    status: str
    cited_chunk_ids: list[UUID]
    unsupported_segments: list[str] = field(default_factory=list)

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class ParsedPage:
    page_number: int | None
    text: str
    section_heading: str | None = None


@dataclass
class ParsedDocument:
    document_id: UUID
    filename: str
    file_type: str
    content_hash: str
    pages: list[ParsedPage] = field(default_factory=list)


@dataclass
class ChunkRecord:
    chunk_id: UUID
    document_id: UUID
    text: str
    content_hash: str
    token_estimate: int
    chunking_strategy: str
    page_number: int | None = None
    section_heading: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class DocumentSummary:
    id: UUID
    filename: str
    file_type: str
    status: str
    content_hash: str | None
    chunk_count: int
    created_at: datetime
    error_message: str | None = None

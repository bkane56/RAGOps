import enum
import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    file_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default=DocumentStatus.PENDING.value)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    chunks: Mapped[list["ChunkModel"]] = relationship(back_populates="document", cascade="all, delete")


class ChunkModel(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section_heading: Mapped[str | None] = mapped_column(String(512), nullable=True)
    token_estimate: Mapped[int] = mapped_column(Integer, default=0)
    chunking_strategy: Mapped[str] = mapped_column(String(64), default="recursive")
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    search_vector = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    document: Mapped[DocumentModel] = relationship(back_populates="chunks")
    embedding: Mapped["ChunkEmbeddingModel | None"] = relationship(
        back_populates="chunk",
        cascade="all, delete",
        uselist=False,
    )


class ChunkEmbeddingModel(Base):
    __tablename__ = "chunk_embeddings"

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chunks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    embedding = mapped_column(Vector(768), nullable=True)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    dimension: Mapped[int] = mapped_column(Integer, default=768)

    chunk: Mapped[ChunkModel] = relationship(back_populates="embedding")


class RagQueryModel(Base):
    __tablename__ = "rag_queries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    retrieval_strategy: Mapped[str] = mapped_column(String(64), nullable=False)
    top_k: Mapped[int] = mapped_column(Integer, default=5)
    document_filters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    retrieval_results: Mapped[list["RetrievalResultModel"]] = relationship(
        back_populates="query",
        cascade="all, delete",
    )
    answer: Mapped["AnswerModel | None"] = relationship(
        back_populates="query",
        cascade="all, delete",
        uselist=False,
    )
    citation_validation: Mapped["CitationValidationModel | None"] = relationship(
        back_populates="query",
        cascade="all, delete",
        uselist=False,
    )


class RetrievalResultModel(Base):
    __tablename__ = "retrieval_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rag_queries.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    reranker_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    strategy_name: Mapped[str] = mapped_column(String(64), nullable=False)
    token_estimate: Mapped[int] = mapped_column(Integer, default=0)
    cited: Mapped[bool] = mapped_column(Boolean, default=False)

    query: Mapped[RagQueryModel] = relationship(back_populates="retrieval_results")


class AnswerModel(Base):
    __tablename__ = "answers"

    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rag_queries.id", ondelete="CASCADE"),
        primary_key=True,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    model_provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    generation_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    insufficient_evidence: Mapped[bool] = mapped_column(Boolean, default=False)
    citations: Mapped[list] = mapped_column(JSONB, default=list)

    query: Mapped[RagQueryModel] = relationship(back_populates="answer")


class CitationValidationModel(Base):
    __tablename__ = "citation_validations"

    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rag_queries.id", ondelete="CASCADE"),
        primary_key=True,
    )
    coverage: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    unsupported_segments: Mapped[list] = mapped_column(JSONB, default=list)

    query: Mapped[RagQueryModel] = relationship(back_populates="citation_validation")


class EvaluationRunModel(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    aggregate_metrics: Mapped[dict] = mapped_column(JSONB, default=dict)
    per_case_results: Mapped[list] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

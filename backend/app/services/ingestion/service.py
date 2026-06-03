from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.documents.models import DocumentSummary
from app.infrastructure.database.models import ChunkModel, DocumentModel, DocumentStatus
from app.infrastructure.file_storage.local import LocalFileStorage
from app.providers.document_store.parsers import ALLOWED_EXTENSIONS, parse_document
from app.providers.embeddings.base import EmbeddingProvider
from app.providers.vector_store.base import VectorStore
from app.services.chunking.service import ChunkingService


class IngestionService:
    def __init__(
        self,
        db: Session,
        storage: LocalFileStorage,
        chunking: ChunkingService,
        embeddings: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self._db = db
        self._storage = storage
        self._chunking = chunking
        self._embeddings = embeddings
        self._vector_store = vector_store

    def list_documents(self) -> list[DocumentSummary]:
        docs = self._db.scalars(select(DocumentModel).order_by(DocumentModel.created_at.desc())).all()
        summaries: list[DocumentSummary] = []
        for doc in docs:
            count = self._db.scalar(
                select(func.count()).select_from(ChunkModel).where(ChunkModel.document_id == doc.id),
            )
            summaries.append(
                DocumentSummary(
                    id=doc.id,
                    filename=doc.filename,
                    file_type=doc.file_type,
                    status=doc.status,
                    content_hash=doc.content_hash,
                    chunk_count=count or 0,
                    created_at=doc.created_at,
                    error_message=doc.error_message,
                ),
            )
        return summaries

    def get_document(self, document_id: UUID) -> DocumentModel | None:
        return self._db.get(DocumentModel, document_id)

    async def ingest_upload(self, content: bytes, filename: str) -> DocumentSummary:
        suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if suffix not in ALLOWED_EXTENSIONS:
            from app.core.errors.handlers import AppError

            raise AppError(
                f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
                code="unsupported_file_type",
                status_code=400,
            )

        doc_id, path = self._storage.save_upload(content, filename)
        parsed = parse_document(content, filename, doc_id)
        doc = DocumentModel(
            id=doc_id,
            filename=filename,
            file_type=parsed.file_type,
            status=DocumentStatus.PROCESSING.value,
            content_hash=parsed.content_hash,
            storage_path=str(path),
        )
        self._db.add(doc)
        self._db.commit()

        try:
            await self._index_document(doc, content, parsed.content_hash)
            doc.status = DocumentStatus.READY.value
            doc.error_message = None
        except Exception as exc:
            doc.status = DocumentStatus.FAILED.value
            doc.error_message = str(exc)[:500]
        self._db.commit()
        self._db.refresh(doc)
        count = self._db.scalar(
            select(func.count()).select_from(ChunkModel).where(ChunkModel.document_id == doc.id),
        )
        return DocumentSummary(
            id=doc.id,
            filename=doc.filename,
            file_type=doc.file_type,
            status=doc.status,
            content_hash=doc.content_hash,
            chunk_count=count or 0,
            created_at=doc.created_at,
            error_message=doc.error_message,
        )

    async def reindex_document(self, document_id: UUID) -> DocumentSummary:
        doc = self._db.get(DocumentModel, document_id)
        if not doc:
            from app.core.errors.handlers import AppError

            raise AppError("Document not found", code="not_found", status_code=404)
        content = self._storage.read_file(doc.storage_path)
        doc.status = DocumentStatus.PROCESSING.value
        self._db.commit()
        try:
            await self._index_document(doc, content, doc.content_hash or "")
            doc.status = DocumentStatus.READY.value
            doc.error_message = None
        except Exception as exc:
            doc.status = DocumentStatus.FAILED.value
            doc.error_message = str(exc)[:500]
        self._db.commit()
        self._db.refresh(doc)
        count = self._db.scalar(
            select(func.count()).select_from(ChunkModel).where(ChunkModel.document_id == doc.id),
        )
        return DocumentSummary(
            id=doc.id,
            filename=doc.filename,
            file_type=doc.file_type,
            status=doc.status,
            content_hash=doc.content_hash,
            chunk_count=count or 0,
            created_at=doc.created_at,
            error_message=doc.error_message,
        )

    async def delete_document(self, document_id: UUID) -> None:
        doc = self._db.get(DocumentModel, document_id)
        if not doc:
            from app.core.errors.handlers import AppError

            raise AppError("Document not found", code="not_found", status_code=404)
        await self._vector_store.delete_by_document(document_id)
        self._db.delete(doc)
        self._db.commit()
        self._storage.delete_document_files(document_id)

    async def _index_document(self, doc: DocumentModel, content: bytes, content_hash: str) -> None:
        parsed = parse_document(content, doc.filename, doc.id)
        doc.content_hash = parsed.content_hash or content_hash
        await self._vector_store.delete_by_document(doc.id)
        existing_chunks = self._db.scalars(
            select(ChunkModel).where(ChunkModel.document_id == doc.id),
        ).all()
        for ch in existing_chunks:
            self._db.delete(ch)
        self._db.commit()

        chunk_records = self._chunking.chunk_document(parsed)
        texts = [c.text for c in chunk_records]
        embeddings_list: list[list[float]] = []
        if texts:
            embeddings_list = await self._embeddings.embed_texts(texts)

        for idx, record in enumerate(chunk_records):
            chunk = ChunkModel(
                id=record.chunk_id,
                document_id=record.document_id,
                text=record.text,
                metadata_json=record.metadata,
                page_number=record.page_number,
                section_heading=record.section_heading,
                token_estimate=record.token_estimate,
                chunking_strategy=record.chunking_strategy,
                content_hash=record.content_hash,
            )
            self._db.add(chunk)
            if idx < len(embeddings_list):
                await self._vector_store.upsert(
                    record.chunk_id,
                    embeddings_list[idx],
                    self._embeddings.model_name,
                    self._embeddings.dimension,
                )
        self._db.commit()

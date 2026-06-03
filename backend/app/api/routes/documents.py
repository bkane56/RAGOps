from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import ChunkResponse, DocumentResponse
from app.infrastructure.database.models import ChunkModel
from app.infrastructure.database.session import get_db
from app.infrastructure.file_storage.local import LocalFileStorage
from app.providers.embeddings.ollama import OllamaEmbeddingProvider
from app.providers.vector_store.pgvector import PgVectorStore
from app.services.chunking.service import ChunkingService
from app.services.ingestion.service import IngestionService

router = APIRouter(prefix="/documents", tags=["documents"])


def _ingestion_service(db: Session = Depends(get_db)) -> IngestionService:
    return IngestionService(
        db=db,
        storage=LocalFileStorage(),
        chunking=ChunkingService(),
        embeddings=OllamaEmbeddingProvider(),
        vector_store=PgVectorStore(db),
    )


@router.post("", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    service: IngestionService = Depends(_ingestion_service),
) -> DocumentResponse:
    content = await file.read()
    summary = await service.ingest_upload(content, file.filename or "upload.txt")
    return DocumentResponse(
        id=summary.id,
        filename=summary.filename,
        file_type=summary.file_type,
        status=summary.status,
        content_hash=summary.content_hash,
        chunk_count=summary.chunk_count,
        created_at=summary.created_at,
        error_message=summary.error_message,
    )


@router.get("", response_model=list[DocumentResponse])
def list_documents(service: IngestionService = Depends(_ingestion_service)) -> list[DocumentResponse]:
    return [
        DocumentResponse(
            id=d.id,
            filename=d.filename,
            file_type=d.file_type,
            status=d.status,
            content_hash=d.content_hash,
            chunk_count=d.chunk_count,
            created_at=d.created_at,
            error_message=d.error_message,
        )
        for d in service.list_documents()
    ]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    service: IngestionService = Depends(_ingestion_service),
) -> DocumentResponse:
    doc = service.get_document(document_id)
    if not doc:
        from app.core.errors.handlers import AppError

        raise AppError("Document not found", code="not_found", status_code=404)
    from sqlalchemy import func

    count = service._db.scalar(
        select(func.count()).select_from(ChunkModel).where(ChunkModel.document_id == doc.id),
    )
    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        status=doc.status,
        content_hash=doc.content_hash,
        chunk_count=count or 0,
        created_at=doc.created_at,
        error_message=doc.error_message,
    )


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: UUID,
    service: IngestionService = Depends(_ingestion_service),
) -> None:
    await service.delete_document(document_id)


@router.post("/{document_id}/reindex", response_model=DocumentResponse)
async def reindex_document(
    document_id: UUID,
    service: IngestionService = Depends(_ingestion_service),
) -> DocumentResponse:
    summary = await service.reindex_document(document_id)
    return DocumentResponse(
        id=summary.id,
        filename=summary.filename,
        file_type=summary.file_type,
        status=summary.status,
        content_hash=summary.content_hash,
        chunk_count=summary.chunk_count,
        created_at=summary.created_at,
        error_message=summary.error_message,
    )


@router.get("/{document_id}/chunks", response_model=list[ChunkResponse])
def list_chunks(document_id: UUID, db: Session = Depends(get_db)) -> list[ChunkResponse]:
    chunks = db.scalars(select(ChunkModel).where(ChunkModel.document_id == document_id)).all()
    return [
        ChunkResponse(
            id=c.id,
            document_id=c.document_id,
            text=c.text,
            page_number=c.page_number,
            section_heading=c.section_heading,
            token_estimate=c.token_estimate,
            chunking_strategy=c.chunking_strategy,
            content_hash=c.content_hash,
            created_at=c.created_at,
        )
        for c in chunks
    ]

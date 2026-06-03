from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.domain.retrieval.models import RetrievedChunk
from app.infrastructure.database.models import ChunkEmbeddingModel, ChunkModel, DocumentModel
from app.providers.vector_store.base import VectorStore


class PgVectorStore(VectorStore):
    def __init__(self, db: Session) -> None:
        self._db = db

    async def upsert(
        self,
        chunk_id: UUID,
        embedding: list[float],
        model_name: str,
        dimension: int,
    ) -> None:
        existing = self._db.get(ChunkEmbeddingModel, chunk_id)
        if existing:
            existing.embedding = embedding
            existing.model_name = model_name
            existing.dimension = dimension
        else:
            self._db.add(
                ChunkEmbeddingModel(
                    chunk_id=chunk_id,
                    embedding=embedding,
                    model_name=model_name,
                    dimension=dimension,
                ),
            )
        self._db.commit()

    async def search(
        self,
        query_embedding: list[float],
        top_k: int,
        document_ids: list[UUID] | None = None,
        metadata_filters: dict | None = None,
    ) -> list[RetrievedChunk]:
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        doc_filter_sql = ""
        params: dict = {"query_embedding": embedding_str, "top_k": top_k}
        if document_ids:
            doc_filter_sql = "AND c.document_id = ANY(CAST(:doc_ids AS uuid[]))"
            params["doc_ids"] = [str(d) for d in document_ids]

        # Use CAST(... AS vector) — :name::vector breaks SQLAlchemy named bind params.
        sql = text(
            f"""
            SELECT c.id, c.document_id, d.filename, c.text, c.page_number,
                   c.token_estimate,
                   1 - (e.embedding <=> CAST(:query_embedding AS vector)) AS similarity
            FROM chunk_embeddings e
            JOIN chunks c ON c.id = e.chunk_id
            JOIN documents d ON d.id = c.document_id
            WHERE d.status = 'ready'
            {doc_filter_sql}
            ORDER BY e.embedding <=> CAST(:query_embedding AS vector)
            LIMIT :top_k
            """
        )
        rows = self._db.execute(sql, params).fetchall()
        results: list[RetrievedChunk] = []
        for row in rows:
            results.append(
                RetrievedChunk(
                    chunk_id=row.id,
                    document_id=row.document_id,
                    filename=row.filename,
                    chunk_text=row.text,
                    strategy_name="basic_vector",
                    page_number=row.page_number,
                    similarity_score=float(row.similarity) if row.similarity else None,
                    token_estimate=row.token_estimate or 0,
                ),
            )
        return results

    async def delete_by_document(self, document_id: UUID) -> None:
        chunk_ids = self._db.scalars(
            select(ChunkModel.id).where(ChunkModel.document_id == document_id),
        ).all()
        for chunk_id in chunk_ids:
            emb = self._db.get(ChunkEmbeddingModel, chunk_id)
            if emb:
                self._db.delete(emb)
        self._db.commit()

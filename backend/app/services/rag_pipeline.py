import time
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.domain.evaluation.models import QueryMetrics
from app.domain.generation.models import CitationValidationResult, GeneratedAnswer
from app.domain.retrieval.models import RetrievalRequest, RetrievalResult, RetrievedChunk
from app.infrastructure.database.models import (
    AnswerModel,
    CitationValidationModel,
    RagQueryModel,
    RetrievalResultModel,
)
from app.providers.embeddings.ollama import OllamaEmbeddingProvider
from app.providers.llm.ollama import OllamaLLMProvider
from app.providers.vector_store.pgvector import PgVectorStore
from app.services.citation_validation.service import CitationValidationService
from app.services.evaluation.metrics import compute_query_metrics
from app.services.generation.context import ContextAssemblyService
from app.services.generation.service import GenerationService
from app.services.retrieval.strategies import get_strategy


class RagPipelineResult:
    def __init__(
        self,
        query_id: UUID,
        answer: GeneratedAnswer,
        retrieval: RetrievalResult,
        validation: CitationValidationResult,
        metrics: QueryMetrics,
        evidence: list[RetrievedChunk],
    ) -> None:
        self.query_id = query_id
        self.answer = answer
        self.retrieval = retrieval
        self.validation = validation
        self.metrics = metrics
        self.evidence = evidence


class RagPipelineService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._embeddings = OllamaEmbeddingProvider()
        self._llm = OllamaLLMProvider()
        self._vector_store = PgVectorStore(db)
        self._context = ContextAssemblyService()
        self._generation = GenerationService(self._llm)
        self._citation = CitationValidationService()
        self._settings = get_settings()

    async def run(
        self,
        question: str,
        strategy_name: str,
        top_k: int = 5,
        document_ids: list[UUID] | None = None,
    ) -> RagPipelineResult:
        start = time.perf_counter()
        query_id = uuid4()
        request = RetrievalRequest(
            query_text=question,
            strategy_name=strategy_name,
            top_k=top_k,
            document_ids=document_ids,
        )
        strategy = get_strategy(strategy_name, self._db, self._embeddings, self._vector_store)
        retrieval = await strategy.retrieve(request)

        threshold = self._settings.insufficient_evidence_threshold
        max_score = max((c.similarity_score or 0 for c in retrieval.chunks), default=0.0)
        if not retrieval.chunks or max_score < threshold:
            answer = GeneratedAnswer(
                text="Insufficient evidence in the indexed documents to answer this question.",
                citations=[],
                model_provider=self._llm.provider_name,
                model_name=self._llm.model_name,
                generation_latency_ms=0.0,
                insufficient_evidence=True,
            )
            validation = self._citation.validate(answer, retrieval.chunks)
        else:
            context = self._context.assemble(retrieval.chunks)
            answer = await self._generation.generate(question, context)
            validation = self._citation.validate(answer, retrieval.chunks)
            cited_set = {str(cid) for cid in validation.cited_chunk_ids}
            for chunk in retrieval.chunks:
                chunk.cited = str(chunk.chunk_id) in cited_set

        total_ms = (time.perf_counter() - start) * 1000
        metrics = compute_query_metrics(retrieval, answer, validation, total_ms)
        self._persist_query(query_id, question, strategy_name, top_k, document_ids, retrieval, answer, validation)
        return RagPipelineResult(
            query_id=query_id,
            answer=answer,
            retrieval=retrieval,
            validation=validation,
            metrics=metrics,
            evidence=retrieval.chunks,
        )

    def _persist_query(
        self,
        query_id: UUID,
        question: str,
        strategy_name: str,
        top_k: int,
        document_ids: list[UUID] | None,
        retrieval: RetrievalResult,
        answer: GeneratedAnswer,
        validation: CitationValidationResult,
    ) -> None:
        q = RagQueryModel(
            id=query_id,
            question=question,
            retrieval_strategy=strategy_name,
            top_k=top_k,
            document_filters={"document_ids": [str(d) for d in document_ids]} if document_ids else None,
        )
        self._db.add(q)
        for chunk in retrieval.chunks:
            self._db.add(
                RetrievalResultModel(
                    query_id=query_id,
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    filename=chunk.filename,
                    page_number=chunk.page_number,
                    chunk_text=chunk.chunk_text,
                    similarity_score=chunk.similarity_score,
                    reranker_score=chunk.reranker_score,
                    strategy_name=chunk.strategy_name,
                    token_estimate=chunk.token_estimate,
                    cited=chunk.cited,
                ),
            )
        self._db.add(
            AnswerModel(
                query_id=query_id,
                text=answer.text,
                model_provider=answer.model_provider,
                model_name=answer.model_name,
                generation_latency_ms=answer.generation_latency_ms,
                insufficient_evidence=answer.insufficient_evidence,
                citations=[{"chunk_id": c.chunk_id, "label": c.label} for c in answer.citations],
            ),
        )
        self._db.add(
            CitationValidationModel(
                query_id=query_id,
                coverage=validation.coverage,
                status=validation.status,
                unsupported_segments=validation.unsupported_segments,
            ),
        )
        self._db.commit()

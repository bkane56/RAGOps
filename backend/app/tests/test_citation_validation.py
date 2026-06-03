from uuid import uuid4

from app.domain.generation.models import CitationRef, GeneratedAnswer
from app.domain.retrieval.models import RetrievedChunk
from app.services.citation_validation.service import CitationValidationService


def test_insufficient_evidence_validation():
    service = CitationValidationService()
    chunk_id = uuid4()
    answer = GeneratedAnswer(
        text="Insufficient evidence",
        citations=[],
        model_provider="test",
        model_name="test",
        generation_latency_ms=1.0,
        insufficient_evidence=True,
    )
    retrieved = [
        RetrievedChunk(
            chunk_id=chunk_id,
            document_id=uuid4(),
            filename="a.txt",
            chunk_text="text",
            strategy_name="basic_vector",
        ),
    ]
    result = service.validate(answer, retrieved)
    assert result.status == "insufficient_evidence"
    assert result.coverage == 0.0


def test_valid_citation():
    service = CitationValidationService()
    chunk_id = uuid4()
    cid = str(chunk_id)
    answer = GeneratedAnswer(
        text="Answer with citation [1].",
        citations=[CitationRef(chunk_id=cid, label="[1]")],
        model_provider="test",
        model_name="test",
        generation_latency_ms=1.0,
        insufficient_evidence=False,
    )
    retrieved = [
        RetrievedChunk(
            chunk_id=chunk_id,
            document_id=uuid4(),
            filename="a.txt",
            chunk_text="text",
            strategy_name="basic_vector",
        ),
    ]
    result = service.validate(answer, retrieved)
    assert result.status in {"valid", "partial"}
    assert len(result.cited_chunk_ids) == 1

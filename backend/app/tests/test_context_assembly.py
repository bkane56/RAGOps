from uuid import uuid4

from app.domain.retrieval.models import RetrievedChunk
from app.services.generation.context import ContextAssemblyService


def test_assemble_context():
    service = ContextAssemblyService()
    chunks = [
        RetrievedChunk(
            chunk_id=uuid4(),
            document_id=uuid4(),
            filename="doc.md",
            chunk_text="Important fact about RAG.",
            strategy_name="basic_vector",
            similarity_score=0.9,
            token_estimate=10,
            page_number=1,
        ),
    ]
    ctx = service.assemble(chunks)
    assert "[1]" in ctx.context_text
    assert "doc.md" in ctx.context_text
    assert ctx.citation_map["[1]"] == str(chunks[0].chunk_id)

from uuid import uuid4

from app.domain.documents.models import ParsedDocument, ParsedPage
from app.services.chunking.service import ChunkingService, estimate_tokens, recursive_chunk_text


def test_estimate_tokens():
    assert estimate_tokens("abcd") >= 1


def test_recursive_chunk_text_splits_long_content():
    text = "word " * 500
    chunks = recursive_chunk_text(text, chunk_size=100, chunk_overlap=10)
    assert len(chunks) >= 2


def test_chunking_service():
    service = ChunkingService()
    parsed = ParsedDocument(
        document_id=uuid4(),
        filename="test.txt",
        file_type="text",
        content_hash="abc",
        pages=[ParsedPage(page_number=1, text="Short text for chunking test.")],
    )
    records = service.chunk_document(parsed)
    assert len(records) >= 1
    assert records[0].chunking_strategy == "recursive"

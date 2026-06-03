from uuid import uuid4

from app.providers.document_store.parsers import (
    ALLOWED_EXTENSIONS,
    compute_content_hash,
    parse_document,
    parse_markdown_file,
    parse_text_file,
)


def test_compute_content_hash():
    h1 = compute_content_hash(b"hello")
    h2 = compute_content_hash(b"hello")
    assert h1 == h2
    assert len(h1) == 64


def test_parse_text_file():
    parsed = parse_text_file(b"Hello world", "notes.txt")
    assert parsed.file_type == "text"
    assert len(parsed.pages) == 1
    assert "Hello" in parsed.pages[0].text


def test_parse_markdown_with_heading():
    content = b"# Title\n\nBody text here."
    parsed = parse_markdown_file(content, "doc.md")
    assert parsed.file_type == "markdown"
    assert any("Title" in p.text or "Body" in p.text for p in parsed.pages)


def test_parse_document_txt():
    parsed = parse_document(b"content", "file.txt", uuid4())
    assert parsed.filename == "file.txt"


def test_allowed_extensions():
    assert ".pdf" in ALLOWED_EXTENSIONS
    assert ".md" in ALLOWED_EXTENSIONS

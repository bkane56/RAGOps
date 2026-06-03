import hashlib
import re
from pathlib import Path
from uuid import UUID, uuid4

from pypdf import PdfReader

from app.domain.documents.models import ParsedDocument, ParsedPage


def compute_content_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def parse_text_file(content: bytes, filename: str, document_id: UUID | None = None) -> ParsedDocument:
    doc_id = document_id or uuid4()
    text = content.decode("utf-8", errors="replace")
    return ParsedDocument(
        document_id=doc_id,
        filename=filename,
        file_type="text",
        content_hash=compute_content_hash(content),
        pages=[ParsedPage(page_number=1, text=text)],
    )


def parse_markdown_file(content: bytes, filename: str, document_id: UUID | None = None) -> ParsedDocument:
    doc_id = document_id or uuid4()
    text = content.decode("utf-8", errors="replace")
    sections = re.split(r"(?=^#{1,3}\s)", text, flags=re.MULTILINE)
    pages: list[ParsedPage] = []
    for idx, section in enumerate(sections, start=1):
        section = section.strip()
        if not section:
            continue
        heading_match = re.match(r"^(#{1,3})\s+(.+)$", section, re.MULTILINE)
        heading = heading_match.group(2) if heading_match else None
        pages.append(ParsedPage(page_number=idx, text=section, section_heading=heading))
    if not pages:
        pages = [ParsedPage(page_number=1, text=text)]
    return ParsedDocument(
        document_id=doc_id,
        filename=filename,
        file_type="markdown",
        content_hash=compute_content_hash(content),
        pages=pages,
    )


def parse_pdf_file(content: bytes, filename: str, document_id: UUID | None = None) -> ParsedDocument:
    doc_id = document_id or uuid4()
    import io

    reader = PdfReader(io.BytesIO(content))
    pages: list[ParsedPage] = []
    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(ParsedPage(page_number=idx, text=text.strip()))
    if not pages:
        pages = [ParsedPage(page_number=1, text="")]
    return ParsedDocument(
        document_id=doc_id,
        filename=filename,
        file_type="pdf",
        content_hash=compute_content_hash(content),
        pages=pages,
    )


def parse_document(content: bytes, filename: str, document_id: UUID | None = None) -> ParsedDocument:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return parse_pdf_file(content, filename, document_id)
    if suffix in {".md", ".markdown"}:
        return parse_markdown_file(content, filename, document_id)
    return parse_text_file(content, filename, document_id)


ALLOWED_EXTENSIONS = {".pdf", ".md", ".markdown", ".txt", ".text"}

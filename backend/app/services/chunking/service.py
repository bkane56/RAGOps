import hashlib
import re
from uuid import UUID, uuid4

from app.core.config import get_settings
from app.domain.documents.models import ChunkRecord, ParsedDocument


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _chunk_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def recursive_chunk_text(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    if not text.strip():
        return []
    separators = ["\n\n", "\n", ". ", " "]
    chunks: list[str] = []

    def split_recursive(content: str, sep_index: int) -> list[str]:
        if len(content) <= chunk_size:
            return [content] if content.strip() else []
        if sep_index >= len(separators):
            parts = [content[i : i + chunk_size] for i in range(0, len(content), chunk_size - chunk_overlap)]
            return [p for p in parts if p.strip()]
        sep = separators[sep_index]
        parts = content.split(sep)
        result: list[str] = []
        current = ""
        for part in parts:
            candidate = f"{current}{sep}{part}" if current else part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current.strip():
                    result.extend(split_recursive(current, sep_index + 1))
                current = part
        if current.strip():
            result.extend(split_recursive(current, sep_index + 1))
        return result

    raw = split_recursive(text, 0)
    merged: list[str] = []
    for piece in raw:
        piece = piece.strip()
        if not piece:
            continue
        if merged and len(merged[-1]) < chunk_overlap:
            merged[-1] = f"{merged[-1]} {piece}"
        else:
            merged.append(piece)
    return merged if merged else [text[:chunk_size]]


class ChunkingService:
    def __init__(self) -> None:
        settings = get_settings()
        self._chunk_size = settings.chunk_size
        self._chunk_overlap = settings.chunk_overlap
        self._strategy = "recursive"

    def chunk_document(self, parsed: ParsedDocument) -> list[ChunkRecord]:
        records: list[ChunkRecord] = []
        for page in parsed.pages:
            text = page.text.strip()
            if not text:
                continue
            pieces = recursive_chunk_text(text, self._chunk_size, self._chunk_overlap)
            for piece in pieces:
                piece = re.sub(r"\s+", " ", piece).strip()
                if not piece:
                    continue
                records.append(
                    ChunkRecord(
                        chunk_id=uuid4(),
                        document_id=parsed.document_id,
                        text=piece,
                        content_hash=_chunk_hash(piece),
                        token_estimate=estimate_tokens(piece),
                        chunking_strategy=self._strategy,
                        page_number=page.page_number,
                        section_heading=page.section_heading,
                        metadata={"filename": parsed.filename, "file_type": parsed.file_type},
                    ),
                )
        return records

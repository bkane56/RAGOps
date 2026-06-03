import re
from pathlib import Path
from uuid import UUID, uuid4

from app.core.config import get_settings
from app.core.errors.handlers import AppError


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    safe = re.sub(r"[^\w.\-]", "_", name)
    return safe[:255] if safe else "upload.bin"


class LocalFileStorage:
    def __init__(self) -> None:
        settings = get_settings()
        self._root = Path(settings.document_storage_path)
        self._root.mkdir(parents=True, exist_ok=True)
        self._max_bytes = settings.max_upload_mb * 1024 * 1024

    def save_upload(self, content: bytes, filename: str, document_id: UUID | None = None) -> tuple[UUID, Path]:
        if len(content) > self._max_bytes:
            raise AppError(
                f"File exceeds maximum size of {self._max_bytes // (1024 * 1024)} MB",
                code="file_too_large",
                status_code=413,
            )
        doc_id = document_id or uuid4()
        safe_name = sanitize_filename(filename)
        doc_dir = self._root / str(doc_id)
        doc_dir.mkdir(parents=True, exist_ok=True)
        path = doc_dir / safe_name
        path.write_bytes(content)
        return doc_id, path

    def read_file(self, storage_path: str) -> bytes:
        path = Path(storage_path)
        resolved = path.resolve()
        root = self._root.resolve()
        if not str(resolved).startswith(str(root)):
            raise AppError("Invalid storage path", code="invalid_path", status_code=400)
        return resolved.read_bytes()

    def delete_document_files(self, document_id: UUID) -> None:
        doc_dir = self._root / str(document_id)
        if doc_dir.exists():
            for child in doc_dir.iterdir():
                child.unlink(missing_ok=True)
            doc_dir.rmdir()

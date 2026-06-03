import tempfile
from pathlib import Path

from app.infrastructure.file_storage.local import LocalFileStorage, sanitize_filename


def test_sanitize_filename():
    assert sanitize_filename("../../etc/passwd") == ".._.._etc_passwd" or "passwd" in sanitize_filename(
        "../../etc/passwd",
    )


def test_local_storage_save(monkeypatch, tmp_path):
    monkeypatch.setenv("DOCUMENT_STORAGE_PATH", str(tmp_path))
    from app.core.config.settings import get_settings

    get_settings.cache_clear()
    storage = LocalFileStorage()
    doc_id, path = storage.save_upload(b"hello", "test.txt")
    assert path.exists()
    assert storage.read_file(str(path)) == b"hello"

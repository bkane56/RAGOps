from app.core.config.settings import validate_required_settings


def test_validate_missing_empty_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")
    from app.core.config.settings import get_settings

    get_settings.cache_clear()
    missing = validate_required_settings()
    assert "DATABASE_URL" in missing
    get_settings.cache_clear()

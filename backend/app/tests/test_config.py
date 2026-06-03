from app.core.config.settings import Settings, validate_required_settings


def test_settings_defaults():
    settings = Settings()
    assert settings.app_name == "RAGOps Platform"
    assert settings.chunk_size > 0


def test_validate_required_settings_empty_db():
    missing = validate_required_settings()
    assert isinstance(missing, list)

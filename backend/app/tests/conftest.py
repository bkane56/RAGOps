import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from app.infrastructure.database.models import Base
from app.main import create_app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr("app.infrastructure.database.session.init_db", lambda: None)
    monkeypatch.setattr("app.infrastructure.database.session.check_db_connection", lambda: False)
    app = create_app()
    with TestClient(app) as c:
        yield c

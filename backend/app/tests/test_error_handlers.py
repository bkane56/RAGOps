from app.core.errors.handlers import AppError, register_exception_handlers
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_app_error_response():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    def boom():
        raise AppError("bad", code="bad_request", status_code=400)

    client = TestClient(app)
    response = client.get("/boom")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_request"

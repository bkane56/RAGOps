from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ask, compare, documents, evaluations, health
from app.api.routes import settings as settings_routes
from app.core.config import get_settings, validate_required_settings
from app.core.errors.handlers import register_exception_handlers
from app.core.logging.setup import setup_logging
from app.infrastructure.database.session import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_logging()
    missing = validate_required_settings()
    if missing:
        import logging

        logging.getLogger(__name__).warning("Missing settings: %s", ", ".join(missing))
    try:
        init_db()
    except Exception as exc:
        import logging

        logging.getLogger(__name__).warning("Database init skipped: %s", exc)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(documents.router)
    app.include_router(ask.router)
    app.include_router(compare.router)
    app.include_router(evaluations.router)
    app.include_router(settings_routes.router)
    return app


app = create_app()

from fastapi import FastAPI
from app.routers import health
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()

    docs_conf = {
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json",
    }

    if not settings.enable_docs:
        docs_conf = {key: None for key in docs_conf}

    app = FastAPI(title=settings.api_name, **docs_conf)

    app.include_router(health.router)

    return app


app = create_app()

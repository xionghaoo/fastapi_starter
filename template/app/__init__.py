from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from starlette.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging import configure_logging
from app.repo.session import Base, engine

__all__ = ["create_app", "Base", "engine"]


def create_app() -> FastAPI:
    configure_logging()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield

    app = FastAPI(
        title=f"{settings.app_name} API",
        version="1.0.0",
        lifespan=lifespan,
        redoc_url=None,
        openapi_tags=[
            {"name": "health", "description": "Health check endpoints"},
        ],
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def read_health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title="ReDoc",
            redoc_js_url="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js",
        )

    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    return app



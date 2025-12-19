from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from starlette.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging import configure_logging
from app.repo.session import Base, engine
from app.api.v1 import router as v1_router
from app.middleware.jwt_middleware import JWTMiddleware
from app.middleware.api_key_middleware import ApiKeyMiddleware
from app.static import STATIC_PATH

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

    app.add_middleware(
        ApiKeyMiddleware,
        include_patterns=(
            r"/api/v1/demo/secure",
            r"/api/v1/signature/.*"
        )
    )
    app.add_middleware(
        JWTMiddleware,
        include_patterns=(
            r"/api/v1/demo/me",
        )
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

    app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
    app.include_router(v1_router, prefix="/api/v1")
    return app



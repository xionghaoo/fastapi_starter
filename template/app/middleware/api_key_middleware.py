from typing import Callable, Iterable, Optional, List
import re
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.repo.api_key_repository import ApiKeyRepository
from app.repo.session import SessionLocal


class ApiKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, include_patterns: Iterable[str] = ()) -> None:
        super().__init__(app)
        self.include_regex: List[re.Pattern[str]] = [re.compile(p) for p in include_patterns]

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)
        path: str = request.url.path
        if not any(r.search(path) for r in self.include_regex):
            return await call_next(request)
        token: Optional[str] = request.headers.get("X-API-Key")
        if not token:
            return Response(status_code=401, content="Missing API key")

        db = SessionLocal()
        try:
            repo = ApiKeyRepository(db)
            entity = repo.verify_plain(token)
            if not entity:
                return Response(status_code=401, content="Invalid API key")
            repo.increment_usage(entity.id)
            request.state.api_key_id = int(entity.id)
            request.state.skip_jwt = True
        finally:
            db.close()

        return await call_next(request)



import re
from typing import Iterable, Pattern, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from app.repo.session import SessionLocal
from app.repo.api_key_repository import ApiKeyRepository
from app.api.response import error


class ApiKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, include_patterns: Iterable[str] | Tuple[str, ...] = ()) -> None:
        super().__init__(app)
        self.patterns: Tuple[Pattern[str], ...] = tuple(re.compile(p) for p in include_patterns)

    async def dispatch(self, request: Request, call_next):
        if self.patterns and not any(p.match(request.url.path) for p in self.patterns):
            return await call_next(request)

        token = request.headers.get("X-API-KEY")
        if not token:
            return error(message="Missing X-API-KEY", status_code=401)
        db = SessionLocal()
        try:
            repo = ApiKeyRepository(db)
            entity = repo.find_by_token_plain(token)
            if not entity or not entity.is_valid():
                return error(message="Invalid API key", status_code=401)
            request.state.api_key_id = entity.id
            return await call_next(request)
        finally:
            db.close()



from typing import Callable, Iterable, List
import re
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.utils.security import decode_access_token


class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, include_patterns: Iterable[str] = ()) -> None:
        super().__init__(app)
        self.include_regex: List[re.Pattern[str]] = [re.compile(p) for p in include_patterns]

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)
        if getattr(request.state, "skip_jwt", False):
            return await call_next(request)

        path: str = request.url.path
        if not any(r.search(path) for r in self.include_regex):
            return await call_next(request)

        auth = request.headers.get("authorization") or request.headers.get("Authorization")
        if not auth or not auth.lower().startswith("bearer "):
            return Response(status_code=401, content="Missing token")

        token = auth.split(" ", 1)[1]
        try:
            payload = decode_access_token(token)
        except Exception:
            return Response(status_code=401, content="Invalid token")

        sub = payload.get("sub")
        try:
            user_id_str = sub.split(":", 1)[1] if isinstance(sub, str) and ":" in sub else sub
            user_id = int(user_id_str)
        except Exception:
            return Response(status_code=401, content="Invalid subject")

        request.state.user_id = user_id
        return await call_next(request)



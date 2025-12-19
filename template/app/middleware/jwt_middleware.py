import re
from typing import Iterable, Pattern, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.api.response import error
from app.utils.security import verify_access_token


class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, include_patterns: Iterable[str] | Tuple[str, ...] = ()) -> None:
        super().__init__(app)
        self.patterns: Tuple[Pattern[str], ...] = tuple(re.compile(p) for p in include_patterns)

    async def dispatch(self, request: Request, call_next):
        if self.patterns and not any(p.match(request.url.path) for p in self.patterns):
            return await call_next(request)

        auth = request.headers.get("Authorization", "")
        parts = auth.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return error(message="Invalid Authorization header", status_code=401)
        token = parts[1]
        subject = verify_access_token(token)
        if subject is None:
            return error(message="Invalid token", status_code=401)
        request.state.user_id = subject
        return await call_next(request)



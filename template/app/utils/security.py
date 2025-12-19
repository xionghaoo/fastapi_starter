import hashlib
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.config import settings


def hash_api_key(token_plain: str, salt: str) -> str:
    data = f"{salt}:{token_plain}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def create_access_token(subject: str, expires_minutes: int = 60) -> str:
    # minimal helper used by demos/tests
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.log_dir + settings.app_name, algorithm="HS256")


def verify_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.log_dir + settings.app_name, algorithms=["HS256"])
        return str(payload.get("sub")) if payload.get("sub") is not None else None
    except JWTError:
        return None



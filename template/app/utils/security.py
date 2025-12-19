import hashlib
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from jose import jwt


JWT_ALG = "HS256"
JWT_SECRET = "CHANGE_ME_SECRET"
# Token validity: 30 days
JWT_EXPIRE_MINUTES = 60 * 24 * 30


def _pre_hash_password(password: str) -> bytes:
    """Pre-hash password with SHA256 to ensure it's always under bcrypt's 72-byte limit."""
    return hashlib.sha256(password.encode('utf-8')).digest()


def hash_password(password: str) -> str:
    """Hash a password using SHA256 + bcrypt to handle passwords longer than 72 bytes."""
    # Pre-hash with SHA256 to get a fixed 32-byte hash (well under bcrypt's 72-byte limit)
    pre_hashed = _pre_hash_password(password)
    # Use bcrypt to hash the pre-hashed password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pre_hashed, salt)
    # Return as string (bcrypt returns bytes)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a password against a hash."""
    # Pre-hash the plain password the same way
    pre_hashed = _pre_hash_password(plain_password)
    # Verify against the stored hash
    try:
        return bcrypt.checkpw(pre_hashed, password_hash.encode('utf-8'))
    except Exception:
        return False


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])



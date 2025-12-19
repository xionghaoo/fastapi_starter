from datetime import datetime, timezone, timedelta
import hashlib
import hmac
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repo.base import Repository
from app.repo.models import ApiKey


def _hash_api_token(token: str) -> str:
    data: str = settings.api_key_salt + token
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


class ApiKeyRepository(Repository[ApiKey]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, ApiKey)

    def find_by_hash(self, key_hash: str) -> Optional[ApiKey]:
        return super().find_one_by(key_hash=key_hash)

    def create_with_plain(self, name: str, token_plain: str, scopes: Optional[str] = None, validity_days: Optional[int] = 30) -> ApiKey:
        key_hash: str = _hash_api_token(token_plain)
        expires_at = datetime.now(timezone.utc) + timedelta(days=validity_days)
        return super().create(
            name=name,
            key_hash=key_hash,
            scopes=scopes,
            usage_count=0,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at
        )

    def increment_usage(self, api_key_id: int) -> None:
        entity = self.find_by_id(api_key_id)
        if not entity:
            return
        entity.usage_count += 1
        self.db.add(entity)
        self.db.commit()

    def verify_plain(self, token_plain: str) -> Optional[ApiKey]:
        key_hash: str = _hash_api_token(token_plain)
        entity = self.find_by_hash(key_hash)
        if not entity:
            return None
        if not entity.is_active:
            return None
        if entity.expires_at is not None:
            now_utc = datetime.now(timezone.utc)
            expires_at = entity.expires_at
            if expires_at.tzinfo is None:
                # assume stored as UTC-naive; normalize to UTC-aware for safe comparison
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at <= now_utc:
                return None
        return entity



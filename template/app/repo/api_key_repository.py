from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.repo.models.api_key import ApiKey
from app.repo.base import Repository
from app.utils.security import hash_api_key
from app.core.config import settings


class ApiKeyRepository(Repository[ApiKey]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, ApiKey)

    def _hash(self, token_plain: str) -> str:
        return hash_api_key(token_plain, settings.app_name + settings.env)

    def create_with_plain(
        self,
        *,
        name: str,
        token_plain: str,
        scopes: Optional[str] = None,
        validity_days: Optional[int] = None,
    ) -> ApiKey:
        valid_until = None
        if validity_days is not None and validity_days > 0:
            valid_until = datetime.utcnow() + timedelta(days=validity_days)
        entity = ApiKey(
            name=name,
            token_hash=self._hash(token_plain),
            scopes=scopes,
            is_active=True,
            valid_until=valid_until,
        )
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def list(self) -> List[ApiKey]:
        return super().list(order_by=ApiKey.id, descending=True)

    def find_by_token_plain(self, token_plain: str) -> Optional[ApiKey]:
        token_hash = self._hash(token_plain)
        stmt = select(ApiKey).where(ApiKey.token_hash == token_hash)
        return self.db.scalar(stmt)



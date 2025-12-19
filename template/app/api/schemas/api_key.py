from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ApiKeyCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    scopes: Optional[str] = Field(default=None, max_length=256)
    validity_days: int = Field(default=30, ge=1, le=3650)


class ApiKeyRead(BaseModel):
    id: int
    name: str
    scopes: Optional[str] = None
    usage_count: int
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None


class ApiKeyWithPlain(BaseModel):
    token: str
    key: ApiKeyRead



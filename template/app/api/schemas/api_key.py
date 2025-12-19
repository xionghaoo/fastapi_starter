from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ApiKeyCreateRequest(BaseModel):
    name: str = Field(description="Key name")
    scopes: Optional[str] = Field(default=None, description="Comma separated scopes")
    validity_days: Optional[int] = Field(default=None, description="Validity in days")


class ApiKeyRead(BaseModel):
    id: int
    name: str
    scopes: Optional[str] = None
    is_active: bool
    valid_until: Optional[datetime] = None
    created_at: datetime


class ApiKeyWithPlain(BaseModel):
    token: str
    key: ApiKeyRead



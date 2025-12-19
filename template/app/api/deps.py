from typing import Annotated
from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repo.session import get_db
from app.repo.api_key_repository import ApiKeyRepository


SessionDep = Annotated[Session, Depends(get_db)]


def _get_api_key_repo(db: SessionDep) -> ApiKeyRepository:
    return ApiKeyRepository(db)


ApiKeyRepoDep = Annotated[ApiKeyRepository, Depends(_get_api_key_repo)]


def _get_current_user_id_from_state(request: Request) -> str:
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthenticated")
    return str(user_id)


CurrentUserIdDep = Annotated[str, Depends(_get_current_user_id_from_state)]


def _get_valid_api_key(request: Request) -> int:
    api_key_id = getattr(request.state, "api_key_id", None)
    if api_key_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthenticated")
    return int(api_key_id)


ApiKeyIdDep = Annotated[int, Depends(_get_valid_api_key)]



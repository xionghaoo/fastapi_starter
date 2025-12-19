import secrets
from fastapi import APIRouter
from app.api.deps import ApiKeyRepoDep
from app.api.schemas.api_key import ApiKeyCreateRequest, ApiKeyRead, ApiKeyWithPlain
from app.api.response import success


router = APIRouter()


@router.post("/api-key", response_model=ApiKeyWithPlain, summary="Create API key")
def create_api_key(payload: ApiKeyCreateRequest, repo: ApiKeyRepoDep):
    token: str = "ra_" + secrets.token_urlsafe(30)
    entity = repo.create_with_plain(
        name=payload.name,
        token_plain=token,
        scopes=payload.scopes,
        validity_days=payload.validity_days,
    )
    ret = ApiKeyWithPlain(token=token, key=ApiKeyRead(**entity.__dict__))
    return success(data=ret)


@router.get("/api-keys", response_model=list[ApiKeyRead], summary="List API keys")
def list_api_keys(repo: ApiKeyRepoDep) -> list[ApiKeyRead]:
    items = repo.list()
    return [ApiKeyRead(**i.__dict__) for i in items]


@router.delete("/api-key/{key_id}", summary="Revoke API key")
def revoke_api_key(key_id: int, repo: ApiKeyRepoDep) -> dict[str, str]:
    entity = repo.find_by_id(key_id)
    if entity:
        entity.is_active = False
        repo.db.add(entity)
        repo.db.commit()
    return {"message": "revoked"}



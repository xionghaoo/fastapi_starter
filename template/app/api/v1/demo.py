from fastapi import APIRouter
from app.api.response import success, error
from app.api.deps import ApiKeyIdDep, CurrentUserIdDep


router = APIRouter()


@router.get("/public", summary="Public echo demo (no auth)")
def public_echo(q: str = "ping") -> dict:
    return success({"echo": q})


@router.get("/secure", summary="Secure demo (requires API key via X-API-KEY)")
def secure_echo(api_key_id: ApiKeyIdDep, q: str = "ping") -> dict:
    return success({"echo": q, "api_key_id": api_key_id})


@router.get("/me", summary="JWT demo (requires Authorization: Bearer <token>)")
def me(user_id: CurrentUserIdDep) -> dict:
    return success({"user_id": user_id})



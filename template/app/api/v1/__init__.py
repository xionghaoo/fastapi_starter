from fastapi import APIRouter
from .signature import router as signature_router
from .demo import router as demo_router

router = APIRouter()
router.include_router(signature_router, prefix="/signature", tags=["signature"])
router.include_router(demo_router, prefix="/demo", tags=["demo"])



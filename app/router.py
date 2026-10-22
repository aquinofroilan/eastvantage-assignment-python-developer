"""Application-wide API router."""

from fastapi import APIRouter

from app.address.router import router as address_router

router = APIRouter()
router.include_router(address_router)

from fastapi import APIRouter

from app.api.v1.endpoints import items
from app.api.v1.endpoints import classify

api_router = APIRouter()
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(classify.router, prefix="/classify", tags=["classify"])
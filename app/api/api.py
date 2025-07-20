from fastapi import APIRouter
from api.endpoints import x


api_router = APIRouter()

api_router.include_router(x.router, prefix="/x", tags=["X Bot"])

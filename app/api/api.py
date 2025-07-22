from fastapi import APIRouter
from app.api.endpoints import post


api_router = APIRouter()

api_router.include_router(post.router, tags=["dev Bot"])

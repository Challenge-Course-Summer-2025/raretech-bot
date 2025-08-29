from fastapi import APIRouter

from app.api.endpoints import post, tally

api_router = APIRouter()

api_router.include_router(post.router, tags=["dev Bot"])
api_router.include_router(tally.router, tags=["dev Bot"])

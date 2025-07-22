import os
from fastapi import APIRouter
from app.services.post import PostService

router = APIRouter()


@router.post("/post")
def post_qiita_to_x():
    org_id = os.getenv("QIITA_ORGANIZATION_ID")
    if not org_id:
        raise ValueError("環境変数 QIITA_ORGANIZATION_ID を設定してください")

    service = PostService(org_id)
    service.run()
    return {"status": "posted if new article found"}

from app.core.config import settings
from app.services.post import PostService


def handler(event, context):
    org_id = settings.QIITA_ORGANIZATION_ID
    if not org_id:
        raise ValueError("環境変数 QIITA_ORGANIZATION_ID を設定してください")

    service = PostService(org_id)
    service.run()

    return {
        "statusCode": 200,
        "body": "PostService executed successfully"
    }

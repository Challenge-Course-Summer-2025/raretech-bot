from app.core.config import settings
from app.services.post import PostService
from app.services.tally import ClickCollector


def handler(event, context):
    action = event.get("action")

    if action == "post":
        org_id = settings.QIITA_ORGANIZATION_ID
        if not org_id:
            raise ValueError(
                "環境変数 QIITA_ORGANIZATION_ID を設定してください"
            )
        PostService(org_id).run()

    elif action == "collect_clicks":
        ClickCollector().run()

    return {"statusCode": 200, "body": f"{action} executed successfully"}

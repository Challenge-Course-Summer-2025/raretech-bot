from app.core.config import settings
from app.services.post import PostService
from app.services.tally import ClickCollector
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """
    EventBridgeのルールによって 'action' を渡す想定:
      - X投稿用ルール: action='post'
      - クリック集計用ルール: action='tally'
    """
    action = event.get("action") or event.get("detail", {}).get("action")
    logger.info(f"Received event: {event}")

    if action == "post":
        org_id = settings.QIITA_ORGANIZATION_ID
        if not org_id:
            raise ValueError(
                "環境変数 QIITA_ORGANIZATION_ID を設定してください"
            )
        PostService(org_id).run()
        logger.info("✅ X投稿処理を実行しました")

    elif action == "tally":
        ClickCollector().run()
        logger.info("✅ クリック集計処理を実行しました")

    else:
        org_id = settings.QIITA_ORGANIZATION_ID
        PostService(org_id).run()
        logger.info("DEBUG✅ X投稿処理を実行しました")
        # logger.warning(f"未対応のアクション: {action}")
        # return {"statusCode": 400, "body": f"Unsupported action: {action}"}

    return {"statusCode": 200, "body": f"{action} executed successfully"}

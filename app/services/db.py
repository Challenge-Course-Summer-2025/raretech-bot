from clients.db import scan_templates, put_post_history
from datetime import datetime
import random
import uuid


DEFAULT_TEMPLATE = "【Qiita】{title} by {user}\n{url} #Qiita #HackathonChallenge"


def get_template():
    try:
        response = scan_templates()
    except Exception as e:
        print(f"テンプレートの取得に失敗: {e}")
        return DEFAULT_TEMPLATE

    items = response.get("Items", [])
    if not items:
        return DEFAULT_TEMPLATE

    # 有効なテンプレートがあるか確認（1つのみが想定されている）
    active_items = [item for item in items if item.get("is_active") is True]
    if active_items:
        return active_items[0]["template"]

    # 有効なテンプレートが無い場合、最新のテンプレートを返す
    try:
        sorted_items = sorted(
            items,
            key=lambda x: datetime.fromisoformat(x["created_at"]),
            reverse=True
        )
        return sorted_items[0]["template"]
    except Exception as e:
        print(f"テンプレートのソートに失敗: {e}")
        return random.choice(items)["template"]


def save_post_history(qiita_item: dict, template_id: str = None):
    now = datetime.utcnow().isoformat()

    item = {
        "post_id": str(uuid.uuid4()),  # 自動採番
        "qiita_id": qiita_item["id"],
        "title": qiita_item["title"],
        "author": qiita_item["user"],
        "url": qiita_item["url"],
        "template_id": template_id,  # Noneまたは文字列
        "created_at": now,
        "updated_at": now,
    }

    return put_post_history(item)

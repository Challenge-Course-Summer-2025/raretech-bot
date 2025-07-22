import random
import uuid
from datetime import datetime, timedelta
from dateutil.parser import isoparse
from app.clients.db import scan_templates, put_post_history
from app.clients.db import scan_post_history, get_post_history_by_index


DEFAULT_TEMPLATE = "【Qiita】{title} by {user}\n{url} #Qiita #HackathonChallenge"


# テンプレートを取得
def get_template():
    try:
        templates = scan_templates().get("Items", [])
    except Exception as e:
        print(f"テンプレート取得に失敗: {e}")
        return DEFAULT_TEMPLATE

    if not templates:
        return DEFAULT_TEMPLATE

    template = (
        get_active_template(templates)
        or get_latest_template(templates)
        or get_fallback_template(templates)
    )

    return template


# 有効なテンプレートを取得
def get_active_template(templates):
    active = [t for t in templates if t.get("is_active") is True]
    return active[0]["template"] if active else None


# 最新のテンプレートを取得
def get_latest_template(templates):
    try:
        sorted_items = sorted(
            templates,
            key=lambda t: datetime.fromisoformat(t["created_at"]),
            reverse=True
        )
        return sorted_items[0]["template"]
    except Exception as e:
        print(f"テンプレートのソートに失敗: {e}")
        return None


# ランダムなテンプレートを返す
def get_fallback_template(templates):
    return random.choice(templates)["template"]


# 投稿履歴を保存
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


# 投稿済みかどうかをチェック
def is_posted(qiita_id: str) -> bool:
    try:
        response = get_post_history_by_index(qiita_id)
        items = response.get("Items", [])
        return len(items) > 0
    except Exception as e:
        print(f"投稿履歴チェックに失敗: {e}")
        return False


# ３ヶ月以上前の投稿履歴を取得
def get_old_post_history(month=3):
    try:
        response = scan_post_history()
        items = response.get("Items", [])
        threshold = datetime.utcnow() - timedelta(days=30*month)
        old_items = [item for item in items
                     if isoparse(item["created_at"]) < threshold]
        return sorted(old_items, key=lambda x: isoparse(x["created_at"]))
    except Exception as e:
        print(f"過去の投稿履歴の取得に失敗: {e}")
        return []

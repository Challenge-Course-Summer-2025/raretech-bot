import uuid
from datetime import datetime, date
from dateutil.parser import isoparse
from app.clients import db as cdb
from app.core.utils import type_cnv_for_db


DEFAULT_TEMPLATE = (
    "【Qiita】{title} by {user}\n{url} #Qiita #HackathonChallenge"
)


def get_template() -> str:
    """有効テンプレート → 最新テンプレート → デフォルトの順で取得"""
    try:
        # 1. 有効なテンプレートをGSIから取得
        active_resp = cdb.query_active_templates(limit=1)
        items = active_resp.get("Items", [])
        if items:
            return items[0]["template"]

        # 2. 有効テンプレートがない場合、最新テンプレートを取得
        latest_resp = cdb.query_latest_templates(limit=1)
        items = latest_resp.get("Items", [])
        if items:
            return items[0]["template"]

        # 3. どちらもない場合はデフォルトを返す
        return DEFAULT_TEMPLATE

    except Exception as e:
        print(f"テンプレート取得に失敗: {e}")
        return DEFAULT_TEMPLATE


# 投稿履歴を保存
def save_post_history(item: dict, template_id: str = None):
    item = type_cnv_for_db(item)
    now = datetime.utcnow().isoformat()
    post_id = str(uuid.uuid4())
    item_db = {
        "id": post_id,
        "post_at": item.get("post_at", now),
        "is_posted_X": item.get("is_posted_X", False),
        "is_posted_Mattermost": item.get("is_posted_Mattermost", False),
        "qiita_id": item["id"],
        "title": item.get("title"),
        "author": item.get("user"),
        "template_id": template_id,
        "qiita_url": item.get("url"),
        "is_tracked": item.get("is_tracked", False),
        "short_url": item.get("short_url"),
        "shortio_id": item.get("shortio_id"),
        "tweet_url": item.get("tweet_url"),
        "created_at": now,
        "updated_at": now,
    }
    item_db = type_cnv_for_db(item_db)
    return cdb.put_post(item_db)


# 投稿済みかどうかをチェック
def is_posted(qiita_id: str) -> bool:
    resp = cdb.query_posts_by_qiita_id(qiita_id)
    return len(resp.get("Items", [])) > 0


# 最も古い既投稿履歴を取得
def get_old_post_history(limit=1):
    try:
        resp = cdb.query_posted_X(
            limit=limit, projection="id, post_at, tweet_url, created_at"
        )
        items = resp.get("Items", [])
        # 既投稿のみフィルタ（投影属性のみ使用）
        posted_items = [
            item
            for item in items
            if item.get("is_posted_X", True) or item.get("tweet_url")
        ]
        return posted_items
    except Exception as e:
        print(f"過去の投稿履歴の取得に失敗: {e}")
        return []


# ▼ POSTを投影付きでページング反復
def iter_posted_X(page_size=50, projection: str = None):
    last_key = None
    while True:
        resp = cdb.query_posted_X(
            limit=page_size, start_key=last_key, projection=projection
        )
        items = resp.get("Items", [])
        if items:
            yield items
        last_key = resp.get("LastEvaluatedKey")
        if not last_key:
            break


# ▼ 記事メトリクス更新
def update_post_metrics_row(
    post_id: str, checked_at: str, clicks: int, x_views: int, ctr: float
):
    return cdb.update_post_metrics(post_id, checked_at, clicks, x_views, ctr)


# ▼ 指定日の POST.x_views 合計
def sum_post_x_views_by_date(target_date: date) -> int:
    total = 0
    projection = "created_at, x_views"
    for items in iter_posted_X(page_size=50, projection=projection):
        for it in items:
            try:
                d = isoparse(it["created_at"]).date()
            except Exception:
                continue
            if d == target_date:
                total += it.get("x_views") or 0
    return total


# ▼ 固定リンク保存
def save_static_link_clicks_record(record: dict):
    return cdb.put_static_link_clicks(record)


# ▼ 指定日の Static_link_clicks.tweet_views 合計
def sum_static_views_by_date(target_date: date) -> int:
    projection = "tweet_views"
    resp = cdb.get_static_by_checked_date(
        target_date.isoformat(), projection=projection
    )
    items = resp.get("Items", []) or []
    return sum(it.get("tweet_views") or 0 for it in items)

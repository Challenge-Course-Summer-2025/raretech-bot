from datetime import datetime
from boto3.dynamodb.conditions import Key
from app.core.db import db
from app.core.config import settings

posts_table = db.Table(settings.DB_TABLE_POST_HISTORY)
templates_table = db.Table(settings.DB_TABLE_TEMPLATE)
article_clicks_table = db.Table(settings.DB_TABLE_ARTICLE_CLICKS)
static_link_clicks_table = db.Table(settings.DB_TABLE_STATIC_LINK_CLICKS)
api_status_table = db.Table(settings.DB_TABLE_API_STATUS)


def query_active_templates(limit=1):
    """
    GSIを使って有効テンプレートを取得（新しい順）
    PK = is_active, SK = created_at
    """
    return templates_table.query(
        IndexName="GSI_ActiveTemplates",
        KeyConditionExpression=Key("is_active").eq(1),
        ScanIndexForward=False,
        Limit=limit,
    )


def query_latest_templates(limit=1):
    """
    全テンプレートから最新を取得（新しい順）
    PK固定値 "TEMPLATES", SK = created_at
    """
    return templates_table.query(
        KeyConditionExpression=Key("PK").eq("TEMPLATES"),
        ScanIndexForward=False,
        Limit=limit,
    )


# 投稿履歴の取得
def get_post_by_id(post_id: str):
    return posts_table.get_item(Key={"post_id": post_id})


def put_post(item: dict):
    return posts_table.put_item(Item=item)


def query_posts_by_qiita_id(qiita_id: str):
    return posts_table.query(
        IndexName="qiita_id-index",
        KeyConditionExpression=Key("qiita_id").eq(qiita_id),
    )


# POST一覧をページング取得
def query_posted_X(limit=10, start_key=None, projection: str = None):
    kwargs = {
        "IndexName": "posted_X-index",
        "KeyConditionExpression": Key("is_posted_X").eq(1),
        "ScanIndexForward": True,
        "Limit": limit,
    }
    if start_key:
        kwargs["ExclusiveStartKey"] = start_key
    if projection:
        kwargs["ProjectionExpression"] = projection
    return posts_table.query(**kwargs)


# 記事の日次メトリクスを更新
def update_post_metrics(
    post_id: str, checked_at: str, clicks: int, x_views: int, ctr: float
):
    now = datetime.utcnow().isoformat()
    return article_clicks_table.update_item(
        Key={"post_id": post_id, "checked_at": checked_at},
        UpdateExpression="SET clicks_article=:c, tweet_views=:xv,\
                        ctr_article=:ctr, updated_at=:u",
        ExpressionAttributeValues={
            ":c": clicks,
            ":xv": x_views,
            ":ctr": ctr,
            ":u": now,
        },
    )


# 固定リンクのレコード保存
def put_static_link_clicks(item: dict):
    return static_link_clicks_table.put_item(Item=item)


# 固定リンクレコード取得
def get_static_by_checked_date(checked_at_iso: str, projection: str = None):
    kwargs = {
        "IndexName": "checked_at-index",
        "KeyConditionExpression": Key("checked_at").eq(checked_at_iso),
    }
    if projection:
        kwargs["ProjectionExpression"] = projection
    return static_link_clicks_table.query(**kwargs)


# APIステータスの保存
def put_api_status(item: dict):
    return api_status_table.put_item(Item=item)

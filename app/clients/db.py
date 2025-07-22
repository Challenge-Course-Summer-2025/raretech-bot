from app.core.db import db
from app.core.config import settings

post_history_table = db.Table(settings.DB_TABLE_POST_HISTORY)
template_table = db.Table(settings.DB_TABLE_TEMPLATE)


def scan_templates():
    return template_table.scan()


def get_item_by_post_id(post_id):
    return post_history_table.get_item(Key={"post_id": post_id})


def put_post_history(item):
    return post_history_table.put_item(Item=item)


def scan_post_history():
    return post_history_table.scan()


def get_post_history_by_index(qiita_id: str):
    return post_history_table.query(
        IndexName="qiita_id-index",
        KeyConditionExpression="qiita_id = :qid",
        ExpressionAttributeValues={":qid": qiita_id}
    )

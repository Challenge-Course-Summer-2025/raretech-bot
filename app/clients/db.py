from core.db import db
from core.config import settings

post_history_table = db.Table(settings.DB_TABLE_POST_HISTORY)
template_table = db.Table(settings.DB_TABLE_TEMPLATE)


def scan_templates():
    return template_table.scan()


def get_item_by_post_id(post_id):
    return post_history_table.get_item(Key={"post_id": post_id})


def put_post_history(item):
    return post_history_table.put_item(Item=item)

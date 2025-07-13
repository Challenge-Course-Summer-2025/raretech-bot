import boto3
import random
import os
from datetime import datetime
from app.core.config import settings


dynamodb = boto3.resource(
    "dynamodb",
    region_name=os.getenv("AWS_REGION", "ap-northeast-1"),
    endpoint_url=os.getenv("DYNAMODB_ENDPOINT"),
)
table = dynamodb.Table(settings.DYNAMO_TABLE_NAME)


def get_template():
    response = table.scan()
    items = response.get("Items", [])
    
    # 1. テンプレートが存在しない → デフォルトテンプレートを返す
    if not items:
        return "🚨 デフォルトテンプレート：記事を読んでね！"

    # 2. 使用フラグが立っているテンプレートがあるか確認（1つのみが想定されている）
    active_items = [item for item in items if item.get("is_active") is True]
    if active_items:
        return active_items[0]["template"]

    # 3. 使用フラグ付きテンプレートが無い場合、最新のテンプレートを返す
    # ※ created_at フィールドが ISO8601文字列で存在すると仮定
    try:
        sorted_items = sorted(
            items,
            key=lambda x: datetime.fromisoformat(x["created_at"]),
            reverse=True
        )
        return sorted_items[0]["template"]
    except Exception as e:
        # フォールバック：どれか1つランダムに返す（created_at が壊れていた場合）
        print(f"テンプレートのソートに失敗: {e}")
        return random.choice(items)["template"]



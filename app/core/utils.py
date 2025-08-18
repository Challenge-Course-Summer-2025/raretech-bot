from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date


def type_cnv_for_db(obj):
    """
    DynamoDBに保存するための型変換
    - bool → 0/1 (N型として保存)
    - float → Decimal (精度を保ちつつ保存)
    - datetime, date → ISOフォーマット文字列
    - dict, list は再帰的に処理
    """
    if isinstance(obj, bool):
        return 1 if obj else 0
    if isinstance(obj, float):
        return Decimal(str(obj)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: type_cnv_for_db(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [type_cnv_for_db(v) for v in obj]
    return obj

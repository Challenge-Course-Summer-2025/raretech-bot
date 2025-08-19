import os
import json
import boto3
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


if os.getenv("ENV") != "production":
    load_dotenv()


class Settings(BaseSettings):
    QIITA_ORGANIZATION_ID: str
    MATTERMOST_WEBHOOK_URL: str
    X_API_KEY: str
    X_API_SECRET: str
    X_ACCESS_TOKEN: str
    X_ACCESS_TOKEN_SECRET: str
    X_USERNAME: str
    SHORTIO_ACCESS_TOKEN: str
    SHORTIO_DOMAIN: Optional[str] = "raretech.short.gy"
    DYNAMODB_ENDPOINT: Optional[str] = None
    DB_TABLE_POST_HISTORY: str
    DB_TABLE_TEMPLATE: str
    DB_TABLE_ARTICLE_CLICKS: str
    DB_TABLE_STATIC_LINK_CLICKS: str
    DB_TABLE_API_STATUS: str
    AWS_REGION: str
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    class Config:
        env_file = ".env"


def get_settings():
    if os.getenv("ENV") == "production":
        load_secrets()
    return Settings()


def load_secrets():
    secret_name = os.getenv("SECRETS_NAME", "raretech-bot")
    region = os.getenv("AWS_REGION", "ap-northeast-1")

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(response["SecretString"])
    except Exception as e:
        raise RuntimeError(
            f"Secrets Managerからシークレットを取得できませんでした: {e}"
        )

    # 各値を上書き
    for key, value in secret_dict.items():
        os.environ[key] = value


settings = get_settings()

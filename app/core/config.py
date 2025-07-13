import os
import json
import boto3
from pydantic import BaseSettings


class Settings(BaseSettings):
    DYNAMO_TABLE_NAME: str = "post_template"
    AWS_REGION: str = "ap-northeast-1"
    X_API_KEY: str
    X_API_SECRET: str
    X_ACCESS_TOKEN: str
    X_ACCESS_TOKEN_SECRET: str

    class Config:
        env_file = ".env"

    def load_secrets(self, secret_name: str):
        """
        AWS Secrets Manager からシークレットを読み込んで環境変数を上書き
        """
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=self.AWS_REGION)

        try:
            response = client.get_secret_value(SecretId=secret_name)
            secret_dict = json.loads(response["SecretString"])
        except Exception as e:
            raise RuntimeError(f"Secrets Managerからシークレットを取得できませんでした: {e}")

        # 各値を上書き
        for key, value in secret_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)




settings = Settings()

# 本番環境の場合は Secrets Manager を適用
if os.getenv("ENV") == "production":
    settings.load_secrets(secret_name=os.getenv("SECRETS_NAME", "raretech-bot-secret"))
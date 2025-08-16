import os
import requests


class MattermostClient:
    def __init__(self):
        self.webhook_url = os.getenv("MATTERMOST_WEBHOOK_URL")

    def post_message(self, text: str):
        payload = {"text": text}
        response = requests.post(self.webhook_url, json=payload)
        if response.status_code != 200:
            print(
                f"❌ Mattermost投稿失敗: {response.status_code}, {response.text}"
            )
        else:
            print("✅ Mattermostに投稿成功")

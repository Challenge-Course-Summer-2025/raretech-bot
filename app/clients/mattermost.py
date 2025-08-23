import os
import requests


class MattermostClient:
    def __init__(self):
        self.webhook_url = os.getenv("MATTERMOST_WEBHOOK_URL")

    def post_message(self, text: str) -> bool:
        payload = {"text": text}
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=5)
            if response.status_code != 200:
                print(
                    f"❌ Mattermost投稿失敗:"
                    f"{response.status_code}, {response.text}"
                )
                return False
            else:
                print("✅ Mattermostに投稿成功")
                return True
        except Exception as e:
            print(f"❌ Mattermost投稿例外: {e}")
            return False

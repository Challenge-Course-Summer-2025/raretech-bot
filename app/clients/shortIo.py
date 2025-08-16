import requests
from app.core.config import settings


class ShortIoClient:
    def __init__(self):
        self.api_key = settings.SHORTIO_ACCESS_TOKEN
        self.base_url = "https://api.short.io"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": self.api_key,
        }

    # 短縮URLを作成
    def shorten_url(self, long_url):
        url = f"{self.base_url}/links"
        payload = {
            "allowDuplicates": False,
            "originalURL": long_url,
            "ttl": "0",
            "domain": settings.SHORTIO_DOMAIN,
        }
        try:
            res = requests.post(
                url, json=payload, headers=self.headers, timeout=5
            )
            res.raise_for_status()
            data = res.json()
            return {"shortURL": data.get("shortURL"), "id": data.get("id")}
        except Exception as e:
            print(
                f"❌ Short.io短縮失敗: {e} {res.text if 'res' in locals() else ''}"
            )
            return None

    # クリック数取得
    def get_clicks(self, link_id):
        url = f"{self.base_url}/links/{link_id}"
        headers = {"accept": "application/json", "Authorization": self.api_key}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data.get("totalClicks")
        except Exception as e:
            print(f"❌ Short.ioクリック取得失敗: {e}")
            return None

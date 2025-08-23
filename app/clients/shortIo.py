import requests
from app.core.config import settings


class ShortIoClient:
    def __init__(self):
        self.api_key = settings.SHORTIO_ACCESS_TOKEN
        self.base_url = "https://api.short.io"
        self.get_clicks_base_url = "https://statistics.short.io"
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
        url = f"{self.get_clicks_base_url}/statistics/link/{link_id}"
        params = {"period": "total", "tz": "UTC"}
        headers = {"accept": "*/*", "Authorization": self.api_key}
        try:
            resp = requests.get(
                url, headers=headers,
                params=params, timeout=10
                )
            if resp.status_code != 200:
                print(
                    f"❌ Short.ioクリック取得失敗: {resp.status_code} {resp.text}"
                )
                return None
            resp.raise_for_status()
            data = resp.json()
            print(
                f"Short.ioクリック取得: {resp.status_code}"
                f"humanClicks={data.get('humanClicks')}"
            )
            return data.get("humanClicks")
        except Exception as e:
            print(f"❌ Short.ioクリック取得失敗: {e}")
            return None

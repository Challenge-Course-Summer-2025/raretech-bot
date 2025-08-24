import requests
from bs4 import BeautifulSoup
from typing import List, Dict


class QiitaClient:
    def __init__(self, request_timeout: int = 10, max_pages: int = 5):
        """
        :param request_timeout: requests.get のタイムアウト秒
        :param max_pages: ページング上限（無限ループ防止）
        """
        self.request_timeout = request_timeout
        self.max_pages = max_pages

    def get_org_items(self, org_id: str, max_items: int = 50) -> List[Dict]:
        """
        Qiita Organizationの最新記事を取得
        :param org_id: Qiita Organization ID
        :param max_items: 最大取得記事数
        :return: 記事リスト [{'id', 'title', 'url', 'user'}]
        """
        items = []
        page = 1

        while len(items) < max_items and page <= self.max_pages:
            url = f"https://qiita.com/organizations/{org_id}/items?page={page}"
            try:
                res = requests.get(url, timeout=self.request_timeout)
                res.raise_for_status()
            except requests.RequestException as e:
                print(f"[ERROR] Qiita記事取得失敗: {e}")
                break

            soup = BeautifulSoup(res.text, "html.parser")
            articles = soup.select("article")
            if not articles:
                break

            for article in articles:
                # 記事リンクとタイトル
                link_tag = article.select_one("h2 a[href*='/items/']")
                if not link_tag:
                    continue
                link = link_tag["href"]
                title = link_tag.get_text(strip=True)

                # ユーザーID
                user_tag = article.select_one("header a[href^='/']")
                user = ""
                if user_tag:
                    href = user_tag.get("href", "")
                    user = href.strip("/").split("/")[-1]

                items.append({
                    "id": link.split("/")[-1],  # Qiita記事ID
                    "title": title,
                    "url": f"https://qiita.com{link}",
                    "user": user,
                })

                if len(items) >= max_items:
                    break

            page += 1

        return items

from datetime import datetime

from app.clients.mattermost import MattermostClient
from app.clients.qiita import QiitaClient
from app.clients.shortIo import ShortIoClient
from app.clients.x import XClient
from app.services.db import (
    get_template,
    is_posted,
    save_post_history,
    update_api_status,
)


class PostService:
    def __init__(self, org_id):
        self.qiita_client = QiitaClient()
        self.x_client = XClient()
        self.mattermost_client = MattermostClient()
        self.shortio_client = ShortIoClient()
        self.org_id = org_id
        self.api_status_id = "x_api_status"

    def run(self):
        try:
            article = self.select_article()
            if not article:
                print("✅ 投稿対象が見つかりませんでした")
                return

            # 投稿処理全体
            article = self._prepare_article(article)
            text_x, text_mm = self.compose_messages(article)
            print(f"[DEBUG] X投稿文例={text_x}")
            tweet_url, is_posted_X = self._post_to_x(text_x)
            is_posted_Mattermost = self._post_to_mattermost(text_mm, tweet_url)

            # 履歴保存
            article.update(
                {
                    "tweet_url": tweet_url,
                    "post_at": datetime.utcnow().date(),
                    "is_posted_X": is_posted_X,
                    "is_posted_Mattermost": is_posted_Mattermost,
                }
            )
            save_post_history(article, template_id=article.get("template_id"))
            update_api_status(self.api_status_id, "正常", None)

        except Exception as e:
            print(f"❌ PostService.run 例外: {e}")
            update_api_status(self.api_status_id, "異常", str(e))
            raise

    # --- private methods ---

    def _prepare_article(self, article: dict) -> dict:
        """短縮URLを付与（失敗時は元URLを使用）"""
        try:
            short_data = self.shortio_client.shorten_url(article["url"])
            if short_data:
                article["short_url"] = short_data["shortURL"]
                article["shortio_id"] = short_data["id"]
                article["is_tracked"] = True
            else:
                print("⚠️ Short.ioが短縮を返さず → 元URLを使用")
                article["short_url"] = article["url"]
                article["is_tracked"] = False
        except Exception as e:
            print(f"❌ Short.io短縮失敗: {e}")
            article["short_url"] = article["url"]
            article["is_tracked"] = False
        return article

    def _post_to_x(self, text: str) -> tuple[str | None, bool]:
        """Xに投稿してURLを返す"""
        try:
            tweet_url = self.x_client.post_tweet(text)
            return tweet_url, bool(tweet_url)
        except Exception as e:
            print(f"❌ X投稿失敗: {e}")
            return None, False

    def _post_to_mattermost(
        self, text_template: str, tweet_url: str | None
    ) -> bool:
        """Mattermostに投稿"""
        try:
            message = text_template.format(tweet_url=tweet_url or "")
            result = self.mattermost_client.post_message(message)
            print(f"[DEBUG] Mattermost投稿成否={result}")
            return result
        except Exception as e:
            print(f"❌ Mattermost投稿失敗: {e}")
            return False

    # --- article selection ---

    def select_article(self):
        items = (
            self.qiita_client.get_org_items(self.org_id, max_items=100) or []
        )
        print(f"[DEBUG] 最新記事取得数={len(items)}")
        if not items:
            return None

        # 未投稿を探して返す
        for raw in items:
            item = self._normalize_qiita_item(raw)
            if not is_posted(item["id"]):
                return item

        print("✅ 全て投稿済み")
        return None

    def _normalize_qiita_item(self, item: dict) -> dict:
        user = item.get("user")
        url = item["url"]
        qiita_id = url.split("/")[-1]
        return {
            "id": qiita_id,
            "title": item["title"],
            "url": url,
            "user": user.get("id") if isinstance(user, dict) else user,
        }

    def compose_messages(self, article):
        template, template_id = get_template()
        article["template_id"] = template_id
        text_x = template.format(
            title=article["title"],
            url=article["short_url"],
            user=article["user"],
        )
        text_mm = (
            f":information_source: **{article['user']}さんの記事がXに投稿されました！**\n"
            f"{article['title']} - {article['url']}\n"
            f"X投稿URL: {{tweet_url}}"
        )
        return text_x, text_mm

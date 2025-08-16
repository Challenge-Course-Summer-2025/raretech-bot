from datetime import datetime
from app.clients.qiita import QiitaClient
from app.clients.x import XClient
from app.clients.mattermost import MattermostClient
from app.clients.shortIo import ShortIoClient
from app.services.db import get_template, save_post_history
from app.services.db import get_old_post_history, is_posted


class PostService:
    def __init__(self, org_id):
        self.qiita_client = QiitaClient()
        self.x_client = XClient()
        self.mattermost_client = MattermostClient()
        self.shortio_client = ShortIoClient()
        self.org_id = org_id

    def run(self):
        # 投稿対象のQiita記事を選択
        article = self.select_article()
        if not article:
            print("✅ 投稿対象が見つかりませんでした")
            return

        # 投稿時刻
        post_at = datetime.utcnow().date()

        # 短縮URL作成（失敗したら元URLを使用）
        try:
            short_data = self.shortio_client.shorten_url(article["url"])
            if not short_data:
                print(
                    "⚠️ Short.ioが短縮を返しませんでした。元URLを使用します（クリック集計不可）。"
                )
                article["short_url"] = article["url"]
                is_tracked = False
            else:
                article["short_url"] = short_data["shortURL"]
                article["shortio_id"] = short_data["id"]
                is_tracked = True
        except Exception as e:
            print(
                f"❌ Short.io短縮で例外: {e}. 元URLを使用します（クリック集計不可）。"
            )
            article["short_url"] = article["url"]
            is_tracked = False

        # 投稿文をテンプレートから生成
        text_x, text_mm = self.compose_messages(article)

        # Xに投稿し、投稿URLを取得
        tweet_url = None
        is_posted_X = False
        try:
            tweet_url = self.x_client.post_tweet(text_x)
            if tweet_url:
                is_posted_X = True
        except Exception as e:
            print(f"❌ X投稿失敗: {e}")

        # Mattermostに投稿
        is_posted_Mattermost = False
        try:
            mm_message = text_mm.format(tweet_url=tweet_url or "")
            mm_result = self.mattermost_client.post_message(mm_message)
            is_posted_Mattermost = bool(mm_result)
        except Exception as e:
            print(f"❌ Mattermost投稿失敗: {e}")

        # 投稿履歴を保存
        article["tweet_url"] = tweet_url
        article["clicks"] = (
            0 if is_tracked else None
        )  # Noneなら後続の集計で無視できる
        article["post_at"] = post_at
        article["is_posted_X"] = is_posted_X
        article["is_posted_Mattermost"] = is_posted_Mattermost
        article["is_tracked"] = (
            is_tracked  # クリック集計対象かどうか。短縮URLが成功した場合はTrue
        )
        save_post_history(article)

    def select_article(self):
        """投稿対象のQiita記事を選ぶ"""
        items = self.qiita_client.get_org_items(self.org_id) or []
        if not items:
            print("⚠️ Qiita記事が見つかりません")
            return None

        # 1) 最新記事（未投稿なら即採用）
        latest = self._normalize_qiita_item(items[0])
        if not is_posted(latest["id"]):
            return latest

        # 2) 未投稿の過去記事（新しい順に見て、未投稿の最初の1件）
        for raw in items[1:]:
            item = self._normalize_qiita_item(raw)
            if not is_posted(item["id"]):
                return item

        # 3) 既投稿の中から最も古いpost_atのもの
        old_posts = get_old_post_history(
            limit=1
        )  # ← DB側で post_at ASC に変更する
        if old_posts:
            row = old_posts[0]
            return {
                "id": row["qiita_id"],
                "title": row["title"],
                "url": row.get("url") or row.get("qiita_url"),
                "user": row["author"],
            }

        return None

    def _normalize_qiita_item(self, item: dict) -> dict:
        """Qiita APIのitemを、アプリ内で使う共通形に正規化する"""
        user = item.get("user")
        user_name = (
            user.get("id") if isinstance(user, dict) else user
        )  # API実体に合わせて安全に
        return {
            "id": item["id"],
            "title": item["title"],
            "url": item["url"],
            "user": user_name,
        }

    def compose_messages(self, article):
        template = get_template()
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

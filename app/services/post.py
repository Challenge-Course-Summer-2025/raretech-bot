from app.clients.qiita import QiitaClient
from app.clients.x import XClient
from app.clients.mattermost import MattermostClient
from app.services.db import get_template, save_post_history
from app.services.db import get_old_post_history, is_posted


class PostService:
    def __init__(self, org_id):
        self.qiita_client = QiitaClient()
        self.x_client = XClient()
        self.mattermost_client = MattermostClient()
        self.org_id = org_id

    def run(self):
        # 投稿対象のQiita記事を選択
        article = self.select_article()
        if not article:
            print("✅ 投稿対象が見つかりませんでした")
            return
        # 投稿文をテンプレートから生成
        text_x, text_mm = self.compose_messages(article)
        # Xに投稿し、投稿URLを取得
        tweet_url = self.x_client.post_tweet(text_x)
        # Mattermostに投稿
        self.mattermost_client.post_message(
            text_mm.format(tweet_url=tweet_url)
            )
        # 投稿履歴を保存
        save_post_history(article)

    def select_article(self):
        items = self.qiita_client.get_org_items(self.org_id)
        if not items:
            print("⚠️ Qiita記事が見つかりません")
            return None

        latest = items[0]
        if not is_posted(latest["id"]):
            return latest

        for item in items:
            if not is_posted(item["id"]):
                return item

        old_posts = get_old_post_history()
        if old_posts:
            return {
                "id": old_posts[0]["qiita_id"],
                "title": old_posts[0]["title"],
                "url": old_posts[0]["url"],
                "user": old_posts[0]["author"]
            }

        return None

    def compose_messages(self, article):
        template = get_template()
        text_x = template.format(
            title=article["title"],
            url=article["url"],
            user=article["user"]
        )
        text_mm = (
            f":information_source: **{article['user']}さんの記事がXに投稿されました！**\n"
            f"{article['title']} - {article['url']}\n"
            f"X投稿URL: {{tweet_url}}"
        )
        return text_x, text_mm

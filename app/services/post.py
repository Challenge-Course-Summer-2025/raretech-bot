from clients.qiita import QiitaClient
from clients.x import XClient
from clients.mattermost import MattermostClient
from services.db import get_template, save_post_history


class PostService:
    def __init__(self, org_id):
        self.qiita_client = QiitaClient()
        self.x_client = XClient()
        self.mattermost_client = MattermostClient()
        self.org_id = org_id

    def run(self):
        # 1. 最新のQiita記事取得
        items = self.qiita_client.get_org_items(self.org_id)
        if not items:
            print("⚠️ Qiita記事が見つかりません")
            return

        latest = items[0]
        # last_id = get_last_qiita_id()

        # if latest["id"] == last_id:
        #     print("🟢 新しい記事はありません")
        #     return

        # 2. 投稿テンプレート取得
        template = get_template()

        # 3. テンプレートに記事情報を埋め込む
        text = template.format(
            title=latest["title"],
            url=latest["url"],
            user=latest["user"]
        )

        # 4. 投稿実行
        self.x_client.post_tweet(text)
        self.mattermost_client.post_message(text)

        # 5. 投稿履歴を保存
        save_post_history(latest, template_id=None)

import tweepy
from app.core.config import settings


class XClient:
    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=settings.X_API_KEY,
            consumer_secret=settings.X_API_SECRET,
            access_token=settings.X_ACCESS_TOKEN,
            access_token_secret=settings.X_ACCESS_TOKEN_SECRET,
        )
        self.username = settings.X_USERNAME

    def post_tweet(self, text: str):
        response = self.client.create_tweet(text=text)
        print("✅ ツイート成功:", response)
        tweet_id = response.data["id"]
        return f"https://twitter.com/{self.username}/status/{tweet_id}"

    def get_tweet_views(self, tweet_url: str) -> int:
        """
        ツイートの表示回数（インプレッション数）を取得する
        """
        try:
            tweet_id = tweet_url.strip().split("/")[-1]
            resp = self.client.get_tweet(
                id=tweet_id,
                tweet_fields=["public_metrics"],  # 公開メトリクス情報を取得
            )

            if resp.data and "public_metrics" in resp.data:
                return resp.data["public_metrics"].get("impression_count", 0)

            return 0

        except Exception as e:
            print(f"❌ ツイート表示回数取得エラー: {e}")
            return 0

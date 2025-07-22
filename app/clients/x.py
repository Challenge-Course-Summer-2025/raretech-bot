import os
import tweepy


class XClient:
    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=os.getenv("BEARER_TOKEN"),
            consumer_key=os.getenv("X_API_KEY"),
            consumer_secret=os.getenv("X_API_SECRET"),
            access_token=os.getenv("X_ACCESS_TOKEN"),
            access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET")
        )
        self.username = os.getenv("X_USERNAME")

    def post_tweet(self, text: str):
        response = self.client.create_tweet(text=text)
        print("✅ ツイート成功:", response)
        tweet_id = response.data["id"]
        return f"https://twitter.com/{self.username}/status/{tweet_id}"

import feedparser


class QiitaClient:
    def __init__(self):
        pass

    def get_org_items(self, org_id: str):
        feed_url = f"https://qiita.com/organizations/{org_id}/activities.atom"
        feed = feedparser.parse(feed_url)

        items = []
        for entry in feed.entries:
            items.append(
                {
                    "id": entry.id,
                    "title": entry.title,
                    "url": entry.link,
                    "user": entry.author,
                }
            )
        return items

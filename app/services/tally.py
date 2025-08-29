import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.clients.shortIo import ShortIoClient
from app.clients.x import XClient
from app.services import db as sdb


class ClickCollector:
    def __init__(self):
        self.shortio = ShortIoClient()
        self.xclient = XClient()
        self.sleep_between_requests = 0.2

        # 固定リンクのlink_id
        self.static_links = {
            "trial": "lnk_68NC_w5gGGBcIk8QE3ZdzZB0bK",
            "counseling": "lnk_68NC_1cImdUG0iCyFYYjflqJa0",
        }

    def _ctr(self, clicks: int, views: int) -> Decimal:
        if not views:
            return Decimal("0")
        return (Decimal(clicks) / Decimal(views)).quantize(Decimal("0.001"))

    def run(self):
        updated = 0
        skipped = 0
        errors = 0

        # 集計日と対象日（前日）
        checked_at = date.today()
        checked_at_str = checked_at.isoformat()
        check_target = checked_at - timedelta(days=1)

        # 1) 記事リンク集計
        projection = (
            "pk, created_at, id, short_url, shortio_id, tweet_url, "
            "is_tracked, clicks_article, ctr_article, x_views"
        )
        link_ids = []
        for items in sdb.iter_posted_X(projection=projection):
            for item in items:
                post_id = item.get("post_id") or item.get("id")
                link_id = item.get("shortio_id")
                # tweet_url = item.get("tweet_url")

                if not post_id:
                    print(f"⚠️ post_id無しでスキップ: item={item}")
                    skipped += 1
                    continue
                link_ids.append((post_id, link_id))

                # 並列に Short.io からクリック数取得
                with ThreadPoolExecutor(max_workers=5) as executor:
                    future_to_post = {
                        executor.submit(
                            self.shortio.get_clicks, link_id
                        ): post_id
                        for post_id, link_id in link_ids
                    }

                    for future in as_completed(future_to_post):
                        post_id = future_to_post[future]
                        try:
                            clicks = future.result()
                            if clicks is None:
                                errors += 1
                                continue
                            sdb.update_post_metrics_row(
                                post_id, checked_at_str, clicks, None, None
                            )
                            updated += 1
                            print(f"✅ 記事 {post_id}: clicks={clicks}")
                        except Exception as e:
                            print(f"[{post_id}] エラー: {e}")
                            errors += 1

                # X表示数
                # try:
                #     x_views = (
                #         self.xclient.get_tweet_views(tweet_url)
                #         if tweet_url
                #         else 0
                #     )
                # except Exception as e:
                #     print(f"[{post_id}] X表示数取得例外: {e}")
                #     errors += 1
                #     continue

                # CTR
                # ctr = self._ctr(clicks, x_views)

                # 保存（記事メトリクス更新）
                try:
                    sdb.update_post_metrics_row(
                        post_id,
                        checked_at_str,
                        clicks,
                        None,
                        None,
                    )
                    updated += 1
                    print(f"✅ 記事 {post_id}: clicks={clicks},")
                except Exception as e:
                    print(f"❌ 記事メトリクス更新失敗 for {post_id}: {e}")
                    errors += 1

                time.sleep(self.sleep_between_requests)

        # 2) 固定リンク（trial / counseling）
        try:
            clicks_trial = self.shortio.get_clicks(self.static_links["trial"])
            clicks_counseling = self.shortio.get_clicks(
                self.static_links["counseling"]
            )

            # X表示数 = 前日の POST 合計 + 前日の STATIC 合計
            x_views = sdb.sum_post_x_views_by_date(
                check_target
            ) + sdb.sum_static_views_by_date(check_target)

            ctr_trial = self._ctr(clicks_trial, x_views)
            ctr_counseling = self._ctr(clicks_counseling, x_views)

            now = datetime.utcnow().isoformat()
            record = {
                "id": f"STATIC-{checked_at_str}",
                "checked_at": checked_at_str,
                "clicks_trial_lesson": clicks_trial,
                "clicks_counseling": clicks_counseling,
                "tweet_views": x_views,
                "ctr_trial_lesson": ctr_trial,
                "ctr_counseling": ctr_counseling,
                "created_at": now,
                "updated_at": now,
            }
            sdb.save_static_link_clicks_record(record)
            updated += 1
            print(
                f"✅ 固定リンク: trial={clicks_trial},\
                counseling={clicks_counseling}, "
                f"views={x_views}, ctr_trial={ctr_trial},\
                ctr_counseling={ctr_counseling}"
            )
        except Exception as e:
            print(f"❌ 固定リンク集計失敗: {e}")
            errors += 1

        print(
            f"集計完了: updated={updated}, skipped={skipped}, errors={errors}"
        )

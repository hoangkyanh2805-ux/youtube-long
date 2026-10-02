import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.youtube_api_fetch import (
    CHANNEL_FIELDS,
    append_snapshot_rows,
    chunked,
    enrich_inventory_rows,
    load_env_file,
    parse_channel_stats,
    parse_video_stats,
)


class YouTubeApiFetchTest(unittest.TestCase):
    def test_load_env_file_reads_key_value_pairs_without_quotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text("YT_API_KEY='abc123'\nYOUTUBE_CHANNEL_ID=chan\n# comment\n", encoding="utf-8")

            values = load_env_file(env_path)

        self.assertEqual(values["YT_API_KEY"], "abc123")
        self.assertEqual(values["YOUTUBE_CHANNEL_ID"], "chan")

    def test_chunked_limits_batches(self):
        self.assertEqual(list(chunked(["a", "b", "c"], 2)), [["a", "b"], ["c"]])

    def test_parse_video_stats_maps_statistics(self):
        payload = {
            "items": [
                {
                    "id": "v1",
                    "statistics": {"viewCount": "12", "likeCount": "3", "commentCount": "2"},
                    "contentDetails": {"duration": "PT1M5S"},
                }
            ]
        }

        stats = parse_video_stats(payload)

        self.assertEqual(stats["v1"]["views"], "12")
        self.assertEqual(stats["v1"]["likes"], "3")
        self.assertEqual(stats["v1"]["comments"], "2")
        self.assertEqual(stats["v1"]["duration_sec"], "65")

    def test_enrich_inventory_rows_adds_rates_and_preserves_fields(self):
        rows = [
            {
                "video_id": "v1",
                "title": "Original",
                "views": "0",
                "likes": "0",
                "comments": "0",
                "like_rate": "0",
                "comment_rate": "0",
            }
        ]
        stats = {"v1": {"views": "100", "likes": "5", "comments": "2", "duration_sec": "65"}}

        enriched = enrich_inventory_rows(rows, stats)

        self.assertEqual(enriched[0]["title"], "Original")
        self.assertEqual(enriched[0]["views"], "100")
        self.assertEqual(enriched[0]["like_rate"], "0.0500")
        self.assertEqual(enriched[0]["comment_rate"], "0.0200")

    def test_parse_channel_stats_returns_rows(self):
        payload = {
            "items": [
                {
                    "id": "chan1",
                    "snippet": {"title": "Azzam"},
                    "statistics": {"subscriberCount": "1000", "viewCount": "2000", "videoCount": "30"},
                }
            ]
        }

        rows = parse_channel_stats(payload, "self")

        self.assertEqual(rows[0]["channel_id"], "chan1")
        self.assertEqual(rows[0]["channel_title"], "Azzam")
        self.assertEqual(rows[0]["subscriber_count"], "1000")
        self.assertEqual(rows[0]["role"], "self")

    def test_append_snapshot_rows_preserves_history_and_replaces_same_day_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "channel_snapshots.csv"
            old_rows = [
                {
                    "snapshot_at": "2026-09-28",
                    "role": "self",
                    "channel_id": "chan1",
                    "channel_title": "Azzam",
                    "subscriber_count": "1900",
                    "view_count": "200000",
                    "video_count": "280",
                },
                {
                    "snapshot_at": "2026-09-29",
                    "role": "self",
                    "channel_id": "chan1",
                    "channel_title": "Azzam stale",
                    "subscriber_count": "1950",
                    "view_count": "220000",
                    "video_count": "288",
                },
            ]
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=CHANNEL_FIELDS)
                writer.writeheader()
                writer.writerows(old_rows)

            append_snapshot_rows(
                path,
                CHANNEL_FIELDS,
                [
                    {
                        "snapshot_at": "2026-09-29",
                        "role": "self",
                        "channel_id": "chan1",
                        "channel_title": "Azzam",
                        "subscriber_count": "1970",
                        "view_count": "233212",
                        "video_count": "289",
                    }
                ],
                ["snapshot_at", "role", "channel_id"],
            )

            with path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["subscriber_count"], "1900")
        self.assertEqual(rows[1]["subscriber_count"], "1970")
        self.assertEqual(rows[1]["channel_title"], "Azzam")


if __name__ == "__main__":
    unittest.main()

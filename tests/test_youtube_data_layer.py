import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.youtube_data_layer import build_outputs, load_search_file, normalize_search_items


class YouTubeDataLayerTest(unittest.TestCase):
    def test_normalizes_search_items_for_inventory(self):
        payload = {
            "items": [
                {
                    "id": {"kind": "youtube#video", "videoId": "abc123"},
                    "snippet": {
                        "publishedAt": "2026-09-28T15:00:35Z",
                        "channelId": "chan1",
                        "channelTitle": "Azzam Master Trading",
                        "title": "FOREX LESSON &amp; #shorts",
                        "description": "Learn XAUUSD strategy",
                        "liveBroadcastContent": "none",
                    },
                },
                {
                    "id": {"kind": "youtube#channel", "channelId": "skipme"},
                    "snippet": {"title": "not a video"},
                },
            ]
        }

        rows = normalize_search_items(payload, "azzam_search.json")

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["video_id"], "abc123")
        self.assertEqual(rows[0]["channel"], "Azzam Master Trading")
        self.assertEqual(rows[0]["title"], "FOREX LESSON & #shorts")
        self.assertEqual(rows[0]["format"], "short")
        self.assertEqual(rows[0]["content_pillar"], "Lesson")
        self.assertEqual(rows[0]["offer_stage"], "Attraction")
        self.assertEqual(rows[0]["source_file"], "azzam_search.json")

    def test_normalizes_mojibake_emoji_out_of_titles(self):
        payload = {
            "items": [
                {
                    "id": {"kind": "youtube#video", "videoId": "live123"},
                    "snippet": {
                        "publishedAt": "2026-09-28T15:00:35Z",
                        "channelId": "chan1",
                        "channelTitle": "Azzam Master Trading",
                        "title": "\u00f0\u0178\u201d\u00b4 LIVE XAUUSD Trading",
                        "description": "Real-time analysis",
                        "liveBroadcastContent": "none",
                    },
                }
            ]
        }

        rows = normalize_search_items(payload, "azzam_search.json")

        self.assertEqual(rows[0]["title"], "LIVE XAUUSD Trading")

    def test_build_outputs_writes_inventory_and_remake_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            search_path = root / "sample_search.json"
            search_path.write_text(
                json.dumps(
                    {
                        "items": [
                            {
                                "id": {"kind": "youtube#video", "videoId": "live1"},
                                "snippet": {
                                    "publishedAt": "2026-09-28T10:33:52Z",
                                    "channelId": "competitor",
                                    "channelTitle": "Gold Trader Alliance",
                                    "title": "LIVE TRADING XAUUSD",
                                    "description": "Trading room and XAUUSD analysis",
                                    "liveBroadcastContent": "upcoming",
                                },
                            },
                            {
                                "id": {"kind": "youtube#video", "videoId": "short1"},
                                "snippet": {
                                    "publishedAt": "2026-09-28T15:00:35Z",
                                    "channelId": "azzam",
                                    "channelTitle": "Azzam Master Trading",
                                    "title": "BEST STRATEGY #shorts",
                                    "description": "Forex lesson",
                                    "liveBroadcastContent": "none",
                                },
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )

            out_dir = root / "processed"
            build_outputs([search_path], out_dir)

            with (out_dir / "video_inventory.csv").open(encoding="utf-8") as handle:
                inventory = list(csv.DictReader(handle))
            with (out_dir / "remake_candidates.csv").open(encoding="utf-8") as handle:
                candidates = list(csv.DictReader(handle))

        self.assertEqual(len(inventory), 2)
        by_id = {row["video_id"]: row for row in inventory}
        self.assertEqual(by_id["live1"]["url"], "https://www.youtube.com/watch?v=live1")
        self.assertEqual(by_id["live1"]["format"], "live")
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["source_video_id"], "live1")
        self.assertEqual(candidates[0]["source_channel"], "Gold Trader Alliance")
        self.assertEqual(candidates[0]["target_format"], "short")
        self.assertEqual(candidates[0]["offer_stage"], "Attraction")


class SearchFileTest(unittest.TestCase):
    def test_load_search_file_rejects_non_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("not json", encoding="utf-8")

            with self.assertRaises(ValueError):
                load_search_file(path)


if __name__ == "__main__":
    unittest.main()

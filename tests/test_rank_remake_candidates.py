import csv
import tempfile
import unittest
from pathlib import Path

from scripts.rank_remake_candidates import build_ranked_candidates, score_inventory_row


class RankRemakeCandidatesTest(unittest.TestCase):
    def test_score_prefers_high_view_competitor_live_with_comments(self):
        row = {
            "video_id": "v1",
            "channel": "Gold Trader Alliance",
            "title": "LIVE TRADING XAUUSD",
            "url": "https://www.youtube.com/watch?v=v1",
            "format": "live",
            "views": "3000",
            "comments": "30",
            "topic": "XAUUSD",
            "offer_stage": "Lead Capture",
            "source_file": "gta_search.json",
            "sync_hash": "abc",
        }

        score = score_inventory_row(row)

        self.assertGreaterEqual(score, 100)

    def test_build_ranked_candidates_sorts_by_real_stats(self):
        rows = [
            {
                "video_id": "low",
                "channel": "Azzam Master Trading",
                "title": "Small Short",
                "url": "https://www.youtube.com/watch?v=low",
                "format": "short",
                "views": "50",
                "comments": "0",
                "topic": "XAUUSD",
                "offer_stage": "Attraction",
                "source_file": "azzam_search.json",
                "sync_hash": "lowhash",
            },
            {
                "video_id": "high",
                "channel": "Gold Trader Alliance",
                "title": "LIVE TRADING XAUUSD",
                "url": "https://www.youtube.com/watch?v=high",
                "format": "live",
                "views": "3000",
                "comments": "30",
                "topic": "XAUUSD",
                "offer_stage": "Lead Capture",
                "source_file": "gta_search.json",
                "sync_hash": "highhash",
            },
        ]

        candidates = build_ranked_candidates(rows)

        self.assertEqual(candidates[0]["source_video_id"], "high")
        self.assertEqual(candidates[0]["evidence_metric"], "youtube_api_views_comments")
        self.assertEqual(candidates[0]["views"], "3000")
        self.assertEqual(candidates[0]["comments"], "30")
        self.assertEqual(candidates[0]["status"], "Backlog")


if __name__ == "__main__":
    unittest.main()

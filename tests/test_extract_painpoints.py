import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.extract_painpoints import classify, normalize_item, run


class ExtractPainpointsTests(unittest.TestCase):
    def test_normalize_youtube_comment_and_hash_author(self):
        row = normalize_item({
            "commentId": "c1",
            "commentText": "How do I set stop loss?",
            "videoId": "v1",
            "videoUrl": "https://youtube.com/watch?v=v1",
            "likesCount": 5,
            "authorName": "viewer",
        }, actor="streamers/youtube-comments-scraper", run_id="run-1")
        self.assertEqual(row["platform"], "youtube")
        self.assertEqual(row["engagement_likes"], 5)
        self.assertEqual(len(row["author_hash"]), 64)
        self.assertNotIn("viewer", row.values())

    def test_classify_vietnamese_question(self):
        result = classify("Làm sao tìm điểm vào và đặt stop loss?")
        self.assertIn("entry_timing", result)
        self.assertIn("risk_management", result)
        self.assertIn("education_gap", result)

    def test_pipeline_deduplicates_and_writes_evidence(self):
        payload = [
            {
                "commentId": "c1",
                "commentText": "Tôi không hiểu cách quản lý vốn?",
                "videoUrl": "https://youtube.com/watch?v=v1",
                "likesCount": 4,
            },
            {
                "commentId": "c1",
                "commentText": "Tôi không hiểu cách quản lý vốn?",
                "videoUrl": "https://youtube.com/watch?v=v1",
                "likesCount": 4,
            },
            {
                "id": "c2",
                "text": "Great video",
                "url": "https://tiktok.com/@x/video/1",
            },
        ]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "comments.json"
            source.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            out = root / "out"
            total, pain_total = run(source, out, actor="test/actor", run_id="r1")
            self.assertEqual(total, 2)
            self.assertEqual(pain_total, 1)
            self.assertTrue((out / "painpoint_report.md").exists())
            with (out / "painpoint_candidates.csv").open(encoding="utf-8-sig") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["comment_id"], "c1")
            self.assertIn("risk_management", rows[0]["categories"])
            self.assertIn("https://youtube.com/watch?v=v1", (out / "painpoint_report.md").read_text(encoding="utf-8"))

    def test_missing_text_is_skipped(self):
        self.assertIsNone(normalize_item({"id": "empty"}))


if __name__ == "__main__":
    unittest.main()

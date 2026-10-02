import csv
import tempfile
import unittest
from pathlib import Path


class YouTubeWorkflowEnrichTest(unittest.TestCase):
    def test_extract_topic_signal_prefers_opening_hook_and_checklist(self):
        from scripts.youtube_workflow_enrich import extract_topic_signal

        signal = extract_topic_signal(
            "Before you follow a live XAUUSD setup, check bias and invalidation first. "
            "Risk comes before entry. Comment CHECKLIST for the prep list."
        )

        self.assertEqual(signal["opening_hook"], "Before you follow a live XAUUSD setup, check bias and invalidation first")
        self.assertIn("invalidation", signal["pain_point"].lower())
        self.assertEqual(signal["cta"], "CHECKLIST")

    def test_extract_topic_signal_ignores_filler_and_uses_title_fallback(self):
        from scripts.youtube_workflow_enrich import extract_topic_signal

        signal = extract_topic_signal(
            "[music] [music] >> [music] [music] [music] >> Nat.",
            source_title="LIVE TRADING XAUUSD - FOREX DAY",
        )

        self.assertEqual(signal["opening_hook"], "Before following a live XAUUSD setup, check the plan first")
        self.assertIn("live setup", signal["pain_point"].lower())

    def test_enrich_candidates_writes_transcript_topics_and_briefs(self):
        from scripts.youtube_workflow_enrich import enrich_candidates

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidates = root / "remake_candidates.csv"
            with candidates.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["candidate_id", "source_video_id", "source_url", "original_title", "priority_score"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "candidate_id": "RC-1",
                        "source_video_id": "abc123",
                        "source_url": "https://www.youtube.com/watch?v=abc123",
                        "original_title": "LIVE TRADING XAUUSD",
                        "priority_score": "99",
                    }
                )

            def fake_fetch(video_url, api_key):
                self.assertEqual(video_url, "https://www.youtube.com/watch?v=abc123")
                self.assertEqual(api_key, "token")
                return {
                    "transcript_text": (
                        "Before you follow a live XAUUSD setup, check bias and invalidation first. "
                        "Risk comes before entry. Comment CHECKLIST for the prep list."
                    ),
                    "metadata_title": "LIVE TRADING XAUUSD",
                    "metadata_author": "Gold Trader Alliance",
                }

            outputs = enrich_candidates(
                root=root,
                candidate_path=candidates,
                api_key="token",
                limit=1,
                fetch_func=fake_fetch,
            )

            rows = list(csv.DictReader(outputs["transcript_topics"].open(encoding="utf-8")))
            self.assertEqual(rows[0]["transcript_status"], "ok")
            self.assertEqual(rows[0]["source_video_id"], "abc123")
            self.assertIn("CHECKLIST", rows[0]["cta"])
            self.assertIn("RC-1", outputs["topic_briefs"].read_text(encoding="utf-8"))
            self.assertIn("Before you follow", outputs["hook_library"].read_text(encoding="utf-8"))

    def test_enrich_candidates_marks_missing_key_without_api_call(self):
        from scripts.youtube_workflow_enrich import enrich_candidates

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidates = root / "remake_candidates.csv"
            candidates.write_text(
                "candidate_id,source_video_id,source_url,original_title,priority_score\n"
                "RC-1,abc123,https://www.youtube.com/watch?v=abc123,LIVE TRADING XAUUSD,99\n",
                encoding="utf-8",
            )

            outputs = enrich_candidates(root=root, candidate_path=candidates, api_key="", limit=1)

            rows = list(csv.DictReader(outputs["transcript_topics"].open(encoding="utf-8")))
            self.assertEqual(rows[0]["transcript_status"], "missing_key")


if __name__ == "__main__":
    unittest.main()

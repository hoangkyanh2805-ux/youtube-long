import csv
import tempfile
import unittest
from pathlib import Path

from scripts.content_bridge import build_content_outputs, generate_short_rows
from scripts.youtube_data_layer import REMAKE_CANDIDATE_FIELDS


class ContentBridgeTest(unittest.TestCase):
    def test_generate_short_rows_turns_candidates_into_reviewable_drafts(self):
        candidates = [
            {
                "candidate_id": "RC-001",
                "source_video_id": "vid1",
                "source_channel": "Gold Trader Alliance",
                "source_url": "https://www.youtube.com/watch?v=vid1",
                "original_title": "LIVE TRADING XAUUSD",
                "remake_angle": "Cut the live topic into one checklist-style XAUUSD short",
                "hook_test": "Before you trade XAUUSD, check this first",
                "priority_score": "100",
                "offer_stage": "Lead Capture",
                "cta_type": "telegram",
                "source_file": "gta_search.json",
                "sync_hash": "abc",
            }
        ]

        rows = generate_short_rows(candidates, limit=1)

        self.assertEqual(rows[0]["short_id"], "S-RC-001")
        self.assertEqual(rows[0]["source_id"], "RC-001")
        self.assertEqual(rows[0]["status"], "Backlog")
        self.assertEqual(rows[0]["review_status"], "Needs human review")
        self.assertEqual(rows[0]["telegram_keyword"], "CHECKLIST")
        self.assertIn("educational", rows[0]["notes"].lower())
        self.assertNotIn("guaranteed", rows[0]["script"].lower())

    def test_build_content_outputs_writes_calendar_scripts_and_live_agenda(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate_path = root / "remake_candidates.csv"
            with candidate_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=REMAKE_CANDIDATE_FIELDS)
                writer.writeheader()
                row = {field: "" for field in REMAKE_CANDIDATE_FIELDS}
                row.update(
                    {
                        "candidate_id": "RC-001",
                        "source_video_id": "vid1",
                        "source_channel": "Gold Trader Alliance",
                        "source_url": "https://www.youtube.com/watch?v=vid1",
                        "original_title": "LIVE TRADING XAUUSD",
                        "format": "live",
                        "remake_angle": "Cut the live topic into one checklist-style XAUUSD short",
                        "hook_test": "Before you trade XAUUSD, check this first",
                        "priority_score": "100",
                        "offer_stage": "Lead Capture",
                        "cta_type": "telegram",
                        "source_file": "gta_search.json",
                        "sync_hash": "abc",
                    }
                )
                writer.writerow(row)

            output_dir = root / "content"
            outputs = build_content_outputs(candidate_path, output_dir, short_limit=1, live_limit=1)
            with outputs["calendar_csv"].open(encoding="utf-8") as handle:
                calendar = list(csv.DictReader(handle))

            self.assertEqual(len(calendar), 1)
            self.assertEqual(calendar[0]["short_id"], "S-RC-001")
            self.assertTrue(outputs["scripts_md"].exists())
            self.assertTrue(outputs["live_agenda_md"].exists())


if __name__ == "__main__":
    unittest.main()

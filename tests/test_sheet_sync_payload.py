import csv
import tempfile
import unittest
from pathlib import Path

from scripts.sheet_sync_payload import SheetSyncTarget, build_paste_data_request, build_sync_payload, resolve_default_targets


class SheetSyncPayloadTest(unittest.TestCase):
    def test_build_paste_data_request_limits_data_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "rows.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["id", "title"])
                writer.writerow(["1", "First"])
                writer.writerow(["2", "Second"])

            target = SheetSyncTarget(
                name="Test",
                csv_path=csv_path,
                sheet_id=123,
                max_data_rows=1,
            )

            request, summary = build_paste_data_request(target)

        self.assertEqual(request["pasteData"]["coordinate"]["sheetId"], 123)
        self.assertEqual(summary["written_rows"], 1)
        self.assertIn("id,title", request["pasteData"]["data"])
        self.assertIn("1,First", request["pasteData"]["data"])
        self.assertNotIn("2,Second", request["pasteData"]["data"])

    def test_build_sync_payload_contains_requests_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            csv_path = root / "rows.csv"
            csv_path.write_text("id,title\n1,First\n", encoding="utf-8")
            target = SheetSyncTarget("Rows", csv_path, 456, 20)

            payload = build_sync_payload([target])

        self.assertEqual(len(payload["requests"]), 1)
        self.assertEqual(payload["summary"][0]["target"], "Rows")
        self.assertEqual(payload["summary"][0]["written_rows"], 1)

    def test_resolve_default_targets_prefers_api_outputs_when_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            processed = root / "data" / "processed"
            processed.mkdir(parents=True)
            (processed / "video_inventory.csv").write_text("id\nold\n", encoding="utf-8")
            (processed / "video_inventory_api.csv").write_text("id\napi\n", encoding="utf-8")
            (processed / "remake_candidates.csv").write_text("id\nold\n", encoding="utf-8")
            (processed / "remake_candidates_api.csv").write_text("id\napi\n", encoding="utf-8")

            targets = resolve_default_targets(root)

        paths = {target.name: target.csv_path for target in targets}
        self.assertEqual(paths["Video Inventory"], processed / "video_inventory_api.csv")
        self.assertEqual(paths["Remake Candidates"], processed / "remake_candidates_api.csv")


if __name__ == "__main__":
    unittest.main()

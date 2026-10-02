import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError


class GoogleSheetApplyTest(unittest.TestCase):
    def test_resolve_google_credentials_path_accepts_both_env_names(self):
        from scripts.google_sheet_apply import resolve_google_credentials_path

        env = {
            "GOOGLE_APPLICATION_CREDENTIALS": "/tmp/application.json",
            "GOOGLE_SHEETS_CREDENTIALS_PATH": "/tmp/sheets.json",
        }

        self.assertEqual(resolve_google_credentials_path(env), "/tmp/sheets.json")
        self.assertEqual(
            resolve_google_credentials_path({"GOOGLE_APPLICATION_CREDENTIALS": "/tmp/application.json"}),
            "/tmp/application.json",
        )

    def test_readback_range_uses_written_rows_and_columns(self):
        from scripts.google_sheet_apply import build_readback_range

        self.assertEqual(
            build_readback_range({"target": "Shorts Pipeline", "written_rows": 20, "column_count": 28}),
            "'Shorts Pipeline'!A1:AB21",
        )

    def test_apply_payload_posts_batch_update_and_reads_back_values(self):
        from scripts.google_sheet_apply import apply_and_read_back

        with tempfile.TemporaryDirectory() as tmp:
            payload_path = Path(tmp) / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "requests": [{"pasteData": {"data": "id,title\n1,First"}}],
                        "summary": [
                            {
                                "target": "Shorts Pipeline",
                                "written_rows": 1,
                                "column_count": 2,
                                "sheet_id": 1003,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            calls = []

            def fake_request(method, url, token, body=None):
                calls.append((method, url, body))
                if method == "POST":
                    return {"replies": [{}]}
                return {"values": [["id", "title"], ["1", "First"]]}

            report = apply_and_read_back(payload_path, "sheet123", "token123", fake_request)

        self.assertEqual(report["apply_status"], "ok")
        self.assertEqual(report["read_back"][0]["status"], "ok")
        post_calls = [call for call in calls if call[0] == "POST"]
        readback_calls = [call for call in calls if call[0] == "GET" and "values" in call[1]]
        self.assertEqual(len(post_calls), 1)
        self.assertIn(":batchUpdate", post_calls[0][1])
        self.assertEqual(len(readback_calls), 1)
        self.assertIn("Shorts%20Pipeline", readback_calls[0][1])

    def test_apply_payload_refreshes_sheet_ids_from_live_metadata(self):
        from scripts.google_sheet_apply import apply_and_read_back

        with tempfile.TemporaryDirectory() as tmp:
            payload_path = Path(tmp) / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "requests": [
                            {
                                "pasteData": {
                                    "coordinate": {"sheetId": 1003, "rowIndex": 0, "columnIndex": 0},
                                    "data": "id,title\n1,First",
                                }
                            }
                        ],
                        "summary": [
                            {
                                "target": "Shorts Pipeline",
                                "written_rows": 1,
                                "column_count": 2,
                                "sheet_id": 1003,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            calls = []

            def fake_request(method, url, token, body=None):
                calls.append((method, url, body))
                if method == "GET" and "fields=sheets" in url:
                    return {
                        "sheets": [
                            {"properties": {"title": "Shorts Pipeline", "sheetId": 987654321}},
                        ]
                    }
                if method == "POST":
                    return {"replies": [{}]}
                return {"values": [["id", "title"], ["1", "First"]]}

            report = apply_and_read_back(payload_path, "sheet123", "token123", fake_request)

        self.assertEqual(report["apply_status"], "ok")
        self.assertEqual(calls[1][2]["requests"][0]["pasteData"]["coordinate"]["sheetId"], 987654321)
        self.assertEqual(report["sheet_id_refresh"][0]["old_sheet_id"], 1003)
        self.assertEqual(report["sheet_id_refresh"][0]["new_sheet_id"], 987654321)

    def test_apply_payload_matches_known_live_sheet_aliases(self):
        from scripts.google_sheet_apply import apply_and_read_back

        with tempfile.TemporaryDirectory() as tmp:
            payload_path = Path(tmp) / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "requests": [
                            {
                                "pasteData": {
                                    "coordinate": {"sheetId": 1006, "rowIndex": 0, "columnIndex": 0},
                                    "data": "id,title\n1,First",
                                }
                            }
                        ],
                        "summary": [
                            {
                                "target": "Video Inventory",
                                "written_rows": 1,
                                "column_count": 2,
                                "sheet_id": 1006,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            calls = []

            def fake_request(method, url, token, body=None):
                calls.append((method, url, body))
                if method == "GET" and "fields=sheets" in url:
                    return {"sheets": [{"properties": {"title": "video_inventory", "sheetId": 1054047411}}]}
                if method == "POST":
                    return {"replies": [{}]}
                return {"values": [["id", "title"], ["1", "First"]]}

            report = apply_and_read_back(payload_path, "sheet123", "token123", fake_request)

        post_body = [call[2] for call in calls if call[0] == "POST"][0]
        self.assertEqual(post_body["requests"][0]["pasteData"]["coordinate"]["sheetId"], 1054047411)
        self.assertEqual(report["sheet_id_refresh"][0]["matched_title"], "video_inventory")
        self.assertEqual(report["read_back"][0]["range"], "'video_inventory'!A1:B2")

    def test_apply_payload_creates_missing_live_sheet_before_paste(self):
        from scripts.google_sheet_apply import apply_and_read_back

        with tempfile.TemporaryDirectory() as tmp:
            payload_path = Path(tmp) / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "requests": [
                            {
                                "pasteData": {
                                    "coordinate": {"sheetId": 1003, "rowIndex": 0, "columnIndex": 0},
                                    "data": "id,title\n1,First",
                                }
                            }
                        ],
                        "summary": [
                            {
                                "target": "Shorts Pipeline",
                                "written_rows": 1,
                                "column_count": 2,
                                "sheet_id": 1003,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            metadata_calls = 0
            calls = []

            def fake_request(method, url, token, body=None):
                nonlocal metadata_calls
                calls.append((method, url, body))
                if method == "GET" and "fields=sheets" in url:
                    metadata_calls += 1
                    if metadata_calls == 1:
                        return {"sheets": []}
                    return {"sheets": [{"properties": {"title": "shorts_pipeline", "sheetId": 333}}]}
                if method == "POST" and body == {"requests": [{"addSheet": {"properties": {"title": "shorts_pipeline"}}}]}:
                    return {"replies": [{"addSheet": {"properties": {"sheetId": 333, "title": "shorts_pipeline"}}}]}
                if method == "POST":
                    return {"replies": [{}]}
                return {"values": [["id", "title"], ["1", "First"]]}

            report = apply_and_read_back(payload_path, "sheet123", "token123", fake_request)

        post_bodies = [call[2] for call in calls if call[0] == "POST"]
        self.assertEqual(post_bodies[0]["requests"][0]["addSheet"]["properties"]["title"], "shorts_pipeline")
        self.assertEqual(post_bodies[1]["requests"][0]["pasteData"]["coordinate"]["sheetId"], 333)
        self.assertEqual(report["created_sheets"], [{"target": "Shorts Pipeline", "title": "shorts_pipeline"}])

    def test_apply_payload_reports_failed_readback(self):
        from scripts.google_sheet_apply import apply_and_read_back

        with tempfile.TemporaryDirectory() as tmp:
            payload_path = Path(tmp) / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "requests": [{"pasteData": {"data": "id,title\n1,First"}}],
                        "summary": [{"target": "Daily Report", "written_rows": 1, "column_count": 2}],
                    }
                ),
                encoding="utf-8",
            )

            def fake_request(method, url, token, body=None):
                if method == "POST":
                    return {"replies": [{}]}
                return {"values": [["id", "title"]]}

            report = apply_and_read_back(payload_path, "sheet123", "token123", fake_request)

        self.assertEqual(report["read_back"][0]["status"], "mismatch")

    def test_google_http_error_description_includes_response_body(self):
        from scripts.google_sheet_apply import describe_google_http_error

        with tempfile.TemporaryFile() as handle:
            handle.write(b'{"error":{"message":"Invalid requests[0].pasteData.coordinate.sheetId"}}')
            handle.seek(0)
            error = HTTPError("https://sheets.example", 400, "Bad Request", {}, handle)

            message = describe_google_http_error(error)

        self.assertIn("HTTP 400 Bad Request", message)
        self.assertIn("Invalid requests[0].pasteData.coordinate.sheetId", message)


if __name__ == "__main__":
    unittest.main()

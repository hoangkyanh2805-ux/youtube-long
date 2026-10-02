import unittest
from urllib.error import HTTPError
from io import BytesIO
import os
import tempfile
from pathlib import Path


class TelegramGatewayTest(unittest.TestCase):
    def test_render_report_command_is_concise_and_secret_free(self):
        from scripts.telegram_gateway import render_command_response

        response = render_command_response(
            "/report",
            daily_status="# Daily\n\n## Snapshot\n\n- Draft Shorts generated: 10\n\n## Today Next Actions\n\n- Review one Short.",
        )

        self.assertIn("Draft Shorts generated", response)
        self.assertIn("Review one Short", response)
        self.assertNotIn("TELEGRAM_BOT_TOKEN", response)

    def test_render_checklist_keyword_returns_learning_pack(self):
        from scripts.telegram_gateway import render_command_response

        response = render_command_response("CHECKLIST", daily_status="")

        self.assertIn("XAUUSD", response)
        self.assertIn("invalidation", response.lower())
        self.assertIn("educational", response.lower())
        self.assertIn("no signal", response.lower())
        self.assertIn("no guaranteed result", response.lower())

    def test_send_message_requires_explicit_approval(self):
        from scripts.telegram_gateway import send_message

        with self.assertRaises(PermissionError):
            send_message("token", "123", "hello", request_func=lambda *args, **kwargs: {})

    def test_send_message_posts_to_telegram_when_approved(self):
        from scripts.telegram_gateway import send_message

        calls = []

        def fake_request(url, payload):
            calls.append((url, payload))
            return {"ok": True, "result": {"message_id": 1}}

        result = send_message("token", "123", "hello", approval="APPROVE", request_func=fake_request)

        self.assertTrue(result["ok"])
        self.assertIn("/sendMessage", calls[0][0])
        self.assertEqual(calls[0][1]["chat_id"], "123")
        self.assertEqual(calls[0][1]["text"], "hello")

    def test_extract_chat_ids_from_updates_includes_thread_id(self):
        from scripts.telegram_gateway import extract_chat_ids

        updates = {
            "result": [
                {
                    "message": {
                        "chat": {"id": -100123, "title": "Azzam Ops", "type": "supergroup"},
                        "message_thread_id": 9,
                    }
                }
            ]
        }

        rows = extract_chat_ids(updates)

        self.assertEqual(rows[0]["chat_id"], "-100123")
        self.assertEqual(rows[0]["thread_id"], "9")

    def test_describe_telegram_error_does_not_expose_token(self):
        from scripts.telegram_gateway import describe_telegram_error

        error = HTTPError("https://api.telegram.org/bot123:SECRET/getUpdates", 404, "Not Found", {}, BytesIO(b""))

        message = describe_telegram_error(error)

        self.assertIn("Telegram API returned HTTP 404", message)
        self.assertIn("bot token", message.lower())
        self.assertNotIn("SECRET", message)

    def test_resolve_thread_id_prefers_cli_then_env(self):
        from scripts.telegram_gateway import resolve_thread_id

        self.assertEqual(resolve_thread_id("11", {"TELEGRAM_THREAD_ID": "22"}), "11")
        self.assertEqual(resolve_thread_id("", {"TELEGRAM_THREAD_ID": "22"}), "22")

    def test_merged_env_prefers_project_env_file_for_bot_token(self):
        from scripts.telegram_gateway import merged_env

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env").write_text("TELEGRAM_BOT_TOKEN=file-token\n", encoding="utf-8")
            old = os.environ.get("TELEGRAM_BOT_TOKEN")
            os.environ["TELEGRAM_BOT_TOKEN"] = "process-token"
            try:
                values = merged_env(root)
            finally:
                if old is None:
                    os.environ.pop("TELEGRAM_BOT_TOKEN", None)
                else:
                    os.environ["TELEGRAM_BOT_TOKEN"] = old

        self.assertEqual(values["TELEGRAM_BOT_TOKEN"], "file-token")


if __name__ == "__main__":
    unittest.main()

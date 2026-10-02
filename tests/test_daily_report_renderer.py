import csv
import html.parser
import tempfile
import unittest
from pathlib import Path

from scripts import daily_report_renderer
from scripts.daily_report_renderer import collect_daily_metrics, render_daily_report, write_daily_report


class DashboardHTMLParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.text = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == "a":
            self.links.append(dict(attrs))

    def handle_data(self, data):
        stripped = data.strip()
        if stripped:
            self.text.append(stripped)


class DailyReportRendererTest(unittest.TestCase):
    def test_collect_daily_metrics_counts_inputs_and_next_actions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            processed = root / "data" / "processed"
            content = root / "outputs" / "content"
            processed.mkdir(parents=True)
            content.mkdir(parents=True)

            self.write_csv(
                processed / "video_inventory.csv",
                ["video_id", "format", "title", "channel"],
                [
                    {"video_id": "v1", "format": "short", "title": "Short lesson", "channel": "Azzam"},
                    {"video_id": "v2", "format": "live", "title": "Live XAUUSD", "channel": "Azzam"},
                ],
            )
            self.write_csv(
                processed / "remake_candidates.csv",
                ["candidate_id", "priority_score", "original_title", "status"],
                [{"candidate_id": "RC-001", "priority_score": "100", "original_title": "Top live", "status": "Backlog"}],
            )
            self.write_csv(
                content / "content_calendar.csv",
                ["short_id", "status", "review_status", "title", "telegram_keyword"],
                [{"short_id": "S-RC-001", "status": "Backlog", "review_status": "Needs human review", "title": "Draft short", "telegram_keyword": "CHECKLIST"}],
            )
            (content / "live_agenda.md").write_text("# Agenda\n", encoding="utf-8")

            metrics = collect_daily_metrics(root, "2026-09-29")

        self.assertEqual(metrics["video_count"], 2)
        self.assertEqual(metrics["short_video_count"], 1)
        self.assertEqual(metrics["live_video_count"], 1)
        self.assertEqual(metrics["remake_candidate_count"], 1)
        self.assertEqual(metrics["draft_short_count"], 1)
        self.assertEqual(metrics["ready_short_count"], 0)
        self.assertEqual(metrics["top_remake_candidate"]["candidate_id"], "RC-001")
        self.assertIn("Review 1 draft Shorts", metrics["next_actions"][0])

    def test_collect_daily_metrics_prefers_api_inventory_when_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            processed = root / "data" / "processed"
            content = root / "outputs" / "content"
            processed.mkdir(parents=True)
            content.mkdir(parents=True)
            self.write_csv(
                processed / "video_inventory.csv",
                ["video_id", "format", "title", "channel", "views"],
                [{"video_id": "old", "format": "short", "title": "Old", "channel": "Azzam", "views": "0"}],
            )
            self.write_csv(
                processed / "video_inventory_api.csv",
                ["video_id", "format", "title", "channel", "views"],
                [{"video_id": "api", "format": "live", "title": "API", "channel": "Azzam", "views": "108"}],
            )
            self.write_csv(processed / "remake_candidates.csv", ["candidate_id", "priority_score"], [])
            self.write_csv(content / "content_calendar.csv", ["short_id", "status"], [])

            metrics = collect_daily_metrics(root, "2026-09-29")

        self.assertEqual(metrics["video_count"], 1)
        self.assertEqual(metrics["live_video_count"], 1)
        self.assertEqual(metrics["short_video_count"], 0)
        self.assertEqual(metrics["views_total"], 108)

    def test_collect_daily_metrics_prefers_api_remake_candidates_when_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            processed = root / "data" / "processed"
            content = root / "outputs" / "content"
            processed.mkdir(parents=True)
            content.mkdir(parents=True)
            self.write_csv(processed / "video_inventory.csv", ["video_id", "format"], [])
            self.write_csv(
                processed / "remake_candidates.csv",
                ["candidate_id", "priority_score", "original_title"],
                [{"candidate_id": "RC-OLD", "priority_score": "100", "original_title": "Old candidate"}],
            )
            self.write_csv(
                processed / "remake_candidates_api.csv",
                ["candidate_id", "priority_score", "original_title"],
                [{"candidate_id": "RC-API-001", "priority_score": "119", "original_title": "API candidate"}],
            )
            self.write_csv(content / "content_calendar.csv", ["short_id", "status"], [])

            metrics = collect_daily_metrics(root, "2026-09-29")

        self.assertEqual(metrics["remake_candidate_count"], 1)
        self.assertEqual(metrics["top_remake_candidate"]["candidate_id"], "RC-API-001")

    def test_collect_daily_metrics_reports_channel_delta_from_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            processed = root / "data" / "processed"
            content = root / "outputs" / "content"
            processed.mkdir(parents=True)
            content.mkdir(parents=True)
            self.write_csv(processed / "video_inventory.csv", ["video_id", "format", "views"], [])
            self.write_csv(processed / "remake_candidates.csv", ["candidate_id", "priority_score"], [])
            self.write_csv(content / "content_calendar.csv", ["short_id", "status"], [])
            self.write_csv(
                processed / "channel_snapshots.csv",
                ["snapshot_at", "role", "channel_id", "channel_title", "subscriber_count", "view_count", "video_count"],
                [
                    {
                        "snapshot_at": "2026-09-28",
                        "role": "self",
                        "channel_id": "chan",
                        "channel_title": "Azzam",
                        "subscriber_count": "1950",
                        "view_count": "230000",
                        "video_count": "288",
                    },
                    {
                        "snapshot_at": "2026-09-29",
                        "role": "self",
                        "channel_id": "chan",
                        "channel_title": "Azzam",
                        "subscriber_count": "1970",
                        "view_count": "233212",
                        "video_count": "289",
                    },
                ],
            )

            metrics = collect_daily_metrics(root, "2026-09-29")

        self.assertEqual(metrics["subscriber_delta"], 20)
        self.assertEqual(metrics["channel_view_delta"], 3212)
        self.assertIn("Subscriber delta from latest snapshots: +20.", metrics["next_actions"])

    def test_render_daily_report_includes_operating_sections(self):
        metrics = {
            "report_date": "2026-09-29",
            "video_count": 100,
            "short_video_count": 20,
            "live_video_count": 50,
            "remake_candidate_count": 84,
            "subscriber_delta": 20,
            "channel_view_delta": 3212,
            "draft_short_count": 10,
            "ready_short_count": 0,
            "top_remake_candidate": {"candidate_id": "RC-002", "original_title": "LIVE TRADING XAUUSD", "priority_score": "100"},
            "top_short": {"short_id": "S-RC-002", "title": "XAUUSD live checklist before entry", "telegram_keyword": "CHECKLIST"},
            "live_agenda_exists": True,
            "next_actions": ["Review 10 draft Shorts"],
            "risks": ["No published Shorts tracked yet"],
        }

        report = render_daily_report(metrics)

        self.assertIn("# Azzam Daily Status - 2026-09-29", report)
        self.assertIn("## Today Next Actions", report)
        self.assertIn("Review 10 draft Shorts", report)
        self.assertIn("Subscriber delta: +20", report)
        self.assertIn("RC-002", report)
        self.assertIn("No published Shorts tracked yet", report)

    def test_write_daily_report_creates_markdown_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report_path = write_daily_report(root, {"report_date": "2026-09-29", "next_actions": [], "risks": []})

            self.assertTrue(report_path.exists())
            self.assertEqual(report_path.name, "daily_status.md")

    def test_render_dashboard_html_includes_operating_sections_and_links(self):
        metrics = {
            "report_date": "2026-10-01",
            "video_count": 100,
            "short_video_count": 13,
            "live_video_count": 58,
            "remake_candidate_count": 50,
            "views_total": 89267,
            "likes_total": 2282,
            "comments_total": 33,
            "subscriber_delta": None,
            "channel_view_delta": None,
            "draft_short_count": 10,
            "ready_short_count": 0,
            "top_remake_candidate": {
                "candidate_id": "RC-API-001",
                "original_title": "LIVE TRADING XAUUSD",
                "priority_score": "119",
            },
            "top_short": {
                "short_id": "S-RC-API-001",
                "title": "XAUUSD live checklist before entry",
                "telegram_keyword": "CHECKLIST",
            },
            "next_actions": ["Review 10 draft Shorts"],
            "risks": ["No Shorts are marked Ready or Scheduled yet."],
        }

        dashboard_html = daily_report_renderer.render_dashboard_html(metrics)
        parser = DashboardHTMLParser()
        parser.feed(dashboard_html)
        page_text = " ".join(parser.text)

        self.assertIn("main", parser.tags)
        self.assertIn("Azzam Hermes Dashboard", page_text)
        self.assertIn("Run Mode: Local L2", page_text)
        self.assertIn("89,267", page_text)
        self.assertIn("Review 10 draft Shorts", page_text)
        self.assertIn("No auto-publish path is enabled", page_text)
        self.assertIn("RC-API-001", page_text)
        self.assertIn("daily_status.md", page_text)
        self.assertTrue(
            any(link.get("href") == "../reports/daily_status.md" for link in parser.links)
        )

    def test_write_dashboard_html_creates_static_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dashboard_path = daily_report_renderer.write_dashboard_html(
                root,
                {
                    "report_date": "2026-10-01",
                    "next_actions": [],
                    "risks": [],
                    "top_short": {},
                    "top_remake_candidate": {},
                },
            )

            self.assertEqual(dashboard_path, root / "outputs" / "dashboard" / "index.html")
            self.assertTrue(dashboard_path.exists())
            self.assertIn("<!doctype html>", dashboard_path.read_text(encoding="utf-8").lower())

    def write_csv(self, path: Path, fieldnames: list[str], rows: list[dict]) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()

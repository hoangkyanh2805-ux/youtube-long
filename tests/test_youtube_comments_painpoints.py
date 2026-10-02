"""Tests for youtube_comments_painpoints.py and aggregate_painpoints.py."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import aggregate_painpoints  # noqa: E402
import youtube_comments_painpoints as ycp  # noqa: E402


def _thread(thread_id: str, top_id: str, top_text: str, author_id: str,
            likes: int = 0, replies: list | None = None,
            total_replies: int = 0) -> dict:
    return {
        "id": thread_id,
        "snippet": {
            "totalReplyCount": total_replies,
            "topLevelComment": {
                "id": top_id,
                "snippet": {
                    "textDisplay": top_text,
                    "publishedAt": "2026-09-01T00:00:00Z",
                    "likeCount": likes,
                    "authorDisplayName": "Viewer",
                    "authorChannelId": {"value": author_id},
                },
            },
        },
        "replies": {"comments": replies or []},
    }


def _reply(rid: str, text: str, author_id: str) -> dict:
    return {
        "id": rid,
        "snippet": {
            "textDisplay": text,
            "publishedAt": "2026-09-01T00:00:00Z",
            "likeCount": 0,
            "authorDisplayName": "Someone",
            "authorChannelId": {"value": author_id},
        },
    }


class ThreadFlattenTests(unittest.TestCase):
    def test_top_level_and_replies_are_flattened(self):
        meta = {"video_id": "v1", "channel": "C", "channel_id": "UC_OWNER",
                "url": "https://youtu.be/v1", "title": "T", "views": "1", "comments": "2"}
        thread = _thread(
            "th1", "c1", "Where should I put my stop loss?", "UC_VIEWER",
            likes=5, total_replies=1,
            replies=[_reply("r1", "Use ATR-based stop loss on gold", "UC_VIEWER2")],
        )
        rows = ycp.thread_to_rows(thread, meta)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["comment_id"], "c1")
        self.assertEqual(rows[0]["engagement_likes"], 5)
        self.assertEqual(rows[0]["reply_count"], 1)
        self.assertEqual(rows[1]["comment_id"], "r1")
        self.assertEqual(rows[1]["parent_comment_id"], "th1")

    def test_owner_replies_are_skipped(self):
        """The channel's own replies are not audience pain-point evidence."""
        meta = {"video_id": "v1", "channel": "C", "channel_id": "UC_OWNER",
                "url": "https://youtu.be/v1", "title": "T", "views": "1", "comments": "2"}
        thread = _thread(
            "th1", "c1", "Great video on XAUUSD entries", "UC_VIEWER",
            total_replies=2,
            replies=[
                _reply("r1", "Thanks for watching! More gold setups coming.", "UC_OWNER"),
                _reply("r2", "What timeframe do you use?", "UC_VIEWER3"),
            ],
        )
        rows = ycp.thread_to_rows(thread, meta)
        ids = [r["comment_id"] for r in rows]
        self.assertIn("c1", ids)
        self.assertIn("r2", ids)
        self.assertNotIn("r1", ids)

    def test_empty_text_is_dropped(self):
        meta = {"video_id": "v1", "channel": "C", "channel_id": "", "url": "u",
                "title": "T", "views": "0", "comments": "0"}
        thread = _thread("th1", "c1", "   ", "UC_VIEWER")
        self.assertEqual(ycp.thread_to_rows(thread, meta), [])

    def test_author_hash_is_derived_downstream(self):
        meta = {"video_id": "v1", "channel": "C", "channel_id": "",
                "url": "u", "title": "T", "views": "0", "comments": "0"}
        thread = _thread("th1", "c1", "How do I manage risk on gold?", "UC_VIEWER")
        row = ycp.thread_to_rows(thread, meta)[0]
        normalized = ycp.normalize_item(row, "youtube-data-api-v3/commentThreads.list")
        self.assertIsNotNone(normalized["author_hash"])
        self.assertEqual(len(normalized["author_hash"]), 64)


class EnvTests(unittest.TestCase):
    def test_bom_is_stripped_from_first_key(self):
        with tempfile.TemporaryDirectory() as temp:
            env = Path(temp) / ".env"
            # utf-8 BOM + key on the first line
            env.write_bytes("\ufeffYT_API_KEY=abc123\nOTHER=1\n".encode("utf-8"))
            values = ycp.load_env_file(env)
            self.assertEqual(values.get("YT_API_KEY"), "abc123")


class SearchTests(unittest.TestCase):
    def test_search_videos_maps_fields(self):
        calls = {"n": 0}

        def fake_get(resource, params, api_key):
            calls["n"] += 1
            return {
                "items": [
                    {"id": {"videoId": "vid1"}, "snippet": {
                        "title": "Gold strategy", "channelTitle": "Chan", "channelId": "UC1"}},
                    {"id": {"videoId": "vid2"}, "snippet": {
                        "title": "XAUUSD", "channelTitle": "Chan2", "channelId": "UC2"}},
                ]
            }

        original = ycp.youtube_get
        ycp.youtube_get = fake_get
        try:
            videos, n = ycp.search_videos("gold", "key", 2)
        finally:
            ycp.youtube_get = original

        self.assertEqual(n, 1)
        self.assertEqual(len(videos), 2)
        self.assertEqual(videos[0]["video_id"], "vid1")
        self.assertEqual(videos[0]["channel_id"], "UC1")
        self.assertEqual(videos[0]["url"], "https://www.youtube.com/watch?v=vid1")


class AggregateTests(unittest.TestCase):
    def _write_run(self, root: Path, name: str, rows: list[dict]) -> None:
        d = root / name
        d.mkdir(parents=True, exist_ok=True)
        fields = ["score", "categories", "platform", "comment_text", "engagement_likes",
                  "reply_count", "content_url", "comment_id", "source_actor", "source_run_id"]
        with (d / "painpoint_candidates.csv").open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    def test_dedupe_and_rank_across_runs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_run(root, "run_a", [
                {"score": "1.5", "categories": "risk_management", "platform": "youtube",
                 "comment_text": "How do I set a stop loss on gold?",
                 "engagement_likes": "2", "reply_count": "0",
                 "content_url": "https://youtu.be/a", "comment_id": "c1"},
            ])
            self._write_run(root, "run_b", [
                # same text, higher score -> wins
                {"score": "9.9", "categories": "risk_management", "platform": "youtube",
                 "comment_text": "How do I set a stop loss on gold?",
                 "engagement_likes": "50", "reply_count": "3",
                 "content_url": "https://youtu.be/b", "comment_id": "c2"},
                {"score": "2.0", "categories": "entry_timing", "platform": "youtube",
                 "comment_text": "When should I enter a XAUUSD trade?",
                 "engagement_likes": "1", "reply_count": "0",
                 "content_url": "https://youtu.be/c", "comment_id": "c3"},
            ])
            out = root / "master"
            argv = sys.argv
            sys.argv = ["aggregate", "--input-dir", str(root), "--output-dir", str(out)]
            try:
                rc = aggregate_painpoints.main()
            finally:
                sys.argv = argv

            self.assertEqual(rc, 0)
            rows = list(csv.DictReader((out / "painpoints_master.csv").open(encoding="utf-8-sig")))
            self.assertEqual(len(rows), 2)  # deduped
            self.assertEqual(rows[0]["score"], "9.9")  # highest first
            self.assertEqual(rows[0]["painpoint_id"], "PP-0001")
            self.assertTrue(rows[0]["reply_short_angle"])
            self.assertEqual(rows[0]["status"], "Backlog")

    def test_no_candidate_files_returns_error(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            argv = sys.argv
            sys.argv = ["aggregate", "--input-dir", str(root), "--output-dir", str(root / "m")]
            try:
                rc = aggregate_painpoints.main()
            finally:
                sys.argv = argv
            self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()

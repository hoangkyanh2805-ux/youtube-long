"""
Stage 1: Scrape comments from LONG-FORM videos (>60s) of competitor channels.

Channels: @TTrades_edu, @ragheehorner, @TradewithPat, @JeaFxForexTrading
Output: outputs/competitor_longform/
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_painpoints import (  # noqa: E402
    FIELDS,
    dedupe,
    normalize_item,
    write_csv,
    write_report,
    candidates as extract_candidates,
)

# Force UTF-8 console: without this, printing Vietnamese crashes with
# UnicodeEncodeError when stdout is a pipe (dagu/cron/CI).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402
ensure_utf8_console()

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
REQUEST_TIMEOUT = 60

CHANNEL_HANDLES = ["@TTrades_edu", "@ragheehorner", "@TradewithPat", "@JeaFxForexTrading"]
LONGFORM_PER_CHANNEL = 12
MAX_COMMENTS_PER_VIDEO = 100


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def resolve_api_key() -> str:
    key = os.environ.get("YT_API_KEY")
    if key:
        return key
    root = Path(__file__).resolve().parents[1]
    for env_file in [root / ".env", Path.home() / "AppData/Local/hermes/profiles/youtube/.env"]:
        key = load_env_file(env_file).get("YT_API_KEY")
        if key and key != "your_youtube_api_key_here":
            return key
    return "AIzaSyAVbkgePW7W80pnwSJjlboWwjR9aZSTz7c"


def youtube_get(resource: str, params: dict[str, str], api_key: str) -> dict:
    query = dict(params)
    query["key"] = api_key
    url = f"{YOUTUBE_API_BASE}/{resource}?{urlencode(query)}"
    try:
        with urlopen(url, timeout=REQUEST_TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        if e.code == 403 and "commentsDisabled" in body:
            return {"items": [], "_comments_disabled": True}
        raise RuntimeError(f"YouTube API error {e.code}: {body[:300]}") from e
    except URLError as e:
        raise RuntimeError(f"YouTube API connection error: {e}") from e


def resolve_handle(handle: str, api_key: str) -> dict:
    payload = youtube_get("channels", {
        "part": "snippet,statistics,brandingSettings",
        "forHandle": handle.lstrip("@"),
    }, api_key)
    items = payload.get("items", [])
    return items[0] if items else {}


def parse_duration_seconds(duration: str) -> int:
    if not duration or not duration.startswith("PT"):
        return 0
    value = duration[2:]
    total, number = 0, ""
    for char in value:
        if char.isdigit():
            number += char
            continue
        if not number:
            continue
        amount = int(number)
        if char == "H":
            total += amount * 3600
        elif char == "M":
            total += amount * 60
        elif char == "S":
            total += amount
        number = ""
    return total


def get_channel_longform(channel_id: str, api_key: str, max_videos: int) -> list[dict]:
    """Fetch top-viewed videos, then filter to long-form (>60s)."""
    candidates = []
    page_token = None
    # Over-fetch because shorts are mixed in; then filter by duration
    while len(candidates) < max_videos * 4:
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "type": "video",
            "maxResults": "50",
            "order": "viewCount",
        }
        if page_token:
            params["pageToken"] = page_token
        payload = youtube_get("search", params, api_key)
        for item in payload.get("items", []):
            vid = item.get("id", {}).get("videoId", "")
            if not vid:
                continue
            snippet = item.get("snippet", {})
            candidates.append({
                "video_id": vid,
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "channel_id": snippet.get("channelId", ""),
                "url": f"https://www.youtube.com/watch?v={vid}",
                "published": snippet.get("publishedAt", ""),
                "description": snippet.get("description", "")[:1000],
            })
        page_token = payload.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.2)

    # Fetch durations + stats, filter long-form
    longform = []
    for i in range(0, len(candidates), 50):
        batch = candidates[i:i+50]
        ids = ",".join(c["video_id"] for c in batch)
        payload = youtube_get("videos", {
            "part": "statistics,contentDetails",
            "id": ids,
        }, api_key)
        stats_by_id = {}
        for item in payload.get("items", []):
            s = item.get("statistics", {})
            c = item.get("contentDetails", {})
            stats_by_id[item["id"]] = {
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "comments": int(s.get("commentCount", 0)),
                "duration": c.get("duration", ""),
                "duration_sec": parse_duration_seconds(c.get("duration", "")),
            }
        for c in batch:
            st = stats_by_id.get(c["video_id"])
            if not st:
                continue
            c.update(st)
            if st["duration_sec"] > 60:
                longform.append(c)
        time.sleep(0.2)

    longform.sort(key=lambda x: x.get("views", 0), reverse=True)
    return longform[:max_videos]


def fetch_comments(video_id: str, api_key: str, max_comments: int) -> tuple[list[dict], int]:
    items, page_token, calls = [], None, 0
    while len(items) < max_comments:
        params = {
            "part": "snippet,replies",
            "videoId": video_id,
            "maxResults": "100",
            "order": "relevance",
            "textFormat": "plainText",
        }
        if page_token:
            params["pageToken"] = page_token
        payload = youtube_get("commentThreads", params, api_key)
        calls += 1
        batch = payload.get("items", [])
        items.extend(batch)
        page_token = payload.get("nextPageToken")
        if not page_token or not batch:
            break
        time.sleep(0.2)
    return items[:max_comments], calls


def thread_to_rows(thread: dict, video_meta: dict) -> list[dict]:
    rows = []
    snippet = thread.get("snippet", {})
    top = snippet.get("topLevelComment", {})
    thread_id = thread.get("id", "")
    owner_channel_id = video_meta.get("channel_id", "").strip()

    def make_row(c: dict, parent_id: str | None) -> dict | None:
        c_snippet = c.get("snippet", {})
        text = str(c_snippet.get("textDisplay") or c_snippet.get("textOriginal") or "").strip()
        if not text:
            return None
        author_channel = c_snippet.get("authorChannelId", {})
        author_id = author_channel.get("value") if isinstance(author_channel, dict) else None
        if owner_channel_id and author_id and str(author_id) == owner_channel_id:
            return None
        return {
            "platform": "youtube",
            "channel_or_account": video_meta.get("channel", ""),
            "content_id": video_meta.get("video_id", ""),
            "content_url": video_meta.get("url", ""),
            "comment_id": c.get("id", ""),
            "comment_text": text,
            "comment_timestamp": c_snippet.get("publishedAt"),
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "engagement_likes": c_snippet.get("likeCount", 0),
            "reply_count": 0,
            "language": c_snippet.get("language") or None,
            "author_hash": None,
            "authorName": c_snippet.get("authorDisplayName", ""),
            "authorChannelId": author_id,
            "parent_comment_id": parent_id,
            "source_actor": "youtube-data-api-v3/commentThreads.list",
            "source_run_id": None,
            "video_id": video_meta.get("video_id", ""),
            "video_title": video_meta.get("title", ""),
            "video_channel": video_meta.get("channel", ""),
            "video_views": video_meta.get("views", ""),
            "video_comments": video_meta.get("comments", ""),
            "video_duration_sec": video_meta.get("duration_sec", ""),
            "thread_id": thread_id,
        }

    top_row = make_row(top, None)
    if top_row:
        top_row["reply_count"] = int(snippet.get("totalReplyCount", 0) or 0)
        rows.append(top_row)
    replies = thread.get("replies", {}).get("comments", []) if isinstance(thread.get("replies"), dict) else []
    for reply in replies:
        rr = make_row(reply, thread_id)
        if rr:
            rows.append(rr)
    return rows


def main() -> int:
    api_key = resolve_api_key()
    output_dir = Path("outputs/competitor_longform")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("LONG-FORM VIDEO COMMENT SCRAPE")
    print("=" * 60)

    # Step 1: resolve + fetch long-form inventory
    channels_info = {}
    all_videos = []
    for handle in CHANNEL_HANDLES:
        print(f"\nResolving {handle}...")
        info = resolve_handle(handle, api_key)
        if not info:
            print("  FAILED")
            continue
        channels_info[handle] = info
        cid = info.get("id", "")
        print(f"  → {info.get('snippet', {}).get('title', '')} ({cid})")
        print(f"  Fetching top long-form videos...")
        videos = get_channel_longform(cid, api_key, LONGFORM_PER_CHANNEL)
        print(f"  → {len(videos)} long-form videos")
        for v in videos:
            print(f"     {v['views']:>10,} | {v['duration']:>10} | {v['title'][:60]}")
        all_videos.extend(videos)
        time.sleep(0.3)

    (output_dir / "channels_info.json").write_text(
        json.dumps(channels_info, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(output_dir / "longform_inventory.csv", all_videos,
              ["video_id", "title", "channel", "channel_id", "url", "published",
               "views", "likes", "comments", "duration", "duration_sec", "description"])
    print(f"\nSaved inventory: {len(all_videos)} long-form videos")

    # Step 2: scrape comments
    print("\n" + "=" * 60)
    print("SCRAPING COMMENTS")
    print("=" * 60)
    all_rows = []
    for i, v in enumerate(all_videos, 1):
        print(f"[{i}/{len(all_videos)}] {v['video_id']} — {v['title'][:55]}...")
        try:
            items, calls = fetch_comments(v["video_id"], api_key, MAX_COMMENTS_PER_VIDEO)
            rows = []
            for thread in items:
                rows.extend(thread_to_rows(thread, v))
            print(f"   → {len(items)} threads, {len(rows)} comments")
            all_rows.extend(rows)
        except Exception as e:
            print(f"   → ERROR: {e}")
        time.sleep(0.3)

    (output_dir / "raw_comments.json").write_text(
        json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {len(all_rows)} raw comments")

    # Step 3: normalize + pain points
    print("\n" + "=" * 60)
    print("NORMALIZING + PAIN POINTS")
    print("=" * 60)
    normalized = []
    for item in all_rows:
        row = normalize_item(item, "youtube-data-api-v3/commentThreads.list")
        if row:
            for extra in ("video_id", "video_title", "video_channel", "video_views",
                          "video_comments", "video_duration_sec"):
                row[extra] = item.get(extra, "")
            normalized.append(row)
    normalized = dedupe(normalized)
    print(f"Normalized unique: {len(normalized)}")

    extra_fields = ["video_id", "video_title", "video_channel", "video_views",
                    "video_comments", "video_duration_sec"]
    write_csv(output_dir / "normalized_comments.csv", normalized, FIELDS + extra_fields)

    pain_rows = extract_candidates(normalized)
    print(f"Pain-point candidates: {len(pain_rows)}")
    pain_fields = ["score", "categories", "platform", "comment_text", "engagement_likes",
                   "reply_count", "content_url", "comment_id", "source_actor", "source_run_id"]
    write_csv(output_dir / "painpoint_candidates.csv", pain_rows, pain_fields)
    write_report(output_dir / "painpoint_report.md", normalized, pain_rows)

    print("\n=== DONE ===")
    print(f"Videos: {len(all_videos)} | Raw comments: {len(all_rows)} | "
          f"Normalized: {len(normalized)} | Pain points: {len(pain_rows)}")
    print(f"Output: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

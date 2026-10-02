"""
YouTube Data API v3 `commentThreads.list` → Pain-Point CSV.

Miễn phí (10,000 units/day), không cần Apify token. Trả về comments đầy đủ
với author, text, likes, replies. Hỗ trợ pagination (100 comments/call).

Usage:
    python scripts/youtube_comments_painpoints.py \
        --input data/processed/video_inventory_api.csv \
        --output-dir outputs/painpoints/yt_api_run_001 \
        --max-comments 200 \
        --max-videos 20

Output:
    outputs/painpoints/yt_api_run_001/
        raw_comments.json          # raw commentThreads API response items
        normalized_comments.csv    # normalized comments (social_comment schema)
        painpoint_candidates.csv   # pain-point candidates (scored)
        painpoint_report.md        # summary report
        run_metadata.json          # run metadata (quota used, timestamps)
"""
from __future__ import annotations

import argparse
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

# Reuse the deterministic extraction/normalization logic
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
DEFAULT_MAX_COMMENTS = 200
DEFAULT_MAX_VIDEOS = 20
REQUEST_TIMEOUT = 60
# commentThreads.list costs 1 unit per call regardless of maxResults
QUOTA_COST_PER_CALL = 1


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    # utf-8-sig strips a leading BOM (the project .env has one, which would
    # otherwise corrupt the first key name and hide YT_API_KEY).
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
    env_files = [root / ".env", Path.home() / "AppData/Local/hermes/profiles/youtube/.env"]
    for env_file in env_files:
        key = load_env_file(env_file).get("YT_API_KEY")
        if key and key != "your_youtube_api_key_here":
            return key
    raise RuntimeError("Missing YT_API_KEY. Put the real key in .env or environment variable.")


# ---------------------------------------------------------------------------
# YouTube API
# ---------------------------------------------------------------------------


def youtube_get(resource: str, params: dict[str, str], api_key: str) -> dict:
    query = dict(params)
    query["key"] = api_key
    url = f"{YOUTUBE_API_BASE}/{resource}?{urlencode(query)}"
    try:
        with urlopen(url, timeout=REQUEST_TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        # commentsDisabled (403) is expected for videos with comments turned off
        if e.code == 403 and "commentsDisabled" in body:
            return {"items": [], "_comments_disabled": True}
        raise RuntimeError(f"YouTube API error {e.code}: {body}") from e
    except URLError as e:
        raise RuntimeError(f"YouTube API connection error: {e}") from e


def fetch_comments_for_video(
    video_id: str,
    api_key: str,
    max_comments: int,
    order: str = "relevance",
) -> tuple[list[dict], int]:
    """Fetch comments for one video via commentThreads.list with pagination.

    Returns (comment_items, api_calls_made).
    """
    items: list[dict] = []
    page_token: str | None = None
    calls = 0
    per_page = min(100, max_comments)

    while len(items) < max_comments:
        params = {
            "part": "snippet,replies",
            "videoId": video_id,
            "maxResults": str(per_page),
            "order": order,
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


# ---------------------------------------------------------------------------
# Flatten commentThreads items -> flat comment rows
# ---------------------------------------------------------------------------


def thread_to_rows(thread: dict, video_meta: dict[str, str]) -> list[dict[str, Any]]:
    """Flatten a commentThread item into top-level + reply comment rows.

    Replies authored by the video's own channel are skipped: an owner's
    reply is not audience pain-point evidence.
    """
    rows: list[dict[str, Any]] = []
    snippet = thread.get("snippet", {})
    top = snippet.get("topLevelComment", {})
    thread_id = thread.get("id", "")
    owner_channel_id = video_meta.get("channel_id", "").strip()

    def make_row(c: dict, parent_id: str | None) -> dict[str, Any] | None:
        c_snippet = c.get("snippet", {})
        text = str(c_snippet.get("textDisplay") or c_snippet.get("textOriginal") or "").strip()
        if not text:
            return None
        author_channel = c_snippet.get("authorChannelId", {})
        author_id = author_channel.get("value") if isinstance(author_channel, dict) else None
        # Skip the channel owner's own comments/replies
        if owner_channel_id and author_id and str(author_id) == owner_channel_id:
            return None
        return {
            "platform": "youtube",
            "channel_or_account": video_meta.get("channel", ""),
            "content_id": video_meta.get("video_id", ""),
            "content_url": video_meta.get("url", f"https://www.youtube.com/watch?v={video_meta.get('video_id', '')}"),
            "comment_id": c.get("id", ""),
            "comment_text": text,
            "comment_timestamp": c_snippet.get("publishedAt"),
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "engagement_likes": c_snippet.get("likeCount", 0),
            "reply_count": 0,
            "language": c_snippet.get("language") or None,
            "author_hash": None,  # hashed downstream by normalize_item
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
            "thread_id": thread_id,
        }

    top_row = make_row(top, None)
    if top_row:
        # reply_count for top-level comes from thread snippet
        top_row["reply_count"] = int(snippet.get("totalReplyCount", 0) or 0)
        rows.append(top_row)

    replies = thread.get("replies", {}).get("comments", []) if isinstance(thread.get("replies"), dict) else []
    for reply in replies:
        reply_row = make_row(reply, thread_id)
        if reply_row:
            rows.append(reply_row)

    return rows


# ---------------------------------------------------------------------------
# Video inventory
# ---------------------------------------------------------------------------


def search_videos(
    query: str,
    api_key: str,
    max_videos: int,
    order: str = "viewCount",
    published_after: str | None = None,
) -> tuple[list[dict[str, str]], int]:
    """Search YouTube for videos matching a query (long-tail keyword mode).

    Returns (video_meta_list, api_calls). search.list costs 100 units/call.
    """
    videos: list[dict[str, str]] = []
    page_token: str | None = None
    calls = 0

    while len(videos) < max_videos:
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": str(min(50, max_videos - len(videos))),
            "order": order,
        }
        if published_after:
            params["publishedAfter"] = published_after
        if page_token:
            params["pageToken"] = page_token
        payload = youtube_get("search", params, api_key)
        calls += 1
        for item in payload.get("items", []):
            vid = item.get("id", {}).get("videoId", "")
            if not vid:
                continue
            snippet = item.get("snippet", {})
            videos.append({
                "video_id": vid,
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "channel_id": snippet.get("channelId", ""),
                "url": f"https://www.youtube.com/watch?v={vid}",
                "views": "",
                "comments": "",
                "format": "",
            })
            if len(videos) >= max_videos:
                break
        page_token = payload.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.2)

    return videos, calls


def load_videos(csv_path: Path, max_videos: int) -> list[dict[str, str]]:
    videos: list[dict[str, str]] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            video_id = (row.get("video_id") or "").strip()
            if not video_id:
                continue
            videos.append({
                "video_id": video_id,
                "title": row.get("title", ""),
                "channel": row.get("channel", ""),
                "channel_id": row.get("channel_id", ""),
                "url": row.get("url", f"https://www.youtube.com/watch?v={video_id}"),
                "views": row.get("views", "0"),
                "comments": row.get("comments", "0"),
                "format": row.get("format", ""),
            })
            if len(videos) >= max_videos:
                break
    return videos


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Video inventory CSV (omit when using --query)")
    parser.add_argument("--query", help="Long-tail keyword to search videos (uses search.list, 100 units/call)")
    parser.add_argument("--order", default="relevance", choices=["relevance", "time"],
                        help="Comment sort order")
    parser.add_argument("--search-order", default="viewCount", choices=["viewCount", "relevance", "date"],
                        help="Video search order when using --query")
    parser.add_argument("--output-dir", required=True, type=Path, help="Output directory")
    parser.add_argument("--max-comments", type=int, default=DEFAULT_MAX_COMMENTS,
                        help="Max comments per video (paginated, 100/call)")
    parser.add_argument("--max-videos", type=int, default=DEFAULT_MAX_VIDEOS,
                        help="Max videos to scrape")
    args = parser.parse_args()

    if not args.input and not args.query:
        parser.error("Provide --input (inventory CSV) or --query (long-tail keyword search)")

    api_key = resolve_api_key()
    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    search_calls = 0
    if args.query:
        videos, search_calls = search_videos(
            args.query, api_key, args.max_videos, order=args.search_order
        )
        print(f"Search query: {args.query!r} (order={args.search_order})")
    else:
        videos = load_videos(args.input, args.max_videos)

    if not videos:
        print("ERROR: No videos found.", file=sys.stderr)
        return 3

    print(f"Loaded {len(videos)} videos")
    print(f"Max comments per video: {args.max_comments}")
    print(f"Comment order: {args.order}")
    print(f"Output dir: {output_dir}")
    print()

    all_rows: list[dict[str, Any]] = []
    run_metadata: dict[str, Any] = {
        "source": "youtube-data-api-v3/commentThreads.list",
        "query": args.query,
        "input": str(args.input) if args.input else None,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "quota_cost_per_call": QUOTA_COST_PER_CALL,
        "search_api_calls": search_calls,
        "search_quota_units": search_calls * 100,
        "total_api_calls": search_calls,
        "total_quota_units": search_calls * 100,
        "videos": [],
    }

    for i, video in enumerate(videos, 1):
        vid = video["video_id"]
        print(f"[{i}/{len(videos)}] {vid} — {video['title'][:60]}")
        try:
            items, calls = fetch_comments_for_video(vid, api_key, args.max_comments, args.order)
            run_metadata["total_api_calls"] += calls
            run_metadata["total_quota_units"] += calls * QUOTA_COST_PER_CALL

            rows: list[dict[str, Any]] = []
            for thread in items:
                rows.extend(thread_to_rows(thread, video))

            print(f"  threads={len(items)} comments(flat)={len(rows)} api_calls={calls}")
            all_rows.extend(rows)
            run_metadata["videos"].append({
                "video_id": vid,
                "threads_fetched": len(items),
                "comments_flat": len(rows),
                "api_calls": calls,
                "status": "ok",
            })
        except Exception as e:  # noqa: BLE001 - record and continue (fail-soft)
            print(f"  ERROR: {e}")
            run_metadata["videos"].append({"video_id": vid, "status": "error", "error": str(e)})

        if i < len(videos):
            time.sleep(0.2)

    # Save raw flattened rows
    raw_path = output_dir / "raw_comments.json"
    raw_path.write_text(json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {len(all_rows)} raw comment rows to {raw_path}")

    # Normalize (dedupe by platform+comment_id+text)
    normalized: list[dict[str, Any]] = []
    for item in all_rows:
        row = normalize_item(item, "youtube-data-api-v3/commentThreads.list")
        if row:
            for extra in ("video_id", "video_title", "video_channel", "video_views", "video_comments"):
                row[extra] = item.get(extra, "")
            normalized.append(row)

    normalized = dedupe(normalized)
    print(f"Normalized unique comments: {len(normalized)}")

    extra_fields = ["video_id", "video_title", "video_channel", "video_views", "video_comments"]
    write_csv(output_dir / "normalized_comments.csv", normalized, FIELDS + extra_fields)
    print(f"Written {output_dir / 'normalized_comments.csv'}")

    # Extract pain-point candidates
    pain_rows = extract_candidates(normalized)
    print(f"Pain-point candidates: {len(pain_rows)}")

    pain_fields = ["score", "categories", "platform", "comment_text", "engagement_likes",
                   "reply_count", "content_url", "comment_id", "source_actor", "source_run_id"]
    write_csv(output_dir / "painpoint_candidates.csv", pain_rows, pain_fields)
    print(f"Written {output_dir / 'painpoint_candidates.csv'}")

    write_report(output_dir / "painpoint_report.md", normalized, pain_rows)
    print(f"Written {output_dir / 'painpoint_report.md'}")

    # Metadata
    run_metadata["finished_at"] = datetime.now(timezone.utc).isoformat()
    run_metadata["total_raw_rows"] = len(all_rows)
    run_metadata["total_normalized"] = len(normalized)
    run_metadata["total_painpoint_candidates"] = len(pain_rows)
    (output_dir / "run_metadata.json").write_text(
        json.dumps(run_metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Written {output_dir / 'run_metadata.json'}")

    print("\n=== DONE ===")
    print(f"Raw rows: {len(all_rows)} | Normalized: {len(normalized)} | "
          f"Pain-point candidates: {len(pain_rows)}")
    print(f"Quota used: {run_metadata['total_quota_units']} units "
          f"({run_metadata['total_api_calls']} calls)")
    print(f"Output: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

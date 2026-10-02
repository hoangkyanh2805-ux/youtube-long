"""
Apify YouTube Comments Scraper → Pain-Point CSV.

Chạy Apify actor `streamers/youtube-comments-scraper` trên danh sách video IDs,
thu thập comments, sau đó normalize + extract pain-point candidates.

Usage:
    python scripts/apify_scrape_comments.py --input data/processed/video_inventory_api.csv \
        --output-dir outputs/painpoints/apify_run_001 \
        --max-comments 100 \
        --max-videos 20

Output:
    outputs/painpoints/apify_run_001/
        raw_comments.json          # raw Apify dataset export
        normalized_comments.csv    # normalized comments
        painpoint_candidates.csv   # pain-point candidates (scored)
        painpoint_report.md        # summary report
        run_metadata.json          # run metadata (actor, run_id, timestamps)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

APIFY_ACTOR = "streamers/youtube-comments-scraper"
APIFY_API_BASE = "https://api.apify.com"
DEFAULT_MAX_COMMENTS = 100
DEFAULT_MAX_VIDEOS = 20
REQUEST_TIMEOUT = 120  # seconds
POLL_INTERVAL = 5  # seconds
MAX_POLL_ATTEMPTS = 60  # 5 minutes max wait

# ---------------------------------------------------------------------------
# Env helpers
# ---------------------------------------------------------------------------


def read_env_value(key: str) -> str | None:
    """Read env var from process env or .env files."""
    val = os.environ.get(key)
    if val:
        return val.strip().strip('"').strip("'") or None

    env_files = [
        Path(__file__).resolve().parents[1] / ".env",
        Path.home() / "AppData/Local/hermes/profiles/youtube/.env",
    ]
    for env_file in env_files:
        if not env_file.exists():
            continue
        for raw_line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            if name.strip() == key:
                return value.strip().strip('"').strip("'") or None
    return None


# ---------------------------------------------------------------------------
# Apify API
# ---------------------------------------------------------------------------


def apify_request(
    method: str,
    url: str,
    token: str,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Make an Apify API request."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Apify API error {e.code}: {error_body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Apify API connection error: {e}") from e


def start_actor_run(
    token: str,
    video_url: str,
    max_comments: int,
) -> dict[str, Any]:
    """Start an Apify actor run for a single video URL."""
    actor_id = APIFY_ACTOR.replace("/", "~")
    url = f"{APIFY_API_BASE}/v2/acts/{actor_id}/runs"
    body = {
        "startUrls": [{"url": video_url}],
        "maxComments": max_comments,
    }
    return apify_request("POST", url, token, body)


def wait_for_run(
    token: str,
    run_id: str,
) -> dict[str, Any]:
    """Poll actor run status until finished."""
    actor_id = APIFY_ACTOR.replace("/", "~")
    url = f"{APIFY_API_BASE}/v2/acts/{actor_id}/runs/{run_id}"
    for attempt in range(MAX_POLL_ATTEMPTS):
        data = apify_request("GET", url, token)
        status = data.get("data", {}).get("status", "")
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            return data
        print(f"  Run {run_id}: {status} (attempt {attempt + 1}/{MAX_POLL_ATTEMPTS})")
        time.sleep(POLL_INTERVAL)
    raise TimeoutError(f"Actor run {run_id} did not finish within {MAX_POLL_ATTEMPTS * POLL_INTERVAL}s")


def fetch_dataset(
    token: str,
    dataset_id: str,
) -> list[dict[str, Any]]:
    """Fetch all items from an Apify dataset."""
    url = f"{APIFY_API_BASE}/v2/datasets/{dataset_id}/items"
    data = apify_request("GET", url, token)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("items", "data", "results"):
            if isinstance(data.get(key), list):
                return data[key]
    return []


# ---------------------------------------------------------------------------
# Video inventory
# ---------------------------------------------------------------------------


def load_video_ids(csv_path: str, max_videos: int) -> list[dict[str, str]]:
    """Load video IDs from inventory CSV."""
    videos = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            video_id = row.get("video_id", "").strip()
            if not video_id:
                continue
            videos.append({
                "video_id": video_id,
                "title": row.get("title", ""),
                "channel": row.get("channel", ""),
                "url": row.get("url", f"https://www.youtube.com/watch?v={video_id}"),
                "views": row.get("views", "0"),
                "comments": row.get("comments", "0"),
            })
            if len(videos) >= max_videos:
                break
    return videos


# ---------------------------------------------------------------------------
# Pain-point extraction (inline from extract_painpoints.py)
# ---------------------------------------------------------------------------

import hashlib
import math
import re
from collections import Counter

# Force UTF-8 console: without this, printing Vietnamese crashes with
# UnicodeEncodeError when stdout is a pipe (dagu/cron/CI).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402
ensure_utf8_console()

CATEGORIES = {
    "risk_management": ("risk", "stop loss", "sl", "lot size", "drawdown", "quản lý vốn", "cắt lỗ"),
    "entry_timing": ("entry", "enter", "when to buy", "when to sell", "vào lệnh", "điểm vào", "timing"),
    "strategy_rules": ("strategy", "setup", "indicator", "timeframe", "chiến lược", "quy tắc", "tín hiệu"),
    "broker_platform": ("broker", "spread", "slippage", "mt4", "mt5", "tradingview", "sàn", "nền tảng"),
    "psychology": ("fear", "greed", "revenge", "discipline", "tâm lý", "sợ", "kỷ luật", "fomo"),
    "education_gap": ("how", "why", "what", "explain", "tutorial", "làm sao", "tại sao", "giải thích", "hướng dẫn"),
}
PAIN_MARKERS = (
    "problem", "struggle", "confused", "don't understand", "cannot", "can't", "issue",
    "khó", "không hiểu", "không biết", "vấn đề", "thua", "lỗ", "mất tiền", "help",
)


def first(item: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return value
    return default


def as_int(value: Any) -> int:
    try:
        return max(0, int(float(value or 0)))
    except (TypeError, ValueError):
        return 0


def infer_platform(item: dict[str, Any], source_actor: str, content_url: str) -> str:
    haystack = f"{first(item, 'platform', default='')} {source_actor} {content_url}".lower()
    for platform in ("youtube", "tiktok", "instagram", "facebook"):
        if platform in haystack or (platform == "youtube" and "youtu.be" in haystack):
            return platform
    return "unknown"


def author_hash(item: dict[str, Any]) -> str | None:
    raw = first(item, "authorId", "authorChannelId", "authorUrl", "authorName", "username", "ownerUsername")
    if not raw:
        author = item.get("author")
        if isinstance(author, dict):
            raw = first(author, "id", "url", "name", "username")
    return hashlib.sha256(str(raw).encode("utf-8")).hexdigest() if raw else None


def normalize_item(item: dict[str, Any], actor: str | None = None, run_id: str | None = None) -> dict[str, Any] | None:
    text = str(first(item, "comment_text", "text", "commentText", "content", "message", default="")).strip()
    if not text:
        return None
    source_actor = str(actor or first(item, "source_actor", "actorId", "actor", default="unknown"))
    content_url = str(first(item, "content_url", "videoUrl", "postUrl", "url", "inputUrl", default=""))
    content_id = str(first(item, "content_id", "videoId", "postId", "awemeId", default=""))
    comment_id = str(first(item, "comment_id", "commentId", "id", "cid", default=""))
    if not comment_id:
        comment_id = hashlib.sha256(f"{content_url}|{text}".encode("utf-8")).hexdigest()[:24]
    return {
        "platform": infer_platform(item, source_actor, content_url),
        "channel_or_account": first(item, "channel_or_account", "channelName", "ownerUsername", "pageName", "username"),
        "content_id": content_id,
        "content_url": content_url,
        "comment_id": comment_id,
        "comment_text": text,
        "comment_timestamp": first(item, "comment_timestamp", "publishedTimeText", "publishedAt", "createTime", "timestamp"),
        "collected_at": str(first(item, "collected_at", default=datetime.now(timezone.utc).isoformat())),
        "engagement_likes": as_int(first(item, "engagement_likes", "likesCount", "likeCount", "diggCount", "likes")),
        "reply_count": as_int(first(item, "reply_count", "replyCount", "repliesCount", "childCommentCount")),
        "language": first(item, "language", "lang"),
        "author_hash": author_hash(item),
        "parent_comment_id": first(item, "parent_comment_id", "parentCommentId", "replyToCommentId"),
        "source_actor": source_actor,
        "source_run_id": run_id or first(item, "source_run_id", "runId"),
    }


def dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    result = []
    for row in rows:
        key = (row["platform"], row["comment_id"], re.sub(r"\s+", " ", row["comment_text"].lower()).strip())
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result


def classify(text: str) -> list[str]:
    lower = text.lower()
    categories = [name for name, keywords in CATEGORIES.items() if any(keyword in lower for keyword in keywords)]
    if not categories and ("?" in text or any(marker in lower for marker in PAIN_MARKERS)):
        categories.append("other_question_or_pain")
    return categories


def score(row: dict[str, Any], categories: list[str]) -> float:
    lower = row["comment_text"].lower()
    return round(
        1.0
        + math.log1p(row["engagement_likes"])
        + 0.5 * math.log1p(row["reply_count"])
        + (1.0 if "?" in row["comment_text"] else 0.0)
        + (1.0 if any(marker in lower for marker in PAIN_MARKERS) else 0.0)
        + (0.25 * min(3, len(categories))),
        3,
    )


def extract_painpoints(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for row in rows:
        cats = classify(row["comment_text"])
        if not cats:
            continue
        result.append({
            "score": score(row, cats),
            "categories": "|".join(cats),
            "platform": row["platform"],
            "comment_text": row["comment_text"],
            "engagement_likes": row["engagement_likes"],
            "reply_count": row["reply_count"],
            "content_url": row["content_url"],
            "comment_id": row["comment_id"],
            "source_actor": row["source_actor"],
            "source_run_id": row["source_run_id"],
        })
    return sorted(result, key=lambda item: (-item["score"], item["platform"], item["comment_id"]))


# ---------------------------------------------------------------------------
# CSV writers
# ---------------------------------------------------------------------------


FIELDS = [
    "platform", "channel_or_account", "content_id", "content_url", "comment_id",
    "comment_text", "comment_timestamp", "collected_at", "engagement_likes",
    "reply_count", "language", "author_hash", "parent_comment_id", "source_actor",
    "source_run_id",
]

PAIN_FIELDS = [
    "score", "categories", "platform", "comment_text", "engagement_likes",
    "reply_count", "content_url", "comment_id", "source_actor", "source_run_id",
]


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, rows: list[dict[str, Any]], pain_rows: list[dict[str, Any]]) -> None:
    counts = Counter(cat for row in pain_rows for cat in row["categories"].split("|") if cat)
    platforms = Counter(row["platform"] for row in rows)
    missing_urls = sum(not row["content_url"] for row in rows)
    lines = [
        "# Pain-Point Candidate Report", "",
        "## Fact", "",
        f"- Normalized unique comments: {len(rows)}",
        f"- Candidate comments: {len(pain_rows)}",
        f"- Missing content URL: {missing_urls}",
        f"- Platforms: {dict(platforms)}", "",
        "## Candidate categories", "",
    ]
    lines.extend(f"- {name}: {count}" for name, count in counts.most_common())
    lines.extend(["", "## Top source-backed candidates", ""])
    for row in pain_rows[:20]:
        excerpt = re.sub(r"\s+", " ", row["comment_text"]).strip()[:240]
        lines.extend([
            f"- Score {row['score']} | {row['platform']} | {row['categories']}",
            f"  - Evidence: \u201c{excerpt}\u201d",
            f"  - Source: {row['content_url'] or 'không có data'} | comment `{row['comment_id']}`",
        ])
    lines.extend([
        "", "## Inference", "",
        "- Categories are deterministic keyword/question matches, not verified audience intent.",
        "", "## Recommendation", "",
        "- content_bridge should cluster and review the top candidates before backlog promotion.",
        "- Human approval is required before Channel Brain, Sheet or publishing changes.",
        "", "## Missing Data", "",
        f"- Content URL missing in {missing_urls} normalized comments.",
        "- Actor fields absent from source exports remain blank; no values were invented.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to video inventory CSV")
    parser.add_argument("--output-dir", required=True, help="Output directory for results")
    parser.add_argument("--max-comments", type=int, default=DEFAULT_MAX_COMMENTS, help="Max comments per video")
    parser.add_argument("--max-videos", type=int, default=DEFAULT_MAX_VIDEOS, help="Max videos to scrape")
    parser.add_argument("--actor", default=APIFY_ACTOR, help="Apify actor ID")
    args = parser.parse_args()

    token = read_env_value("APIFY_TOKEN")
    if not token:
        print("ERROR: APIFY_TOKEN not found in env or .env files.", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    videos = load_video_ids(args.input, args.max_videos)
    if not videos:
        print("ERROR: No video IDs found in input CSV.", file=sys.stderr)
        return 3

    print(f"Loaded {len(videos)} videos from {args.input}")
    print(f"Apify actor: {args.actor}")
    print(f"Max comments per video: {args.max_comments}")
    print(f"Output dir: {output_dir}")
    print()

    all_raw_comments: list[dict[str, Any]] = []
    run_metadata = {
        "actor": args.actor,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "videos": [],
    }

    for i, video in enumerate(videos, 1):
        video_id = video["video_id"]
        video_url = video["url"]
        print(f"[{i}/{len(videos)}] Scraping: {video_id} — {video['title'][:60]}")

        try:
            # Start actor run
            run_data = start_actor_run(token, video_url, args.max_comments)
            run_id = run_data.get("data", {}).get("id", "")
            dataset_id = run_data.get("data", {}).get("defaultDatasetId", "")

            if not run_id or not dataset_id:
                print(f"  WARNING: No run_id or dataset_id returned. Skipping.")
                run_metadata["videos"].append({
                    "video_id": video_id,
                    "status": "error",
                    "error": "No run_id or dataset_id",
                })
                continue

            print(f"  Run ID: {run_id}")
            print(f"  Dataset ID: {dataset_id}")

            # Wait for completion
            final_run = wait_for_run(token, run_id)
            status = final_run.get("data", {}).get("status", "")

            if status != "SUCCEEDED":
                print(f"  WARNING: Run status = {status}. Skipping.")
                run_metadata["videos"].append({
                    "video_id": video_id,
                    "run_id": run_id,
                    "status": status,
                })
                continue

            # Fetch dataset
            comments = fetch_dataset(token, dataset_id)
            print(f"  Fetched {len(comments)} comments")

            # Tag comments with video metadata
            for c in comments:
                c["_video_id"] = video_id
                c["_video_title"] = video["title"]
                c["_video_channel"] = video["channel"]
                c["_video_views"] = video["views"]
                c["_video_comments"] = video["comments"]

            all_raw_comments.extend(comments)
            run_metadata["videos"].append({
                "video_id": video_id,
                "run_id": run_id,
                "dataset_id": dataset_id,
                "status": status,
                "comments_fetched": len(comments),
            })

        except Exception as e:
            print(f"  ERROR: {e}")
            run_metadata["videos"].append({
                "video_id": video_id,
                "status": "error",
                "error": str(e),
            })

        # Rate limit between videos
        if i < len(videos):
            time.sleep(2)

    # Save raw comments
    raw_path = output_dir / "raw_comments.json"
    raw_path.write_text(json.dumps(all_raw_comments, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {len(all_raw_comments)} raw comments to {raw_path}")

    # Normalize
    normalized = []
    for item in all_raw_comments:
        row = normalize_item(item, args.actor)
        if row:
            # Enrich with video metadata
            row["video_id"] = item.get("_video_id", "")
            row["video_title"] = item.get("_video_title", "")
            row["video_channel"] = item.get("_video_channel", "")
            row["video_views"] = item.get("_video_views", "")
            row["video_comments"] = item.get("_video_comments", "")
            normalized.append(row)

    normalized = dedupe(normalized)
    print(f"Normalized unique comments: {len(normalized)}")

    # Write normalized CSV
    norm_path = output_dir / "normalized_comments.csv"
    write_csv(norm_path, normalized, FIELDS + ["video_id", "video_title", "video_channel", "video_views", "video_comments"])
    print(f"Written {norm_path}")

    # Extract pain-points
    pain_rows = extract_painpoints(normalized)
    print(f"Pain-point candidates: {len(pain_rows)}")

    # Write pain-point CSV
    pain_path = output_dir / "painpoint_candidates.csv"
    write_csv(pain_path, pain_rows, PAIN_FIELDS)
    print(f"Written {pain_path}")

    # Write report
    report_path = output_dir / "painpoint_report.md"
    write_report(report_path, normalized, pain_rows)
    print(f"Written {report_path}")

    # Write run metadata
    run_metadata["finished_at"] = datetime.now(timezone.utc).isoformat()
    run_metadata["total_raw_comments"] = len(all_raw_comments)
    run_metadata["total_normalized"] = len(normalized)
    run_metadata["total_painpoint_candidates"] = len(pain_rows)
    meta_path = output_dir / "run_metadata.json"
    meta_path.write_text(json.dumps(run_metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Written {meta_path}")

    print(f"\n=== DONE ===")
    print(f"Total raw comments: {len(all_raw_comments)}")
    print(f"Normalized unique: {len(normalized)}")
    print(f"Pain-point candidates: {len(pain_rows)}")
    print(f"Output: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

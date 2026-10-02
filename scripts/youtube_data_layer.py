"""Build local YouTube data tables from YouTube Search API JSON exports."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from pathlib import Path
from typing import Iterable


VIDEO_INVENTORY_FIELDS = [
    "video_id",
    "channel",
    "channel_id",
    "title",
    "url",
    "format",
    "published_at",
    "duration_sec",
    "views",
    "likes",
    "comments",
    "like_rate",
    "comment_rate",
    "topic",
    "content_pillar",
    "offer_stage",
    "cta_type",
    "telegram_keyword",
    "source_file",
    "snapshot_at",
    "sync_hash",
    "notes",
]


REMAKE_CANDIDATE_FIELDS = [
    "candidate_id",
    "source_video_id",
    "source_channel",
    "source_url",
    "original_title",
    "reason",
    "evidence_metric",
    "views",
    "comments",
    "format",
    "remake_angle",
    "hook_test",
    "target_format",
    "priority_score",
    "offer_stage",
    "cta_type",
    "status",
    "assigned_to",
    "target_due_date",
    "output_short_id",
    "source_file",
    "sync_hash",
    "notes",
]


def load_search_file(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid JSON") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise ValueError(f"{path} is not a YouTube searchListResponse-like JSON file")
    return payload


def normalize_search_items(payload: dict, source_file: str, snapshot_at: str = "2026-09-29") -> list[dict]:
    rows: list[dict] = []
    for item in payload.get("items", []):
        item_id = item.get("id") or {}
        if item_id.get("kind") != "youtube#video":
            continue

        snippet = item.get("snippet") or {}
        video_id = str(item_id.get("videoId") or "").strip()
        if not video_id:
            continue

        title = clean_text(str(snippet.get("title") or ""))
        description = clean_text(str(snippet.get("description") or ""))
        channel = clean_text(str(snippet.get("channelTitle") or ""))
        fmt = classify_format(title, snippet.get("liveBroadcastContent"))

        row = {
            "video_id": video_id,
            "channel": channel,
            "channel_id": str(snippet.get("channelId") or "").strip(),
            "title": title,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "format": fmt,
            "published_at": str(snippet.get("publishedAt") or snippet.get("publishTime") or "").strip(),
            "duration_sec": "0",
            "views": "0",
            "likes": "0",
            "comments": "0",
            "like_rate": "0",
            "comment_rate": "0",
            "topic": classify_topic(title, description),
            "content_pillar": classify_content_pillar(title, description, fmt),
            "offer_stage": classify_offer_stage(title, description, fmt),
            "cta_type": "telegram" if "telegram" in description.lower() or "t.me/" in description.lower() else "subscribe",
            "telegram_keyword": keyword_for(title, fmt),
            "source_file": source_file,
            "snapshot_at": snapshot_at,
            "sync_hash": stable_hash(video_id, title, source_file),
            "notes": "Search export row; stats pending API enrichment",
        }
        rows.append(row)
    return rows


def clean_text(value: str) -> str:
    decoded = html.unescape(value)
    ascii_only = decoded.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_only).strip()


def classify_format(title: str, live_broadcast_content: object) -> str:
    lowered = title.lower()
    live_value = str(live_broadcast_content or "").lower()
    if live_value in {"live", "upcoming"} or "live" in lowered:
        return "live"
    if "#shorts" in lowered or "shorts" in lowered:
        return "short"
    return "video"


def classify_topic(title: str, description: str) -> str:
    text = f"{title} {description}".lower()
    if "xau" in text or "gold" in text:
        return "XAUUSD"
    if "forex" in text:
        return "Forex"
    return "Trading"


def classify_content_pillar(title: str, description: str, fmt: str) -> str:
    text = f"{title} {description}".lower()
    if fmt == "live":
        return "Live Proof"
    if "lesson" in text or "learn" in text or "strategy" in text:
        return "Lesson"
    if "mistake" in text or "lose" in text or "loss" in text:
        return "Mistake"
    return "Market Insight"


def classify_offer_stage(title: str, description: str, fmt: str) -> str:
    text = f"{title} {description}".lower()
    if "telegram" in text or "t.me/" in text or "join" in text:
        return "Lead Capture"
    if fmt == "live":
        return "Attraction"
    return "Attraction"


def keyword_for(title: str, fmt: str) -> str:
    text = title.lower()
    if fmt == "live":
        return "LIVE"
    if "lesson" in text or "strategy" in text:
        return "CHECKLIST"
    return "XAUUSD"


def build_remake_candidates(inventory_rows: Iterable[dict]) -> list[dict]:
    candidates: list[dict] = []
    for row in inventory_rows:
        if not should_consider_for_remake(row):
            continue

        candidate_id = f"RC-{len(candidates) + 1:03d}"
        fmt = row["format"]
        reason = "Competitor or live topic can be remade into a short lesson"
        angle = remake_angle_for(row)
        hook = hook_for(row)
        priority_score = priority_for(row)
        candidates.append(
            {
                "candidate_id": candidate_id,
                "source_video_id": row["video_id"],
                "source_channel": row["channel"],
                "source_url": row["url"],
                "original_title": row["title"],
                "reason": reason,
                "evidence_metric": "search_export_presence",
                "views": row["views"],
                "comments": row["comments"],
                "format": fmt,
                "remake_angle": angle,
                "hook_test": hook,
                "target_format": "short",
                "priority_score": str(priority_score),
                "offer_stage": row["offer_stage"],
                "cta_type": "telegram",
                "status": "Backlog",
                "assigned_to": "Content Bridge Agent",
                "target_due_date": "",
                "output_short_id": "",
                "source_file": row["source_file"],
                "sync_hash": stable_hash("remake", row["video_id"], row["title"]),
                "notes": "Seed candidate; enrich with views/comments when API stats are available",
            }
        )
    return candidates


def should_consider_for_remake(row: dict) -> bool:
    channel = row.get("channel", "").lower()
    return row.get("format") == "live" or "azzam master trading" not in channel


def remake_angle_for(row: dict) -> str:
    if row.get("format") == "live":
        return "Cut the live topic into one checklist-style XAUUSD short"
    return "Turn the topic into an Azzam proof/process short"


def hook_for(row: dict) -> str:
    topic = row.get("topic") or "trading"
    return f"Before you trade {topic}, check this first"


def priority_for(row: dict) -> int:
    score = 50
    if row.get("format") == "live":
        score += 20
    if row.get("topic") == "XAUUSD":
        score += 20
    if "azzam master trading" not in row.get("channel", "").lower():
        score += 10
    return min(score, 100)


def stable_hash(*parts: str) -> str:
    joined = "|".join(parts)
    return hashlib.sha1(joined.encode("utf-8")).hexdigest()[:12]


def build_outputs(search_files: Iterable[Path], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    inventory_rows: list[dict] = []
    seen_video_ids: set[str] = set()

    for search_file in search_files:
        payload = load_search_file(search_file)
        for row in normalize_search_items(payload, search_file.name):
            if row["video_id"] in seen_video_ids:
                continue
            seen_video_ids.add(row["video_id"])
            inventory_rows.append(row)

    inventory_rows.sort(key=lambda row: row["published_at"], reverse=True)
    remake_rows = build_remake_candidates(inventory_rows)

    inventory_path = output_dir / "video_inventory.csv"
    remake_path = output_dir / "remake_candidates.csv"
    write_csv(inventory_path, VIDEO_INVENTORY_FIELDS, inventory_rows)
    write_csv(remake_path, REMAKE_CANDIDATE_FIELDS, remake_rows)
    return inventory_path, remake_path


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Azzam YouTube data layer CSVs")
    parser.add_argument("search_files", nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    args = parser.parse_args()

    inventory_path, remake_path = build_outputs(args.search_files, args.output_dir)
    print(f"wrote {inventory_path}")
    print(f"wrote {remake_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

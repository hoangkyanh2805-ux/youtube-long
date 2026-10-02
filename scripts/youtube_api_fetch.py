"""Fetch public YouTube Data API stats for Azzam Phase 1."""

from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import date
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode
from urllib.request import urlopen


YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

CHANNEL_FIELDS = [
    "snapshot_at",
    "role",
    "channel_id",
    "channel_title",
    "subscriber_count",
    "view_count",
    "video_count",
]


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def resolve_config(root: Path) -> dict[str, str]:
    env_file = load_env_file(root / ".env")
    config = {
        "YT_API_KEY": os.environ.get("YT_API_KEY") or env_file.get("YT_API_KEY", ""),
        "YOUTUBE_CHANNEL_ID": os.environ.get("YOUTUBE_CHANNEL_ID")
        or env_file.get("YOUTUBE_CHANNEL_ID", "UCBZ7LaffmEPv91sWcfroJdQ"),
        "COMPETITOR_CHANNEL_ID": os.environ.get("COMPETITOR_CHANNEL_ID")
        or env_file.get("COMPETITOR_CHANNEL_ID", "UCdS8VXFlNvVohM09qzZGCkA"),
    }
    if not config["YT_API_KEY"] or config["YT_API_KEY"] == "your_youtube_api_key_here":
        raise RuntimeError("Missing YT_API_KEY. Put the real key in .env or environment variable.")
    return config


def youtube_get(resource: str, params: dict[str, str], api_key: str, opener=urlopen) -> dict:
    query = dict(params)
    query["key"] = api_key
    url = f"{YOUTUBE_API_BASE}/{resource}?{urlencode(query)}"
    with opener(url) as response:
        return json.loads(response.read().decode("utf-8"))


def chunked(items: list[str], size: int) -> Iterable[list[str]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def parse_iso8601_duration_seconds(value: str) -> int:
    if not value or not value.startswith("PT"):
        return 0
    value = value[2:]
    total = 0
    number = ""
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


def parse_video_stats(payload: dict) -> dict[str, dict[str, str]]:
    stats: dict[str, dict[str, str]] = {}
    for item in payload.get("items", []):
        item_stats = item.get("statistics", {})
        content_details = item.get("contentDetails", {})
        video_id = item.get("id", "")
        stats[video_id] = {
            "views": str(item_stats.get("viewCount", "0")),
            "likes": str(item_stats.get("likeCount", "0")),
            "comments": str(item_stats.get("commentCount", "0")),
            "duration_sec": str(parse_iso8601_duration_seconds(content_details.get("duration", ""))),
        }
    return stats


def parse_channel_stats(payload: dict, role: str, snapshot_at: str | None = None) -> list[dict]:
    snapshot = snapshot_at or date.today().isoformat()
    rows: list[dict] = []
    for item in payload.get("items", []):
        statistics = item.get("statistics", {})
        snippet = item.get("snippet", {})
        rows.append(
            {
                "snapshot_at": snapshot,
                "role": role,
                "channel_id": item.get("id", ""),
                "channel_title": snippet.get("title", ""),
                "subscriber_count": str(statistics.get("subscriberCount", "")),
                "view_count": str(statistics.get("viewCount", "")),
                "video_count": str(statistics.get("videoCount", "")),
            }
        )
    return rows


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def append_snapshot_rows(path: Path, fieldnames: list[str], rows: list[dict], unique_keys: list[str]) -> None:
    existing: list[dict] = []
    if path.exists():
        existing = read_csv(path)

    merged: dict[tuple[str, ...], dict] = {}
    order: list[tuple[str, ...]] = []
    for row in existing + rows:
        key = tuple(row.get(field, "") for field in unique_keys)
        if key not in merged:
            order.append(key)
        merged[key] = row

    write_csv(path, fieldnames, [merged[key] for key in order])


def enrich_inventory_rows(rows: list[dict], stats_by_video_id: dict[str, dict[str, str]]) -> list[dict]:
    enriched: list[dict] = []
    for row in rows:
        updated = dict(row)
        stats = stats_by_video_id.get(row.get("video_id", ""), {})
        for field in ["views", "likes", "comments", "duration_sec"]:
            if field in stats:
                updated[field] = stats[field]
        views = int(updated.get("views") or 0)
        likes = int(updated.get("likes") or 0)
        comments = int(updated.get("comments") or 0)
        updated["like_rate"] = f"{likes / views:.4f}" if views else "0"
        updated["comment_rate"] = f"{comments / views:.4f}" if views else "0"
        enriched.append(updated)
    return enriched


def fetch_video_stats(video_ids: list[str], api_key: str) -> dict[str, dict[str, str]]:
    stats: dict[str, dict[str, str]] = {}
    for batch in chunked(video_ids, 50):
        payload = youtube_get(
            "videos",
            {"part": "statistics,contentDetails", "id": ",".join(batch)},
            api_key,
        )
        stats.update(parse_video_stats(payload))
    return stats


def fetch_channel_rows(channel_roles: dict[str, str], api_key: str, snapshot_at: str) -> list[dict]:
    rows: list[dict] = []
    for role, channel_id in channel_roles.items():
        payload = youtube_get(
            "channels",
            {"part": "snippet,statistics", "id": channel_id},
            api_key,
        )
        rows.extend(parse_channel_stats(payload, role, snapshot_at=snapshot_at))
    return rows


def run_fetch(root: Path, snapshot_at: str) -> dict[str, Path]:
    config = resolve_config(root)
    input_path = root / "data" / "processed" / "video_inventory.csv"
    inventory_rows = read_csv(input_path)
    video_ids = [row["video_id"] for row in inventory_rows if row.get("video_id")]
    stats = fetch_video_stats(video_ids, config["YT_API_KEY"])
    enriched = enrich_inventory_rows(inventory_rows, stats)

    processed = root / "data" / "processed"
    api_inventory_path = processed / "video_inventory_api.csv"
    snapshots_path = processed / "video_snapshots.csv"
    snapshot_history_path = processed / "video_snapshots_history.csv"
    channels_path = processed / "channels.csv"
    channel_history_path = processed / "channel_snapshots.csv"
    fieldnames = list(enriched[0].keys()) if enriched else []
    if "snapshot_at" not in fieldnames:
        fieldnames.append("snapshot_at")
    write_csv(api_inventory_path, fieldnames, enriched)

    snapshot_rows = []
    for row in enriched:
        snapshot = dict(row)
        snapshot["snapshot_at"] = snapshot_at
        snapshot_rows.append(snapshot)
    write_csv(snapshots_path, fieldnames, snapshot_rows)
    append_snapshot_rows(snapshot_history_path, fieldnames, snapshot_rows, ["snapshot_at", "video_id"])

    channel_rows = fetch_channel_rows(
        {
            "self": config["YOUTUBE_CHANNEL_ID"],
            "competitor": config["COMPETITOR_CHANNEL_ID"],
        },
        config["YT_API_KEY"],
        snapshot_at,
    )
    write_csv(channels_path, CHANNEL_FIELDS, channel_rows)
    append_snapshot_rows(channel_history_path, CHANNEL_FIELDS, channel_rows, ["snapshot_at", "role", "channel_id"])
    return {
        "video_inventory_api": api_inventory_path,
        "video_snapshots": snapshots_path,
        "video_snapshots_history": snapshot_history_path,
        "channels": channels_path,
        "channel_snapshots": channel_history_path,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Azzam YouTube public API stats")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--check-key-only", action="store_true")
    args = parser.parse_args()

    if args.check_key_only:
        resolve_config(args.root)
        print("YT_API_KEY is configured")
        return 0

    outputs = run_fetch(args.root, args.date)
    for label, path in outputs.items():
        print(f"wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

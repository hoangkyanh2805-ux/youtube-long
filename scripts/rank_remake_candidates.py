"""Rank remake candidates using real YouTube API stats."""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.youtube_data_layer import REMAKE_CANDIDATE_FIELDS


def safe_int(value: str | None) -> int:
    try:
        return int(value or 0)
    except ValueError:
        return 0


def score_inventory_row(row: dict) -> int:
    views = safe_int(row.get("views"))
    comments = safe_int(row.get("comments"))
    score = 0
    score += min(views // 100, 60)
    score += min(comments * 2, 40)
    if row.get("format") == "live":
        score += 25
    if row.get("topic") == "XAUUSD":
        score += 15
    if "azzam master trading" not in (row.get("channel") or "").lower():
        score += 20
    return min(score, 150)


def build_ranked_candidates(inventory_rows: list[dict], limit: int | None = None) -> list[dict]:
    scored = [row for row in inventory_rows if should_rank(row)]
    scored.sort(key=score_inventory_row, reverse=True)
    if limit:
        scored = scored[:limit]

    candidates: list[dict] = []
    for index, row in enumerate(scored, start=1):
        candidate_id = f"RC-API-{index:03d}"
        candidates.append(
            {
                "candidate_id": candidate_id,
                "source_video_id": row.get("video_id", ""),
                "source_channel": row.get("channel", ""),
                "source_url": row.get("url", ""),
                "original_title": row.get("title", ""),
                "reason": reason_for(row),
                "evidence_metric": "youtube_api_views_comments",
                "views": row.get("views", "0"),
                "comments": row.get("comments", "0"),
                "format": row.get("format", ""),
                "remake_angle": remake_angle_for(row),
                "hook_test": hook_for(row),
                "target_format": "short",
                "priority_score": str(score_inventory_row(row)),
                "offer_stage": row.get("offer_stage", "Attraction"),
                "cta_type": "telegram",
                "status": "Backlog",
                "assigned_to": "Content Bridge Agent",
                "target_due_date": "",
                "output_short_id": "",
                "source_file": row.get("source_file", ""),
                "sync_hash": stable_hash("api-rank", row.get("video_id", ""), row.get("views", "")),
                "notes": "Ranked with real YouTube API views/comments",
            }
        )
    return candidates


def should_rank(row: dict) -> bool:
    views = safe_int(row.get("views"))
    if views <= 0:
        return False
    if row.get("format") == "live":
        return True
    return "azzam master trading" not in (row.get("channel") or "").lower()


def reason_for(row: dict) -> str:
    return (
        f"Real stats: {row.get('views', '0')} views and {row.get('comments', '0')} comments; "
        "use as evidence-backed remake input"
    )


def remake_angle_for(row: dict) -> str:
    if row.get("format") == "live":
        return "Cut the strongest live topic into one checklist-style XAUUSD short"
    return "Turn proven competitor topic into an Azzam proof/process short"


def hook_for(row: dict) -> str:
    if row.get("format") == "live":
        return "Before you follow a live XAUUSD setup, check these boxes"
    return "Before you trade XAUUSD, check this first"


def stable_hash(*parts: str) -> str:
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:12]


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REMAKE_CANDIDATE_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in REMAKE_CANDIDATE_FIELDS})


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank Azzam remake candidates from API inventory")
    parser.add_argument("--inventory", type=Path, default=Path("data/processed/video_inventory_api.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/remake_candidates_api.csv"))
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    rows = read_csv(args.inventory)
    candidates = build_ranked_candidates(rows, limit=args.limit)
    write_csv(args.output, candidates)
    print(f"wrote {args.output}")
    print(f"ranked {len(candidates)} candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

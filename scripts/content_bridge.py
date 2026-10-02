"""Generate draft content assets from Azzam remake candidates."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


SHORTS_PIPELINE_FIELDS = [
    "short_id",
    "source_type",
    "source_id",
    "title",
    "hook",
    "script",
    "visual_notes",
    "cta_type",
    "telegram_keyword",
    "offer_stage",
    "target_audience",
    "content_pillar",
    "status",
    "owner",
    "due_date",
    "published_at",
    "published_url",
    "views_24h",
    "comments_24h",
    "likes_24h",
    "telegram_leads",
    "subs_proxy",
    "review_status",
    "lesson_learned",
    "source_file",
    "sync_hash",
    "notes",
]


def load_candidates(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return sorted(rows, key=lambda row: int(row.get("priority_score") or 0), reverse=True)


def generate_short_rows(candidates: list[dict], limit: int = 10) -> list[dict]:
    rows: list[dict] = []
    for candidate in candidates[:limit]:
        title = make_short_title(candidate)
        hook = candidate.get("hook_test") or "Before you trade XAUUSD, check this first"
        rows.append(
            {
                "short_id": f"S-{candidate['candidate_id']}",
                "source_type": "Remake Candidate",
                "source_id": candidate["candidate_id"],
                "title": title,
                "hook": hook,
                "script": make_script(candidate, hook),
                "visual_notes": make_visual_notes(candidate),
                "cta_type": "comment_keyword",
                "telegram_keyword": "CHECKLIST",
                "offer_stage": candidate.get("offer_stage") or "Attraction",
                "target_audience": "XAUUSD beginner or losing trader",
                "content_pillar": "Live Proof" if candidate.get("format") == "live" else "Lesson",
                "status": "Backlog",
                "owner": "Content Bridge Agent",
                "due_date": "",
                "published_at": "",
                "published_url": "",
                "views_24h": "0",
                "comments_24h": "0",
                "likes_24h": "0",
                "telegram_leads": "0",
                "subs_proxy": "0",
                "review_status": "Needs human review",
                "lesson_learned": "",
                "source_file": candidate.get("source_file", ""),
                "sync_hash": candidate.get("sync_hash", ""),
                "notes": "Draft educational content only; no profit promise; human approval required",
            }
        )
    return rows


def make_short_title(candidate: dict) -> str:
    original = candidate.get("original_title", "XAUUSD setup")
    if "live" in original.lower():
        return "XAUUSD live checklist before entry"
    if "strategy" in original.lower():
        return "XAUUSD strategy checklist for safer entries"
    return "XAUUSD mistake to check before entry"


def make_script(candidate: dict, hook: str) -> str:
    source_title = candidate.get("original_title", "source topic")
    return (
        f"{hook}\n"
        f"1. Source topic: {source_title}.\n"
        "2. Mark bias, liquidity, entry trigger, invalidation, and risk before entry.\n"
        "3. If one box is missing, skip the trade and wait for confirmation.\n"
        "CTA: comment CHECKLIST to get the educational XAUUSD prep list on Telegram."
    )


def make_visual_notes(candidate: dict) -> str:
    return (
        "Screen-record chart replay; show checklist overlay: bias, liquidity, trigger, "
        "invalidation, risk. End with Telegram keyword card."
    )


def build_live_agenda(candidates: list[dict], limit: int = 3) -> str:
    live_candidates = [row for row in candidates if row.get("format") == "live"][:limit]
    lines = [
        "# Azzam Live Agenda Draft",
        "",
        "Status: draft, human review required before live.",
        "",
        "## Objective",
        "",
        "Turn recent XAUUSD live/remake topics into trust-building education and Shorts source material.",
        "",
        "## Agenda",
        "",
        "1. Market context and session risk.",
        "2. Bias, liquidity zones, and invalidation.",
        "3. Walk through one setup checklist without promising results.",
        "4. Answer one common pain point: why traders lose even with signals.",
        "5. CTA: comment or message CHECKLIST for the educational prep list.",
        "",
        "## Source Topics",
        "",
    ]
    for candidate in live_candidates:
        lines.append(
            f"- {candidate.get('candidate_id')}: {candidate.get('original_title')} "
            f"({candidate.get('source_url')})"
        )
    lines.extend(
        [
            "",
            "## Compliance Notes",
            "",
            "- Educational only.",
            "- No guaranteed profit claims.",
            "- Do not show private lead/account data.",
            "- Do not execute trades from the Telegram gateway.",
            "",
        ]
    )
    return "\n".join(lines)


def build_scripts_markdown(short_rows: list[dict]) -> str:
    lines = ["# Azzam Shorts Scripts Draft", "", "All scripts require human review before recording or publishing.", ""]
    for row in short_rows:
        lines.extend(
            [
                f"## {row['short_id']} - {row['title']}",
                "",
                f"Source: {row['source_id']}",
                f"Offer stage: {row['offer_stage']}",
                f"Telegram keyword: {row['telegram_keyword']}",
                "",
                "```text",
                row["script"],
                "```",
                "",
                f"Visual notes: {row['visual_notes']}",
                "",
            ]
        )
    return "\n".join(lines)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def build_content_outputs(
    candidate_path: Path,
    output_dir: Path,
    short_limit: int = 10,
    live_limit: int = 3,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates = load_candidates(candidate_path)
    short_rows = generate_short_rows(candidates, limit=short_limit)

    calendar_csv = output_dir / "content_calendar.csv"
    calendar_json = output_dir / "content_calendar.json"
    scripts_md = output_dir / "shorts_scripts.md"
    live_agenda_md = output_dir / "live_agenda.md"

    write_csv(calendar_csv, SHORTS_PIPELINE_FIELDS, short_rows)
    calendar_json.write_text(json.dumps(short_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    scripts_md.write_text(build_scripts_markdown(short_rows), encoding="utf-8")
    live_agenda_md.write_text(build_live_agenda(candidates, limit=live_limit), encoding="utf-8")

    return {
        "calendar_csv": calendar_csv,
        "calendar_json": calendar_json,
        "scripts_md": scripts_md,
        "live_agenda_md": live_agenda_md,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Azzam draft content assets")
    parser.add_argument("--candidates", type=Path, default=Path("data/processed/remake_candidates.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/content"))
    parser.add_argument("--short-limit", type=int, default=10)
    parser.add_argument("--live-limit", type=int, default=3)
    args = parser.parse_args()

    outputs = build_content_outputs(args.candidates, args.output_dir, args.short_limit, args.live_limit)
    for label, path in outputs.items():
        print(f"wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

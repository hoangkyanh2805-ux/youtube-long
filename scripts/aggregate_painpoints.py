"""
Aggregate pain-point candidate CSVs from multiple runs into one master file.

Deduplicates by comment_id + text, ranks by score, and adds a stable
painpoint_id plus a "reply_short_angle" column that turns each pain point
into a Shorts reply-comment angle.

Usage:
    python scripts/aggregate_painpoints.py \
        --input-dir outputs/painpoints \
        --output-dir outputs/painpoints/master

Output:
    outputs/painpoints/master/painpoints_master.csv
    outputs/painpoints/master/painpoints_master.md
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import sys

# Force UTF-8 console: without this, printing Vietnamese crashes with
# UnicodeEncodeError when stdout is a pipe (dagu/cron/CI).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402
ensure_utf8_console()

# ---------------------------------------------------------------------------
# Shorts reply-comment angle templates, keyed by pain-point category.
# These are draft angles for a human/Content Bridge to review — not final copy.
# ---------------------------------------------------------------------------

ANGLE_TEMPLATES = {
    "risk_management": "Short (trả lời comment): mở bằng “{excerpt}” → 3 bước quản lý vốn/stop loss cho XAUUSD.",
    "entry_timing": "Short (trả lời comment): “{excerpt}” → 3 điểm xác nhận trước khi vào lệnh, demo trên chart.",
    "strategy_rules": "Short (trả lời comment): “{excerpt}” → chiến lược này dùng khung nào, áp dụng ra sao trong 60 giây.",
    "broker_platform": "Short (trả lời comment): “{excerpt}” → spread/slippage/sàn cần kiểm tra gì trước khi chọn broker.",
    "psychology": "Short (trả lời comment): “{excerpt}” → cách lấy lại kỷ luật sau chuỗi thua, 1 phút thực hành.",
    "education_gap": "Short (trả lời comment): “{excerpt}” → giải thích cực gọn cho người mới trong 45 giây.",
    "other_question_or_pain": "Short (trả lời comment): “{excerpt}” → câu trả lời thẳng + 1 bước hành động ngay.",
}


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def norm_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True,
                        help="Directory containing per-run painpoint_candidates.csv files")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    candidate_files = sorted(args.input_dir.glob("*/painpoint_candidates.csv"))
    if not candidate_files:
        print(f"No painpoint_candidates.csv found under {args.input_dir}")
        return 1

    print(f"Found {len(candidate_files)} candidate files")
    merged: dict[str, dict[str, Any]] = {}
    seen_files = []

    for path in candidate_files:
        run_name = path.parent.name
        rows = read_csv(path)
        seen_files.append((run_name, len(rows)))
        for row in rows:
            text = (row.get("comment_text") or "").strip()
            if not text:
                continue
            key = hashlib.sha256(norm_text(text).encode("utf-8")).hexdigest()[:20]
            if key in merged:
                # keep the higher score
                try:
                    if float(row.get("score") or 0) > float(merged[key].get("score") or 0):
                        merged[key] = {**row, "_run": run_name}
                except ValueError:
                    pass
                continue
            merged[key] = {**row, "_run": run_name}

    # Rank by score desc
    def score_of(r: dict[str, Any]) -> float:
        try:
            return float(r.get("score") or 0)
        except ValueError:
            return 0.0

    rows = sorted(merged.values(), key=score_of, reverse=True)

    # Build master rows with painpoint_id + reply angle
    master: list[dict[str, Any]] = []
    for i, row in enumerate(rows, 1):
        cats = [c for c in (row.get("categories") or "").split("|") if c]
        primary = cats[0] if cats else "other_question_or_pain"
        excerpt = re.sub(r"\s+", " ", row.get("comment_text") or "").strip()
        template = ANGLE_TEMPLATES.get(primary, ANGLE_TEMPLATES["other_question_or_pain"])
        angle = template.format(topic=primary.replace("_", " "), excerpt=excerpt[:80])
        master.append({
            "painpoint_id": f"PP-{i:04d}",
            "score": row.get("score", ""),
            "categories": row.get("categories", ""),
            "primary_category": primary,
            "comment_text": excerpt,
            "engagement_likes": row.get("engagement_likes", ""),
            "reply_count": row.get("reply_count", ""),
            "content_url": row.get("content_url", ""),
            "comment_id": row.get("comment_id", ""),
            "reply_short_angle": angle,
            "source_run": row.get("_run", ""),
            "status": "Backlog",
        })

    args.output_dir.mkdir(parents=True, exist_ok=True)
    fields = ["painpoint_id", "score", "categories", "primary_category", "comment_text",
              "engagement_likes", "reply_count", "content_url", "comment_id",
              "reply_short_angle", "source_run", "status"]
    out_csv = args.output_dir / "painpoints_master.csv"
    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(master)
    print(f"Written {out_csv} ({len(master)} rows)")

    # Markdown summary
    cat_counts = Counter(r["primary_category"] for r in master)
    lines = [
        "# Pain Points Master — Nguyên liệu Shorts trả lời comment", "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Source runs: {len(candidate_files)}",
        f"- Total unique pain points: {len(master)}", "",
        "## Nguồn dữ liệu", "",
    ]
    lines.extend(f"- {name}: {n} candidates" for name, n in seen_files)
    lines.extend(["", "## Phân bố theo category", ""])
    lines.extend(f"- {name}: {n}" for name, n in cat_counts.most_common())
    lines.extend(["", "## Top 30 pain point + góc Short trả lời", ""])
    for r in master[:30]:
        lines.extend([
            f"### {r['painpoint_id']} — score {r['score']} ({r['primary_category']})",
            f"- Comment: “{r['comment_text'][:200]}”",
            f"- Nguồn: {r['content_url']}",
            f"- Góc Short: {r['reply_short_angle']}",
            "",
        ])
    out_md = args.output_dir / "painpoints_master.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Written {out_md}")

    print(f"\n=== DONE ===\nTotal unique pain points: {len(master)}")
    print("Categories:", dict(cat_counts.most_common()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

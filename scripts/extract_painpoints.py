"""Normalize Apify comment exports and extract source-backed pain-point candidates."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

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

# Spam / scam / self-promotion patterns — these are not audience pain points.
SPAM_PATTERNS = (
    "pay off my debt", "paying off my debt", "financial struggle",
    "investing in crypto", "bitcoin", "forex mentor", "dm me",
    "whatsapp", "telegram me", "join my", "signal group", "vip signal",
    "make $", "made $", "earn $", "passive income", "dm for",
    "click the link", "link in bio", "t.me/", "wa.me/",
    "crypto fearless", "garage full of", "lamborghini",
    "crypto market fundamentals", "sold a property", "stocks, i know",
)

# Trading-domain vocabulary. A candidate must be about trading to be useful
# as Shorts reply-comment material; generic education_gap matches ("how",
# "what") alone are not enough.
TRADING_DOMAIN = (
    "trade", "trading", "trader", "forex", "xauusd", "xau/usd", "gold",
    "chart", "candle", "candlestick", "price action", "support", "resistance",
    "entry", "stop loss", "take profit", "risk", "lot", "pip", "leverage",
    "indicator", "timeframe", "trend", "breakout", "retest", "liquidity",
    "scalp", "swing", "strategy", "setup", "signal", "broker", "spread",
    "mt4", "mt5", "tradingview", "profit", "loss", "drawdown", "backtest",
    "vàng", "lệnh", "chỉ báo", "chiến lược", "cắt lỗ", "vào lệnh",
)

FIELDS = [
    "platform", "channel_or_account", "content_id", "content_url", "comment_id",
    "comment_text", "comment_timestamp", "collected_at", "engagement_likes",
    "reply_count", "language", "author_hash", "parent_comment_id", "source_actor",
    "source_run_id",
]


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


def load_items(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    payload = json.loads(text)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("items", "data", "results"):
            if isinstance(payload.get(key), list):
                return payload[key]
        return [payload]
    raise ValueError("Expected a JSON object/list or JSONL records")


def dedupe(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    result = []
    for row in rows:
        key = (row["platform"], row["comment_id"], re.sub(r"\s+", " ", row["comment_text"].lower()).strip())
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result


def is_spam(text: str) -> bool:
    """Detect spam/scam/self-promotion comments that are not pain-point evidence."""
    lower = text.lower()
    if any(pattern in lower for pattern in SPAM_PATTERNS):
        return True
    # Pure emoji / punctuation / very short noise
    if len(re.sub(r"[^\w\s]", "", lower).strip()) < 3:
        return True
    return False


def is_trading_relevant(text: str) -> bool:
    """Reject generic non-trading noise while keeping real trading pain points.

    Generic question words ("how", "what", "why") are too broad on their own —
    they match comments on any viral video. So:
    - A specific category keyword (risk/entry/strategy/broker/psychology)
      already implies trading context and qualifies on its own.
    - education_gap / other_question_or_pain need actual trading vocabulary.
    """
    lower = text.lower()
    specific_categories = ("risk_management", "entry_timing", "strategy_rules",
                           "broker_platform", "psychology")
    if any(name in classify(text) for name in specific_categories):
        return True
    return any(term in lower for term in TRADING_DOMAIN)


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


def candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for row in rows:
        if is_spam(row["comment_text"]):
            continue
        if not is_trading_relevant(row["comment_text"]):
            continue
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
            f"  - Evidence: “{excerpt}”",
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


def run(input_path: Path, output_dir: Path, actor: str | None = None, run_id: str | None = None) -> tuple[int, int]:
    raw_items = load_items(input_path)
    rows = dedupe(row for item in raw_items if (row := normalize_item(item, actor, run_id)))
    pain_rows = candidates(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "normalized_comments.csv", rows, FIELDS)
    pain_fields = ["score", "categories", "platform", "comment_text", "engagement_likes", "reply_count", "content_url", "comment_id", "source_actor", "source_run_id"]
    write_csv(output_dir / "painpoint_candidates.csv", pain_rows, pain_fields)
    write_report(output_dir / "painpoint_report.md", rows, pain_rows)
    return len(rows), len(pain_rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--actor")
    parser.add_argument("--run-id")
    args = parser.parse_args()
    total, pain_total = run(args.input, args.output_dir, args.actor, args.run_id)
    print(f"normalized={total} painpoint_candidates={pain_total} output={args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

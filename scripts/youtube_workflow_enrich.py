"""Enrich remake candidates with YouTube transcript topic signals."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TRANSCRIPT_API_BASE = "https://transcriptapi.com/api/v2/youtube/transcript"

TRANSCRIPT_TOPIC_FIELDS = [
    "candidate_id",
    "source_video_id",
    "source_url",
    "transcript_status",
    "opening_hook",
    "pain_point",
    "setup_type",
    "proof_moment",
    "cta",
    "remake_note",
]


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def merged_env(root: Path) -> dict[str, str]:
    values = {key: value for key, value in os.environ.items() if value}
    values.update(load_env_file(root / ".env"))
    return values


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRANSCRIPT_TOPIC_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in TRANSCRIPT_TOPIC_FIELDS})


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    return [part.strip(" .!?") for part in re.split(r"(?<=[.!?])\s+", cleaned) if part.strip(" .!?")]


def is_filler_sentence(sentence: str) -> bool:
    if "[music]" in sentence.lower() or ">>" in sentence:
        trading_terms = {"xauusd", "entry", "risk", "invalidation", "liquidity", "bias", "setup"}
        if not any(term in sentence.lower() for term in trading_terms):
            return True
    normalized = re.sub(r"[^a-z0-9 ]", " ", sentence.lower())
    words = [word for word in normalized.split() if word]
    if len(words) < 5:
        return True
    filler = {"music", "hey", "heat", "hello", "okay", "ok", "um", "uh"}
    return all(word in filler for word in words)


def title_fallback_hook(source_title: str) -> str:
    title = source_title.lower()
    if "xauusd" in title and "live" in title:
        return "Before following a live XAUUSD setup, check the plan first"
    if "xauusd" in title:
        return "Before trading XAUUSD, check these risk boxes first"
    if "entry" in title:
        return "Before taking the entry, check what would make it wrong"
    return "Before copying a setup, check the plan first"


def extract_topic_signal(transcript_text: str, source_title: str = "") -> dict[str, str]:
    sentences = split_sentences(transcript_text)
    meaningful = [sentence for sentence in sentences if not is_filler_sentence(sentence)]
    opening_hook = meaningful[0] if meaningful else title_fallback_hook(source_title)
    lower = f"{transcript_text} {source_title}".lower()

    if "invalidation" in lower:
        pain_point = "Trader follows setup without clear invalidation"
    elif "risk" in lower:
        pain_point = "Trader enters without defining risk first"
    elif "live" in lower and "xauusd" in lower:
        pain_point = "Trader follows live setup without a written plan"
    elif "entry" in lower:
        pain_point = "Trader focuses on entry before checklist"
    else:
        pain_point = "Needs manual pain point review"

    setup_type = "XAUUSD live checklist" if "xauusd" in lower else "Trading checklist"
    cta = "CHECKLIST" if "checklist" in lower else ""
    proof_moment = next((sentence for sentence in sentences if "risk" in sentence.lower()), "")
    remake_note = "Turn transcript into checklist Short with educational CTA"

    return {
        "opening_hook": opening_hook,
        "pain_point": pain_point,
        "setup_type": setup_type,
        "proof_moment": proof_moment,
        "cta": cta,
        "remake_note": remake_note,
    }


def fetch_transcript(video_url: str, api_key: str) -> dict[str, str]:
    query = urlencode(
        {
            "video_url": video_url,
            "format": "json",
            "include_timestamp": "true",
            "send_metadata": "true",
        }
    )
    request = Request(f"{TRANSCRIPT_API_BASE}?{query}")
    request.add_header("Authorization", f"Bearer {api_key}")
    request.add_header("User-Agent", "CodexYouTubeWorkflow/1.0")
    request.add_header("Accept", "application/json")
    with urlopen(request) as response:
        payload = json.loads(response.read().decode("utf-8"))

    transcript_items = payload.get("transcript", [])
    transcript_text = " ".join(item.get("text", "") for item in transcript_items if isinstance(item, dict))
    metadata = payload.get("metadata", {}) or {}
    return {
        "transcript_text": transcript_text,
        "metadata_title": metadata.get("title", ""),
        "metadata_author": metadata.get("author_name", ""),
    }


def render_topic_briefs(rows: list[dict]) -> str:
    lines = ["# YouTube Workflow Topic Briefs", "", "Generated from TranscriptAPI enrichment.", ""]
    for row in rows:
        lines.extend(
            [
                f"## {row.get('candidate_id') or row.get('source_video_id')}",
                "",
                f"- Source: {row.get('source_url', '')}",
                f"- Status: {row.get('transcript_status', '')}",
                f"- Hook: {row.get('opening_hook', '')}",
                f"- Pain point: {row.get('pain_point', '')}",
                f"- Setup type: {row.get('setup_type', '')}",
                f"- Proof moment: {row.get('proof_moment', '')}",
                f"- CTA: {row.get('cta', '')}",
                f"- Remake note: {row.get('remake_note', '')}",
                "",
            ]
        )
    return "\n".join(lines)


def render_hook_library(rows: list[dict]) -> str:
    lines = ["# Hook Library", "", "| Hook | Source | CTA | Guardrail |", "|---|---|---|---|"]
    for row in rows:
        hook = row.get("opening_hook", "")
        if not hook:
            continue
        lines.append(
            f"| {hook} | {row.get('candidate_id') or row.get('source_video_id')} | "
            f"{row.get('cta', '')} | Educational only; no profit promise |"
        )
    return "\n".join(lines) + "\n"


def select_candidates(rows: list[dict], limit: int) -> list[dict]:
    def priority(row: dict) -> int:
        try:
            return int(row.get("priority_score") or 0)
        except ValueError:
            return 0

    return sorted(rows, key=priority, reverse=True)[:limit]


def enrich_candidates(
    root: Path,
    candidate_path: Path,
    api_key: str,
    limit: int = 5,
    fetch_func=fetch_transcript,
) -> dict[str, Path]:
    candidates = select_candidates(read_csv(candidate_path), limit)
    enriched: list[dict] = []

    for candidate in candidates:
        base = {
            "candidate_id": candidate.get("candidate_id", ""),
            "source_video_id": candidate.get("source_video_id", ""),
            "source_url": candidate.get("source_url", ""),
        }
        if not api_key:
            enriched.append({**base, "transcript_status": "missing_key", "remake_note": "Set TRANSCRIPT_API_KEY"})
            continue

        try:
            payload = fetch_func(candidate.get("source_url") or candidate.get("source_video_id", ""), api_key)
            signal = extract_topic_signal(
                payload.get("transcript_text", ""),
                source_title=payload.get("metadata_title") or candidate.get("original_title", ""),
            )
            enriched.append({**base, "transcript_status": "ok", **signal})
        except Exception as exc:  # API errors are recorded per candidate so the batch can continue.
            enriched.append({**base, "transcript_status": f"error:{type(exc).__name__}", "remake_note": "Review API error"})

    transcript_topics = root / "data" / "processed" / "transcript_topics.csv"
    topic_briefs = root / "outputs" / "youtube_workflow" / "topic_briefs.md"
    hook_library = root / "outputs" / "youtube_workflow" / "hook_library.md"
    write_csv(transcript_topics, enriched)
    topic_briefs.parent.mkdir(parents=True, exist_ok=True)
    topic_briefs.write_text(render_topic_briefs(enriched), encoding="utf-8")
    hook_library.write_text(render_hook_library(enriched), encoding="utf-8")
    return {"transcript_topics": transcript_topics, "topic_briefs": topic_briefs, "hook_library": hook_library}


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich YouTube remake candidates with transcript topic signals")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--candidates", type=Path, default=Path("data/processed/remake_candidates_api.csv"))
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    root = args.root.resolve()
    env = merged_env(root)
    outputs = enrich_candidates(
        root=root,
        candidate_path=root / args.candidates,
        api_key=env.get("TRANSCRIPT_API_KEY", ""),
        limit=args.limit,
    )
    for label, path in outputs.items():
        print(f"wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

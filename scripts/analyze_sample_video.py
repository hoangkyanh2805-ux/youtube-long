from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT = ROOT / "outputs" / "research" / "sample_AOz1YPOKvEs_transcript.json"
METADATA = ROOT / "outputs" / "research" / "sample_AOz1YPOKvEs_metadata.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> None:
    meta = load(METADATA)
    transcript_doc = load(TRANSCRIPT)
    transcript = transcript_doc.get("transcript") or []
    summary = {
        "metadata_keys": list(meta.keys())[:40],
        "title": meta.get("title") or (meta.get("details") or {}).get("title"),
        "author": meta.get("author_name") or (meta.get("details") or {}).get("author_name"),
        "duration": meta.get("duration") or (meta.get("details") or {}).get("duration"),
        "transcript_metadata": transcript_doc.get("metadata"),
        "segments": len(transcript),
        "first_35": [
            {"start": item.get("start"), "text": item.get("text")}
            for item in transcript[:35]
        ],
        "around_119s": [
            {"start": item.get("start"), "text": item.get("text")}
            for item in transcript
            if 100 <= float(item.get("start") or 0) <= 170
        ],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

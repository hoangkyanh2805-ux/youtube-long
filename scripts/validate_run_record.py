"""Validate workflow Run Records for the YouTube operating system."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Force UTF-8 console: without this, printing Vietnamese crashes with
# UnicodeEncodeError when stdout is a pipe (dagu/cron/CI).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402
ensure_utf8_console()

WORKFLOWS = {f"WF{i:02d}" for i in range(1, 8)}
AUTOMATION_LEVELS = {f"L{i}" for i in range(5)}
STATUSES = {
    "DRAFT",
    "READY",
    "RUNNING",
    "PENDING_APPROVAL",
    "COMPLETE",
    "MEASURED",
    "IMPROVED",
    "HOLD",
    "REJECTED",
}
APPROVAL_STATUSES = {"PENDING", "APPROVED", "NOT_REQUIRED", "REJECTED", "HOLD"}
FINAL_STATUSES = {"COMPLETE", "MEASURED", "IMPROVED"}
EMPTY_VALUES = {"", "TBD", "TODO", "N/A", "[NONE]", "[TBD]"}

REQUIRED_FIELDS = {
    "goal",
    "workflow",
    "automation level",
    "owner",
    "status",
    "inputs",
    "missing inputs",
    "tools allowed",
    "guardrail result",
    "human approval required",
    "human approval status",
    "output paths",
    "external action",
    "external action read-back",
    "feedback destination",
    "next owner/action",
}

RUN_FILENAME = re.compile(r"^RUN-\d{8}-WF0[1-7]-[a-z0-9][a-z0-9-]*\.md$")
FIELD_LINE = re.compile(r"^-\s+([^:]+):\s*(.*)$")


def parse_fields(text: str) -> dict[str, str]:
    """Parse top-level `- Label: value` fields from a Run Record."""
    fields: dict[str, str] = {}
    for line in text.splitlines():
        match = FIELD_LINE.match(line.strip())
        if not match:
            continue
        key = match.group(1).strip().lower()
        fields.setdefault(key, match.group(2).strip())
    return fields


def _is_blank(value: str | None) -> bool:
    if value is None:
        return True
    normalized = value.strip().upper()
    return normalized in EMPTY_VALUES or normalized.startswith("[")


def _enum_token(value: str) -> str:
    """Extract the enum token from a field value.

    Run Records legitimately annotate an enum with context, e.g.
    "COMPLETE (local artifacts only)" or "PENDING (chờ Alan review)".
    Take the token before the first bracket/parenthesis/dash so those
    annotations do not read as schema violations.
    """
    if not value:
        return ""
    head = re.split(r"[(\[\u2013\u2014]|\s+-\s+", value, maxsplit=1)[0]
    return head.strip().upper()


def validate_run_record(path: Path, *, enforce_filename: bool = True) -> list[str]:
    """Return validation errors for one Run Record."""
    errors: list[str] = []
    if not path.exists():
        return [f"missing file {path}"]
    if not path.is_file():
        return [f"not a file {path}"]
    if enforce_filename and not RUN_FILENAME.fullmatch(path.name):
        errors.append(
            "invalid filename; expected RUN-YYYYMMDD-WFNN-short-slug.md"
        )

    text = path.read_text(encoding="utf-8")
    fields = parse_fields(text)

    for field in sorted(REQUIRED_FIELDS):
        if field not in fields:
            errors.append(f"missing field: {field}")
        elif _is_blank(fields[field]):
            errors.append(f"blank or placeholder field: {field}")

    workflow = _enum_token(fields.get("workflow", ""))
    if workflow and workflow not in WORKFLOWS:
        errors.append(f"invalid workflow: {workflow}")

    level = _enum_token(fields.get("automation level", ""))
    if level and level not in AUTOMATION_LEVELS:
        errors.append(f"invalid automation level: {level}")

    status = _enum_token(fields.get("status", ""))
    if status and status not in STATUSES:
        errors.append(f"invalid status: {status}")

    approval_status = _enum_token(fields.get("human approval status", ""))
    if approval_status and approval_status not in APPROVAL_STATUSES:
        errors.append(f"invalid human approval status: {approval_status}")

    if level == "L3" and approval_status != "APPROVED":
        errors.append("L3 requires Human approval status: APPROVED")

    read_back = _enum_token(fields.get("external action read-back", ""))
    if level == "L3" and status in FINAL_STATUSES:
        if read_back in {"", "NOT_RUN", "PENDING", "N/A", "NONE"}:
            errors.append("completed L3 Run Record requires external action read-back evidence")

    if workflow and enforce_filename and f"-{workflow}-" not in path.name:
        errors.append(f"filename workflow does not match field: {workflow}")

    return errors


def discover_records(targets: list[Path]) -> list[Path]:
    """Expand files/directories into sorted Run Record paths."""
    records: list[Path] = []
    for target in targets:
        if target.is_dir():
            records.extend(sorted(target.glob("RUN-*.md")))
        else:
            records.append(target)
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate YouTube workflow Run Records")
    parser.add_argument(
        "targets",
        nargs="+",
        type=Path,
        help="Run Record file(s) or directories containing RUN-*.md",
    )
    args = parser.parse_args()

    # Run Record paths/filenames contain Vietnamese characters. When stdout is a
    # pipe (dagu, cron, CI) Python falls back to the Windows cp1252 codec and
    # crashes with UnicodeEncodeError, which aborts the whole workflow. Force
    # UTF-8 on the streams instead of losing the run.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    records = discover_records(args.targets)
    if not records:
        print("ERROR: no Run Records found")
        return 1

    failed = False
    for record in records:
        errors = validate_run_record(record)
        if errors:
            failed = True
            for error in errors:
                print(f"ERROR: {record}: {error}")
        else:
            print(f"VALID: {record}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

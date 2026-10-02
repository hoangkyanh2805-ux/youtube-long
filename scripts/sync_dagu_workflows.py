"""
Sync workflow YAML from dagu/ (source of truth) into the dagu home that the
UI actually reads (.dagu-local/dags/).

WHY THIS EXISTS
dagu's UI only lists DAGs found in its `dags` directory. This project keeps the
editable copies in `dagu/`, so a new workflow silently never appears in the UI
until it is copied. That happened with WF10/WF11/WF12 and the WF04 analytics
pair — the UI showed 7 workflows while 12 existed.

Run this after adding or editing anything in dagu/.

Usage:
    python scripts/sync_dagu_workflows.py            # copy + report
    python scripts/sync_dagu_workflows.py --check    # report only, exit 1 if drift
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dagu"
TARGET = ROOT / ".dagu-local" / "dags"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="Report drift only; exit 1 if out of sync")
    args = ap.parse_args()

    if not SOURCE.is_dir():
        print(f"ERROR: source dir missing: {SOURCE}", file=sys.stderr)
        return 2
    TARGET.mkdir(parents=True, exist_ok=True)

    copied, current, missing = [], [], []
    for src in sorted(SOURCE.glob("*.yaml")):
        dst = TARGET / src.name
        if not dst.exists():
            missing.append(src.name)
        elif src.read_bytes() == dst.read_bytes():
            current.append(src.name)
            continue
        if not args.check:
            shutil.copy2(src, dst)
        copied.append(src.name)

    # Files present in the UI dir but not in source. dagu writes its own
    # `example-*` DAGs into the home on first run — those are not drift, so
    # exclude them or every check reports a false positive.
    stale = [p.name for p in sorted(TARGET.glob("*.yaml"))
             if not (SOURCE / p.name).exists() and not p.name.startswith("example-")]

    print(f"source : {SOURCE}")
    print(f"target : {TARGET}")
    print(f"  in sync : {len(current)}")
    print(f"  {'would copy' if args.check else 'copied'}  : {len(copied)}")
    for n in copied:
        print(f"      + {n}")
    if stale:
        print(f"  stale in target (not in source): {len(stale)}")
        for n in stale:
            print(f"      ? {n}")

    if args.check and (copied or stale):
        print("\nOUT OF SYNC — run without --check to fix.")
        return 1
    print("\nOK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

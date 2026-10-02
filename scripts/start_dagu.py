"""
Start the dagu stack the way this project needs it.

WHY THIS SCRIPT EXISTS
`dagu --dagu-home <path>` does NOT redirect the data directory. Only the
DAGU_HOME environment variable does. Starting with the flag makes dagu use
~/AppData/Local/dagu for queue/state while reading DAGs from the project,
so runs sit in "queued" forever and never execute. This script sets the
environment variable instead, plus:

  DAGU_COORDINATOR_ENABLED=false
      The coordinator puts runs on a gRPC queue that needs a separate
      `dagu worker` process to dequeue. On a single machine that is pure
      overhead and a common source of stuck runs.

Usage:
    python scripts/start_dagu.py            # start in background
    python scripts/start_dagu.py --stop     # stop every dagu process
    python scripts/start_dagu.py --status   # report ports + running state
"""
from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
DAGU_HOME = ROOT / ".dagu-local"
UI_PORT = 8080
LOG = Path(os.environ.get("LOCALAPPDATA", str(ROOT))) / "Temp" / "dagu-start.log"


def port_open(port: int, host: str = "127.0.0.1") -> bool:
    s = socket.socket()
    s.settimeout(1)
    try:
        s.connect((host, port))
        return True
    except Exception:
        return False
    finally:
        s.close()


def dagu_pids() -> list[str]:
    try:
        out = subprocess.run(["tasklist"], capture_output=True, text=True,
                             timeout=20).stdout
    except Exception:
        return []
    pids = []
    for line in out.splitlines():
        if "dagu" in line.lower():
            parts = line.split()
            if len(parts) > 1 and parts[1].isdigit():
                pids.append(parts[1])
    return pids


def stop_all() -> int:
    pids = dagu_pids()
    if not pids:
        print("No dagu process running.")
        return 0
    for pid in pids:
        subprocess.run(["taskkill", "/F", "/PID", pid],
                       capture_output=True, timeout=20)
        print(f"  stopped PID {pid}")
    time.sleep(3)
    for lock in (DAGU_HOME / "data").rglob("*.lock"):
        try:
            lock.unlink()
        except OSError:
            pass
    print("Cleared lock files.")
    return 0


def status() -> int:
    running = port_open(UI_PORT)
    pids = dagu_pids()
    print(f"UI port {UI_PORT}: {'LISTENING' if running else 'closed'}")
    print(f"dagu processes: {len(pids)} {pids}")
    print(f"DAGU_HOME: {DAGU_HOME}")
    if running:
        print(f"\nOpen: http://127.0.0.1:{UI_PORT}")
    return 0 if running else 1


def resolve_dagu() -> str:
    """Locate the dagu executable.

    On Windows `dagu` is an npm shim (a shell/cmd script), which Popen cannot
    launch directly with shell=False. Prefer the real .exe that the npm package
    ships, then fall back to whatever is on PATH.
    """
    candidates = [
        Path.home() / "AppData/Roaming/npm/node_modules/@dagucloud/dagu/node_modules/"
        "@dagucloud/dagu-win32-x64/bin/dagu.exe",
        Path.home() / "AppData/Roaming/npm/dagu.cmd",
        Path.home() / "AppData/Roaming/npm/dagu",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return "dagu"


def start() -> int:
    if port_open(UI_PORT):
        print(f"UI already listening on {UI_PORT} — nothing to do.")
        return 0

    env = dict(os.environ)
    # The variable, not the flag, is what redirects dagu's data directory.
    env["DAGU_HOME"] = str(DAGU_HOME)
    env["DAGU_COORDINATOR_ENABLED"] = "false"

    exe = resolve_dagu()
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("w", encoding="utf-8") as fh:
        subprocess.Popen(
            [exe, "start-all"],
            env=env, stdout=fh, stderr=subprocess.STDOUT,
            cwd=str(ROOT), start_new_session=True,
        )

    for _ in range(30):
        time.sleep(1)
        if port_open(UI_PORT):
            print(f"dagu UI is up: http://127.0.0.1:{UI_PORT}")
            print(f"executable: {exe}")
            print(f"DAGU_HOME={DAGU_HOME}")
            print(f"log: {LOG}")
            return 0
    print("dagu did not start within 30s. Check the log:", LOG, file=sys.stderr)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--stop", action="store_true")
    g.add_argument("--status", action="store_true")
    args = ap.parse_args()

    if args.stop:
        return stop_all()
    if args.status:
        return status()
    return start()


if __name__ == "__main__":
    raise SystemExit(main())

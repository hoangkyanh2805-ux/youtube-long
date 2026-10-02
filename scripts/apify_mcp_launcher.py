"""Launch the official Apify MCP server without storing secrets in MCP config."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_ENV = Path.home() / "AppData/Local/hermes/profiles/youtube/.env"
ENV_FILES = (ROOT / ".env", PROFILE_ENV)
ACTORS = (
    "streamers/youtube-comments-scraper",
    "clockworks/tiktok-comments-scraper",
    "apify/instagram-comment-scraper",
    "apify/facebook-comments-scraper",
)


def read_env_value(path: Path, key: str) -> str | None:
    if not path.exists():
        return None
    for raw_line in path.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == key:
            return value.strip().strip('"').strip("'") or None
    return None


def resolve_token() -> str | None:
    token = os.environ.get("APIFY_TOKEN")
    if token:
        return token
    for env_file in ENV_FILES:
        token = read_env_value(env_file, "APIFY_TOKEN")
        if token:
            return token
    return None


def main() -> int:
    token = resolve_token()
    if not token:
        print(
            "APIFY_TOKEN is missing. Add it to the YouTube profile .env or project .env; "
            "never place it in MCP config or source files.",
            file=sys.stderr,
        )
        return 2

    npx = shutil.which("npx")
    if not npx:
        print("npx is not installed or not on PATH.", file=sys.stderr)
        return 3

    env = os.environ.copy()
    env["APIFY_TOKEN"] = token
    command = [
        npx,
        "-y",
        "@apify/actors-mcp-server",
        "--actors",
        ",".join(ACTORS),
        "--telemetry-enabled",
        "false",
        "--ui",
        "off",
    ]
    return subprocess.run(command, env=env, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())

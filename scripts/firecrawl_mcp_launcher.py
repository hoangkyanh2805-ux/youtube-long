#!/usr/bin/env python3
"""Launch the official Firecrawl MCP server without storing the key in MCP config.

Lý do có file này: `hermes config` lưu mcp_servers vào config.yaml — nếu nhét
FIRECRAWL_API_KEY thẳng vào `env:` của config thì key nằm trong file cấu hình
(không phải .env) và dễ bị commit/lộ. Launcher này đọc key từ .env rồi truyền
qua biến môi trường của tiến trình con, giống cách apify_mcp_launcher.py làm.

Cần: FIRECRAWL_API_KEY trong project .env hoặc profile .env.

Tools cung cấp (firecrawl-mcp):
    firecrawl_scrape            — scrape 1 URL → markdown/html
    firecrawl_map               — liệt kê URL trên site
    firecrawl_search            — search web + trả nội dung
    firecrawl_crawl             — crawl nhiều trang
    firecrawl_check_crawl_status
    firecrawl_extract           — trích dữ liệu có cấu trúc theo schema

Dùng cho dự án: lấy transcript/nội dung video, bài viết ngành trading,
trang broker/prop firm để làm nguyên liệu content (P02/P05).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_ENV = Path.home() / "AppData/Local/hermes/profiles/youtube/.env"
ENV_FILES = (ROOT / ".env", PROFILE_ENV)

KEY_NAME = "FIRECRAWL_API_KEY"


def read_env_value(path: Path, key: str) -> str | None:
    if not path.exists():
        return None
    # utf-8-sig: project .env có BOM, nếu đọc utf-8 thường thì key đầu tiên hỏng
    for raw_line in path.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == key:
            return value.strip().strip('"').strip("'") or None
    return None


def resolve_key() -> str | None:
    key = os.environ.get(KEY_NAME)
    if key:
        return key
    for env_file in ENV_FILES:
        key = read_env_value(env_file, KEY_NAME)
        if key:
            return key
    return None


def main() -> int:
    key = resolve_key()
    if not key:
        print(
            f"{KEY_NAME} is missing. Add it to the YouTube profile .env or project .env; "
            "never place it in MCP config or source files.",
            file=sys.stderr,
        )
        return 2

    npx = shutil.which("npx")
    if not npx:
        print("npx is not installed or not on PATH.", file=sys.stderr)
        return 3

    env = os.environ.copy()
    env[KEY_NAME] = key
    # Tắt telemetry của firecrawl-mcp
    env["FIRECRAWL_MCP_TELEMETRY"] = "0"

    command = [npx, "-y", "firecrawl-mcp@latest"]
    return subprocess.run(command, env=env, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())

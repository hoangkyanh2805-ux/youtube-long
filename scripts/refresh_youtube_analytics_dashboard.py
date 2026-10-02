from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "youtube-analytics-dashboard"
OUTPUT = ROOT / "outputs" / "dashboard" / "youtube-analytics-real.html"

# Kênh Azzam là **Brand Account**, không phải kênh cá nhân của tài khoản consent.
# `channel==MINE` sẽ trả về kênh cá nhân của tài khoản Google đã cấp quyền
# (số liệu hoàn toàn sai), nên phải chỉ định channel id tường minh.
CHANNEL_ID = "UCBZ7LaffmEPv91sWcfroJdQ"


def load_env_key() -> str | None:
    key = os.environ.get("YT_API_KEY", "").strip()
    if key:
        return key

    env_path = ROOT / ".env"
    if not env_path.exists():
        return None

    # utf-8-sig strips the leading BOM. The project .env starts with a BOM, so
    # reading it as plain utf-8 leaves "\ufeffYT_API_KEY" as the first key name
    # and the lookup below silently fails even though the key exists.
    for raw in env_path.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == "YT_API_KEY":
            return value.strip().strip('"').strip("'")
    return None


def run_step(label: str, args: list[str], env: dict[str, str]) -> None:
    print(f"==> {label}")
    subprocess.run(args, cwd=VENDOR, env=env, check=True)


def main() -> int:
    if not VENDOR.exists():
        print(f"Missing vendor dashboard: {VENDOR}", file=sys.stderr)
        return 1

    api_key = load_env_key()
    if not api_key:
        print("Missing YT_API_KEY in environment or root .env.", file=sys.stderr)
        return 2

    env = dict(os.environ)
    env["YT_API_KEY"] = api_key
    env["PYTHONUTF8"] = "1"

    run_step("Public YouTube Data API stats/comments", [sys.executable, "yt_stats.py"], env)

    has_client_secret = any(VENDOR.glob("client_secret*.json"))
    if has_client_secret:
        run_step("Private YouTube Analytics API OAuth",
                 [sys.executable, "yt_analytics.py", "--channel", CHANNEL_ID], env)
    else:
        print("==> Private YouTube Analytics API OAuth")
        print("SKIP: missing vendor/youtube-analytics-dashboard/client_secret*.json")

    run_step("Build dashboard", [sys.executable, "build_dashboard.py"], env)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(VENDOR / "dashboard.html", OUTPUT)
    print(f"Dashboard: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

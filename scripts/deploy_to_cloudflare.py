#!/usr/bin/env python3
"""Deploy dashboard lên Cloudflare Pages + verify domain.

Dùng cho WF23 (chạy sau khi build_report_hub + build_static_deploy).

Cần:
    CLOUDFLARE_API_TOKEN  — token có `Cloudflare Pages:Edit` + `User:Memberships:Read`
    CLOUDFLARE_ACCOUNT_ID — account id

Usage:
    python scripts/deploy_to_cloudflare.py              # dry-run (chỉ build)
    python scripts/deploy_to_cloudflare.py --apply      # deploy thật
    python scripts/deploy_to_cloudflare.py --status     # kiểm tra domain
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deploy"
PROJECT = "azzam-reports"
DOMAIN = "dashboard.azzamedu.com"
ACCOUNT = "0eb2f3d4cdb9f1d335ed2c7671b8eb2c"
TOKEN_FILE = ROOT / "secrets" / "cloudflare_token.txt"
SITE = f"https://{DOMAIN}"


def get_token() -> str:
    """Token từ env hoặc file (không hardcode trong script)."""
    t = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if t:
        return t
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text(encoding="utf-8").strip()
    return ""


def cf(path: str, token: str):
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4{path}",
        headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"_err": e.code, "_b": e.read().decode("utf-8", "replace")[:200]}


def check_status(token: str) -> int:
    d = cf(f"/accounts/{ACCOUNT}/pages/projects/{PROJECT}/domains/{DOMAIN}", token)
    res = d.get("result") or {}
    if not res:
        print(f"  ✗ Không đọc được domain: {d.get('_err')}")
        return 1
    print(f"  domain : {res.get('name')}")
    print(f"  status : {res.get('status')}")
    print(f"  verify : {res.get('verification_data', {}).get('status')}")
    print(f"  cert   : {res.get('validation_data', {}).get('status')}")

    # thử truy cập thật
    try:
        req = urllib.request.Request(SITE + "/", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            b = r.read()
        print(f"  live   : ✓ HTTP {r.status}, {len(b):,} B")
        return 0
    except Exception as e:
        print(f"  live   : ✗ {type(e).__name__}")
        return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="deploy thật")
    ap.add_argument("--status", action="store_true", help="chỉ kiểm tra")
    args = ap.parse_args()

    token = get_token()
    if not token:
        print("Thiếu CLOUDFLARE_API_TOKEN (env hoặc secrets/cloudflare_token.txt)",
              file=sys.stderr)
        return 1

    if args.status:
        return check_status(token)

    if not DEPLOY.exists():
        print(f"Thiếu {DEPLOY} — chạy scripts/build_static_deploy.py trước.",
              file=sys.stderr)
        return 1

    n = sum(1 for p in DEPLOY.rglob("*") if p.is_file())
    print(f"Package: {n} file, {sum(p.stat().st_size for p in DEPLOY.rglob('*') if p.is_file())/1024:,.0f} KB")

    if not args.apply:
        print("\n(dry-run — thêm --apply để deploy thật)")
        print(f"  Sẽ deploy lên project '{PROJECT}' → {SITE}")
        return 0

    env = dict(os.environ)
    env["CLOUDFLARE_API_TOKEN"] = token
    env["CLOUDFLARE_ACCOUNT_ID"] = ACCOUNT

    # Trên Windows, `npx` là file .cmd → subprocess với shell=False báo
    # WinError 2 khi chạy từ dagu/cron (PATH khác). Gọi trực tiếp qua npx.cmd
    # KHÔNG bọc quote (cmd /c tự xử lý); truyền từng arg riêng để tránh lỗi quoting.
    npx = shutil.which("npx") or "npx"
    if os.name == "nt":
        argv = [npx, "--yes", "wrangler@latest", "pages", "deploy", "deploy",
                "--project-name", PROJECT, "--commit-dirty=true"]
        use_shell = True   # cần shell để cmd.exe chạy được file .cmd
    else:
        argv = [npx, "--yes", "wrangler@latest", "pages", "deploy", "deploy",
                "--project-name", PROJECT, "--commit-dirty=true"]
        use_shell = False

    print(f"\n▶ Deploy lên Cloudflare Pages…")
    # LƯU Ý Windows: KHÔNG dùng text=True — Python fallback sang cp1252 và crash
    # với UnicodeDecodeError khi wrangler in ký tự Unicode (✨ 🌎). Đọc bytes rồi
    # tự decode utf-8 errors=replace. Cũng tránh p.stdout=None khi có lỗi.
    p = subprocess.run(argv, cwd=str(ROOT), env=env, shell=use_shell,
                       capture_output=True, timeout=600)
    out = ((p.stdout or b"") + (p.stderr or b"")).decode("utf-8", errors="replace")
    for line in out.splitlines():
        if any(k in line for k in ("Uploading", "Success", "Deploying",
                                   "complete", "ERROR", "pages.dev")):
            print("  " + line.strip()[:110])

    if p.returncode != 0:
        print(f"\n✗ Deploy thất bại (exit {p.returncode})")
        return 1

    print(f"\n✓ Deploy xong — verify:")
    return check_status(token)


if __name__ == "__main__":
    raise SystemExit(main())

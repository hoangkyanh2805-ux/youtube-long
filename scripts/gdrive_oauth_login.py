#!/usr/bin/env python3
"""OAuth login cho Google Drive — upload file bằng token của CHÍNH user.

Vì sao cần script riêng: **service account không có dung lượng Drive**
(`Service Accounts do not have storage quota`). File do SA tạo không thuộc
ai → Google chặn. Muốn upload vào Drive cá nhân phải dùng OAuth token của
chính tài khoản sở hữu Drive đó.

Dùng cùng `client_secret.json` (OAuth Desktop client) như dashboard.

Cách dùng:
    python scripts/gdrive_oauth_login.py            # consent, lưu token
    python scripts/gdrive_oauth_login.py --check    # kiểm tra token còn hạn
"""
from __future__ import annotations

import argparse
import http.server
import json
import os
import secrets
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "vendor" / "youtube-analytics-dashboard"
CLIENT_SECRET = DASH / "client_secret.json"
TOKEN_PATH = ROOT / "secrets" / "gdrive_token.json"

AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/drive"
REDIRECT_HOST = "127.0.0.1"
DEFAULT_EMAIL = "hoang.kyanh2805@gmail.com"


def load_client():
    if not CLIENT_SECRET.exists():
        sys.exit(f"Thiếu {CLIENT_SECRET} — cần OAuth Desktop client.")
    d = json.loads(CLIENT_SECRET.read_text(encoding="utf-8"))
    node = d.get("installed") or d.get("web")
    if not node:
        sys.exit("client_secret.json thiếu block 'installed'/'web'.")
    return node["client_id"], node["client_secret"]


class _H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        p = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        self.server.code = p.get("code", [None])[0]
        self.server.state = p.get("state", [None])[0]
        self.server.err = p.get("error", [None])[0]
        ok = self.server.code is not None
        msg = ("Authorized. Bạn có thể đóng tab này." if ok
               else f"Failed: {self.server.err or 'no code'}")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(f"<html><body><h3>{msg}</h3></body></html>".encode())

    def log_message(self, *a):
        pass


def run_flow(cid, csec, email):
    srv = http.server.HTTPServer((REDIRECT_HOST, 0), _H)
    srv.code = srv.state = srv.err = None
    port = srv.server_address[1]
    redirect = f"http://{REDIRECT_HOST}:{port}/"
    state = secrets.token_urlsafe(16)
    params = {
        "client_id": cid, "redirect_uri": redirect, "response_type": "code",
        "scope": SCOPE, "state": state, "access_type": "offline",
        "prompt": "consent",
    }
    if email:
        params["login_hint"] = email
    url = f"{AUTH_URI}?" + urllib.parse.urlencode(params)
    print("Mở browser cấp quyền Google Drive...")
    print(f"Nếu không tự mở:\n  {url}\n")
    webbrowser.open(url)
    t = threading.Thread(target=srv.handle_request)
    t.start()
    t.join(timeout=300)
    srv.server_close()
    if srv.err:
        sys.exit(f"Google trả lỗi: {srv.err}")
    if not srv.code:
        sys.exit("Không nhận được code (timeout 300s).")
    if srv.state != state:
        sys.exit("OAuth state mismatch — dừng.")
    req = urllib.request.Request(
        TOKEN_URI,
        data=urllib.parse.urlencode({
            "code": srv.code, "client_id": cid, "client_secret": csec,
            "redirect_uri": redirect, "grant_type": "authorization_code",
        }).encode())
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def refresh(token_path: Path):
    cid, csec = load_client()
    tok = json.loads(token_path.read_text(encoding="utf-8"))
    req = urllib.request.Request(
        TOKEN_URI,
        data=urllib.parse.urlencode({
            "client_id": cid, "client_secret": csec,
            "refresh_token": tok["refresh_token"], "grant_type": "refresh_token",
        }).encode())
    with urllib.request.urlopen(req, timeout=30) as r:
        fresh = json.load(r)
    fresh.setdefault("refresh_token", tok["refresh_token"])
    return fresh["access_token"]


def whoami(token):
    req = urllib.request.Request(
        "https://www.googleapis.com/drive/v3/about?fields=user",
        headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            u = json.load(r).get("user", {})
        return f"{u.get('emailAddress')} ({u.get('displayName')})"
    except Exception as e:
        return f"(không đọc được: {e})"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--email", default=DEFAULT_EMAIL)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if args.check:
        if not TOKEN_PATH.exists():
            print("Chưa có token. Chạy: python scripts/gdrive_oauth_login.py")
            return 1
        try:
            tok = refresh(TOKEN_PATH)
            print("✓ Token còn hiệu lực")
            print("  account:", whoami(tok))
            return 0
        except urllib.error.HTTPError as e:
            print(f"✗ Token hết hạn/không hợp lệ (HTTP {e.code}) — cần login lại.")
            return 1

    cid, csec = load_client()
    tok = run_flow(cid, csec, args.email)
    if not tok.get("refresh_token"):
        sys.exit("Không nhận được refresh_token — chạy lại.")
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(json.dumps(tok, indent=2), encoding="utf-8")
    try:
        os.chmod(TOKEN_PATH, 0o600)
    except OSError:
        pass
    print(f"\n✓ Đã lưu {TOKEN_PATH}")
    print("  account:", whoami(tok["access_token"]))
    print("  scope  :", SCOPE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

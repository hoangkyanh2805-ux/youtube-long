#!/usr/bin/env python3
"""OAuth login cho YouTube Analytics dashboard, có login_hint.

Khác với yt_analytics.py gốc (không hỗ trợ login_hint), script này ghim sẵn
tài khoản Google chủ kênh để Google không tự chọn nhầm khi browser đang
đăng nhập nhiều tài khoản.

Cách dùng:
    python scripts/yt_oauth_login.py                      # dùng email mặc định
    python scripts/yt_oauth_login.py --email a@b.com      # ghim email khác
    python scripts/yt_oauth_login.py --check              # chỉ kiểm tra token hiện có

Ghi token.json vào vendor/youtube-analytics-dashboard/ (chmod 600).
"""
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

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASH = os.path.join(REPO, "vendor", "youtube-analytics-dashboard")
CLIENT_SECRET = os.path.join(DASH, "client_secret.json")
TOKEN_PATH = os.path.join(DASH, "token.json")

AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/yt-analytics.readonly"
REDIRECT_HOST = "127.0.0.1"
DEFAULT_EMAIL = "hoang.kyanh2805@gmail.com"
# Kênh Azzam là Brand Account → verify phải so MINE với id tường minh.
DEFAULT_CHANNEL_ID = "UCBZ7LaffmEPv91sWcfroJdQ"


def load_client():
    if not os.path.exists(CLIENT_SECRET):
        sys.exit(f"Missing {CLIENT_SECRET} — tải OAuth Desktop client từ Google Cloud Console.")
    with open(CLIENT_SECRET, encoding="utf-8") as fh:
        data = json.load(fh)
    node = data.get("installed") or data.get("web")
    if not node:
        sys.exit("client_secret.json thiếu block 'installed'/'web'.")
    return node["client_id"], node["client_secret"]


class _CodeHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        self.server.auth_code = params.get("code", [None])[0]
        self.server.auth_state = params.get("state", [None])[0]
        self.server.auth_error = params.get("error", [None])[0]
        ok = self.server.auth_code is not None
        if ok:
            msg = "Authorized. Bạn có thể đóng tab này."
        elif self.server.auth_error:
            msg = f"Authorization failed: {self.server.auth_error}"
        else:
            msg = "Authorization failed."
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(f"<html><body><h3>{msg}</h3></body></html>".encode())

    def log_message(self, *args):
        pass


def run_flow(client_id, client_secret, email):
    server = http.server.HTTPServer((REDIRECT_HOST, 0), _CodeHandler)
    server.auth_code = server.auth_state = server.auth_error = None
    port = server.server_address[1]
    redirect_uri = f"http://{REDIRECT_HOST}:{port}/"
    state = secrets.token_urlsafe(16)

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": SCOPE,
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    if email:
        # Gim tài khoản: Google bỏ qua bước chọn account, tránh chọn nhầm.
        params["login_hint"] = email

    auth_url = f"{AUTH_URI}?" + urllib.parse.urlencode(params)
    print("Mở browser để cấp quyền...")
    print(f"Nếu không tự mở, truy cập:\n  {auth_url}\n")
    webbrowser.open(auth_url)

    t = threading.Thread(target=server.handle_request)
    t.start()
    t.join(timeout=300)
    server.server_close()

    if server.auth_error:
        sys.exit(f"Google trả lỗi: {server.auth_error}")
    if not server.auth_code:
        sys.exit("Không nhận được authorization code (timeout 300s?).")
    if server.auth_state != state:
        sys.exit("OAuth state mismatch — dừng để an toàn.")

    req = urllib.request.Request(
        TOKEN_URI,
        data=urllib.parse.urlencode({
            "code": server.auth_code, "client_id": client_id,
            "client_secret": client_secret, "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }).encode(),
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def whoami(access_token):
    """Xác định token đang trỏ tới kênh nào.

    KHÔNG dùng oauth2/v2/userinfo: scope `yt-analytics.readonly` không bao gồm
    openid/email nên endpoint đó luôn trả 401 — không phải lỗi token.

    Thay vào đó so `channel==MINE` với channel id tường minh. Đây chính là phép
    kiểm bắt được bẫy Brand Account: nếu MINE trả số liệu khác hẳn kênh đích thì
    consent đang trỏ sai kênh (kênh cá nhân thay vì Brand Account).
    """
    import datetime as _dt

    end = _dt.date.today() - _dt.timedelta(days=2)
    start = end - _dt.timedelta(days=28)
    ids = [("MINE", "channel==MINE")]
    if DEFAULT_CHANNEL_ID:
        ids.append((f"kênh đích {DEFAULT_CHANNEL_ID[:12]}…",
                    f"channel=={DEFAULT_CHANNEL_ID}"))

    out = []
    for label, cid in ids:
        q = urllib.parse.urlencode({
            "ids": cid, "startDate": start.isoformat(), "endDate": end.isoformat(),
            "metrics": "views",
        })
        req = urllib.request.Request(
            f"https://youtubeanalytics.googleapis.com/v2/reports?{q}",
            headers={"Authorization": f"Bearer {access_token}"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                rows = json.load(r).get("rows") or [[0]]
            out.append(f"{label}: {rows[0][0]:,} views/28d")
        except Exception as e:
            out.append(f"{label}: lỗi {e}")

    result = " | ".join(out)
    if len(out) > 1 and DEFAULT_CHANNEL_ID:
        try:
            mine = int(out[0].split(":")[1].strip().split()[0].replace(",", ""))
            tgt = int(out[1].split(":")[1].strip().split()[0].replace(",", ""))
            if mine != tgt:
                result += ("\n  ⚠ MINE ≠ kênh đích → consent đang trỏ kênh cá nhân, "
                           "KHÔNG phải Brand Account. Luôn dùng --channel <UC...>.")
        except (ValueError, IndexError):
            pass
    return result


def check_existing():
    if not os.path.exists(TOKEN_PATH):
        print("Chưa có token.json — cần chạy login.")
        return False
    with open(TOKEN_PATH, encoding="utf-8") as fh:
        tok = json.load(fh)
    if not tok.get("refresh_token"):
        print("token.json không có refresh_token — cần login lại.")
        return False
    cid, csec = load_client()
    req = urllib.request.Request(
        TOKEN_URI,
        data=urllib.parse.urlencode({
            "client_id": cid, "client_secret": csec,
            "refresh_token": tok["refresh_token"], "grant_type": "refresh_token",
        }).encode(),
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            fresh = json.load(resp)
        print("✓ Refresh token còn hiệu lực — không cần login lại.")
        print("  account:", whoami(fresh["access_token"]))
        return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:200]
        print(f"✗ Refresh token hết hạn/không hợp lệ (HTTP {e.code}): {body}")
        print("  → cần login lại (app ở trạng thái Testing thì token hết hạn sau 7 ngày).")
        return False


def main():
    ap = argparse.ArgumentParser(description="OAuth login cho YouTube Analytics dashboard.")
    ap.add_argument("--email", default=DEFAULT_EMAIL,
                    help=f"tài khoản Google chủ kênh (mặc định {DEFAULT_EMAIL})")
    ap.add_argument("--check", action="store_true", help="chỉ kiểm tra token hiện có")
    args = ap.parse_args()

    if args.check:
        sys.exit(0 if check_existing() else 1)

    client_id, client_secret = load_client()
    token = run_flow(client_id, client_secret, args.email)

    if not token.get("refresh_token"):
        sys.exit("Không nhận được refresh_token — chạy lại với prompt=consent.")

    os.makedirs(DASH, exist_ok=True)
    with open(TOKEN_PATH, "w", encoding="utf-8") as fh:
        json.dump(token, fh, indent=2)
    try:
        os.chmod(TOKEN_PATH, 0o600)
    except OSError:
        pass

    print(f"\n✓ Đã lưu {TOKEN_PATH}")
    print("  Tài khoản cấp quyền:", whoami(token["access_token"]))
    print("  Scope:", SCOPE)


if __name__ == "__main__":
    main()

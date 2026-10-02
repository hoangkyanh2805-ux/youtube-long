#!/usr/bin/env python3
"""HTTP server cho dashboard + tải báo cáo — phục vụ team online.

Khác `python -m http.server` ở chỗ:
  /                      → thư mục outputs/dashboard (HTML xem trực tiếp)
  /download/<path>       → tải file bất kỳ trong repo (docx, xlsx, csv, json, md)
  /api/status            → JSON trạng thái dữ liệu (để dashboard poll)

Bảo mật: chỉ phục vụ file nằm trong repo, chặn path traversal, chặn mọi file
khớp pattern secret (.env, token.json, client_secret*, secrets/).

Usage:
    python scripts/dashboard_server.py --port 8899
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import socket
import sys
from datetime import datetime
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "outputs" / "dashboard"

# Chặn tuyệt đối — không bao giờ phục vụ những file này
BLOCK_PATTERNS = (".env", "token.json", "client_secret", "secrets",
                  ".git-credentials", "id_rsa", ".bak")


def is_blocked(p: Path) -> bool:
    s = str(p).lower()
    return any(b in s for b in BLOCK_PATTERNS)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, directory=None, **kw):
        super().__init__(*a, directory=str(directory), **kw)

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        path = unquote(urlparse(self.path).path)

        # API trạng thái
        if path == "/api/status":
            an = ROOT / "vendor/youtube-analytics-dashboard/analytics_latest.json"
            data = {"ok": True, "time": datetime.now().isoformat(timespec="seconds")}
            if an.exists():
                try:
                    m = json.loads(an.read_text(encoding="utf-8")).get("metrics", {})
                    data["views"] = m.get("views")
                    data["watch_min"] = m.get("estimatedMinutesWatched")
                except Exception:
                    pass
            self._send(200, json.dumps(data, ensure_ascii=False).encode(),
                       "application/json; charset=utf-8")
            return

        # Tải file báo cáo
        if path.startswith("/download/"):
            rel = path[len("/download/"):]
            target = (ROOT / rel).resolve()
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                self._send(403, b"forbidden", "text/plain")
                return
            if is_blocked(target) or not target.is_file():
                self._send(404, b"not found", "text/plain")
                return
            ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
            # ép tải về cho file không hiển thị được trên browser
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(target.stat().st_size))
            if target.suffix.lower() in (".docx", ".xlsx", ".csv", ".json", ".md"):
                self.send_header("Content-Disposition",
                                 f'attachment; filename="{target.name}"')
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            with target.open("rb") as f:
                while chunk := f.read(64 * 1024):
                    self.wfile.write(chunk)
            return

        # Dashboard mặc định
        if path in ("/", ""):
            self.path = "/REPORT_HUB.html"
        return super().do_GET()

    def do_HEAD(self):  # noqa: N802
        return self.do_GET()

    def log_message(self, fmt, *args):
        # gọn log, bỏ request 200 cho file tĩnh để đỡ rối
        if args and str(args[1]).startswith("2"):
            return
        sys.stderr.write(f"  {self.address_string()} {fmt % args}\n")


def lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8899)
    ap.add_argument("--host", default="0.0.0.0")
    args = ap.parse_args()

    if not DASH.exists():
        print(f"Thiếu {DASH} — chạy scripts/build_report_hub.py trước.", file=sys.stderr)
        return 1

    h = partial(Handler, directory=DASH)
    srv = ThreadingHTTPServer((args.host, args.port), h)
    srv.daemon_threads = True
    ip = lan_ip()
    print(f"Dashboard server → http://127.0.0.1:{args.port}/REPORT_HUB.html")
    print(f"LAN              → http://{ip}:{args.port}/REPORT_HUB.html")
    print(f"Tải báo cáo      → /download/outputs/reports/<file>")
    print("Ctrl+C để dừng.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nDừng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

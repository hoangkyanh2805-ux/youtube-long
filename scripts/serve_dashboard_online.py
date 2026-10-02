#!/usr/bin/env python3
"""Host dashboard HTML online cho team — không cần account, không cần cài gì thêm.

Vấn đề: file:// chỉ mở được trên máy này. Team ở xa không mở được.

Giải pháp: serve thư mục dashboard qua HTTP nội bộ + mở public URL bằng
Cloudflare Tunnel (không cần account, không cần domain).

    python scripts/serve_dashboard_online.py            # mở public URL
    python scripts/serve_dashboard_online.py --lan      # chỉ LAN (nhanh hơn)
    python scripts/serve_dashboard_online.py --status   # kiểm tra đang chạy
    python scripts/serve_dashboard_online.py --stop

Public URL dạng https://<random>.trycloudflare.com — gửi link này cho team.
URL sống đến khi script dừng. Muốn URL cố định thì cần domain + Cloudflare account.

Usage:
    python scripts/serve_dashboard_online.py
"""
from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "outputs" / "dashboard"
CF = ROOT / "tools" / "cloudflared" / "cloudflared.exe"
PID_FILE = ROOT / ".dashboard_serve.json"

PORT = 8899


def port_open(port: int, host="127.0.0.1") -> bool:
    s = socket.socket()
    s.settimeout(1)
    try:
        s.connect((host, port))
        return True
    except Exception:
        return False
    finally:
        s.close()


def lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def read_state() -> dict:
    if PID_FILE.exists():
        try:
            return json.loads(PID_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def status() -> int:
    st = read_state()
    if not st:
        print("Chưa chạy. Khởi động: python scripts/serve_dashboard_online.py")
        return 1
    alive = []
    for k, pid in (st.get("pids") or {}).items():
        r = subprocess.run(f'tasklist /FI "PID eq {pid}" 2>nul',
                           shell=True, capture_output=True, text=True)
        ok = str(pid) in (r.stdout or "")
        alive.append(f"{k}={'chạy' if ok else 'đã dừng'} (pid {pid})")
    print("Trạng thái:", " | ".join(alive))
    print("HTTP  :", "mở" if port_open(PORT) else "đóng", f"(port {PORT})")
    if st.get("public_url"):
        print("Public:", st["public_url"])
    if st.get("lan_url"):
        print("LAN   :", st["lan_url"])
    print("Local :", f"http://127.0.0.1:{PORT}/REPORT_HUB.html")
    return 0


def stop() -> int:
    st = read_state()
    for k, pid in (st.get("pids") or {}).items():
        r = subprocess.run(f"taskkill /F /PID {pid} 2>&1",
                           shell=True, capture_output=True, text=True)
        print(f"  dừng {k} (pid {pid}): {'OK' if r.returncode == 0 else 'đã dừng rồi'}")
    if PID_FILE.exists():
        PID_FILE.unlink()
    print("Đã dừng.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lan", action="store_true",
                    help="chỉ serve trong LAN, không mở tunnel")
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--stop", action="store_true")
    args = ap.parse_args()

    if args.status:
        return status()
    if args.stop:
        return stop()

    if not DASH.exists():
        print(f"Thiếu {DASH} — chạy scripts/build_report_hub.py trước.",
              file=sys.stderr)
        return 1
    if port_open(args.port):
        print(f"Port {args.port} đang được dùng. Xem: --status | Dừng: --stop",
              file=sys.stderr)
        return 1

    pids = {}

    # ── 1. HTTP server phục vụ dashboard + tải báo cáo ────────────────────
    print(f"▶ Serve {DASH} tại port {args.port}")
    log_http = ROOT / ".dashboard_http.log"
    http_proc = subprocess.Popen(
        [sys.executable, str(ROOT / "scripts" / "dashboard_server.py"),
         "--port", str(args.port)],
        stdout=open(log_http, "w", encoding="utf-8"),
        stderr=subprocess.STDOUT,
        cwd=str(ROOT),
    )
    pids["http"] = http_proc.pid

    for _ in range(30):
        if port_open(args.port):
            break
        time.sleep(0.5)
    else:
        print("✗ HTTP server không lên được. Xem .dashboard_http.log", file=sys.stderr)
        http_proc.kill()
        return 1
    print(f"  ✓ HTTP OK  http://127.0.0.1:{args.port}/REPORT_HUB.html")

    ip = lan_ip()
    lan_url = f"http://{ip}:{args.port}/REPORT_HUB.html"
    print(f"  ✓ LAN      {lan_url}")

    public_url = None

    # ── 2. Cloudflare Tunnel → public URL ────────────────────────────────
    if not args.lan:
        if not CF.exists():
            print(f"\n✗ Không có {CF}")
            print("  Tải: curl -sL -o tools/cloudflared/cloudflared.exe "
                  "https://github.com/cloudflare/cloudflared/releases/latest/"
                  "download/cloudflared-windows-amd64.exe")
            print("  Hoặc chạy với --lan để chỉ dùng trong mạng nội bộ.")
        else:
            print(f"\n▶ Mở Cloudflare Tunnel (không cần account)…")
            log_cf = ROOT / ".dashboard_tunnel.log"
            cf_proc = subprocess.Popen(
                [str(CF), "tunnel", "--url", f"http://127.0.0.1:{args.port}",
                 "--no-autoupdate"],
                stdout=open(log_cf, "w", encoding="utf-8"),
                stderr=subprocess.STDOUT,
                cwd=str(ROOT),
            )
            pids["tunnel"] = cf_proc.pid

            # đọc URL từ log
            pat = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")
            for _ in range(60):
                time.sleep(1)
                if log_cf.exists():
                    txt = log_cf.read_text(encoding="utf-8", errors="ignore")
                    m = pat.search(txt)
                    if m:
                        public_url = m.group(0)
                        break
                if cf_proc.poll() is not None:
                    print("✗ Tunnel thoát sớm. Xem .dashboard_tunnel.log",
                          file=sys.stderr)
                    break

            if public_url:
                print(f"  ✓ PUBLIC   {public_url}/REPORT_HUB.html")
            else:
                print("  ✗ Không lấy được public URL — xem .dashboard_tunnel.log")

    # ── 3. Lưu state ─────────────────────────────────────────────────────
    PID_FILE.write_text(json.dumps({
        "pids": pids,
        "port": args.port,
        "public_url": public_url,
        "lan_url": lan_url,
        "started": time.strftime("%Y-%m-%d %H:%M:%S"),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'='*68}")
    print("  DASHBOARD ĐANG CHẠY — gửi link này cho team:")
    print(f"{'='*68}")
    if public_url:
        print(f"\n  🌐 TEAM (mọi nơi):  {public_url}/REPORT_HUB.html")
        print(f"     Trang khác:      {public_url}/ops.html")
        print(f"                      {public_url}/youtube-analytics-real.html")
    else:
        print(f"\n  🏠 CHỈ TRONG LAN:   {lan_url}")
    print(f"\n  💻 Máy này:          http://127.0.0.1:{args.port}/REPORT_HUB.html")
    print(f"\n  Trạng thái:  python scripts/serve_dashboard_online.py --status")
    print(f"  Dừng:        python scripts/serve_dashboard_online.py --stop")
    if public_url:
        print(f"\n  ⚠ URL trycloudflare là TẠM — đổi mỗi lần chạy lại.")
        print(f"    Muốn URL cố định: cần domain + Cloudflare account (miễn phí).")
    print(f"{'='*68}")

    if not args.lan and public_url:
        print("\nNhấn Ctrl+C để dừng (hoặc chạy --stop ở terminal khác).")
        try:
            while True:
                time.sleep(5)
                if cf_proc.poll() is not None or http_proc.poll() is not None:
                    print("Một tiến trình đã thoát.")
                    break
        except KeyboardInterrupt:
            print("\nĐang dừng…")
            stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

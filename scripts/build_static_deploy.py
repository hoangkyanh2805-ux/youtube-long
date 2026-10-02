#!/usr/bin/env python3
"""Đóng gói static site để deploy lên hosting (GitHub Pages / Netlify / Cloudflare Pages).

Mục đích: có link CỐ ĐỊNH (dashboard.azzamedu.com) mà KHÔNG cần đổi nameserver
(giữ email Zoho ở iNET hoạt động bình thường).

Vì sao không dùng Cloudflare Tunnel: named tunnel BẮT BUỘC nameserver phải trỏ
về Cloudflare → sẽ làm hỏng MX record (Zoho Mail) nếu làm ẩu.

Cách hoạt động:
    deploy/          ← thư mục tĩnh, deploy nguyên thư mục này
    ├── index.html   ← copy của REPORT_HUB.html, link đã rewrite sang Drive
    ├── ops.html
    ├── youtube-analytics-real.html
    ├── data/        ← JSON/CSV công khai (không có secret)
    └── .nojekyll    ← cho GitHub Pages

Sau khi deploy, ở iNET thêm CNAME:
    dashboard  →  <site>.netlify.app   (hoặc github.io, pages.dev)

Script tự:
  - rewrite link Word/Excel trong hub → trỏ về Google Drive (vì hosting tĩnh
    không có endpoint /download/)
  - CHẶN mọi file secret (.env, token.json, client_secret, secrets/)
  - verify không có secret nào lọt vào deploy/

Usage:
    python scripts/build_static_deploy.py
    python scripts/build_static_deploy.py --drive-folder <id>
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "outputs" / "dashboard"
DEPLOY = ROOT / "deploy"

# Không bao giờ copy những file này
BLOCKED = (".env", "token.json", "client_secret", "secrets",
           ".git-credentials", "service-account", ".bak")

# File công khai được copy vào deploy/data/
# LƯU Ý: đây là bản public — KHÔNG chứa secret, KHÔNG chứa dữ liệu riêng tư
# (analytics_latest.json có số liệu private OAuth nên KHÔNG nằm ở đây).
PUBLIC_DATA = [
    # Plan & dây chuyền sản xuất
    "outputs/strategy/EVERGREEN_PLAN.csv",
    "outputs/strategy/content_backlog.csv",
    "outputs/strategy/PRODUCTION_30D.csv",
    "outputs/strategy/AUDIENCE_SEGMENTS.csv",
    "outputs/strategy/SEO_PACKAGES.json",
    "outputs/strategy/THUMBNAIL_CONCEPTS.json",
    "outputs/strategy/REPURPOSE_PACKAGES.json",
    # Báo cáo & phân tích
    "outputs/reports/blindspots.json",
    "outputs/mrbeast_audit/azzam_videos.json",
    "outputs/mrbeast_audit/gta_videos.json",
    "vendor/youtube-analytics-dashboard/history.csv",
]

DEFAULT_DRIVE = "1AzIiixGpZ4miW7ht7snpz7D5-4RZDycc"


def is_blocked(p: Path) -> bool:
    s = str(p).lower()
    return any(b in s for b in BLOCKED)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--drive-folder", default=DEFAULT_DRIVE,
                    help="id folder Google Drive chứa báo cáo")
    ap.add_argument("--site-url", default="",
                    help="URL site sau khi deploy (để hiện trong footer)")
    args = ap.parse_args()

    if DEPLOY.exists():
        shutil.rmtree(DEPLOY)
    DEPLOY.mkdir(parents=True)
    (DEPLOY / "data").mkdir()

    # ── 1. Copy dashboard HTML ────────────────────────────────────────────
    pages = {
        "REPORT_HUB.html": "index.html",          # trang chính
        "ops.html": "ops.html",
        "youtube-analytics-real.html": "youtube-analytics-real.html",
        "guides.html": "guides.html",             # mục lục hướng dẫn
    }
    copied = 0
    for src_name, dst_name in pages.items():
        src = DASH / src_name
        if not src.exists():
            print(f"  ✗ thiếu {src_name}")
            continue
        if is_blocked(src):
            print(f"  ⛔ CHẶN {src_name}")
            continue
        shutil.copy2(src, DEPLOY / dst_name)
        copied += 1
        print(f"  ✓ {src_name:34} → {dst_name}")

    # ── 1b. Copy trang hướng dẫn (SOP guide) ──────────────────────────────
    # Mỗi báo cáo có 1 trang riêng: 5W1H + SOP + đường dẫn bấm được.
    gsrc = DASH / "guides"
    gdst = DEPLOY / "guides"
    if gsrc.is_dir():
        gdst.mkdir(parents=True, exist_ok=True)
        n_g = 0
        for f in sorted(gsrc.glob("*.html")):
            if is_blocked(f):
                print(f"  ⛔ CHẶN guides/{f.name}")
                continue
            shutil.copy2(f, gdst / f.name)
            n_g += 1
        copied += n_g
        print(f"  ✓ guides/  → guides/  ({n_g} trang hướng dẫn)")
    else:
        print(f"  ✗ thiếu {gsrc.relative_to(ROOT)} — chạy build_sop_guides.py")

    # ── 2. Copy dữ liệu công khai ─────────────────────────────────────────
    for rel in PUBLIC_DATA:
        src = ROOT / rel
        if not src.exists():
            continue
        if is_blocked(src):
            print(f"  ⛔ CHẶN {rel}")
            continue
        dst = DEPLOY / "data" / src.name
        shutil.copy2(src, dst)
        print(f"  ✓ {rel:48} → data/{src.name}")

    # ── 3. Rewrite link trong index.html ──────────────────────────────────
    idx = DEPLOY / "index.html"
    if idx.exists():
        html = idx.read_text(encoding="utf-8")
        drive = f"https://drive.google.com/drive/folders/{args.drive_folder}"

        # Thay JS chọn prefix: trên hosting tĩnh, link file → trỏ về Drive.
        old_js = re.search(r"<script>.*?</script>", html, re.S)
        new_js = f"""<script>
(function () {{
  var DRIVE = "{drive}";
  // Hosting tĩnh không có /download/ → link tài liệu trỏ về Google Drive.
  document.querySelectorAll("a[data-rel]").forEach(function (a) {{
    var kind = a.getAttribute("data-kind");
    if (kind === "dash") {{
      a.href = a.getAttribute("data-rel").split("/").pop();
    }} else {{
      a.href = DRIVE;
      a.title = "Mở Google Drive để tải báo cáo";
    }}
  }});
  var b = document.getElementById("onlinebox");
  if (b) {{
    b.style.display = "block";
    b.innerHTML = "<b>✅ Đang xem ONLINE</b> — link chia sẻ được cho team. "
      + "Bấm tài liệu Word/Excel sẽ mở <b>Google Drive</b> để tải.";
  }}
  var s = document.querySelector(".sub");
  if (s) s.innerHTML += " • <b style='color:#4ade80'>ONLINE</b>";
}})();
</script>"""
        if old_js:
            html = html[:old_js.start()] + new_js + html[old_js.end():]

        # banner Drive ở đầu trang
        drive_bar = (
            f'<div class="online" style="display:block">'
            f'<b>📁 Báo cáo Word/Excel:</b> '
            f'<a href="{drive}" target="_blank" rel="noopener" '
            f'style="color:#4ade80">mở Google Drive</a> '
            f'— tất cả báo cáo đã tổ chức theo thư mục.</div>'
        )
        html = html.replace('<div class="warn">', drive_bar + '\n<div class="warn">', 1)

        # footer
        if args.site_url:
            html = html.replace(
                "nằm trong WF23, chạy 8:00 mỗi ngày).",
                f"nằm trong WF23, chạy 8:00 mỗi ngày).<br>"
                f"Site: <code>{args.site_url}</code>")
        idx.write_text(html, encoding="utf-8")
        print(f"\n  ✓ rewrite link → Drive ({drive})")

    # ── 4. .nojekyll cho GitHub Pages ─────────────────────────────────────
    (DEPLOY / ".nojekyll").write_text("", encoding="utf-8")

    # ── 5. VERIFY: không có secret nào lọt vào ────────────────────────────
    print("\n=== VERIFY: quét secret trong deploy/ ===")
    leaked = []
    for p in DEPLOY.rglob("*"):
        if p.is_file() and is_blocked(p):
            leaked.append(str(p.relative_to(DEPLOY)))
    if leaked:
        print("  ✗✗ CÓ SECRET LỌT VÀO:")
        for l in leaked:
            print("     ", l)
        return 1
    print("  ✓ sạch — không có file secret nào")

    # quét nội dung tìm key pattern
    pat = re.compile(r"(AIzaSy[A-Za-z0-9_\-]{20,}|sk_[A-Za-z0-9]{20,}|"
                     r"\d{8,10}:AA[A-Za-z0-9_\-]{30,}|GOCSPX-[A-Za-z0-9_\-]{20,})")
    hits = []
    for p in DEPLOY.rglob("*"):
        if p.is_file() and p.suffix.lower() in (".html", ".json", ".csv", ".md", ".js"):
            try:
                t = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for m in pat.finditer(t):
                hits.append((str(p.relative_to(DEPLOY)), m.group(0)[:18] + "…"))
    if hits:
        print("  ✗✗ PHÁT HIỆN KEY TRONG NỘI DUNG:")
        for f, k in hits[:10]:
            print(f"      {f}: {k}")
        return 1
    print("  ✓ không có API key / token trong nội dung")

    # ── 6. Tổng kết ───────────────────────────────────────────────────────
    total = sum(1 for p in DEPLOY.rglob("*") if p.is_file())
    size = sum(p.stat().st_size for p in DEPLOY.rglob("*") if p.is_file())
    print(f"\n{'='*66}")
    print(f"  DEPLOY PACKAGE SẴN SÀNG: {DEPLOY}")
    print(f"  {total} file, {size/1024:,.0f} KB")
    print(f"{'='*66}")
    print("\n  Bước tiếp theo:")
    print("    • Netlify:  netlify deploy --dir=deploy --prod")
    print("    • GitHub Pages: push thư mục deploy/ lên repo, bật Pages")
    print("    • Cloudflare Pages: npx wrangler pages deploy deploy")
    print(f"\n  Sau đó ở iNET thêm CNAME:")
    print(f"    dashboard  →  <tên-site>.netlify.app")
    print(f"  → https://dashboard.azzamedu.com")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

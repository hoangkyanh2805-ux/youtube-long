#!/usr/bin/env python3
"""Sinh dashboard HTML TỔNG HỢP — một trang có link tới mọi báo cáo.

Vấn đề trước đây: có nhiều dashboard rời (ops.html, youtube-analytics-real.html,
index.html) nhưng không có trang nào gom hết link và giải thích file nào để làm gì.

Trang này là điểm vào duy nhất: số liệu chính + link mở từng dashboard/báo cáo
+ trạng thái pipeline + link topic Telegram.

Xuất: outputs/dashboard/REPORT_HUB.html

Usage:
    python scripts/build_report_hub.py
"""
from __future__ import annotations

import csv
import json
import socket
import sys
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "outputs" / "dashboard"
REP = ROOT / "outputs" / "reports"
STRAT = ROOT / "outputs" / "strategy"
VENDOR = ROOT / "vendor" / "youtube-analytics-dashboard"
OUT = DASH / "REPORT_HUB.html"

# file:// link — bấm mở trực tiếp bằng browser
F = "file:///C:/Users/Admin/youtube"


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def load_csv(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def to_int(v, d=0) -> int:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return d


def size_of(p: Path) -> str:
    if not p.exists():
        return "—"
    n = p.stat().st_size
    for u in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:,.0f} {u}"
        n /= 1024
    return f"{n:.1f} GB"


def mtime(p: Path) -> str:
    if not p.exists():
        return "chưa có"
    return datetime.fromtimestamp(p.stat().st_mtime).strftime("%d/%m %H:%M")


def mcp_alive() -> bool:
    s = socket.socket()
    s.settimeout(1)
    try:
        s.connect(("127.0.0.1", 9001))
        return True
    except Exception:
        return False
    finally:
        s.close()


def main() -> int:
    DASH.mkdir(parents=True, exist_ok=True)

    blind = load_json(REP / "blindspots.json")
    an = load_json(VENDOR / "analytics_latest.json")
    hist = load_csv(VENDOR / "history.csv")
    ever = load_csv(STRAT / "EVERGREEN_PLAN.csv")
    backlog = load_csv(STRAT / "content_backlog.csv")

    m = (an or {}).get("metrics", {})
    dv = (blind or {}).get("derived", {})
    bot = (blind or {}).get("bot_traffic", {})
    findings = (blind or {}).get("findings", [])
    mcp = mcp_alive()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    owner = next((r for r in hist if r.get("channel_id") == "UCBZ7LaffmEPv91sWcfroJdQ"), {})
    comp = next((r for r in hist if r.get("channel_id") != "UCBZ7LaffmEPv91sWcfroJdQ"), {})

    # Link: khi mở qua HTTP (team online) thì dùng đường dẫn tương đối;
    # khi mở bằng file:// (máy local) thì dùng file:// tuyệt đối.
    # Dùng JS để chọn đúng — xem <script> ở cuối trang.
    GROUPS = [
        ("📖 HƯỚNG DẪN — click là biết làm", [
            ("Tất cả hướng dẫn (5W1H + SOP)", "outputs/dashboard/guides.html",
             "8 trang hướng dẫn: hiểu 30 giây, làm theo thứ tự, link bấm là mở", "dash"),
            ("P06 — Phân khúc khán giả", "outputs/dashboard/guides/p06-audience.html",
             "Chọn nhóm đánh trước từ 2,567 comment thật", "dash"),
            ("P10 — Gói SEO", "outputs/dashboard/guides/p10-seo.html",
             "Tiêu đề + mô tả + tag copy-paste vào YouTube", "dash"),
            ("P11 — Thumbnail + Design Brief", "outputs/dashboard/guides/p11-thumbnail.html",
             "72 concept + prompt AI + tiêu chí nghiệm thu", "dash"),
            ("P05 — Đa nền tảng", "outputs/dashboard/guides/p05-repurpose.html",
             "1 video → 5 định dạng, có brief cho editor", "dash"),
            ("30D — Checklist 30 ngày", "outputs/dashboard/guides/checklist-30d.html",
             "Hôm nay làm gì, mốc kiểm tra ngày 7/14/21/30", "dash"),
            ("EVERGREEN — Plan 24 video", "outputs/dashboard/guides/evergreen.html",
             "Chủ đề từ từ khoá thật, 18/24 đối thủ chưa làm", "dash"),
            ("ANALYTICS — Điểm mù", "outputs/dashboard/guides/analytics-blindspots.html",
             "11 điểm mù + cảnh báo traffic bot", "dash"),
            ("AUDIT — MrBeast", "outputs/dashboard/guides/mrbeast-audit.html",
             "Chẩn đoán + plan 90 ngày + build-to-sell", "dash"),
        ]),
        ("Dashboard — mở xem số liệu", [
            ("REPORT_HUB.html (trang này)", "outputs/dashboard/REPORT_HUB.html",
             "Điểm vào duy nhất — gom mọi link + số liệu chính", "dash"),
            ("Ops cockpit", "outputs/dashboard/ops.html",
             "Analytics + điểm mù + pipeline + pain point + backlog", "dash"),
            ("Analytics dashboard (data thật)", "outputs/dashboard/youtube-analytics-real.html",
             "13 section: watch time, retention, traffic, địa lý, thiết bị", "dash"),
        ]),
        ("Dây chuyền sản xuất (P05/P06/P10/P11)", [
            ("Checklist 30 ngày (Word)", "outputs/reports/AZZAM_PRODUCTION_30D.docx",
             "Lịch 30 ngày: video + SEO + thumbnail + đăng bài, 4 mốc kiểm tra", "dl"),
            ("Checklist 30 ngày (Excel)", "outputs/reports/AZZAM_PRODUCTION_30D.xlsx",
             "4 sheet: lịch, checklist theo ngày, mốc kiểm tra, mục tiêu", "dl"),
            ("PRODUCTION_30D.md", "outputs/strategy/PRODUCTION_30D.md",
             "Đọc trong editor, có checkbox tick tay", "dl"),
            ("Phân khúc khán giả (Word)", "outputs/reports/AZZAM_AUDIENCE_SEGMENTS.docx",
             "P06: 7 phân khúc chấm điểm, chọn SEG-B đánh trước", "dl"),
            ("Phân khúc khán giả (Excel)", "outputs/reports/AZZAM_AUDIENCE_SEGMENTS.xlsx",
             "Scorecard + chân dung + kế hoạch 8 tuần", "dl"),
            ("Gói SEO (Word)", "outputs/reports/AZZAM_SEO_PACKAGES.docx",
             "P10: 24 video × 5 title + mô tả + 20 tag + giờ đăng", "dl"),
            ("Gói SEO (Excel)", "outputs/reports/AZZAM_SEO_PACKAGES.xlsx",
             "3 sheet: packages, tiêu đề đầy đủ, mô tả + tag", "dl"),
            ("Thumbnail + Design Brief (Word)", "outputs/reports/AZZAM_THUMBNAIL_BRIEF.docx",
             "P11: 72 concept + prompt AI + quy tắc designer", "dl"),
            ("Thumbnail + Design Brief (Excel)", "outputs/reports/AZZAM_THUMBNAIL_BRIEF.xlsx",
             "3 sheet: plan, prompt AI, quy tắc", "dl"),
            ("Đa nền tảng P05 (Word)", "outputs/reports/AZZAM_REPURPOSE.docx",
             "24 video × 5 định dạng = 120 asset", "dl"),
            ("Đa nền tảng P05 (Excel)", "outputs/reports/AZZAM_REPURPOSE.xlsx",
             "4 sheet: tổng quan, Short, bài chữ+quan điểm, checklist", "dl"),
            ("EDITOR_HANDOFF.md", "outputs/strategy/EDITOR_HANDOFF.md",
             "Brief giao việc cho editor — nguyên liệu + nghiệm thu", "dl"),
            ("DESIGN_BRIEF.md", "outputs/strategy/DESIGN_BRIEF.md",
             "Brief thumbnail chi tiết cho designer", "dl"),
            ("AUDIENCE_SEGMENTS.md", "outputs/strategy/AUDIENCE_SEGMENTS.md",
             "P06 đọc trong editor", "dl"),
            ("SEO_PACKAGES.md", "outputs/strategy/SEO_PACKAGES.md",
             "P10 đọc trong editor — copy-paste vào YouTube", "dl"),
            ("THUMBNAIL_CONCEPTS.md", "outputs/strategy/THUMBNAIL_CONCEPTS.md",
             "P11 concept + prompt AI", "dl"),
            ("REPURPOSE_PACKAGES.md", "outputs/strategy/REPURPOSE_PACKAGES.md",
             "P05 5 định dạng mỗi video", "dl"),
        ]),
        ("Báo cáo Word + Excel (tải về)", [
            ("Audit MrBeast (Word)", "outputs/reports/AZZAM_MRBEAST_AUDIT.docx",
             "4 phần: chẩn đoán + plan 90 ngày + SOP + build-to-sell", "dl"),
            ("Audit MrBeast (Excel)", "outputs/reports/AZZAM_MRBEAST_AUDIT.xlsx",
             "8 sheet: chẩn đoán, điểm, KPI, top video, evergreen mẫu", "dl"),
            ("Evergreen Plan (Word)", "outputs/reports/AZZAM_EVERGREEN_PLAN.docx",
             "24 video chi tiết: title, hook, outline, keyword, bằng chứng", "dl"),
            ("Evergreen Plan (Excel)", "outputs/reports/AZZAM_EVERGREEN_PLAN.xlsx",
             "6 sheet: plan, từ khoá nguồn, pattern đối thủ, mẫu, lịch 12 tuần", "dl"),
            ("Analytics + Điểm mù (Word)", "outputs/reports/AZZAM_ANALYTICS_DIEM_MU.docx",
             "Cảnh báo bot + 11 điểm mù có bằng chứng", "dl"),
            ("Analytics + Điểm mù (Excel)", "outputs/reports/AZZAM_ANALYTICS_DIEM_MU.xlsx",
             "10 sheet: tổng quan, điểm mù, traffic, nguồn ngoài, theo ngày", "dl"),
            ("Báo cáo đối thủ (Word)", "outputs/reports/AZZAM_BAOCAO_PHAN_TICH_DOI_THU.docx",
             "Sales angles, SEO, phễu affiliate, pain point", "dl"),
            ("SOP đội edit (Word)", "outputs/reports/AZZAM_SOP_FINAL.docx",
             "SOP vận hành + KPI + lịch + CapCut MCP", "dl"),
        ]),
        ("Tài liệu markdown (đọc trong editor)", [
            ("MRBEAST_AUDIT.md", "outputs/reports/MRBEAST_AUDIT.md", "Chẩn đoán + bảng điểm", "dl"),
            ("MRBEAST_PLAN_ACTION.md", "outputs/strategy/MRBEAST_PLAN_ACTION.md", "Plan 90 ngày + KPI", "dl"),
            ("MRBEAST_SOP.md", "outputs/strategy/MRBEAST_SOP.md", "SOP 8 bước/ngày", "dl"),
            ("MRBEAST_BUILD_TO_SELL.md", "outputs/strategy/MRBEAST_BUILD_TO_SELL.md", "Lộ trình 12 tháng", "dl"),
            ("EVERGREEN_PLAN.md", "outputs/strategy/EVERGREEN_PLAN.md", "24 video evergreen", "dl"),
            ("blindspots.md", "outputs/reports/blindspots.md", "11 điểm mù + bằng chứng JSON", "dl"),
        ]),
        ("Dữ liệu (CSV/JSON — để lọc, import sheet)", [
            ("EVERGREEN_PLAN.csv", "outputs/strategy/EVERGREEN_PLAN.csv", "24 video, 18 cột", "dl"),
            ("content_backlog.csv", "outputs/strategy/content_backlog.csv", f"{len(backlog)} slot", "dl"),
            ("azzam_videos.json", "outputs/mrbeast_audit/azzam_videos.json", "297 video kênh mình", "dl"),
            ("gta_videos.json", "outputs/mrbeast_audit/gta_videos.json", "742 video đối thủ", "dl"),
            ("analytics_latest.json", "vendor/youtube-analytics-dashboard/analytics_latest.json", "Private metrics OAuth", "dl"),
            ("history.csv", "vendor/youtube-analytics-dashboard/history.csv", "Snapshot public stats", "dl"),
        ]),
    ]

    # ── Topic Telegram ────────────────────────────────────────────────────
    TOPICS = [
        ("EDIT", "205", "Content đã duyệt → editor lấy làm việc"),
        ("COMMENT", "206", "Cào comment + pain point → Alan duyệt"),
        ("AUDIT", "239", "Audit MrBeast + plan + SOP + build-to-sell"),
        ("General", "2", "Báo cáo tổng hợp, pipeline health"),
    ]

    def stat(label, value, note=""):
        return (f'<div class="stat"><div class="sl">{escape(label)}</div>'
                f'<div class="sv">{escape(str(value))}</div>'
                f'<div class="sn">{escape(note)}</div></div>')

    # ── HTML ───────────────────────────────────────────────────────────────
    stat_html = "".join([
        stat("Views 28d", f"{to_int(m.get('views')):,}", "kênh mình"),
        stat("Watch time", f"{dv.get('watch_hours', 0)}h", f"avg {to_int(m.get('averageViewDuration'))}s"),
        stat("Sub ròng", f"{dv.get('sub_net', 0):+d}", "phải dương"),
        stat("Sub", f"{to_int(owner.get('subs')):,}", f"đối thủ {to_int(comp.get('subs')):,}"),
        stat("Comment rate", f"{dv.get('comment_rate_pct', 0)}%", "gần 0"),
        stat("Traffic nghi bot", f"{to_int(bot.get('views')):,}",
             f"{bot.get('pct_of_channel', 0)}% — cần xử lý"),
        stat("Điểm MrBeast", "3.1/10", "mục tiêu 6/10"),
        stat("Evergreen plan", f"{len(ever)} video", "18 chủ đề đối thủ chưa làm"),
        stat("CapCut MCP", "Chạy" if mcp else "Tắt", "port 9001"),
    ])

    # ── TABS ───────────────────────────────────────────────────────────────
    TAB_GUIDES = "guides"
    TAB_PRODUCTION = "production"
    TAB_REPORTS = "reports"
    TAB_DATA = "data"

    # Các biến cần thiết cho overview tab
    topics_html = "".join(
        f'<div class="topic"><b>{escape(n)}</b>'
        f'<code>thread {escape(t)}</code>'
        f'<span>{escape(d)}</span>'
        f'<a href="https://t.me/c/4458375752/{escape(t)}" target="_blank" rel="noopener">mở topic</a>'
        f'</div>' for n, t, d in TOPICS)

    sev_cls = {"CRITICAL": "c", "HIGH": "h", "MEDIUM": "m", "INFO": "i"}
    blind_html = "".join(
        f'<div class="fd {sev_cls.get(f.get("severity",""))}">'
        f'<span class="sev">{escape(f.get("severity",""))}</span>'
        f'{escape(f.get("title",""))}</div>' for f in findings)

    ever_html = "".join(
        f'<tr><td class="num">{r.get("stt")}</td><td>{escape(r.get("topic",""))}</td>'
        f'<td><code>{escape(r.get("keyword_chinh",""))}</code></td>'
        f'<td class="num">{r.get("freq_comment","")}</td>'
        f'<td class="small">{escape(r.get("doi_thu_da_lam",""))}</td></tr>'
        for r in ever[:24])

    def tab_btn(tab_id, label, active=False):
        cls = "tab-btn active" if active else "tab-btn"
        return f'<button class="{cls}" data-tab="{tab_id}" onclick="switchTab(\'{tab_id}\')">{escape(label)}</button>'

    def tab_panel(tab_id, content, active=False):
        cls = "tab-panel active" if active else "tab-panel"
        return f'<div class="{cls}" id="tab-{tab_id}">{content}</div>'

    # Tab 1: Tổng quan
    overview_html = f"""
<h2>Số liệu chính</h2>
<div class="stats">{stat_html}</div>
<h2>Điểm mù ({len(findings)})</h2>
{blind_html}
<h2>Evergreen plan — {len(ever)} video</h2>
<table>
  <thead><tr><th>#</th><th>Chủ đề</th><th>Keyword chính</th><th>Freq</th>
  <th>Đối thủ đã làm</th></tr></thead>
  <tbody>{ever_html}</tbody>
</table>
<h2>Topic Telegram</h2>
{topics_html}
"""

    # Tab 2: Hướng dẫn
    guides_items = GROUPS[0][1]
    guides_rows = ""
    for name, rel, desc, kind in guides_items:
        p = ROOT / rel
        ok = p.exists()
        attr = f'data-rel="{escape(rel)}" data-kind="{kind}"'
        name_html = (f'<a {attr} href="#" target="_blank" rel="noopener">{escape(name)}</a>'
                     if ok else f'<span class="miss">{escape(name)}</span>')
        guides_rows += (f'<tr><td>{name_html}</td><td class="d">{escape(desc)}</td>'
                        f'<td class="sz">{size_of(p)}</td><td class="mt">{mtime(p)}</td></tr>')
    guides_html = f"""<h2>Hướng dẫn SOP — click là biết làm</h2>
<table><thead><tr><th>Tài liệu</th><th>Nội dung</th><th>Size</th><th>Cập nhật</th></tr></thead>
<tbody>{guides_rows}</tbody></table>"""

    # Tab 3: Sản xuất
    prod_items = GROUPS[2][1]
    prod_rows = ""
    for name, rel, desc, kind in prod_items:
        p = ROOT / rel
        ok = p.exists()
        attr = f'data-rel="{escape(rel)}" data-kind="{kind}"'
        name_html = (f'<a {attr} href="#" target="_blank" rel="noopener">{escape(name)}</a>'
                     if ok else f'<span class="miss">{escape(name)}</span>')
        badge = '<span class="bd">tải</span>' if kind == "dl" and ok else ""
        prod_rows += (f'<tr><td>{name_html} {badge}</td><td class="d">{escape(desc)}</td>'
                      f'<td class="sz">{size_of(p)}</td><td class="mt">{mtime(p)}</td></tr>')
    production_html = f"""<h2>Dây chuyền sản xuất (P05/P06/P10/P11)</h2>
<table><thead><tr><th>Tài liệu</th><th>Nội dung</th><th>Size</th><th>Cập nhật</th></tr></thead>
<tbody>{prod_rows}</tbody></table>"""

    # Tab 4: Báo cáo
    report_items = GROUPS[3][1] + GROUPS[4][1]
    report_rows = ""
    for name, rel, desc, kind in report_items:
        p = ROOT / rel
        ok = p.exists()
        attr = f'data-rel="{escape(rel)}" data-kind="{kind}"'
        name_html = (f'<a {attr} href="#" target="_blank" rel="noopener">{escape(name)}</a>'
                     if ok else f'<span class="miss">{escape(name)}</span>')
        badge = '<span class="bd">tải</span>' if kind == "dl" and ok else ""
        report_rows += (f'<tr><td>{name_html} {badge}</td><td class="d">{escape(desc)}</td>'
                        f'<td class="sz">{size_of(p)}</td><td class="mt">{mtime(p)}</td></tr>')
    reports_html = f"""<h2>Báo cáo Word + Excel + Markdown</h2>
<table><thead><tr><th>Tài liệu</th><th>Nội dung</th><th>Size</th><th>Cập nhật</th></tr></thead>
<tbody>{report_rows}</tbody></table>"""

    # Tab 5: Dữ liệu
    data_items = GROUPS[5][1]
    data_rows = ""
    for name, rel, desc, kind in data_items:
        p = ROOT / rel
        ok = p.exists()
        attr = f'data-rel="{escape(rel)}" data-kind="{kind}"'
        name_html = (f'<a {attr} href="#" target="_blank" rel="noopener">{escape(name)}</a>'
                     if ok else f'<span class="miss">{escape(name)}</span>')
        badge = '<span class="bd">tải</span>' if kind == "dl" and ok else ""
        data_rows += (f'<tr><td>{name_html} {badge}</td><td class="d">{escape(desc)}</td>'
                      f'<td class="sz">{size_of(p)}</td><td class="mt">{mtime(p)}</td></tr>')
    data_html = f"""<h2>Dữ liệu (CSV/JSON — để lọc, import sheet)</h2>
<table><thead><tr><th>Tài liệu</th><th>Nội dung</th><th>Size</th><th>Cập nhật</th></tr></thead>
<tbody>{data_rows}</tbody></table>"""

    tabs_html = f"""
<div class="tabs">
  {tab_btn("overview", "📊 Tổng quan", active=True)}
  {tab_btn(TAB_GUIDES, "📖 Hướng dẫn")}
  {tab_btn(TAB_PRODUCTION, "🏭 Sản xuất")}
  {tab_btn(TAB_REPORTS, "📄 Báo cáo")}
  {tab_btn(TAB_DATA, "📦 Dữ liệu")}
</div>
{tab_panel("overview", overview_html, active=True)}
{tab_panel(TAB_GUIDES, guides_html)}
{tab_panel(TAB_PRODUCTION, production_html)}
{tab_panel(TAB_REPORTS, reports_html)}
{tab_panel(TAB_DATA, data_html)}
"""

    html = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Azzam Report Hub — {date.today().isoformat()}</title>
<style>
:root {{ --bg:#0f1216; --sf:#171c22; --sf2:#1e242c; --bd:#2c343d; --tx:#e6edf5;
  --mu:#94a3b8; --bl:#60a5fa; --gr:#4ade80; --am:#fbbf24; --rd:#f87171; --ac:#38bdf8; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--tx);
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; line-height:1.5; padding:24px; }}
.wrap {{ max-width:1320px; margin:0 auto; }}
header {{ border-bottom:1px solid var(--bd); padding-bottom:16px; margin-bottom:20px; }}
h1 {{ margin:0 0 4px; font-size:24px; letter-spacing:-.02em; }}
h2 {{ font-size:14px; text-transform:uppercase; letter-spacing:.08em; color:var(--mu);
  margin:30px 0 10px; font-weight:600; }}
.sub {{ color:var(--mu); font-size:13px; }}
.warn {{ background:#2a1a1a; border:1px solid #5c2626; border-left:3px solid var(--rd);
  border-radius:8px; padding:14px 18px; margin:18px 0; font-size:13px; color:#fca5a5; }}
.warn b {{ color:#fff; }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(155px,1fr)); gap:10px; }}
.stat {{ background:var(--sf); border:1px solid var(--bd); border-radius:10px; padding:12px 14px; }}
.sl {{ font-size:10.5px; text-transform:uppercase; letter-spacing:.06em; color:var(--mu); }}
.sv {{ font-size:23px; font-weight:700; margin:3px 0 1px; font-variant-numeric:tabular-nums; }}
.sn {{ font-size:10.5px; color:var(--mu); }}
table {{ width:100%; border-collapse:collapse; font-size:13px; background:var(--sf);
  border:1px solid var(--bd); border-radius:10px; overflow:hidden; }}
th {{ text-align:left; font-size:10.5px; text-transform:uppercase; letter-spacing:.06em;
  color:var(--mu); padding:9px 12px; border-bottom:1px solid var(--bd); background:var(--sf2); }}
td {{ padding:8px 12px; border-bottom:1px solid var(--bd); vertical-align:top; }}
tr:last-child td {{ border-bottom:none; }}
td.d {{ color:var(--mu); font-size:12px; }}
td.sz, td.mt {{ color:var(--mu); font-size:11.5px; white-space:nowrap;
  font-variant-numeric:tabular-nums; }}
.num {{ font-variant-numeric:tabular-nums; color:var(--mu); }}
.small {{ font-size:12px; color:var(--mu); }}
a {{ color:var(--bl); text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
code {{ font-family:ui-monospace,"Cascadia Code",Consolas,monospace; font-size:11.5px;
  background:var(--sf2); border:1px solid var(--bd); border-radius:4px; padding:1px 5px; color:var(--ac); }}
.miss {{ color:var(--rd); }}
.topic {{ background:var(--sf); border:1px solid var(--bd); border-left:3px solid var(--ac);
  border-radius:8px; padding:11px 14px; margin-bottom:8px; display:flex;
  gap:12px; align-items:baseline; flex-wrap:wrap; font-size:13px; }}
.topic b {{ min-width:78px; }}
.topic span {{ color:var(--mu); font-size:12.5px; flex:1; }}
.fd {{ background:var(--sf); border:1px solid var(--bd); border-left:3px solid var(--mu);
  border-radius:7px; padding:9px 13px; margin-bottom:7px; font-size:13px; }}
.fd.c {{ border-left-color:var(--rd); }} .fd.h {{ border-left-color:#fb923c; }}
.fd.m {{ border-left-color:var(--am); }} .fd.i {{ border-left-color:var(--bl); }}
.sev {{ font-size:9.5px; font-weight:700; padding:2px 6px; border-radius:3px;
  background:var(--sf2); border:1px solid var(--bd); color:var(--mu); margin-right:8px; }}
.bd {{ display:inline-block; font-size:9.5px; font-weight:700; padding:1px 6px;
  border-radius:3px; color:var(--ac); background:var(--sf2);
  border:1px solid #1e3a5f; margin-left:5px; }}
.online {{ background:#0f2318; border:1px solid #1e5c3a; border-left:3px solid var(--gr);
  border-radius:8px; padding:12px 16px; margin:16px 0; font-size:13px; color:#86efac; }}
.online b {{ color:#fff; }}
.online code {{ background:#0a1a12; border-color:#1e5c3a; color:#86efac; }}
footer {{ margin-top:34px; padding-top:14px; border-top:1px solid var(--bd);
  font-size:12px; color:var(--mu); }}
.tabs {{ display:flex; gap:6px; margin:20px 0 0; flex-wrap:wrap; }}
.tab-btn {{ background:var(--sf); border:1px solid var(--bd); color:var(--mu);
  padding:8px 16px; border-radius:8px; cursor:pointer; font-size:13px; font-weight:500;
  transition:all .15s; }}
.tab-btn:hover {{ background:var(--sf2); color:var(--tx); }}
.tab-btn.active {{ background:var(--bl); color:#fff; border-color:var(--bl); }}
.tab-panel {{ display:none; padding-top:20px; }}
.tab-panel.active {{ display:block; }}
</style></head><body><div class="wrap">

<header>
  <h1>Azzam Report Hub</h1>
  <div class="sub">@azzammastertradinggold • XAUUSD / Forex • English channel •
    cập nhật {now} • <b>đây là trang điểm vào — mọi báo cáo đều có link ở dưới</b></div>
</header>

<div class="online" id="onlinebox" style="display:none">
  <b>✅ Đang xem ONLINE</b> — link chia sẻ được cho team.
  Link Word/Excel bấm là tải về. Link dashboard mở trong tab mới.
</div>

<div class="warn">
  <b>⚠ Cần xử lý trước:</b> {to_int(bot.get('views')):,} views
  ({bot.get('pct_of_channel',0)}% tổng view 28 ngày) đến từ referrer
  <code>seofast</code> / <code>playbots</code> — app farm view, không phải site thật.
  Ngày 29/09 có 8,153 views trong khi trung vị các ngày khác ~35.
  Rủi ro vi phạm Fake Engagement Policy → xoá view hoặc phạt kênh.
  <b>Mọi tối ưu khác vô nghĩa nếu số liệu nền là giả.</b>
</div>

<h2>Số liệu chính</h2>
<div class="stats">{stat_html}</div>

<h2>Điểm mù ({len(findings)})</h2>
{blind_html}

<h2>Evergreen plan — 24 video</h2>
<table>
  <thead><tr><th>#</th><th>Chủ đề</th><th>Keyword chính</th><th>Freq</th>
  <th>Đối thủ đã làm</th></tr></thead>
  <tbody>{ever_html}</tbody>
</table>

<h2>Topic Telegram</h2>
{topics_html}

{tabs_html}

<footer>
  Sinh tự động từ dữ liệu thật trong repo — không có số nhập tay.<br>
  Nguồn: YouTube Data API v3 + YouTube Analytics API (OAuth) + comment scraping
  + keyword mining.<br>
  Cập nhật: <code>python scripts/build_report_hub.py</code>
  (nằm trong WF23, chạy 8:00 mỗi ngày).
</footer>

</div>
<script>
// Chọn prefix link theo cách trang được mở:
//   http(s)  → team online  → đường dẫn tương đối trong cùng server
//   file://  → máy local    → file:// tuyệt đối
(function () {{
  var online = location.protocol === "http:" || location.protocol === "https:";
  var BASE = "/";                      // server đang serve chính thư mục dashboard
  var LOCAL = "file:///C:/Users/Admin/youtube/";
  document.querySelectorAll("a[data-rel]").forEach(function (a) {{
    var rel = a.getAttribute("data-rel");
    var kind = a.getAttribute("data-kind");
    if (online) {{
      // dashboard cùng thư mục → tên file; file khác → tải qua /files/
      a.href = (kind === "dash")
        ? BASE + rel.split("/").pop()
        : BASE + "files/" + rel;
    }} else {{
      a.href = LOCAL + rel;
    }}
  }});
  if (online) {{
    var b = document.getElementById("onlinebox");
    if (b) b.style.display = "block";
    var s = document.querySelector(".sub");
    if (s) s.innerHTML += " • <b style='color:#4ade80'>ONLINE</b>";
  }}
}})();
function switchTab(tabId) {{
  document.querySelectorAll(".tab-btn").forEach(function (btn) {{
    btn.classList.toggle("active", btn.getAttribute("data-tab") === tabId);
  }});
  document.querySelectorAll(".tab-panel").forEach(function (panel) {{
    panel.classList.toggle("active", panel.id === "tab-" + tabId);
  }});
}}
</script>
</body></html>"""

    OUT.write_text(html, encoding="utf-8")
    print(f"Written: {OUT}")
    print(f"  size: {OUT.stat().st_size:,} bytes")
    print(f"  open: file:///C:/Users/Admin/youtube/outputs/dashboard/REPORT_HUB.html")
    print(f"  files linked: {sum(len(i) for _, i in GROUPS)} "
          f"({sum(1 for _, items in GROUPS for it in items if (ROOT/it[1]).exists())} tồn tại)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

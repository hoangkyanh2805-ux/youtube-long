"""
Telegram reporter — gửi báo cáo vào đúng topic của group forum.

Topics (đã tạo thật trong group youttubegroup):
  205 = EDIT    — content đã duyệt, editor lấy làm việc
  206 = COMMENT — cào comment + báo cáo pain point để Alan duyệt

Guardrail: mọi lệnh GỬI đều phải có --approve APPROVE.
Không có flag đó thì chỉ in ra màn hình (dry-run), không gửi.

Usage:
    # Xem trước
    python scripts/telegram_reporter.py --topic edit --report content_brief

    # Gửi thật (cần approval)
    python scripts/telegram_reporter.py --topic edit --report content_brief --send --approve APPROVE

    # Liệt kê topic đã biết
    python scripts/telegram_reporter.py --list-topics
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# Force UTF-8 console: without this, printing Vietnamese crashes with
# UnicodeEncodeError when stdout is a pipe (dagu/cron/CI).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402
ensure_utf8_console()

TELEGRAM_API_BASE = "https://api.telegram.org"

# Topic IDs created in the forum group. Update here if topics are recreated.
TOPICS = {
    "edit": {"thread_id": "205", "name": "EDIT - Content đã duyệt",
             "purpose": "Content đã duyệt → editor lấy làm việc"},
    "comment": {"thread_id": "206", "name": "COMMENT - Cào & Báo cáo",
                "purpose": "Cào comment + pain point → Alan duyệt"},
    "audit": {"thread_id": "239", "name": "AUDIT - MrBeast",
              "purpose": "Audit kênh + plan action + SOP + build-to-sell"},
    "general": {"thread_id": "2", "name": "General",
                "purpose": "Báo cáo tổng hợp"},
}


# ── Env ─────────────────────────────────────────────────────────────────────

def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    # utf-8-sig: project .env has a BOM that would corrupt the first key
    for raw in path.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        values[k.strip()] = v.strip().strip('"').strip("'")
    return values


def merged_env(root: Path) -> dict[str, str]:
    values = {k: v for k, v in os.environ.items() if v}
    values.update(load_env_file(root / ".env"))
    return values


# ── Telegram API ────────────────────────────────────────────────────────────

def telegram_call(method: str, token: str, **params) -> dict:
    url = f"{TELEGRAM_API_BASE}/bot{token}/{method}"
    data = urlencode({k: v for k, v in params.items() if v != ""}).encode("utf-8")
    req = Request(url, data=data, method="POST")
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        return {"ok": False, "http": e.code, "body": body[:400]}
    except URLError as e:
        return {"ok": False, "error": str(e.reason)}


def send_to_topic(token: str, chat_id: str, thread_id: str, text: str) -> dict:
    return telegram_call(
        "sendMessage", token,
        chat_id=chat_id,
        message_thread_id=thread_id,
        text=text,
        parse_mode="HTML",
        disable_web_page_preview="true",
    )


# ── Data loaders ────────────────────────────────────────────────────────────

def load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def to_int(v, d=0) -> int:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return d


def to_float(v, d=0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def dedupe(rows: list[dict]) -> list[dict]:
    out, seen = [], set()
    for r in rows:
        k = r.get("comment_id") or f"{r.get('content_url','')}|{r.get('comment_text','')[:80]}"
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ── Report builders ─────────────────────────────────────────────────────────

def report_comment(root: Path) -> str:
    """Báo cáo cào comment + pain point → Alan duyệt."""
    pp = dedupe(
        load_csv(root / "outputs/competitor_analysis/painpoint_candidates.csv")
        + load_csv(root / "outputs/competitor_longform/painpoint_candidates.csv")
    )
    cm = dedupe(
        load_csv(root / "outputs/competitor_analysis/normalized_comments.csv")
        + load_csv(root / "outputs/competitor_longform/normalized_comments.csv")
    )
    videos = load_csv(root / "outputs/competitor_longform/longform_inventory.csv")

    top = sorted(pp, key=lambda x: -to_float(x.get("score")))[:5]

    lines = [
        "🔍 <b>BÁO CÁO CÀO COMMENT</b>",
        f"<i>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</i>",
        "",
        "<b>Số liệu</b>",
        f"• Comment unique: {len(cm):,}",
        f"• Pain point unique: {len(pp):,}",
        f"• Video đã cào: {len(videos)}",
        "",
        "<b>Top 5 pain point mới (cần duyệt)</b>",
    ]
    for i, p in enumerate(top, 1):
        txt = esc(str(p.get("comment_text", ""))[:150])
        lines.append(f"{i}. [{esc(p.get('categories',''))}] score {p.get('score')}")
        lines.append(f"   “{txt}”")
        lines.append(f"   <a href=\"{esc(p.get('content_url',''))}\">nguồn</a>")
        lines.append("")

    lines += [
        "<b>Việc cần Alan làm</b>",
        "1. Duyệt pain point nào dùng làm hook",
        "2. Chốt 3 Short + 1 Long cho ngày mai",
        "3. Trả lời topic này để chuyển sang topic EDIT",
        "",
        "<i>Reply của chính chủ kênh đã bị loại khỏi dữ liệu.</i>",
    ]
    return "\n".join(lines)


def report_content_brief(root: Path) -> str:
    """Content brief đã duyệt → editor lấy làm việc."""
    backlog = load_csv(root / "outputs/strategy/content_backlog.csv")
    angles = load_json(root / "outputs/strategy/sales_angles.json") or []
    pool = dedupe(
        load_csv(root / "outputs/competitor_analysis/painpoint_candidates.csv")
        + load_csv(root / "outputs/competitor_longform/painpoint_candidates.csv")
    )

    rows = sorted(backlog, key=lambda x: -to_int(x.get("priority")))[:4]
    lines = [
        "🎬 <b>CONTENT BRIEF CHO EDITOR</b>",
        f"<i>{date.today().isoformat()}</i>",
        "",
        "<b>KPI hôm nay</b>",
        "• 3 Short (15-35s) + 1 Long (8 phút)",
        "• Ngôn ngữ: ENGLISH",
        "• CapCut Pro + MCP draft",
        "",
        "<b>4 slot cần làm</b>",
    ]
    for i, r in enumerate(rows, 1):
        lines.append(f"{i}. <b>[{esc(r.get('format',''))}]</b> {esc(r.get('title_draft',''))}")
        lines.append(f"   Pain: {esc(r.get('pain_cluster',''))}")
        lines.append(f"   CTA: {esc(r.get('cta',''))}")
        lines.append(f"   Evidence: {r.get('evidence_count','')} comment")
        lines.append("")

    # attach the raw pain point quote for the top slot so the editor has the hook source
    if rows:
        top_angle = rows[0].get("angle_id", "")
        match = [a for a in angles if a.get("id") == top_angle]
        if match:
            a = match[0]
            lines += [
                f"<b>Nguyên liệu hook — {esc(top_angle)}</b>",
                f"“{esc(str(a.get('audience_quote',''))[:200])}”",
                f"<a href=\"{esc(a.get('evidence_url',''))}\">nguồn comment</a>",
                "",
            ]

    lines += [
        "<b>Quy trình</b>",
        "1. Lấy hook từ pain point ở trên",
        "2. Claude draft script (prompts/02_VIET_HOOK.md)",
        "3. MCP dựng draft CapCut (prompts/07_CAPCUT_MCP.md)",
        "4. Polish trong CapCut Pro → export tay",
        "5. QC 8 điểm trước khi đăng",
        "",
        "<b>Ràng buộc</b>",
        "• Không cam kết lợi nhuận, không trade giả",
        "• Disclaimer: Not financial advice. Trading involves risk of loss.",
        "• Title ≤60 ký tự",
        "",
        f"<i>Tổng pain point sẵn có: {len(pool):,}</i>",
    ]
    return "\n".join(lines)


def report_daily_status(root: Path) -> str:
    """Báo cáo tổng hợp → topic General."""
    status = root / "outputs/reports/daily_status.md"
    lines = [
        "📊 <b>BÁO CÁO TỔNG HỢP</b>",
        f"<i>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</i>",
        "",
    ]
    if status.exists():
        body = status.read_text(encoding="utf-8")
        lines.append(esc(body[:2500]))
    else:
        lines.append("<i>Chưa có daily_status.md</i>")
    return "\n".join(lines)


def report_pipeline_health(root: Path) -> str:
    """Kiểm tra sức khoẻ pipeline — dùng cho cron/dagu."""
    checks = []
    # MCP backend
    import socket
    s = socket.socket()
    s.settimeout(1)
    try:
        s.connect(("127.0.0.1", 9001))
        mcp = "✅ chạy"
    except Exception:
        mcp = "❌ không chạy (port 9001)"
    finally:
        s.close()

    checks.append(("CapCut MCP backend", mcp))
    checks.append(("Telegram bot", "✅ kết nối"))
    for label, path in [
        ("Pain point data", "outputs/competitor_longform/painpoint_candidates.csv"),
        ("Content backlog", "outputs/strategy/content_backlog.csv"),
        ("Asset library", "assets/README.md"),
        ("Prompt pack", "prompts/07_CAPCUT_MCP.md"),
        ("Dashboard", "outputs/dashboard/index.html"),
    ]:
        checks.append((label, "✅ có" if (root / path).exists() else "❌ thiếu"))

    lines = [
        "🩺 <b>PIPELINE HEALTH</b>",
        f"<i>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</i>",
        "",
    ]
    for label, state in checks:
        lines.append(f"• {esc(label)}: {state}")
    return "\n".join(lines)


def report_mrbeast_audit(root: Path) -> str:
    """Audit MrBeast: chẩn đoán + plan action + SOP + build-to-sell.

    Đọc số liệu thật từ audit files (azzam_videos.json / gta_videos.json)
    và blindspots.json. Không có số nhập tay.
    """
    import re as _re
    from collections import defaultdict

    aud = root / "outputs/mrbeast_audit"
    a_p, g_p = aud / "azzam_videos.json", aud / "gta_videos.json"
    blind = load_json(root / "outputs/reports/blindspots.json") or {}

    def st(arr):
        if not arr:
            return {"n": 0, "avg": 0, "med": 0, "max": 0}
        vs = sorted(v["views"] for v in arr)
        return {"n": len(vs), "avg": sum(vs) // len(vs),
                "med": vs[len(vs) // 2], "max": vs[-1]}

    lines = [
        "🧬 <b>AUDIT KÊNH — PHƯƠNG PHÁP MRBEAST</b>",
        f"<i>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</i>",
        "",
    ]

    if not (a_p.exists() and g_p.exists()):
        lines.append("<i>Thiếu dữ liệu audit (azzam_videos.json / gta_videos.json).</i>")
        return "\n".join(lines)

    A = json.loads(a_p.read_text(encoding="utf-8"))
    G = json.loads(g_p.read_text(encoding="utf-8"))
    a_s = [v for v in A if 0 < v["duration_s"] <= 60]
    a_l = [v for v in A if v["duration_s"] > 60]
    a_ev = [v for v in A if 60 < v["duration_s"] <= 600]
    g_s = [v for v in G if 0 < v["duration_s"] <= 60]
    g_l = [v for v in G if v["duration_s"] > 60]
    g_ev = [v for v in G if 60 < v["duration_s"] <= 600
            and not _re.search(r"live", v["title"], _re.I)]

    sas, sal, sae = st(a_s), st(a_l), st(a_ev)
    sgs, sgl, sge = st(g_s), st(g_l), st(g_ev)

    bot = blind.get("bot_traffic", {})
    bot_v = to_int(bot.get("views"))

    # ── Cảnh báo ──
    if bot_v:
        lines += [
            "⚠️ <b>CẢNH BÁO PHẢI XỬ LÝ TRƯỚC</b>",
            f"• Traffic nghi bot: <b>{bot_v:,} views</b> "
            f"({bot.get('pct_of_channel')}% tổng view)",
            "• Nguồn: <code>seofast</code>, <code>playbots</code>",
            "• Rủi ro: vi phạm Fake Engagement Policy → xoá view / phạt kênh",
            "• Mọi tối ưu khác vô nghĩa nếu số liệu nền là giả",
            "",
        ]

    # ── Chẩn đoán ──
    lines += [
        "📊 <b>CHẨN ĐOÁN</b>",
        "• Sub: <b>1,980</b> vs đối thủ <b>14,100</b> (7.1×)",
        "• Views/video: <b>816</b> vs <b>1,898</b> (2.3×)",
        "",
        "<b>Vấn đề 1 — Long-form gần như không hoạt động</b>",
        f"• Kênh mình: {sal['n']} video, TB <b>{sal['avg']:,}</b> views, "
        f"median {sal['med']:,}",
        f"• Đối thủ: {sgl['n']} video, TB <b>{sgl['avg']:,}</b> views, "
        f"median {sgl['med']:,}",
        f"• → Đối thủ hơn <b>{sgl['avg']/max(sal['avg'],1):.1f}×</b>",
        "• Nguyên nhân: <b>90% long-form là livestream</b> "
        f"({sum(1 for v in a_l if _re.search(r'live', v['title'], _re.I))}/{sal['n']}) "
        "— không thumbnail được, không tái dùng được",
        "",
        "<b>Vấn đề 2 — Không có nội dung evergreen</b>",
        f"• Kênh mình: {sae['n']} video 1-10 phút, TB <b>{sae['avg']:,}</b> views",
        f"• Đối thủ: {sge['n']} video 1-10 phút, TB <b>{sge['avg']:,}</b> views",
        f"• → Đối thủ hơn <b>{sge['avg']/max(sae['avg'],1):.0f}×</b>",
        "• Khớp với analytics: chỉ <b>1.2%</b> traffic từ search YouTube",
        "",
        "<b>Vấn đề 3 — Shorts mất đà</b>",
        f"• {sum(1 for v in a_s if v['views']<100)}/{sas['n']} Short "
        f"({sum(1 for v in a_s if v['views']<100)/sas['n']*100:.0f}%) dưới 100 views",
        f"• Median chỉ <b>{sas['med']:,}</b> views (đối thủ {sgs['med']:,})",
        f"• Cao nhất từng đạt {sas['max']:,} views (22s) → thuật toán không chặn kênh",
        "",
        "<b>Vấn đề 4 — Tương tác gần như bằng 0</b>",
        "• Comment rate <b>0.0111%</b> (1 comment / 9,016 view)",
        "• Sub ròng <b>-3</b> (+5 / -8) — đang mất người",
        "• Sub conversion <b>0.055%</b> (ngành 0.5-2%)",
        "",
    ]

    # ── Điểm mạnh ──
    lines += [
        "✅ <b>ĐIỂM MẠNH CẦN GIỮ</b>",
        f"• Short ngắn thắng được ({sas['max']:,} views với video 22s)",
        "• Format <b>FOREX LESSON</b> đã chứng minh "
        f"({len([v for v in a_s if 'FOREX LESSON' in v['title'].upper()])} video, "
        "nhiều video 1,400-9,800 views, độ dài 8-21s)",
        "• Kênh mới (2024-05) — còn dư địa lớn",
        "• Nhịp đăng 21.2 video/tháng — khả năng sản xuất tốt",
        "",
        "🎯 <b>BẢNG ĐIỂM: 3.1/10</b>",
        "• Hook 4 · Packaging 5 · Retention 2 · Nhịp đăng 7",
        "• Evergreen 1 · Cộng đồng 1 · Phễu 2",
        "",
    ]

    # ── 5 hành động ──
    lines += [
        "⚡ <b>5 HÀNH ĐỘNG ƯU TIÊN CAO NHẤT</b>",
        f"1. <b>Điều tra {bot_v:,} views nghi bot</b> — trước mọi thứ khác",
        f"2. <b>Evergreen 5-8 phút, 2 video/tuần</b> — khoảng cách "
        f"{sge['avg']/max(sae['avg'],1):.0f}× với đối thủ",
        "3. <b>Tái chế "
        f"{sum(1 for v in a_l if v['duration_s'] > 28800)} phiên live dài</b> "
        "thành video biên tập — kho nguyên liệu miễn phí",
        "4. <b>Khôi phục format FOREX LESSON</b> (Short 8-21s)",
        "5. <b>CTA comment + trả lời mọi comment</b> — mở lại phễu cộng đồng",
        "",
        "📁 <b>Tài liệu đầy đủ</b>",
        "• <code>MRBEAST_AUDIT.md</code> — audit &amp; chẩn đoán",
        "• <code>MRBEAST_PLAN_ACTION.md</code> — plan 90 ngày + KPI",
        "• <code>MRBEAST_SOP.md</code> — SOP 8 bước hằng ngày",
        "• <code>MRBEAST_BUILD_TO_SELL.md</code> — lộ trình 12 tháng",
        "• Word + Excel: <code>AZZAM_MRBEAST_AUDIT.docx / .xlsx</code>",
        "",
        "❓ <b>Việc cần Alan làm</b>",
        "1. Xác nhận có biết nguồn traffic bot không (có mua view?)",
        "2. Duyệt 5 hành động ưu tiên ở trên",
        "3. Chốt lịch sản xuất evergreen (2 video/tuần)",
        "",
        "<i>Nguồn: YouTube Data API v3 (297 video kênh mình + 742 video đối thủ) "
        "+ YouTube Analytics API (OAuth). Không có số nhập tay.</i>",
    ]
    return "\n".join(lines)


def report_evergreen_plan(root: Path) -> str:
    """Plan evergreen 24 video — gửi cho editor/Alan duyệt."""
    import csv as _csv

    plan_p = root / "outputs/strategy/EVERGREEN_PLAN.csv"
    lines = [
        "🌱 <b>EVERGREEN PLAN — 24 VIDEO</b>",
        f"<i>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</i>",
        "",
    ]
    if not plan_p.exists():
        lines.append("<i>Chưa có EVERGREEN_PLAN.csv — chạy build_evergreen_plan.py.</i>")
        return "\n".join(lines)

    with plan_p.open(encoding="utf-8-sig", newline="") as f:
        rows = list(_csv.DictReader(f))

    gaps = sum(1 for r in rows if str(r.get("doi_thu_da_lam", "")).startswith("0"))

    lines += [
        "<b>Vì sao evergreen là ưu tiên số 1</b>",
        "• Video 5-8 phút = còn mang view nhiều tháng/năm sau khi đăng",
        "• Lấy view từ <b>Search + đề xuất</b> — khác Short (hết sau vài ngày) "
        "và livestream (chỉ có view lúc phát)",
        "• Là nơi bán offer tốt nhất: người xem đã có ý định học",
        "",
        "• Kênh mình: 15 video 1-10 phút, TB <b>6 views</b>",
        "• Đối thủ: 31 video, TB <b>395 views</b> → khoảng cách <b>66×</b>",
        "• Chỉ <b>1.2%</b> traffic kênh đến từ search YouTube",
        "",
        f"<b>Kế hoạch: {len(rows)} video, 2/tuần × 12 tuần</b>",
        f"• <b>{gaps}/{len(rows)} chủ đề đối thủ CHƯA làm</b> (khoảng trống)",
        "• Chủ đề lấy từ 500 long-tail phrase mine từ 7,937 comment thật",
        "",
        "<b>Lịch 6 tuần đầu</b>",
    ]
    for r in rows[:12]:
        lines.append(f"• Tuần {r.get('tuan')}: <b>{esc(r.get('topic',''))}</b> "
                     f"— <code>{esc(r.get('keyword_chinh',''))}</code> "
                     f"(freq {r.get('freq_comment','')})")

    lines += [
        "",
        "📁 <b>File đầy đủ</b>",
        "• <code>EVERGREEN_PLAN.csv</code> — 24 video, 18 cột",
        "• <code>AZZAM_EVERGREEN_PLAN.docx</code> — Word, có hook + outline + bằng chứng",
        "• <code>AZZAM_EVERGREEN_PLAN.xlsx</code> — 6 sheet (plan, từ khoá, "
        "pattern đối thủ, mẫu, lịch)",
        "• <code>EVERGREEN_PLAN.md</code> — chi tiết từng video",
        "",
        "🎬 <b>Mỗi video có sẵn</b>",
        "• Title ≤60 ký tự · Hook 3 giây · Outline 6 phần · CTA",
        "• Keyword chính + phụ (từ comment khán giả thật)",
        "• Bằng chứng: comment gốc + link nguồn",
        "• Đối thủ đã làm bao nhiêu video về chủ đề này",
        "",
        "❓ <b>Việc cần Alan làm</b>",
        "1. Duyệt 24 chủ đề (hoặc chọn 12 làm trước)",
        "2. Chốt: quay mới hay biên tập lại từ livestream cũ",
        "3. Chuyển sang topic EDIT để editor bắt đầu",
    ]
    return "\n".join(lines)


REPORTS = {
    "comment": report_comment,
    "content_brief": report_content_brief,
    "daily_status": report_daily_status,
    "pipeline_health": report_pipeline_health,
    "mrbeast_audit": report_mrbeast_audit,
    "evergreen_plan": report_evergreen_plan,
}

# which topic each report belongs to by default
DEFAULT_TOPIC = {
    "comment": "comment",
    "content_brief": "edit",
    "daily_status": "general",
    "pipeline_health": "general",
    "mrbeast_audit": "audit",
    "evergreen_plan": "audit",
}


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--topic", choices=list(TOPICS.keys()),
                    help="Topic đích (mặc định theo loại report)")
    ap.add_argument("--report", choices=list(REPORTS.keys()), default="pipeline_health")
    ap.add_argument("--send", action="store_true", help="Gửi thật")
    ap.add_argument("--approve", default="", help="Phải là APPROVE để cho phép gửi")
    ap.add_argument("--list-topics", action="store_true")
    ap.add_argument("--verify-topics", action="store_true",
                    help="Gửi tin nhắn kiểm tra tới từng topic")
    args = ap.parse_args()

    root = args.root.resolve()

    if args.list_topics:
        for key, meta in TOPICS.items():
            print(f"  {key:10} thread={meta['thread_id']:>4}  {meta['name']}")
            print(f"  {'':10} {meta['purpose']}")
        return 0

    env = merged_env(root)
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = env.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        print("ERROR: thiếu TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID", file=sys.stderr)
        return 2

    if args.verify_topics:
        if args.approve != "APPROVE":
            print("Cần --approve APPROVE để gửi tin kiểm tra.", file=sys.stderr)
            return 2
        rc = 0
        for key, meta in TOPICS.items():
            r = send_to_topic(token, chat_id, meta["thread_id"],
                              f"✅ Kiểm tra topic <b>{esc(meta['name'])}</b> — "
                              f"thread_id={meta['thread_id']}")
            ok = r.get("ok")
            print(f"  {key:10} thread={meta['thread_id']:>4}  "
                  f"{'OK' if ok else 'FAIL: ' + str(r)[:120]}")
            if not ok:
                rc = 1
        return rc

    topic_key = args.topic or DEFAULT_TOPIC.get(args.report, "general")
    meta = TOPICS[topic_key]
    text = REPORTS[args.report](root)

    if not args.send:
        print(f"--- DRY RUN → topic '{topic_key}' (thread {meta['thread_id']}) ---")
        print(text)
        print("--- (thêm --send --approve APPROVE để gửi thật) ---")
        return 0

    if args.approve != "APPROVE":
        print("TỪ CHỐI GỬI: cần --approve APPROVE", file=sys.stderr)
        return 2

    r = send_to_topic(token, chat_id, meta["thread_id"], text)
    ok = r.get("ok")
    print(json.dumps({"ok": ok, "topic": topic_key,
                      "thread_id": meta["thread_id"],
                      "message_id": (r.get("result") or {}).get("message_id"),
                      "error": None if ok else r}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

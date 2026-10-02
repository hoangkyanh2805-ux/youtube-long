"""
Build a multi-sheet Excel workbook from all analysis outputs.

Writes: outputs/reports/AZZAM_PHAN_TICH_DOI_THU.xlsx

Sheets:
  01_TONG_QUAN          executive summary + data-quality caveats
  02_KENH_DOI_THU       competitor channel metadata
  03_VIDEO_INVENTORY    unique videos (deduped) with stats + derived metrics
  04_SALES_ANGLES       8 angles with evidence + funnel mapping
  05_CONTENT_BACKLOG    prioritized content queue
  06_KEYWORD_CHINH      main keyword frequency
  07_KEYWORD_DAI        long-tail (audience language)
  08_TITLE_PATTERN      competitor title patterns
  09_PAINPOINT_ALL      all pain points, deduped, flagged by source run
  10_COMMENTS_RAW       all normalized comments, deduped
  11_LICH_DANG          publishing calendar

Design rules:
  - Every count is computed from data, never hardcoded.
  - Dedupe by comment_id / video_id before writing, and say so in the sheet.
  - Freeze header row, autofilter, column widths, number formats.
"""
from __future__ import annotations

import csv
import json
import re
from datetime import date
from html import unescape
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
import sys

# Force UTF-8 console: without this, printing Vietnamese crashes with
# UnicodeEncodeError when stdout is a pipe (dagu/cron/CI).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402
ensure_utf8_console()

OUT = Path("outputs/reports")
OUT.mkdir(parents=True, exist_ok=True)

HEADER_FILL = PatternFill("solid", fgColor="1F3864")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=10)
TITLE_FONT = Font(bold=True, size=14, color="1F3864")
NOTE_FONT = Font(italic=True, size=9, color="555555")
WARN_FONT = Font(italic=True, size=9, color="B03060")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


# ── Loaders ─────────────────────────────────────────────────────────────────

def load_csv(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_json(path: str):
    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def parse_iso_seconds(d: str) -> int:
    if not d or not d.startswith("PT"):
        return 0
    total, num = 0, ""
    for ch in d[2:]:
        if ch.isdigit():
            num += ch
            continue
        if not num:
            continue
        n = int(num)
        if ch == "H":
            total += n * 3600
        elif ch == "M":
            total += n * 60
        elif ch == "S":
            total += n
        num = ""
    return total


def to_int(v, default: int = 0) -> int:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def to_float(v, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


# ── Sheet helpers ───────────────────────────────────────────────────────────

def setup_sheet(ws, title: str, note: str | None = None):
    """Write a sheet title (+ optional note) and return the header row index."""
    ws["A1"] = title
    ws["A1"].font = TITLE_FONT
    row = 2
    if note:
        ws.cell(row=row, column=1, value=note).font = NOTE_FONT
        row += 1
    ws.freeze_panes = None
    return row + 1  # leave one blank row before the table


def write_table(ws, start_row: int, headers: list[str], rows: list[list],
                widths: dict[str, int] | None = None,
                number_cols: set[str] | None = None,
                wrap_cols: set[str] | None = None,
                col_formats: dict[str, str] | None = None):
    """Write a header + data table, style it, add autofilter."""
    widths = widths or {}
    number_cols = number_cols or set()
    wrap_cols = wrap_cols or set()
    col_formats = col_formats or {}

    for j, h in enumerate(headers, 1):
        c = ws.cell(row=start_row, column=j, value=h)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER

    for i, row in enumerate(rows, start=start_row + 1):
        for j, val in enumerate(row, 1):
            c = ws.cell(row=i, column=j, value=val)
            c.border = BORDER
            c.font = Font(size=10)
            if headers[j - 1] in number_cols and isinstance(val, (int, float)):
                c.alignment = Alignment(horizontal="right")
                c.number_format = col_formats.get(headers[j - 1], "#,##0")
            elif headers[j - 1] in wrap_cols:
                c.alignment = Alignment(wrap_text=True, vertical="top")
            else:
                c.alignment = Alignment(vertical="top")

    for j, h in enumerate(headers, 1):
        letter = get_column_letter(j)
        if h in widths:
            ws.column_dimensions[letter].width = widths[h]
        else:
            # auto width from content, capped
            longest = len(str(h))
            for row in rows[:300]:
                if j - 1 < len(row):
                    longest = max(longest, len(str(row[j - 1])))
            ws.column_dimensions[letter].width = min(max(longest + 2, 10), 60)

    if rows:
        ws.auto_filter.ref = (
            f"A{start_row}:{get_column_letter(len(headers))}{start_row + len(rows)}"
        )
    ws.freeze_panes = ws.cell(row=start_row + 1, column=1)


def add_warning(ws, row: int, text: str) -> int:
    c = ws.cell(row=row, column=1, value=text)
    c.font = WARN_FONT
    return row + 1


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> int:
    wb = Workbook()

    # ═══ Load everything once ═══════════════════════════════════════════════
    channels = load_json("outputs/competitor_analysis/channels_info.json") or {}
    shorts_inv = load_csv("outputs/competitor_analysis/shorts_inventory.csv")
    long_inv = load_csv("outputs/competitor_longform/longform_inventory.csv")
    pp_shorts = load_csv("outputs/competitor_analysis/painpoint_candidates.csv")
    pp_long = load_csv("outputs/competitor_longform/painpoint_candidates.csv")
    cm_shorts = load_csv("outputs/competitor_analysis/normalized_comments.csv")
    cm_long = load_csv("outputs/competitor_longform/normalized_comments.csv")
    angles = load_json("outputs/strategy/sales_angles.json") or []
    kw_main = load_json("outputs/strategy/keywords_main.json") or {}
    kw_long = load_json("outputs/strategy/keywords_longtail.json") or {}
    kw_title = load_json("outputs/strategy/keywords_title_patterns.json") or {}
    backlog = load_csv("outputs/strategy/content_backlog.csv")

    # ── Dedupe (the two runs overlap ~57%) ────────────────────────────────
    vid_merge: dict[str, dict] = {}
    for v in shorts_inv + long_inv:
        vid = v.get("video_id", "")
        if not vid:
            continue
        if vid not in vid_merge:
            vid_merge[vid] = dict(v)
        elif not parse_iso_seconds(vid_merge[vid].get("duration", "")) \
                and parse_iso_seconds(v.get("duration", "")):
            vid_merge[vid] = dict(v)
    videos = [v for v in vid_merge.values() if to_int(v.get("views")) > 0]

    def dedupe_by_cid(rows: list[dict]) -> list[dict]:
        out, seen = [], set()
        for r in rows:
            cid = r.get("comment_id", "")
            key = cid or f"{r.get('content_url','')}|{r.get('comment_text','')[:80]}"
            if key in seen:
                continue
            seen.add(key)
            out.append(r)
        return out

    pain_all = dedupe_by_cid(pp_shorts + pp_long)
    comments_all = dedupe_by_cid(cm_shorts + cm_long)

    raw_comments = len(cm_shorts) + len(cm_long)
    raw_pain = len(pp_shorts) + len(pp_long)

    # ═══ 01 TỔNG QUAN ══════════════════════════════════════════════════════
    ws = wb.active
    ws.title = "01_TONG_QUAN"
    ws["A1"] = "BÁO CÁO PHÂN TÍCH ĐỐI THỦ & CHIẾN LƯỢC KÊNH"
    ws["A1"].font = Font(bold=True, size=16, color="1F3864")
    ws["A2"] = "@azzammastertradinggold  •  Ngách: XAUUSD / Forex"
    ws["A2"].font = Font(bold=True, size=11)
    ws["A3"] = f"Ngày lập: {date.today().isoformat()}"
    ws["A3"].font = NOTE_FONT
    ws["A4"] = ("Nguồn: YouTube Data API v3 — channels.list, search.list, "
                "videos.list, commentThreads.list")
    ws["A4"].font = NOTE_FONT

    r = 6
    ws.cell(row=r, column=1, value="CHỈ SỐ CHÍNH").font = Font(bold=True, size=12, color="1F3864")
    r += 1
    metrics = [
        ("Kênh đối thủ phân tích", len(channels)),
        ("Video (unique, đã dedupe)", len(videos)),
        ("Video — nguồn video ngắn (raw)", len(shorts_inv)),
        ("Video — nguồn video dài (raw)", len(long_inv)),
        ("Comments (raw)", raw_comments),
        ("Comments (unique sau dedupe)", len(comments_all)),
        ("Comments trùng giữa 2 run", raw_comments - len(comments_all)),
        ("Pain-point (raw)", raw_pain),
        ("Pain-point (unique sau dedupe)", len(pain_all)),
        ("Sales angles", len(angles)),
        ("Content backlog", len(backlog)),
    ]
    write_table(ws, r, ["Chỉ số", "Giá trị"],
                [[k, v] for k, v in metrics],
                widths={"Chỉ số": 40, "Giá trị": 14},
                number_cols={"Giá trị"})

    r = r + len(metrics) + 3
    ws.cell(row=r, column=1, value="PHÁT HIỆN CHÍNH").font = Font(bold=True, size=12, color="1F3864")
    r += 1
    for txt in [
        "Hai run thu thập (video ngắn + video dài) trùng nhau phần lớn — số raw phải "
        "dedupe theo comment_id / video_id trước khi dùng.",
        "Video 15-30 phút thắng rõ rệt về median views so với nhóm ngắn hơn.",
        "Pain point lớn nhất: học sai thứ tự — nhảy vào SMC/ICT khi chưa vững basic.",
        "Tham số duration=short của YouTube API không lọc được Shorts thật.",
    ]:
        c = ws.cell(row=r, column=1, value="• " + txt)
        c.font = Font(size=10)
        c.alignment = Alignment(wrap_text=True)
        r += 1

    r += 1
    ws.cell(row=r, column=1, value="CẢNH BÁO CHẤT LƯỢNG DỮ LIỆU").font = \
        Font(bold=True, size=12, color="B03060")
    r += 1
    for txt in [
        "search.list với duration=short KHÔNG lọc Shorts: nhiều video trả về dài 10-30 phút.",
        "Không có search volume thật (không có Keyword Planner) — chỉ có tần suất trong dữ liệu.",
        "Không có retention / CTR / watch time (không có YouTube Analytics access).",
        "Category do bộ phân loại từ khoá gán tự động — bucket rộng như education_gap "
        "có thể phóng đại độ mạnh tín hiệu.",
        "Không có số liệu nào được tạo ra ngoài dữ liệu API trả về.",
    ]:
        add_warning(ws, r, "! " + txt)
        ws.cell(row=r, column=1).alignment = Alignment(wrap_text=True)
        r += 1

    # ═══ 02 KÊNH ĐỐI THỦ ═══════════════════════════════════════════════════
    ws = wb.create_sheet("02_KENH_DOI_THU")
    hdr = setup_sheet(ws, "KÊNH ĐỐI THỦ — THÔNG TIN CƠ BẢN",
                      "Nguồn: channels.list (part=snippet,statistics,brandingSettings)")
    rows = []
    for handle, info in channels.items():
        s = info.get("statistics", {})
        sn = info.get("snippet", {})
        rows.append([
            handle,
            sn.get("title", ""),
            info.get("id", ""),
            to_int(s.get("subscriberCount")),
            to_int(s.get("viewCount")),
            to_int(s.get("videoCount")),
            sn.get("country", "N/A"),
            unescape(sn.get("description", ""))[:300],
        ])
    write_table(ws, hdr,
                ["Handle", "Tên kênh", "Channel ID", "Subscribers", "Tổng views",
                 "Số video", "Quốc gia", "Mô tả"],
                rows,
                widths={"Handle": 20, "Tên kênh": 18, "Channel ID": 26,
                        "Subscribers": 14, "Tổng views": 15, "Số video": 11,
                        "Quốc gia": 11, "Mô tả": 70},
                number_cols={"Subscribers", "Tổng views", "Số video"},
                wrap_cols={"Mô tả"})

    # ═══ 03 VIDEO INVENTORY ════════════════════════════════════════════════
    ws = wb.create_sheet("03_VIDEO_INVENTORY")
    hdr = setup_sheet(
        ws, "VIDEO INVENTORY (unique, đã dedupe theo video_id)",
        f"Raw: {len(shorts_inv)} (nguồn video ngắn) + {len(long_inv)} (nguồn video dài) "
        f"→ {len(videos)} unique. Cột Nhóm thời lượng tính từ duration thật.")
    rows = []
    for v in sorted(videos, key=lambda x: -to_int(x.get("views"))):
        dur = parse_iso_seconds(v.get("duration", ""))
        views = to_int(v.get("views"))
        likes = to_int(v.get("likes"))
        cmts = to_int(v.get("comments"))
        if dur == 0:
            grp = "không rõ"
        elif dur <= 60:
            grp = "≤60s (Short thật)"
        elif dur <= 300:
            grp = "1-5 phút"
        elif dur <= 900:
            grp = "5-15 phút"
        elif dur <= 1800:
            grp = "15-30 phút"
        else:
            grp = "30+ phút"
        rows.append([
            v.get("video_id", ""),
            unescape(v.get("title", "")),
            v.get("channel", ""),
            v.get("url", ""),
            (v.get("published", "") or "")[:10],
            views,
            likes,
            cmts,
            dur,
            grp,
            round(likes / views * 100, 2) if views else 0,
            round(cmts / views * 100, 2) if views else 0,
        ])
    write_table(ws, hdr,
                ["Video ID", "Tiêu đề", "Kênh", "URL", "Ngày đăng", "Views",
                 "Likes", "Comments", "Giây", "Nhóm thời lượng",
                 "Like rate %", "Comment rate %"],
                rows,
                widths={"Video ID": 14, "Tiêu đề": 60, "Kênh": 16, "URL": 42,
                        "Ngày đăng": 12, "Views": 12, "Likes": 10, "Comments": 10,
                        "Giây": 8, "Nhóm thời lượng": 17,
                        "Like rate %": 12, "Comment rate %": 15},
                number_cols={"Views", "Likes", "Comments", "Giây",
                             "Like rate %", "Comment rate %"},
                col_formats={"Like rate %": "0.00", "Comment rate %": "0.00"})

    # ═══ 04 SALES ANGLES ═══════════════════════════════════════════════════
    ws = wb.create_sheet("04_SALES_ANGLES")
    hdr = setup_sheet(
        ws, "SALES ANGLES — 8 GÓC BÁN HÀNG TỪ PAIN POINT THẬT",
        "Evidence = số comment pain-point unique khớp angle. Mọi quote đều có "
        "comment_id + URL để đối chiếu. Draft — cần duyệt trước khi dùng.")
    offer_map = {
        "SA-01": ("Trading Plan Template", "Complete System", "Journal app"),
        "SA-02": ("1-Setup Template", "Complete System", "TradingView"),
        "SA-03": ("Risk Calculator", "Complete System", "Broker IB"),
        "SA-04": ("Entry Checklist", "Complete System", "TradingView"),
        "SA-05": ("Trading Journal", "VIP Mentorship", "Journal app"),
        "SA-06": ("Telegram group access", "VIP Mentorship", "—"),
        "SA-07": ("30-Day Roadmap", "Core Course", "—"),
        "SA-08": ("Prop Firm Checklist", "—", "Prop firm affiliate"),
    }
    rows = []
    for a in angles:
        lm, off, aff = offer_map.get(a["id"], ("—", "—", "—"))
        rows.append([
            a["id"],
            a["pain_cluster"],
            a.get("evidence_count", 0),
            a.get("category_evidence", 0),
            a.get("keyword_evidence", 0),
            unescape(a.get("audience_quote", "")),
            a.get("evidence_url", ""),
            a.get("evidence_comment_id", ""),
            a.get("sales_angle", ""),
            a.get("big_promise", ""),
            a.get("proof_hook", ""),
            a.get("urgency", ""),
            a.get("cta", ""),
            " | ".join(a.get("content_formats", [])),
            lm, off, aff,
        ])
    write_table(ws, hdr,
                ["ID", "Pain cluster", "Evidence", "Ev. category", "Ev. keyword",
                 "Quote khán giả", "URL nguồn", "Comment ID", "Sales angle",
                 "Big promise", "Proof hook", "Urgency", "CTA",
                 "Format đề xuất", "Lead magnet", "Offer", "Affiliate"],
                rows,
                widths={"ID": 8, "Pain cluster": 34, "Evidence": 10,
                        "Ev. category": 12, "Ev. keyword": 12,
                        "Quote khán giả": 65, "URL nguồn": 40, "Comment ID": 26,
                        "Sales angle": 50, "Big promise": 50, "Proof hook": 50,
                        "Urgency": 45, "CTA": 30, "Format đề xuất": 45,
                        "Lead magnet": 22, "Offer": 18, "Affiliate": 20},
                number_cols={"Evidence", "Ev. category", "Ev. keyword"},
                wrap_cols={"Quote khán giả", "Sales angle", "Big promise",
                           "Proof hook", "Urgency", "Format đề xuất"})

    # ═══ 05 CONTENT BACKLOG ════════════════════════════════════════════════
    ws = wb.create_sheet("05_CONTENT_BACKLOG")
    hdr = setup_sheet(ws, "CONTENT BACKLOG — ƯU TIÊN THEO EVIDENCE",
                      "Sắp theo số comment pain-point. Status = draft, cần human approval.")
    rows = []
    for b in sorted(backlog, key=lambda x: -to_int(x.get("priority"))):
        rows.append([
            to_int(b.get("priority")),
            b.get("angle_id", ""),
            b.get("pain_cluster", ""),
            b.get("format", ""),
            unescape(b.get("title_draft", "")),
            b.get("keyword", ""),
            b.get("cta", ""),
            to_int(b.get("evidence_count")),
            b.get("evidence_url", ""),
            b.get("status", ""),
        ])
    write_table(ws, hdr,
                ["Ưu tiên", "Angle", "Pain cluster", "Format", "Tiêu đề nháp",
                 "Keyword", "CTA", "Evidence", "URL nguồn", "Status"],
                rows,
                widths={"Ưu tiên": 10, "Angle": 9, "Pain cluster": 34,
                        "Format": 9, "Tiêu đề nháp": 50, "Keyword": 20,
                        "CTA": 40, "Evidence": 10, "URL nguồn": 42, "Status": 28},
                number_cols={"Ưu tiên", "Evidence"},
                wrap_cols={"Tiêu đề nháp", "CTA"})

    # ═══ 06 KEYWORD CHÍNH ══════════════════════════════════════════════════
    ws = wb.create_sheet("06_KEYWORD_CHINH")
    hdr = setup_sheet(
        ws, "TỪ KHOÁ CHÍNH — TẦN SUẤT TRONG COMMENT",
        f"Nguồn: mine từ {kw_main.get('total_comments', 0):,} comment unique + "
        f"{kw_main.get('total_pain_points', 0):,} pain point. "
        "KHÔNG phải search volume — chỉ là tần suất xuất hiện.")
    rows = []
    for i, w in enumerate(kw_main.get("top_unigrams", []), 1):
        f = w.get("freq", 0)
        prio = "CAO" if f >= 100 else ("TRUNG" if f >= 40 else "THẤP")
        rows.append([i, w.get("word", ""), f, prio])
    write_table(ws, hdr, ["#", "Từ khoá", "Tần suất", "Ưu tiên"], rows,
                widths={"#": 6, "Từ khoá": 24, "Tần suất": 12, "Ưu tiên": 11},
                number_cols={"Tần suất"})

    # ═══ 07 KEYWORD DÀI ════════════════════════════════════════════════════
    ws = wb.create_sheet("07_KEYWORD_DAI")
    hdr = setup_sheet(
        ws, "TỪ KHOÁ DÀI — NGÔN NGỮ KHÁN GIẢ (từ comment text)",
        "Dùng làm hook / tiêu đề. Tần suất = số comment chứa cụm này.")
    rows = []
    for i, t in enumerate(kw_long.get("top_longtail", []), 1):
        f = t.get("freq", 0)
        rows.append([i, t.get("phrase", ""), f, t.get("words", 0),
                     "Title + Description" if f >= 6 else "Tag + Description"])
    write_table(ws, hdr, ["#", "Cụm từ", "Tần suất", "Số từ", "Dùng cho"], rows,
                widths={"#": 6, "Cụm từ": 34, "Tần suất": 11, "Số từ": 8,
                        "Dùng cho": 22},
                number_cols={"Tần suất", "Số từ"})

    # ═══ 08 TITLE PATTERN ══════════════════════════════════════════════════
    ws = wb.create_sheet("08_TITLE_PATTERN")
    hdr = setup_sheet(
        ws, "PATTERN TIÊU ĐỀ ĐỐI THỦ",
        "Mine 1 lần / video unique (không phải 1 lần / comment) — dùng làm công thức "
        "đặt tiêu đề, không phải tần suất khán giả.")
    rows = []
    for i, t in enumerate(kw_title.get("top_patterns", []), 1):
        rows.append([i, t.get("phrase", ""), t.get("video_count", 0)])
    write_table(ws, hdr, ["#", "Pattern tiêu đề", "Số video dùng"], rows,
                widths={"#": 6, "Pattern tiêu đề": 40, "Số video dùng": 15},
                number_cols={"Số video dùng"})

    # ═══ 09 PAINPOINT ALL ══════════════════════════════════════════════════
    ws = wb.create_sheet("09_PAINPOINT_ALL")
    hdr = setup_sheet(
        ws, "TẤT CẢ PAIN POINT (unique, đã dedupe)",
        f"Raw {raw_pain:,} → unique {len(pain_all):,}. Đã lọc spam + domain relevance. "
        "Giữ comment_id + URL để truy vết.")
    rows = []
    for p in sorted(pain_all, key=lambda x: -to_float(x.get("score"))):
        rows.append([
            to_float(p.get("score")),
            p.get("categories", ""),
            to_int(p.get("engagement_likes")),
            to_int(p.get("reply_count")),
            unescape(p.get("comment_text", "")),
            p.get("content_url", ""),
            p.get("comment_id", ""),
            p.get("source_actor", ""),
        ])
    write_table(ws, hdr,
                ["Score", "Categories", "Likes", "Replies", "Nội dung comment",
                 "URL nguồn", "Comment ID", "Nguồn thu thập"],
                rows,
                widths={"Score": 9, "Categories": 32, "Likes": 8, "Replies": 9,
                        "Nội dung comment": 90, "URL nguồn": 42,
                        "Comment ID": 26, "Nguồn thu thập": 34},
                number_cols={"Score", "Likes", "Replies"},
                col_formats={"Score": "0.000"},
                wrap_cols={"Nội dung comment"})

    # ═══ 10 COMMENTS RAW ═══════════════════════════════════════════════════
    ws = wb.create_sheet("10_COMMENTS_RAW")
    hdr = setup_sheet(
        ws, "TẤT CẢ COMMENT (unique, đã dedupe)",
        f"Raw {raw_comments:,} → unique {len(comments_all):,}. "
        "Reply của chính chủ kênh đã bị loại.")
    rows = []
    for c in comments_all:
        rows.append([
            c.get("channel_or_account", ""),
            c.get("video_title", "") and unescape(c.get("video_title", "")) or "",
            unescape(c.get("comment_text", "")),
            to_int(c.get("engagement_likes")),
            to_int(c.get("reply_count")),
            (c.get("comment_timestamp", "") or "")[:19],
            c.get("content_url", ""),
            c.get("comment_id", ""),
        ])
    write_table(ws, hdr,
                ["Kênh", "Video", "Nội dung comment", "Likes", "Replies",
                 "Thời điểm", "URL", "Comment ID"],
                rows,
                widths={"Kênh": 16, "Video": 50, "Nội dung comment": 90,
                        "Likes": 8, "Replies": 9, "Thời điểm": 20,
                        "URL": 42, "Comment ID": 26},
                number_cols={"Likes", "Replies"},
                wrap_cols={"Nội dung comment"})

    # ═══ 11 LỊCH ĐĂNG ══════════════════════════════════════════════════════
    ws = wb.create_sheet("11_LICH_DANG")
    hdr = setup_sheet(ws, "LỊCH ĐĂNG ĐỀ XUẤT (1 tuần mẫu)",
                      "Keyword lấy từ sheet 06/07. Điều chỉnh theo năng lực sản xuất thực tế.")
    cal = [
        ("Thứ 2", "Short", "3 dấu hiệu bạn thiếu hệ thống", "trading discipline", "Comment 'PLAN'"),
        ("Thứ 2", "Short", "1 lệnh này xoá sạch tài khoản", "risk management", "Comment 'RISK'"),
        ("Thứ 3", "Long", "5 Risk Rules Saved My Account", "risk management", "Join Telegram"),
        ("Thứ 4", "Short", "Đừng học ICT khi chưa biết cái này", "trading basics", "Comment 'ROADMAP'"),
        ("Thứ 4", "Live", "XAUUSD London Session Bias", "xauusd", "Join Telegram"),
        ("Thứ 5", "Short", "Revenge trading: 3 quy tắc chặn", "trading psychology", "Comment 'PSYCH'"),
        ("Thứ 6", "Long", "Entry Confirmation A-Z", "entry timing", "Comment 'ENTRY'"),
        ("Thứ 6", "Live", "XAUUSD NY Session", "xauusd", "Join Telegram"),
        ("Thứ 7", "Short", "Prop firm: đọc cái này trước khi mua", "prop firm", "Comment 'PROP'"),
        ("Chủ nhật", "Short", "Trading một mình = thua chậm", "trading community", "Join Telegram"),
    ]
    write_table(ws, hdr, ["Ngày", "Loại", "Nội dung", "Keyword chính", "CTA"], cal,
                widths={"Ngày": 11, "Loại": 9, "Nội dung": 42, "Keyword chính": 22,
                        "CTA": 20})

    # ── Save ───────────────────────────────────────────────────────────────
    out_path = OUT / "AZZAM_PHAN_TICH_DOI_THU.xlsx"
    wb.save(out_path)

    print(f"Saved: {out_path.resolve()}")
    print(f"Size: {out_path.stat().st_size:,} bytes")
    print(f"Sheets: {len(wb.sheetnames)}")
    for s in wb.sheetnames:
        print(f"  - {s}")
    print()
    print(f"Videos unique: {len(videos)} | Comments unique: {len(comments_all)} "
          f"(raw {raw_comments}) | Pain unique: {len(pain_all)} (raw {raw_pain})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

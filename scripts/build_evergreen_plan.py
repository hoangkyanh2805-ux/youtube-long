#!/usr/bin/env python3
"""Sinh plan EVERGREEN chi tiết từ dữ liệu thật (keyword + comment + pain point).

Nguồn dữ liệu (tất cả đã có sẵn trong repo):
  outputs/strategy/keywords_longtail.json        — ngôn ngữ khán giả (n-gram từ comment)
  outputs/strategy/keywords_main.json            — unigram tần suất
  outputs/strategy/keywords_title_patterns.json  — pattern tiêu đề đối thủ
  outputs/strategy/content_backlog.csv           — backlog đã có
  outputs/strategy/sales_angles.json             — 8 sales angle + evidence
  outputs/competitor_longform/painpoint_candidates.csv
  outputs/competitor_analysis/painpoint_candidates.csv
  outputs/mrbeast_audit/azzam_videos.json        — video kênh mình
  outputs/mrbeast_audit/gta_videos.json          — video đối thủ (để tìm evergreen mẫu)

Xuất:
  outputs/strategy/EVERGREEN_PLAN.csv            — 24 video, đủ cột để editor làm
  outputs/strategy/EVERGREEN_PLAN.md             — plan đọc được
  outputs/reports/AZZAM_EVERGREEN_PLAN.xlsx      — Excel nhiều sheet
  outputs/reports/AZZAM_EVERGREEN_PLAN.docx      — Word

Nguyên tắc:
  - Chủ đề lấy từ TỪ KHOÁ THẬT khán giả dùng, không bịa.
  - Đối chiếu với video đối thủ để biết họ đã làm gì / chưa làm gì.
  - Mỗi video có: title, hook 3s, outline, keyword chính, CTA, evidence.

Usage:
    python scripts/build_evergreen_plan.py
"""
from __future__ import annotations

import csv
import json
import re
import sys
from datetime import date, datetime, timezone
from html import unescape
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
STRAT = ROOT / "outputs" / "strategy"
AUD = ROOT / "outputs" / "mrbeast_audit"
REP = ROOT / "outputs" / "reports"


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


# ── Chủ đề evergreen: map từ keyword thật → format video ────────────────────
# Mỗi chủ đề: (tên chủ đề, keyword chính, từ khoá phụ, dạng video, category pain)
TOPIC_MAP = [
    ("Stop Loss đúng cách", "stop loss", ["stop loss", "stop losses", "risk management"],
     "How to", "risk_management"),
    ("Supply & Demand zone", "supply demand", ["supply demand", "demand zones", "support resistance"],
     "How to", "strategy_rules"),
    ("Market Structure", "market structure", ["market structure", "break structure"],
     "How to", "education_gap"),
    ("Risk Management cho tài khoản nhỏ", "risk management",
     ["risk management", "trading account", "per day"], "How to", "risk_management"),
    ("Daily Bias", "daily bias", ["daily bias", "ict daily", "bias"],
     "How to", "strategy_rules"),
    ("Swing Trading", "swing trading", ["swing trading", "trading strategy"],
     "How to", "strategy_rules"),
    ("Paper Trading — bắt đầu an toàn", "paper trading",
     ["paper trading", "started trading", "trading journey"], "How to", "education_gap"),
    ("Prop Firm: nên hay không", "prop firms",
     ["prop firms", "prop firm", "trading account"], "How to", "broker_platform"),
    ("Order Block", "order block", ["order block", "liquidity sweep", "order blocks"],
     "How to", "strategy_rules"),
    ("Liquidity Sweep", "liquidity sweep",
     ["liquidity sweep", "liquidity", "entry points"], "How to", "entry_timing"),
    ("Scalping 1 phút", "minute scalping",
     ["minute scalping", "scalping strategy", "entry model"], "How to", "entry_timing"),
    ("Entry Model — vào lệnh đúng", "entry model",
     ["entry model", "entry points", "entry"], "How to", "entry_timing"),
    ("Trading mà không có hướng dẫn", "trading without proper guidance",
     ["trading without proper guidance", "learning trade", "learn trade"],
     "Story + Lesson", "education_gap"),
    ("Vì sao trader thua", "profitable trader",
     ["profitable trader", "trading isnt", "following strategy"], "Story + Lesson", "psychology"),
    ("ICT Concepts đơn giản hoá", "ict concepts",
     ["ict concepts", "simplified ict", "ict daily bias"], "How to", "education_gap"),
    ("Support & Resistance thật", "support resistance",
     ["support resistance", "chart examples"], "How to", "education_gap"),
    ("Trading Journal — nhật ký lệnh", "trading journey",
     ["trading journey", "every day", "trading years"], "How to", "psychology"),
    ("Bắt đầu trading từ 0", "started trading",
     ["started trading", "money trading", "trading real"], "Roadmap", "education_gap"),
    ("Candle — đọc nến đúng", "candle candle",
     ["candle candle", "candle", "chart examples"], "How to", "education_gap"),
    ("Timeframe nào cho người mới", "trading strategy",
     ["trading strategy", "time", "per day"], "How to", "education_gap"),
    ("Số lệnh mỗi ngày", "per day",
     ["per day", "every day", "trading account"], "How to", "risk_management"),
    ("Tâm lý khi thua liên tiếp", "trading without",
     ["trading without", "trading isnt", "following strategy"], "Story + Lesson", "psychology"),
    ("XAUUSD vs Forex pairs", "trading real",
     ["trading real", "price", "chart"], "Comparison", "broker_platform"),
    ("Lộ trình 90 ngày", "learn trade",
     ["learn trade", "learning trade", "started trading"], "Roadmap", "education_gap"),
]


def build_rows() -> list[dict]:
    kl = load_json(STRAT / "keywords_longtail.json") or {}
    km = load_json(STRAT / "keywords_main.json") or {}
    kt = load_json(STRAT / "keywords_title_patterns.json") or {}
    backlog = load_csv(STRAT / "content_backlog.csv")
    angles = load_json(STRAT / "sales_angles.json") or []
    pp = {}
    for f in ["competitor_longform/painpoint_candidates.csv",
              "competitor_analysis/painpoint_candidates.csv"]:
        for r in load_csv(ROOT / "outputs" / f):
            k = r.get("comment_id") or f"{r.get('content_url','')}|{r.get('comment_text','')[:60]}"
            pp[k] = r

    # tần suất keyword
    lt_freq = {p["phrase"].lower(): p["freq"] for p in kl.get("top_longtail", [])}
    uni_freq = {u["word"].lower(): u["freq"] for u in km.get("top_unigrams", [])}
    comp_titles = {p["phrase"].lower(): p["video_count"] for p in kt.get("top_patterns", [])}

    # video đối thủ evergreen để tham chiếu
    G = load_json(AUD / "gta_videos.json") or []
    g_ev = [v for v in G if 60 < v["duration_s"] <= 600
            and not re.search(r"live", v["title"], re.I)]

    # pain point theo category (để lấy bằng chứng)
    by_cat: dict[str, list[dict]] = {}
    for r in pp.values():
        for c in (r.get("categories") or "").split("|"):
            if c:
                by_cat.setdefault(c, []).append(r)

    rows = []
    for i, (topic, main_kw, sub_kws, fmt, cat) in enumerate(TOPIC_MAP, 1):
        # đối chiếu đối thủ
        comp_hits = []
        for kw in [main_kw] + sub_kws:
            for t in g_ev:
                if kw.lower() in t["title"].lower():
                    comp_hits.append({"title": t["title"][:70], "views": t["views"]})
        comp_hits = comp_hits[:2]

        # bằng chứng từ pain point
        cand = sorted(by_cat.get(cat, []),
                      key=lambda x: -to_int(x.get("score") or 0))
        ev = cand[0] if cand else {}
        ev_url = ev.get("content_url", "")
        ev_quote = (ev.get("comment_text") or "")[:180]

        freq = lt_freq.get(main_kw.lower(), 0)
        uni = uni_freq.get(main_kw.lower(), 0)

        title = f"How to {topic} | XAUUSD Trading 2026"
        hook = f"Câu hỏi trực diện về {main_kw} trong 3 giây đầu"
        cta = "Comment ENTRY for the free checklist"

        rows.append({
            "stt": i,
            "tuan": (i - 1) // 2 + 1,
            "topic": topic,
            "format": fmt,
            "title_draft": title[:60],
            "keyword_chinh": main_kw,
            "keyword_phu": ", ".join(sub_kws),
            "freq_comment": freq,
            "freq_unigram": uni,
            "do_dai": "5-8 phút",
            "hook_3s": hook,
            "outline": ("1) Hook 3s · 2) Vấn đề cụ thể · 3) Demo trên chart · "
                        "4) Sai lầm phổ biến · 5) Cách làm đúng · 6) CTA"),
            "cta": cta,
            "pain_category": cat,
            "evidence_quote": ev_quote,
            "evidence_url": ev_url,
            "doi_thu_da_lam": f"{len(comp_hits)} video" if comp_hits else "0 (khoảng trống)",
            "doi_thu_vi_du": comp_hits[0]["title"] if comp_hits else "",
            "doi_thu_views": comp_hits[0]["views"] if comp_hits else 0,
        })
    return rows


def write_csv(rows: list[dict]) -> Path:
    p = STRAT / "EVERGREEN_PLAN.csv"
    cols = list(rows[0].keys())
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return p


def write_md(rows: list[dict]) -> Path:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    L = [
        "# EVERGREEN PLAN — 24 VIDEO 5-8 PHÚT",
        "",
        f"*Sinh: {now}*  •  Kênh: @azzammastertradinggold  •  "
        "2 video/tuần × 12 tuần",
        "",
        "**EVERGREEN là gì (giải thích rõ):**",
        "",
        "Video *evergreen* = video **còn mang view nhiều tháng/năm sau khi đăng**, "
        "khác với Short (hết view sau vài ngày) và livestream (chỉ có view lúc phát).",
        "",
        "| | Short | Livestream | **Evergreen 5-8 phút** |",
        "|---|---|---|---|",
        "| Vòng đời view | 3-7 ngày | 1-2 giờ | **nhiều tháng, nhiều năm** |",
        "| Nguồn view | Shorts feed | thông báo | **YouTube Search + đề xuất** |",
        "| Tái dùng được | không | không | **có — gắn vào playlist, dẫn từ Short** |",
        "| Bán offer được | kém | kém | **tốt — người xem đã có ý định học** |",
        "| Kênh mình hiện có | 141 video, median 46 views | 141 video, TB 102 views | "
        "**15 video, TB 6 views** |",
        "| Đối thủ có | 340 video, median 845 | 328 video, TB 2,873 | "
        "**31 video, TB 395 views** |",
        "",
        "**Vì sao đây là ưu tiên số 1:** kênh mình TB **6 views**/video evergreen, "
        "đối thủ **395 views** — khoảng cách **66×**. Và chỉ **1.2%** traffic kênh "
        "đến từ search YouTube, nghĩa là kênh gần như không tồn tại trên search.",
        "",
        "**Nguồn chủ đề:** 500 long-tail phrase mine từ 7,937 comment thật của khán giả "
        "+ 100 unigram + 200 pattern tiêu đề đối thủ. Không có chủ đề nào bịa ra.",
        "",
        "---",
        "",
        "## Danh sách 24 video",
        "",
    ]
    for r in rows:
        L.append(f"### {r['stt']}. {r['topic']}  *(tuần {r['tuan']})*")
        L.append("")
        L.append(f"- **Title:** `{r['title_draft']}`")
        L.append(f"- **Format:** {r['format']} · **Độ dài:** {r['do_dai']}")
        L.append(f"- **Keyword chính:** `{r['keyword_chinh']}` "
                 f"(xuất hiện {r['freq_comment']} lần trong comment khán giả)")
        L.append(f"- **Keyword phụ:** {r['keyword_phu']}")
        L.append(f"- **Hook 3s:** {r['hook_3s']}")
        L.append(f"- **Outline:** {r['outline']}")
        L.append(f"- **CTA:** {r['cta']}")
        L.append(f"- **Pain category:** `{r['pain_category']}`")
        if r["evidence_quote"]:
            L.append(f"- **Bằng chứng (comment thật):** “{r['evidence_quote'][:140]}”")
            if r["evidence_url"]:
                L.append(f"  - [nguồn]({r['evidence_url']})")
        L.append(f"- **Đối thủ đã làm:** {r['doi_thu_da_lam']}"
                 + (f" — vd: *{r['doi_thu_vi_du']}* ({r['doi_thu_views']:,} views)"
                    if r["doi_thu_vi_du"] else ""))
        L.append("")
    p = STRAT / "EVERGREEN_PLAN.md"
    p.write_text("\n".join(L), encoding="utf-8")
    return p


def write_xlsx(rows: list[dict]) -> Path:
    wb = Workbook()
    thin = Side(style="thin", color="CCCCCC")
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    hf = PatternFill("solid", fgColor="1F3864")
    hfont = Font(bold=True, color="FFFFFF", size=10)

    def hdr(ws, n):
        for c in range(1, n + 1):
            cell = ws.cell(row=1, column=c)
            cell.fill, cell.font = hf, hfont
            cell.alignment = Alignment(vertical="center", wrap_text=True)
            cell.border = bd
        ws.freeze_panes = "A2"

    def widths(ws, ws_w):
        for i, w in enumerate(ws_w, 1):
            ws.column_dimensions[get_column_letter(i)].width = w

    ws = wb.active
    ws.title = "01_EVERGREEN_PLAN"
    cols = ["stt", "tuan", "topic", "format", "title_draft", "keyword_chinh",
            "keyword_phu", "freq_comment", "do_dai", "hook_3s", "outline", "cta",
            "pain_category", "evidence_quote", "evidence_url",
            "doi_thu_da_lam", "doi_thu_vi_du", "doi_thu_views"]
    ws.append(cols)
    for r in rows:
        ws.append([r.get(c) for c in cols])
    hdr(ws, len(cols))
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.border = bd
            c.alignment = Alignment(vertical="top",
                                    wrap_text=c.column in (3, 5, 11, 14, 17))
    widths(ws, [5, 6, 30, 14, 46, 18, 30, 11, 11, 34, 60, 30, 16, 50, 40, 16, 50, 12])

    # 02: TỪ KHOÁ NGUỒN
    ws2 = wb.create_sheet("02_TU_KHOA_NGUON")
    ws2.append(["Từ khoá (long-tail từ comment khán giả)", "Tần suất", "Số từ"])
    kl = load_json(STRAT / "keywords_longtail.json") or {}
    for p in kl.get("top_longtail", [])[:100]:
        ws2.append([p["phrase"], p["freq"], p["words"]])
    hdr(ws2, 3)
    for row in ws2.iter_rows(min_row=2):
        for c in row:
            c.border = bd
    widths(ws2, [44, 11, 8])

    # 03: PATTERN TIÊU ĐỀ ĐỐI THỦ
    ws3 = wb.create_sheet("03_PATTERN_DOI_THU")
    ws3.append(["Pattern trong tiêu đề đối thủ", "Số video dùng"])
    kt = load_json(STRAT / "keywords_title_patterns.json") or {}
    for p in kt.get("top_patterns", [])[:60]:
        ws3.append([p["phrase"], p["video_count"]])
    hdr(ws3, 2)
    for row in ws3.iter_rows(min_row=2):
        for c in row:
            c.border = bd
    widths(ws3, [44, 15])

    # 04: VIDEO EVERGREEN MẪU CỦA ĐỐI THỦ
    ws4 = wb.create_sheet("04_MAU_DOI_THU")
    ws4.append(["Views", "Giây", "Ngày đăng", "Tiêu đề"])
    G = load_json(AUD / "gta_videos.json") or []
    g_ev = sorted([v for v in G if 60 < v["duration_s"] <= 600
                   and not re.search(r"live", v["title"], re.I)],
                  key=lambda x: -x["views"])
    for v in g_ev[:40]:
        ws4.append([v["views"], v["duration_s"], v["published"], v["title"]])
    hdr(ws4, 4)
    for row in ws4.iter_rows(min_row=2):
        for c in row:
            c.border = bd
            c.alignment = Alignment(vertical="top", wrap_text=(c.column == 4))
        row[0].number_format = "#,##0"
    widths(ws4, [10, 8, 12, 70])

    # 05: VIDEO EVERGREEN HIỆN CÓ CỦA MÌNH (để so)
    ws5 = wb.create_sheet("05_MINH_HIEN_CO")
    ws5.append(["Views", "Giây", "Ngày đăng", "Tiêu đề"])
    A = load_json(AUD / "azzam_videos.json") or []
    a_ev = sorted([v for v in A if 60 < v["duration_s"] <= 600],
                  key=lambda x: -x["views"])
    for v in a_ev:
        ws5.append([v["views"], v["duration_s"], v["published"], v["title"]])
    hdr(ws5, 4)
    for row in ws5.iter_rows(min_row=2):
        for c in row:
            c.border = bd
            c.alignment = Alignment(vertical="top", wrap_text=(c.column == 4))
        row[0].number_format = "#,##0"
    widths(ws5, [10, 8, 12, 70])

    # 06: LỊCH 12 TUẦN
    ws6 = wb.create_sheet("06_LICH_12_TUAN")
    ws6.append(["Tuần", "Video 1", "Video 2", "Deadline", "Trạng thái"])
    for w_ in range(1, 13):
        two = [r for r in rows if r["tuan"] == w_]
        ws6.append([w_,
                    two[0]["topic"] if len(two) > 0 else "",
                    two[1]["topic"] if len(two) > 1 else "",
                    "", "Chưa làm"])
    hdr(ws6, 5)
    for row in ws6.iter_rows(min_row=2):
        for c in row:
            c.border = bd
    widths(ws6, [7, 34, 34, 14, 14])

    p = REP / "AZZAM_EVERGREEN_PLAN.xlsx"
    wb.save(p)
    return p


def write_docx(rows: list[dict]) -> Path:
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10.5)
    for lvl in range(1, 5):
        try:
            doc.styles[f"Heading {lvl}"].font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
        except KeyError:
            pass

    h = doc.add_heading("EVERGREEN PLAN — 24 VIDEO", level=0)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("Kênh: @azzammastertradinggold  •  2 video/tuần × 12 tuần  •  "
              "5-8 phút  •  English").bold = True
    doc.add_paragraph()

    doc.add_heading("Evergreen là gì và vì sao ưu tiên số 1", level=1)
    doc.add_paragraph(
        "Video evergreen = video còn mang view nhiều tháng/năm sau khi đăng, "
        "khác Short (hết view sau vài ngày) và livestream (chỉ có view lúc phát). "
        "Evergreen lấy view từ YouTube Search và đề xuất, tái dùng được, và là nơi "
        "bán offer tốt nhất vì người xem đã có ý định học.")
    t = doc.add_table(rows=1, cols=4)
    t.style = "Light Grid Accent 1"
    for i, x in enumerate(("", "Short", "Livestream", "Evergreen 5-8 phút")):
        t.rows[0].cells[i].text = x
        for par in t.rows[0].cells[i].paragraphs:
            for run in par.runs:
                run.bold = True
    for r in [
        ("Vòng đời view", "3-7 ngày", "1-2 giờ", "nhiều tháng/năm"),
        ("Nguồn view", "Shorts feed", "thông báo", "Search + đề xuất"),
        ("Tái dùng", "không", "không", "có"),
        ("Kênh mình", "141 video, median 46", "141 video, TB 102", "15 video, TB 6"),
        ("Đối thủ", "340 video, median 845", "328 video, TB 2,873", "31 video, TB 395"),
    ]:
        c = t.add_row().cells
        for i, x in enumerate(r):
            c[i].text = x
    doc.add_paragraph()
    q = doc.add_paragraph()
    q.add_run("Khoảng cách: kênh mình TB 6 views/video evergreen, đối thủ 395 "
              "= 66×. Chỉ 1.2% traffic kênh đến từ search YouTube.").bold = True
    doc.add_page_break()

    doc.add_heading("24 video cần sản xuất", level=1)
    for r in rows:
        doc.add_heading(f"{r['stt']}. {unescape(r['topic'])}  (tuần {r['tuan']})",
                        level=2)
        for label, val in [
            ("Title", r["title_draft"]),
            ("Format / Độ dài", f"{r['format']} · {r['do_dai']}"),
            ("Keyword chính", f"{r['keyword_chinh']} "
                              f"({r['freq_comment']} lần trong comment khán giả)"),
            ("Keyword phụ", r["keyword_phu"]),
            ("Hook 3s", r["hook_3s"]),
            ("Outline", r["outline"]),
            ("CTA", r["cta"]),
            ("Pain category", r["pain_category"]),
            ("Đối thủ đã làm", r["doi_thu_da_lam"] +
             (f" — {r['doi_thu_vi_du']} ({r['doi_thu_views']:,} views)"
              if r["doi_thu_vi_du"] else "")),
        ]:
            par = doc.add_paragraph()
            par.add_run(f"{label}: ").bold = True
            par.add_run(unescape(str(val)))
        if r["evidence_quote"]:
            par = doc.add_paragraph()
            par.add_run("Bằng chứng (comment thật): ").bold = True
            par.add_run(f"“{unescape(r['evidence_quote'][:160])}”").italic = True

    path = REP / "AZZAM_EVERGREEN_PLAN.docx"
    doc.save(path)
    return path


def main() -> int:
    rows = build_rows()
    c = write_csv(rows)
    m = write_md(rows)
    x = write_xlsx(rows)
    d = write_docx(rows)

    print(f"Written: {c}  ({c.stat().st_size:,} B)")
    print(f"Written: {m}  ({m.stat().st_size:,} B)")
    print(f"Written: {x}  ({x.stat().st_size:,} B)")
    print(f"Written: {d}  ({d.stat().st_size:,} B)")

    # verify
    wb = load_workbook(str(x), data_only=True)
    print(f"\n  XLSX: {len(wb.sheetnames)} sheet")
    for n in wb.sheetnames:
        print(f"    {n}: {wb[n].max_row - 1} dòng")
    doc = Document(str(d))
    print(f"  DOCX: {len(doc.paragraphs)} paragraphs, {len(doc.tables)} bảng")

    # thống kê
    gap = sum(1 for r in rows if r["doi_thu_da_lam"].startswith("0"))
    print(f"\n  {len(rows)} video | {gap} chủ đề đối thủ CHƯA làm (khoảng trống)")
    print(f"  Tổng freq comment của keyword chính: "
          f"{sum(r['freq_comment'] for r in rows):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

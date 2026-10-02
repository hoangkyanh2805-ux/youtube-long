#!/usr/bin/env python3
"""Xuất bộ audit MrBeast ra Word (.docx) + Excel (.xlsx).

Đọc 4 markdown đã sinh bởi `build_mrbeast_audit.py` + dữ liệu video thật,
xuất vào outputs/reports/.

Usage:
    python scripts/build_mrbeast_report.py
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from html import unescape
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.shared import Pt, RGBColor
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
AUD = ROOT / "outputs" / "mrbeast_audit"
OUT = ROOT / "outputs" / "reports"

INLINE_RE = re.compile(r"(\*\*.+?\*\*|`[^`\n]+?`|\*[^*\n]+?\*)", re.DOTALL)


def add_inline(par, text: str) -> None:
    text = unescape(text)
    for part in INLINE_RE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            par.add_run(part[2:-2]).bold = True
        elif part.startswith("`") and part.endswith("`"):
            r = par.add_run(part[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(0xB0, 0x30, 0x60)
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            par.add_run(part[1:-1]).italic = True
        else:
            par.add_run(part)


def shade(cell, hex_color: str) -> None:
    from docx.oxml.ns import qn
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    tc_pr.append(shd)


def render_md(doc, md: str, demote: int = 1) -> None:
    """Render markdown vào docx: heading, bảng pipe, bullet, code block."""
    lines = md.splitlines()
    i = 0
    in_code = False
    while i < len(lines):
        ln = lines[i]

        if ln.strip().startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            p = doc.add_paragraph()
            r = p.add_run(ln)
            r.font.name = "Consolas"
            r.font.size = Pt(8.5)
            p.paragraph_format.space_after = Pt(0)
            i += 1
            continue

        m = re.match(r"^(#{1,5})\s+(.*)$", ln)
        if m:
            lvl = min(len(m.group(1)) + demote, 4)
            doc.add_heading(unescape(m.group(2)), level=lvl)
            i += 1
            continue

        # bảng pipe
        if ln.strip().startswith("|") and i + 1 < len(lines) and \
                re.match(r"^\s*\|[\s:\-|]+\|\s*$", lines[i + 1]):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                if not re.match(r"^\s*\|[\s:\-|]+\|\s*$", lines[i]):
                    cells = [c.strip().replace("\\|", "|")
                             for c in lines[i].strip().strip("|").split("|")]
                    rows.append(cells)
                i += 1
            if rows:
                ncols = max(len(r) for r in rows)
                t = doc.add_table(rows=1, cols=ncols)
                t.style = "Light Grid Accent 1"
                for j in range(ncols):
                    cell = t.rows[0].cells[j]
                    cell.text = ""
                    add_inline(cell.paragraphs[0],
                               rows[0][j] if j < len(rows[0]) else "")
                    for par in cell.paragraphs:
                        for run in par.runs:
                            run.bold = True
                    shade(cell, "DCE6F1")
                for r_ in rows[1:]:
                    cells = t.add_row().cells
                    for j in range(ncols):
                        cells[j].text = ""
                        add_inline(cells[j].paragraphs[0],
                                   r_[j] if j < len(r_) else "")
            doc.add_paragraph()
            continue

        if re.match(r"^\s*[-*]\s+", ln):
            p = doc.add_paragraph(style="List Bullet")
            add_inline(p, re.sub(r"^\s*[-*]\s+", "", ln))
            i += 1
            continue
        if re.match(r"^\s*\d+\.\s+", ln):
            p = doc.add_paragraph(style="List Number")
            add_inline(p, re.sub(r"^\s*\d+\.\s+", "", ln))
            i += 1
            continue
        if ln.strip() in ("---", "***", "___"):
            doc.add_paragraph()
            i += 1
            continue
        if not ln.strip():
            i += 1
            continue

        p = doc.add_paragraph()
        add_inline(p, ln)
        i += 1


def build_docx() -> Path:
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10.5)
    st.paragraph_format.space_after = Pt(4)
    for lvl in range(1, 5):
        try:
            doc.styles[f"Heading {lvl}"].font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
        except KeyError:
            pass

    h = doc.add_heading("AUDIT KÊNH & KẾ HOẠCH TĂNG TRƯỞNG", level=0)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("Kênh: @azzammastertradinggold  •  Ngách: XAUUSD / Forex  •  "
              "Ngôn ngữ: English").bold = True
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.add_run("Phương pháp MrBeast · Chẩn đoán · Plan action · SOP · Build-to-sell\n"
               f"Sinh: {date.today().isoformat()}")
    doc.add_paragraph()
    doc.add_page_break()

    SECTIONS = [
        ("outputs/reports/MRBEAST_AUDIT.md",
         "PHẦN 1 — AUDIT & CHẨN ĐOÁN"),
        ("outputs/strategy/MRBEAST_PLAN_ACTION.md",
         "PHẦN 2 — PLAN ACTION 90 NGÀY"),
        ("outputs/strategy/MRBEAST_SOP.md",
         "PHẦN 3 — SOP TRIỂN KHAI"),
        ("outputs/strategy/MRBEAST_BUILD_TO_SELL.md",
         "PHẦN 4 — BUILD TO SELL"),
    ]
    for idx, (rel, title) in enumerate(SECTIONS):
        src = ROOT / rel
        if idx:
            doc.add_page_break()
        t = doc.add_heading(title, level=1)
        t.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph()
        if src.exists():
            render_md(doc, src.read_text(encoding="utf-8"), demote=1)
        else:
            doc.add_paragraph(f"(thiếu {rel})")

    path = OUT / "AZZAM_MRBEAST_AUDIT.docx"
    doc.save(path)
    return path


def build_xlsx() -> Path:
    wb = Workbook()
    thin = Side(style="thin", color="CCCCCC")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    hf = PatternFill("solid", fgColor="1F3864")
    hfont = Font(bold=True, color="FFFFFF", size=10)

    def hdr(ws, n):
        for c in range(1, n + 1):
            cell = ws.cell(row=1, column=c)
            cell.fill, cell.font = hf, hfont
            cell.alignment = Alignment(vertical="center", wrap_text=True)
            cell.border = border
        ws.freeze_panes = "A2"

    def widths(ws, ws_widths):
        for i, w in enumerate(ws_widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w

    A = json.loads((AUD / "azzam_videos.json").read_text(encoding="utf-8"))
    G = json.loads((AUD / "gta_videos.json").read_text(encoding="utf-8"))

    def st(arr):
        if not arr:
            return 0, 0, 0, 0
        vs = sorted(v["views"] for v in arr)
        return len(vs), sum(vs) // len(vs), vs[len(vs) // 2], vs[-1]

    a_s = [v for v in A if 0 < v["duration_s"] <= 60]
    a_l = [v for v in A if v["duration_s"] > 60]
    a_ev = [v for v in A if 60 < v["duration_s"] <= 600]
    g_s = [v for v in G if 0 < v["duration_s"] <= 60]
    g_l = [v for v in G if v["duration_s"] > 60]
    g_ev = [v for v in G if 60 < v["duration_s"] <= 600
            and not re.search(r"live", v["title"], re.I)]

    # 01 CHẨN ĐOÁN
    ws = wb.active
    ws.title = "01_CHAN_DOAN"
    ws.append(["Chỉ số", "Kênh mình", "Đối thủ GTA", "Khoảng cách", "Ghi chú"])
    rows = [
        ("Subscribers", 1980, 14100, "7.1×", ""),
        ("Tổng views", 242480, 1404476, "5.8×", ""),
        ("Số video", 297, 742, "2.5×", ""),
        ("Views/video", 816, 1898, "2.3×", ""),
    ]
    ns, avs, meds, maxs = st(a_s)
    ng, avg_, medg, maxg = st(g_s)
    rows.append(("Short: số lượng", ns, ng, "", "≤60s"))
    rows.append(("Short: views TB", avs, avg_, f"{avg_/max(avs,1):.1f}×", ""))
    rows.append(("Short: median", meds, medg, f"{medg/max(meds,1):.0f}×", ""))
    rows.append(("Short: cao nhất", maxs, maxg, "", ""))
    nl, avl, medl, maxl = st(a_l)
    ng2, avg2, medg2, maxg2 = st(g_l)
    rows.append(("Long: số lượng", nl, ng2, "", ">60s"))
    rows.append(("Long: views TB", avl, avg2, f"{avg2/max(avl,1):.1f}×", "KHOẢNG CÁCH LỚN NHẤT"))
    rows.append(("Long: median", medl, medg2, f"{medg2/max(medl,1):.0f}×", ""))
    ne, ave, mede, maxe = st(a_ev)
    ng3, avg3, medg3, maxg3 = st(g_ev)
    rows.append(("Evergreen 1-10p: số lượng", ne, ng3, "", "Không phải livestream"))
    rows.append(("Evergreen 1-10p: TB", ave, avg3, f"{avg3/max(ave,1):.0f}×", "KHOẢNG CÁCH LỚN THỨ 2"))
    for r in rows:
        ws.append(list(r))
    hdr(ws, 5)
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.border = border
        for idx in (1, 2):
            row[idx].number_format = "#,##0"
    widths(ws, [26, 14, 14, 12, 30])

    # 02 ĐIỂM MRBEAST
    ws2 = wb.create_sheet("02_DIEM_MRBEAST")
    ws2.append(["Trụ cột", "Điểm /10", "Căn cứ"])
    for r in [
        ("Hook (3 giây đầu)", 4, "Short thắng 14s vs thua 21s"),
        ("Packaging (title/thumbnail)", 5, "Emoji 35% vs đối thủ 46%; năm 6% vs 51%"),
        ("Retention", 2, "Avg view 98s / 0.29% video"),
        ("Nhịp đăng", 7, "21.2 video/tháng, nhưng 90% long-form là livestream"),
        ("Nội dung evergreen", 1, "15 video 1-10p, TB 6 views"),
        ("Cộng đồng", 1, "1 comment / 9,016 view, sub ròng âm"),
        ("Phễu chuyển đổi", 2, "Không có offer rõ"),
        ("TỔNG", 3.1, ""),
    ]:
        ws2.append(list(r))
    hdr(ws2, 3)
    for row in ws2.iter_rows(min_row=2):
        for c in row:
            c.border = border
            c.alignment = Alignment(vertical="top", wrap_text=True)
    widths(ws2, [30, 11, 52])

    # 03 KPI 90 NGÀY
    ws3 = wb.create_sheet("03_KPI_90_NGAY")
    ws3.append(["Chỉ số", "Hiện tại", "Ngày 30", "Ngày 60", "Ngày 90"])
    for r in [
        ("Median views/Short", meds, 200, 400, 700),
        ("TB views/video evergreen", ave, 100, 250, 400),
        ("Comment rate %", 0.0111, 0.05, 0.1, 0.15),
        ("Sub ròng/tháng", -3, 20, 60, 120),
        ("Sub conversion %", 0.055, 0.15, 0.3, 0.5),
        ("Tỷ lệ traffic từ search %", 1.2, 4, 8, 12),
        ("Video evergreen/tuần", 0, 2, 2, 3),
        ("Tỷ lệ long-form là livestream %", 90, 70, 60, 50),
    ]:
        ws3.append(list(r))
    hdr(ws3, 5)
    for row in ws3.iter_rows(min_row=2):
        for c in row:
            c.border = border
        row[1].number_format = "#,##0.###"
    widths(ws3, [34, 13, 11, 11, 11])

    # 04 TOP VIDEO MÌNH
    ws4 = wb.create_sheet("04_TOP_VIDEO_MINH")
    ws4.append(["Views", "Loại", "Giây", "Ngày đăng", "Likes", "Comments", "Tiêu đề"])
    for v in sorted(A, key=lambda x: -x["views"])[:40]:
        typ = "Short" if 0 < v["duration_s"] <= 60 else "Long"
        ws4.append([v["views"], typ, v["duration_s"], v["published"],
                    v["likes"], v["comments"], v["title"]])
    hdr(ws4, 7)
    for row in ws4.iter_rows(min_row=2):
        for c in row:
            c.border = border
            c.alignment = Alignment(vertical="top", wrap_text=(c.column == 7))
        row[0].number_format = "#,##0"
    widths(ws4, [10, 8, 7, 12, 8, 10, 62])

    # 05 TOP VIDEO ĐỐI THỦ
    ws5 = wb.create_sheet("05_TOP_VIDEO_DOI_THU")
    ws5.append(["Views", "Loại", "Giây", "Ngày đăng", "Likes", "Comments", "Tiêu đề"])
    for v in sorted(G, key=lambda x: -x["views"])[:40]:
        typ = "Short" if 0 < v["duration_s"] <= 60 else "Long"
        ws5.append([v["views"], typ, v["duration_s"], v["published"],
                    v["likes"], v["comments"], v["title"]])
    hdr(ws5, 7)
    for row in ws5.iter_rows(min_row=2):
        for c in row:
            c.border = border
            c.alignment = Alignment(vertical="top", wrap_text=(c.column == 7))
        row[0].number_format = "#,##0"
    widths(ws5, [10, 8, 7, 12, 8, 10, 62])

    # 06 SHORTS MÌNH THEO THÁNG
    ws6 = wb.create_sheet("06_SHORTS_THEO_THANG")
    ws6.append(["Tháng", "Số Short", "Views TB", "Median", "Cao nhất"])
    from collections import defaultdict
    bym = defaultdict(list)
    for v in a_s:
        bym[v["published"][:7]].append(v)
    for m in sorted(bym):
        arr = bym[m]
        vs = sorted(x["views"] for x in arr)
        ws6.append([m, len(arr), sum(vs) // len(vs), vs[len(vs) // 2], vs[-1]])
    hdr(ws6, 5)
    for row in ws6.iter_rows(min_row=2):
        for c in row:
            c.border = border
        for idx in (2, 3, 4):
            row[idx].number_format = "#,##0"
    widths(ws6, [12, 11, 12, 11, 11])

    # 07 EVERGREEN ĐỐI THỦ (mẫu để học)
    ws7 = wb.create_sheet("07_EVERGREEN_MAU")
    ws7.append(["Views", "Giây", "Ngày đăng", "Tiêu đề (mẫu đối thủ)"])
    for v in sorted(g_ev, key=lambda x: -x["views"])[:30]:
        ws7.append([v["views"], v["duration_s"], v["published"], v["title"]])
    hdr(ws7, 4)
    for row in ws7.iter_rows(min_row=2):
        for c in row:
            c.border = border
            c.alignment = Alignment(vertical="top", wrap_text=(c.column == 4))
        row[0].number_format = "#,##0"
    widths(ws7, [10, 8, 12, 70])

    # 08 CÂU HỎI KHÁN GIẢ (content ideas)
    ws8 = wb.create_sheet("08_CAU_HOI_KHAN_GIA")
    ws8.append(["Câu hỏi khán giả (nguồn content)", "Nguồn"])
    qs = [
        "What is the best paper trading account you have been using?",
        "What would you suggest for a beginner? Go through those videos first or start from here?",
        "Can you suggest the order to watch these videos?",
        "I'm a beginner and I can frame a daily bias this way but how exactly to trade with this?",
        "Where is the PDF? / I need this PDF",
        "How to identify liquidity zones?",
        "What is the best entry confirmation?",
        "How do you manage risk with a small account?",
        "What timeframe should a beginner use?",
        "How to deal with losing streaks?",
    ]
    for q in qs:
        ws8.append([q, "comment khán giả đã cào (7,937 unique)"])
    hdr(ws8, 2)
    for row in ws8.iter_rows(min_row=2):
        for c in row:
            c.border = border
            c.alignment = Alignment(vertical="top", wrap_text=True)
    widths(ws8, [66, 34])

    path = OUT / "AZZAM_MRBEAST_AUDIT.xlsx"
    wb.save(path)
    return path


def main() -> int:
    d = build_docx()
    x = build_xlsx()
    print(f"Saved: {d}  ({d.stat().st_size:,} bytes)")
    print(f"Saved: {x}  ({x.stat().st_size:,} bytes)")

    # Verify bằng cách đọc lại
    doc = Document(str(d))
    print(f"\n  DOCX: {len(doc.paragraphs)} paragraphs, {len(doc.tables)} tables")
    for p in doc.paragraphs:
        if p.style.name == "Heading 1":
            print(f"    H1: {p.text[:60]}")
    wb = load_workbook(str(x), data_only=True)
    print(f"\n  XLSX: {len(wb.sheetnames)} sheets")
    for n in wb.sheetnames:
        print(f"    {n}: {wb[n].max_row - 1} data rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

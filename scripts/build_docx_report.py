"""
Convert all strategy reports (markdown) into ONE Word document (.docx).

Reads:  outputs/strategy/*.md + the two painpoint_report.md
Writes: outputs/reports/AZZAM_BAOCAO_PHAN_TICH_DOI_THU.docx

Handles: headings, tables (pipe), fenced code blocks, bullet/numbered lists,
blockquotes, inline bold/italic/code.
"""
from __future__ import annotations

import re
from datetime import date
from html import unescape
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
import sys

# Force UTF-8 console: without this, printing Vietnamese crashes with
# UnicodeEncodeError when stdout is a pipe (dagu/cron/CI).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402
ensure_utf8_console()

OUT = Path("outputs/reports")
OUT.mkdir(parents=True, exist_ok=True)

# ── Inline formatting ───────────────────────────────────────────────────────

INLINE_RE = re.compile(
    r"(\*\*.+?\*\*|__.+?__|\*[^*\n]+?\*|`[^`\n]+?`)",
    re.DOTALL,
)


def add_inline(par, text: str) -> None:
    """Add text to a paragraph, honouring **bold**, *italic*, `code`.

    YouTube titles in the source data contain HTML entities (&amp;, &#39;),
    so decode them here — otherwise the Word file shows raw entities.
    """
    text = unescape(text)
    for part in INLINE_RE.split(text):
        if not part:
            continue
        if (part.startswith("**") and part.endswith("**")) or \
           (part.startswith("__") and part.endswith("__")):
            run = par.add_run(part[2:-2])
            run.bold = True
        elif part.startswith("`") and part.endswith("`"):
            run = par.add_run(part[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(0xB0, 0x30, 0x60)
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            run = par.add_run(part[1:-1])
            run.italic = True
        else:
            par.add_run(part)


def shade(cell, hex_color: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tc_pr.append(shd)


def split_row(line: str) -> list[str]:
    """Split a markdown table row on unescaped pipes."""
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    # protect escaped pipes
    line = line.replace("\\|", "\x00")
    cells = [c.strip().replace("\x00", "|") for c in line.split("|")]
    return cells


def is_sep_row(line: str) -> bool:
    return bool(re.fullmatch(r"\|?[\s:|-]+\|?", line.strip())) and "-" in line


def add_table(doc: Document, rows: list[list[str]]) -> None:
    if not rows:
        return
    ncols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=ncols)
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for i, row in enumerate(rows):
        for j in range(ncols):
            cell = table.cell(i, j)
            cell.text = ""
            par = cell.paragraphs[0]
            par.paragraph_format.space_before = Pt(2)
            par.paragraph_format.space_after = Pt(2)
            val = row[j] if j < len(row) else ""
            if i == 0:
                run = par.add_run(re.sub(r"[*`]", "", unescape(val)))
                run.bold = True
                run.font.size = Pt(9.5)
                shade(cell, "1F3864")
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            else:
                add_inline(par, val)
                for r in par.runs:
                    r.font.size = Pt(9)
    doc.add_paragraph()


def add_code_block(doc: Document, lines: list[str]) -> None:
    par = doc.add_paragraph()
    par.paragraph_format.left_indent = Inches(0.25)
    par.paragraph_format.space_before = Pt(4)
    par.paragraph_format.space_after = Pt(8)
    run = par.add_run("\n".join(lines))
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    # light background via paragraph shading
    p_pr = par._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), "F2F2F2")
    p_pr.append(shd)


def md_to_doc(doc: Document, md: str) -> None:
    """Render a markdown string into the document."""
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # fenced code block
        if stripped.startswith("```"):
            block: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            add_code_block(doc, block)
            i += 1
            continue

        # table
        if stripped.startswith("|") and i + 1 < len(lines) and is_sep_row(lines[i + 1]):
            rows = [split_row(stripped)]
            i += 2  # skip header + separator
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            add_table(doc, rows)
            continue

        # horizontal rule
        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", stripped):
            par = doc.add_paragraph()
            par.paragraph_format.space_before = Pt(6)
            par.paragraph_format.space_after = Pt(6)
            p_pr = par._p.get_or_add_pPr()
            bdr = OxmlElement("w:pBdr")
            bottom = OxmlElement("w:bottom")
            bottom.set(qn("w:val"), "single")
            bottom.set(qn("w:sz"), "6")
            bottom.set(qn("w:color"), "999999")
            bdr.append(bottom)
            p_pr.append(bdr)
            i += 1
            continue

        # headings
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            text = m.group(2)
            if level == 1:
                h = doc.add_heading(level=0)
            else:
                h = doc.add_heading(level=min(level - 1, 4))
            add_inline(h, text)
            i += 1
            continue

        # blockquote
        if stripped.startswith(">"):
            text = stripped.lstrip(">").strip()
            par = doc.add_paragraph()
            par.paragraph_format.left_indent = Inches(0.3)
            add_inline(par, text)
            for r in par.runs:
                r.italic = True
                r.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
            i += 1
            continue

        # bullet list
        if re.match(r"^\s*[-*+]\s+", line):
            indent = (len(line) - len(line.lstrip())) // 2
            text = re.sub(r"^\s*[-*+]\s+", "", line)
            par = doc.add_paragraph(style="List Bullet")
            par.paragraph_format.left_indent = Inches(0.3 + 0.25 * indent)
            add_inline(par, text)
            i += 1
            continue

        # numbered list
        if re.match(r"^\s*\d+[.)]\s+", line):
            indent = (len(line) - len(line.lstrip())) // 2
            text = re.sub(r"^\s*\d+[.)]\s+", "", line)
            par = doc.add_paragraph(style="List Number")
            par.paragraph_format.left_indent = Inches(0.3 + 0.25 * indent)
            add_inline(par, text)
            i += 1
            continue

        # blank
        if not stripped:
            i += 1
            continue

        # normal paragraph
        par = doc.add_paragraph()
        add_inline(par, stripped)
        i += 1


# ── Report assembly ─────────────────────────────────────────────────────────

SECTIONS = [
    ("outputs/strategy/mrbeast_playbook.md",
     "PHẦN 1 — MRBEAST PLAYBOOK: PACKAGING, PILLAR, PHỄU"),
    ("outputs/strategy/sales_angles.md",
     "PHẦN 2 — SALES ANGLES (8 góc bán hàng từ pain point thật)"),
    ("outputs/strategy/seo_strategy.md",
     "PHẦN 3 — CHIẾN LƯỢC SEO KÊNH"),
    ("outputs/strategy/affiliate_funnel.md",
     "PHẦN 4 — PHỄU AFFILIATE 6 TẦNG"),
    ("outputs/competitor_longform/painpoint_report.md",
     "PHẦN 5 — PAIN POINT TỪ LONG-FORM VIDEO"),
    ("outputs/competitor_analysis/painpoint_report.md",
     "PHẦN 6 — PAIN POINT TỪ VIDEO NGẮN"),
]


def main() -> int:
    doc = Document()

    # base style
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)
    style.paragraph_format.space_after = Pt(4)

    for lvl in range(1, 5):
        try:
            doc.styles[f"Heading {lvl}"].font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
        except KeyError:
            pass

    # ── Cover ──
    t = doc.add_heading("BÁO CÁO PHÂN TÍCH ĐỐI THỦ & CHIẾN LƯỢC KÊNH", level=0)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run("Kênh: @azzammastertradinggold  •  Ngách: XAUUSD / Forex")
    r.bold = True
    r.font.size = Pt(13)

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.add_run(f"Ngày lập: {date.today().isoformat()}\n").italic = True
    meta.add_run("Nguồn dữ liệu: YouTube Data API v3 (channels.list, search.list, "
                 "videos.list, commentThreads.list)").italic = True

    doc.add_paragraph()

    # ── Summary box ──
    doc.add_heading("TÓM TẮT ĐIỀU HÀNH", level=1)
    summary_rows = [
        ["Chỉ số", "Giá trị"],
        ["Kênh đối thủ phân tích", "4"],
        ["Video phân tích (unique)", "44"],
        ["Comments thu thập (raw)", "9,247"],
        ["Comments (unique sau dedupe)", "5,883"],
        ["Pain-point candidates (unique)", "1,286"],
        ["Sales angles xây dựng", "8"],
        ["Content backlog", "16 item"],
    ]
    add_table(doc, summary_rows)

    facts = doc.add_paragraph()
    facts.add_run("Phát hiện chính:\n").bold = True
    for txt in [
        "Hai run thu thập (video ngắn + video dài) trùng nhau 57% — số raw phải "
        "dedupe trước khi dùng, nếu không mọi kết luận bị thổi phồng.",
        "Video 15-30 phút thắng rõ rệt về median views (665K) so với nhóm ngắn hơn.",
        "Pain point lớn nhất là nhóm học sai thứ tự: nhảy vào SMC/ICT khi chưa vững basic.",
        "Tham số duration=short của YouTube API không lọc được Shorts thật — 35 video "
        "lấy về chỉ 6 video đúng dưới 60 giây.",
    ]:
        p = doc.add_paragraph(txt, style="List Bullet")

    doc.add_page_break()

    # ── Mục lục ──
    doc.add_heading("MỤC LỤC", level=1)
    for idx, (_, title) in enumerate(SECTIONS, 1):
        p = doc.add_paragraph(f"{title}")
        p.paragraph_format.left_indent = Inches(0.2)
    doc.add_page_break()

    # ── Sections ──
    missing = []
    for path_str, title in SECTIONS:
        p = Path(path_str)
        doc.add_heading(title, level=1)
        if not p.exists():
            missing.append(path_str)
            warn = doc.add_paragraph()
            warn.add_run(f"[THIẾU FILE: {path_str}]").bold = True
            continue
        md = p.read_text(encoding="utf-8")
        # demote all headings by one level so section titles stay on top
        md = re.sub(r"^(#{1,5})\s", lambda m: "#" * (len(m.group(1)) + 1) + " ", md, flags=re.M)
        md_to_doc(doc, md)
        doc.add_page_break()

    # ── Guardrail appendix ──
    doc.add_heading("PHỤ LỤC — GUARDRAIL & DỮ LIỆU CÒN THIẾU", level=1)
    md_to_doc(doc, """
## Nguyên tắc bắt buộc

| Được phép | Không được phép |
|-----------|-----------------|
| Show lệnh thua và cách xử lý | Show trade giả / chart mô phỏng như trade thật |
| Nói về quy trình, xác suất, kỷ luật | Cam kết lợi nhuận, % thắng, "chắc chắn lãi" |
| Affiliate có disclosure rõ ràng | Affiliate ngầm, giấu quan hệ thương mại |
| Sales copy ở dạng draft | Auto-send sales/affiliate khi chưa có approval |
| Dùng comment thật làm evidence (có link) | Bịa testimonial / quote khán giả |

## Dữ liệu còn thiếu

- Search volume thật (không có quyền truy cập Keyword Planner) — chỉ có tần suất
  trong dữ liệu thu thập, không phải volume tìm kiếm.
- Retention, CTR, watch time (không có YouTube Analytics access).
- Tỷ lệ chuyển đổi YouTube sang Telegram.
- Chưa xác nhận target khán giả tiếng Việt hay tiếng Anh.

## Cần phê duyệt trước khi thực thi

1. Telegram gateway riêng cho project YouTube (bot / chat ID).
2. Offer ladder và mức giá.
3. Chọn broker / prop firm để làm affiliate.
4. Ngôn ngữ target của kênh.

## Truy vết nguồn

- Mọi pain point đều giữ `comment_id` + `content_url` để đối chiếu.
- Không có số liệu nào được tạo ra ngoài dữ liệu API trả về.
- Category do bộ phân loại từ khoá gán tự động, không phải nhãn thủ công —
  bucket rộng như `education_gap` có thể phóng đại độ mạnh tín hiệu.
""")

    out_path = OUT / "AZZAM_BAOCAO_PHAN_TICH_DOI_THU.docx"
    doc.save(out_path)

    print(f"Saved: {out_path.resolve()}")
    print(f"Size: {out_path.stat().st_size:,} bytes")
    if missing:
        print(f"MISSING FILES: {missing}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

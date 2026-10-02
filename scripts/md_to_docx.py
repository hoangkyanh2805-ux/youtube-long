#!/usr/bin/env python3
"""Xuất 1 file markdown bất kỳ ra Word — dùng renderer đã có trong repo.

Dùng chung `render_md` từ `build_mrbeast_report.py` (xử lý heading, bảng pipe,
bullet, code block, inline bold/italic/code).

Usage:
    python scripts/md_to_docx.py outputs/reports/SOP_INET_CNAME.md
    python scripts/md_to_docx.py <input.md> --out outputs/reports/<ten>.docx
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402
from build_mrbeast_report import render_md  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", help="file markdown nguồn")
    ap.add_argument("--out", default="", help="file .docx đích")
    ap.add_argument("--title", default="", help="tiêu đề bìa (mặc định: H1 của file)")
    args = ap.parse_args()

    src = (ROOT / args.input).resolve() if not Path(args.input).is_absolute() else Path(args.input)
    if not src.exists():
        print(f"Không tìm thấy: {src}", file=sys.stderr)
        return 1

    md = src.read_text(encoding="utf-8")

    # lấy H1 làm tiêu đề nếu không truyền
    title = args.title
    if not title:
        for ln in md.splitlines():
            if ln.startswith("# "):
                title = ln[2:].strip()
                break
        title = title or src.stem

    out = Path(args.out) if args.out else src.with_suffix(".docx")
    if not out.is_absolute():
        out = ROOT / out

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

    h = doc.add_heading(title, level=0)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.add_run(f"Kênh: @azzammastertradinggold  •  Nguồn: {src.name}")
    doc.add_paragraph()

    # bỏ H1 đầu vì đã làm tiêu đề bìa
    body = "\n".join(l for l in md.splitlines() if not l.startswith("# "))
    render_md(doc, body, demote=1)

    doc.save(out)
    print(f"Saved: {out}  ({out.stat().st_size:,} bytes)")

    # verify bằng cách đọc lại
    d = Document(str(out))
    print(f"  {len(d.paragraphs)} paragraphs, {len(d.tables)} bảng")
    for p in d.paragraphs:
        if p.style.name == "Heading 1":
            print(f"    H1: {p.text[:60]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

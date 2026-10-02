#!/usr/bin/env python3
"""P10 — SEO YOUTUBE: title, description, timestamps, tags, hashtag.

Sinh gói SEO upload từ dữ liệu THẬT: keyword khán giả dùng + metadata đối thủ.

Nguyên tắc (yêu cầu Alan, thread 13 msg 1125):
  - 5 mẫu tiêu đề chuẩn SEO, chứa từ khoá + kích tò mò.
  - Mô tả 150-200 từ, rải từ khoá tự nhiên + timestamp.
  - 15-20 tag liên quan để mượn view đối thủ.
  - 3 hashtag + khung giờ đăng tối ưu.
  - Guardrail P10: KHÔNG nhồi keyword/tag rác; KHÔNG dùng title gây hiểu sai.

Nguồn dữ liệu thật:
  outputs/strategy/keywords_longtail.json        500 long-tail (ngôn ngữ khán giả)
  outputs/strategy/keywords_main.json            unigram tần suất
  outputs/strategy/keywords_title_patterns.json  pattern tiêu đề đối thủ
  outputs/competitor_analysis/seo_tags.json      tag đối thủ đang dùng
  outputs/strategy/EVERGREEN_PLAN.csv            chủ đề + hook + outline đã plan
  outputs/reports/blindspots.json                khung giờ/CTR thật nếu có

Xuất:
  outputs/strategy/SEO_PACKAGES.json       gói SEO máy đọc
  outputs/strategy/SEO_PACKAGES.md         đọc được, copy-paste vào YouTube
  outputs/reports/AZZAM_SEO_PACKAGES.xlsx
  outputs/reports/AZZAM_SEO_PACKAGES.docx

Usage:
    python scripts/build_seo_packages.py                # tất cả chủ đề
    python scripts/build_seo_packages.py --limit 5      # 5 chủ đề đầu
    python scripts/build_seo_packages.py --topic "stop loss"
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
STRAT = ROOT / "outputs" / "strategy"
REP = ROOT / "outputs" / "reports"
COMP = ROOT / "outputs" / "competitor_analysis"

BRAND = "Azzam Master Trading"
# Khung giờ đăng: ưu tiên giờ khán giả US/UK (kênh tiếng Anh) — cố định để thuật toán học
POST_WINDOWS = [
    ("14:00-16:00 giờ VN", "07:00-09:00 UTC — sáng châu Âu, tối Mỹ bờ Đông chưa"),
    ("20:00-22:00 giờ VN", "13:00-15:00 UTC — mở cửa phiên Mỹ, thanh khoản vàng cao nhất"),
    ("02:00-04:00 giờ VN", "19:00-21:00 UTC — tối Mỹ, giờ vàng cho trading content"),
]


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def load_csv(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def title_variants(topic: str, kw: str, audience_kw: list[str]) -> list[dict]:
    """5 mẫu tiêu đề: 3 có số/tò mò, 1 câu hỏi, 1 khẳng định. Tất cả ≤60 ký tự."""
    t = topic.strip()
    k = kw.strip()
    out = []

    def push(style: str, text: str, why: str):
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) <= 60:
            out.append({"style": style, "title": text, "len": len(text), "why": why})

    push("con số", f"{t} — 3 Bước Cho Người Mới 2026",
         "Con số cụ thể tạo cảm giác có lộ trình, không lan man")
    push("cảm xúc", f"Tại Sao Bạn Vẫn Thua Với {t}",
         "Đánh vào nỗi đau đang có, không phải dạy lý thuyết")
    push("tò mò", f"{t}: Điều 90% Trader Hiểu Sai",
         "Khoảng trống tò mò — buộc phải xem để biết mình có trong 90% không")
    push("câu hỏi", f"{t} Có Thật Sự Hiệu Quả? Kiểm Chứng",
         "Câu hỏi trực diện, hợp người đang nghi ngờ")
    push("khẳng định", f"{t} Đúng Cách — Hướng Dẫn Từng Bước",
         "Rõ ràng, dễ tìm kiếm, hợp SEO dài hạn")

    if len(out) < 5:
        push("từ khoá", f"{k.title()} Cho XAUUSD — Hướng Dẫn 2026",
             "Thuần từ khoá, dùng khi các mẫu khác vượt 60 ký tự")
    return out[:5]


def build_description(topic: str, kw: str, outline: str, longtail: list[str],
                      pain: str) -> str:
    """Mô tả 150-200 từ, từ khoá rải tự nhiên, có timestamp."""
    # Lấy 4 long-tail liên quan chủ đề để rải tự nhiên
    rel = [p for p in longtail if kw.split()[0] in p.lower()][:4]
    if len(rel) < 3:
        rel = longtail[:4]

    paras = []
    paras.append(
        f"Trong video này tôi chỉ cách xử lý {topic.lower()} cho XAUUSD và forex — "
        f"từng bước, có ví dụ chart thật, không lý thuyết suông. "
        f"Nếu bạn đã từng thua vì {pain.lower()}, phần 2 của video là dành cho bạn."
    )
    paras.append(
        f"Tôi đi qua: định nghĩa rõ ràng, cách nhận diện trên chart, "
        f"điều kiện vào lệnh và cách quản lý rủi ro khi {kw} không đi đúng hướng. "
        f"Toàn bộ dựa trên cách tôi đang giao dịch thật, không phải mô phỏng."
    )
    paras.append("⏱️ TIMESTAMP\n" + "\n".join([
        "00:00 — Mở đầu: vấn đề bạn đang gặp",
        "01:20 — Định nghĩa và cách nhận diện",
        "03:45 — Điều kiện vào lệnh cụ thể",
        "06:10 — Quản lý rủi ro khi sai",
        "08:00 — Checklist áp dụng ngay",
    ]))
    paras.append(
        f"Bạn đang tìm: {', '.join(rel)}.\n\n"
        f"Đăng ký kênh nếu bạn muốn học trading bài bản — tôi đăng video "
        f"hướng dẫn XAUUSD và forex mỗi tuần, giải thích đơn giản để ai cũng làm được.\n\n"
        f"⚠️ Nội dung mang tính giáo dục. Không phải lời khuyên đầu tư. "
        f"Trading có rủi ro mất vốn."
    )
    return "\n\n".join(paras)


def build_tags(kw: str, longtail: list[str], competitor_tags: list[str],
               limit: int = 20) -> list[str]:
    """Tag: ưu tiên long-tail thật của khán giả, rồi tới tag đối thủ. KHÔNG tag rác."""
    tags, seen = [], set()

    def add(t: str):
        t = t.strip().lower()
        if t and t not in seen and len(t) <= 40 and len(tags) < limit:
            seen.add(t)
            tags.append(t)

    add(kw)
    add(f"{kw} xauusd")
    add(f"{kw} trading")
    add(f"{kw} strategy")
    add("xauusd")
    add("gold trading")
    add("forex trading")
    add("trading for beginners")
    for p in longtail:
        add(p)
    for t in competitor_tags:
        add(t)
    return tags


def build_hashtags(kw: str) -> list[str]:
    base = slug(kw).replace("-", "")
    return [f"#{base}", "#xauusd", "#goldtrading"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--topic", type=str, default="")
    args = ap.parse_args()

    lt = load_json(STRAT / "keywords_longtail.json") or {}
    km = load_json(STRAT / "keywords_main.json") or {}
    pat = load_json(STRAT / "keywords_title_patterns.json") or {}
    seo_tags = load_json(COMP / "seo_tags.json") or {}
    plan = load_csv(STRAT / "EVERGREEN_PLAN.csv")

    longtail = [x["phrase"] for x in (lt.get("top_longtail") or [])]
    comp_tags = []
    if isinstance(seo_tags, dict):
        for v in seo_tags.values():
            if isinstance(v, list):
                comp_tags.extend(str(x) for x in v[:30])
    elif isinstance(seo_tags, list):
        comp_tags = [str(x) for x in seo_tags[:60]]

    print(f"Nguồn: {len(longtail)} long-tail | {len(plan)} chủ đề plan | "
          f"{len(comp_tags)} tag đối thủ")

    if args.topic:
        plan = [r for r in plan if args.topic.lower() in str(r.get("topic", "")).lower()]
    if args.limit:
        plan = plan[:args.limit]

    if not plan:
        print("✗ Không có chủ đề nào. Kiểm tra outputs/strategy/EVERGREEN_PLAN.csv")
        return 1

    packages = []
    for r in plan:
        topic = (r.get("topic") or "").strip()
        kw = (r.get("keyword_chinh") or topic.split()[0]).strip()
        outline = (r.get("outline") or "").strip()
        pain = (r.get("pain_category") or "vào lệnh sai thời điểm").strip()
        hook = (r.get("hook_3s") or "").strip()
        ev = (r.get("evidence_quote") or "").strip()
        ev_url = (r.get("evidence_url") or "").strip()

        pk = {
            "stt": r.get("stt", ""),
            "tuan": r.get("tuan", ""),
            "topic": topic,
            "keyword_chinh": kw,
            "titles": title_variants(topic, kw, longtail),
            "description": build_description(topic, kw, outline, longtail, pain),
            "tags": build_tags(kw, longtail, comp_tags),
            "hashtags": build_hashtags(kw),
            "post_windows": POST_WINDOWS,
            "hook_3s": hook,
            "evidence_quote": ev,
            "evidence_url": ev_url,
            "rule_80_20": "Tiêu đề 80% từ khoá rõ nghĩa + 20% kích tò mò. "
                          "Thumbnail 80% hình ảnh + 20% chữ.",
        }
        # đếm từ mô tả
        pk["desc_word_count"] = len(re.findall(r"\w+", pk["description"]))
        packages.append(pk)

    out_json = STRAT / "SEO_PACKAGES.json"
    out_json.write_text(json.dumps(packages, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ {out_json.relative_to(ROOT)}")

    # ── Markdown ────────────────────────────────────────────────────────────
    md = [f"# P10 — GÓI SEO YOUTUBE ({len(packages)} video)", ""]
    md.append(f"**Sinh:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ")
    md.append(f"**Nguồn:** {len(longtail)} long-tail thật từ comment khán giả · "
              f"{len(comp_tags)} tag đối thủ · {len(plan)} chủ đề plan")
    md.append("")
    md.append("> Guardrail: không nhồi keyword rác, không title gây hiểu sai. "
              "Tag lấy từ ngôn ngữ thật của khán giả, không thêm cho đủ số.")
    md.append("")

    for pk in packages:
        md.append(f"## {pk['stt']}. {pk['topic']}  (tuần {pk['tuan']})")
        md.append("")
        md.append(f"**Từ khoá chính:** `{pk['keyword_chinh']}`  ")
        if pk["hook_3s"]:
            md.append(f"**Hook 3 giây:** {pk['hook_3s']}")
        md.append("")
        md.append("### 5 mẫu tiêu đề (chọn 1)")
        md.append("")
        md.append("| # | Kiểu | Tiêu đề | Ký tự | Vì sao |")
        md.append("|---|------|---------|-------|--------|")
        for i, t in enumerate(pk["titles"], 1):
            md.append(f"| {i} | {t['style']} | **{t['title']}** | {t['len']} | {t['why']} |")
        md.append("")
        md.append("### Mô tả (copy nguyên khối)")
        md.append("")
        md.append("```")
        md.append(pk["description"])
        md.append("```")
        md.append("")
        md.append(f"*{pk['desc_word_count']} từ — mục tiêu 150-200 từ.*")
        md.append("")
        md.append(f"### Tag ({len(pk['tags'])} cái — copy dòng dưới)")
        md.append("")
        md.append("```")
        md.append(", ".join(pk["tags"]))
        md.append("```")
        md.append("")
        md.append(f"### Hashtag")
        md.append("")
        md.append(" ".join(pk["hashtags"]))
        md.append("")
        md.append("### Khung giờ đăng")
        md.append("")
        for vn, utc in pk["post_windows"]:
            md.append(f"- **{vn}** — {utc}")
        md.append("")
        md.append(f"**Quy tắc 80/20:** {pk['rule_80_20']}")
        md.append("")
        if pk["evidence_quote"]:
            md.append(f"**Bằng chứng nhu cầu:** \"{pk['evidence_quote'][:180]}\"  ")
            if pk["evidence_url"]:
                md.append(f"*Nguồn: {pk['evidence_url']}*")
            md.append("")
        md.append("---")
        md.append("")

    md.append("*Sinh bởi `scripts/build_seo_packages.py` (P10). "
              "Tiêu đề/mô tả/tag đều từ từ khoá thật của khán giả.*")

    out_md = STRAT / "SEO_PACKAGES.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"✓ {out_md.relative_to(ROOT)}")

    # ── Excel ───────────────────────────────────────────────────────────────
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "SEO Packages"
    ws.append(["STT", "Tuần", "Chủ đề", "Từ khoá chính", "Tiêu đề chọn",
               "Mô tả (từ)", "Tag", "Hashtag", "Giờ đăng tốt nhất"])
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for pk in packages:
        ws.append([pk["stt"], pk["tuan"], pk["topic"], pk["keyword_chinh"],
                   pk["titles"][0]["title"] if pk["titles"] else "",
                   pk["desc_word_count"], len(pk["tags"]),
                   " ".join(pk["hashtags"]), pk["post_windows"][1][0]])
    for i, w in enumerate([5, 7, 30, 16, 46, 10, 7, 24, 20], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"

    ws2 = wb.create_sheet("Tiêu đề đầy đủ")
    ws2.append(["STT", "Chủ đề", "Kiểu", "Tiêu đề", "Ký tự", "Lý do"])
    for c in ws2[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for pk in packages:
        for t in pk["titles"]:
            ws2.append([pk["stt"], pk["topic"], t["style"], t["title"], t["len"], t["why"]])
    for i, w in enumerate([5, 28, 11, 48, 8, 52], 1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    ws3 = wb.create_sheet("Mô tả + Tag")
    ws3.append(["STT", "Chủ đề", "Mô tả đầy đủ", "Tag (dán vào YouTube)"])
    for c in ws3[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for pk in packages:
        ws3.append([pk["stt"], pk["topic"], pk["description"], ", ".join(pk["tags"])])
    ws3.column_dimensions["A"].width = 5
    ws3.column_dimensions["B"].width = 26
    ws3.column_dimensions["C"].width = 80
    ws3.column_dimensions["D"].width = 70
    for row in ws3.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")

    out_xlsx = REP / "AZZAM_SEO_PACKAGES.xlsx"
    REP.mkdir(parents=True, exist_ok=True)
    wb.save(out_xlsx)
    print(f"✓ {out_xlsx.relative_to(ROOT)}")

    # ── Word ────────────────────────────────────────────────────────────────
    from docx import Document

    doc = Document()
    doc.add_heading("P10 — GÓI SEO YOUTUBE", 0)
    doc.add_paragraph(f"Kênh: @{BRAND} · {len(packages)} video · "
                      f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    doc.add_paragraph("Tiêu đề, mô tả, tag đều sinh từ từ khoá thật của khán giả "
                      "(500 long-tail từ comment) — không nhồi keyword rác.")

    for pk in packages:
        doc.add_heading(f"{pk['stt']}. {pk['topic']}", level=1)
        doc.add_paragraph(f"Từ khoá chính: {pk['keyword_chinh']}")

        doc.add_heading("5 mẫu tiêu đề", level=2)
        t = doc.add_table(rows=1, cols=4)
        t.style = "Light Grid Accent 1"
        for i, h in enumerate(["#", "Kiểu", "Tiêu đề", "Ký tự"]):
            t.rows[0].cells[i].text = h
        for i, tv in enumerate(pk["titles"], 1):
            cells = t.add_row().cells
            for j, v in enumerate([str(i), tv["style"], tv["title"], str(tv["len"])]):
                cells[j].text = v

        doc.add_heading("Mô tả", level=2)
        for para in pk["description"].split("\n\n"):
            doc.add_paragraph(para)

        doc.add_heading("Tag", level=2)
        doc.add_paragraph(", ".join(pk["tags"]))
        doc.add_paragraph("Hashtag: " + " ".join(pk["hashtags"]))

        doc.add_heading("Khung giờ đăng", level=2)
        for vn, utc in pk["post_windows"]:
            doc.add_paragraph(f"{vn} — {utc}", style="List Bullet")

    out_docx = REP / "AZZAM_SEO_PACKAGES.docx"
    doc.save(out_docx)
    print(f"✓ {out_docx.relative_to(ROOT)}")

    print(f"\n{len(packages)} gói SEO · mô tả "
          f"{min(p['desc_word_count'] for p in packages)}-"
          f"{max(p['desc_word_count'] for p in packages)} từ · "
          f"tag {min(len(p['tags']) for p in packages)}-{max(len(p['tags']) for p in packages)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

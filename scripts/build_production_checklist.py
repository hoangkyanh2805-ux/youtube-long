#!/usr/bin/env python3
"""CHECKLIST SẢN XUẤT 30 NGÀY — video + SEO + thumbnail + đăng bài.

Alan yêu cầu (thread 13 msg 1129): "tổng hợp thành 1 checklist sản xuất 30 ngày
(video + SEO + thumbnail + đăng bài) để bạn có cái nhìn tổng quan trước khi triển khai".

Gộp 4 nguồn đã sinh thành MỘT lịch 30 ngày dùng được:
  outputs/strategy/EVERGREEN_PLAN.csv        24 video, tuần 1-8
  outputs/strategy/SEO_PACKAGES.json         tiêu đề/mô tả/tag mỗi video
  outputs/strategy/THUMBNAIL_CONCEPTS.json   concept thumbnail + prompt AI
  outputs/strategy/REPURPOSE_PACKAGES.json   5 định dạng mỗi video
  outputs/strategy/AUDIENCE_SEGMENTS.csv     phân khúc để chọn thứ tự
  outputs/strategy/EDITOR_HANDOFF.md         giao việc cho editor

Xuất:
  outputs/strategy/PRODUCTION_30D.csv        lịch 30 ngày, mỗi ngày 1 dòng
  outputs/strategy/PRODUCTION_30D.md         đọc được, có checkbox
  outputs/reports/AZZAM_PRODUCTION_30D.xlsx  lịch + checklist theo ngày
  outputs/reports/AZZAM_PRODUCTION_30D.docx  Word in ra dán tường

Usage:
    python scripts/build_production_checklist.py
    python scripts/build_production_checklist.py --start 2026-10-05
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
STRAT = ROOT / "outputs" / "strategy"
REP = ROOT / "outputs" / "reports"

# Nhịp: 2 ngày 1 video long (Alan chốt msg 1167). Mỗi video kèm 3 Short.
CYCLE_DAYS = 2
SHORTS_PER_LONG = 3

# Việc lặp mỗi ngày — bất kể đang ở chu kỳ nào
DAILY_ALWAYS = [
    ("08:00", "Kiểm tra comment mới", "Trả lời ít nhất 5 comment, ưu tiên câu hỏi về entry/risk"),
    ("08:30", "Kiểm tra số liệu 24h", "Xem view/CTR/%xem của video đã đăng — ghi vào journal"),
    ("21:00", "Đăng nội dung phụ", "1 trong 5 định dạng (F2 bài chữ / F3 carousel / F4 quan điểm)"),
]

# Việc theo pha trong chu kỳ 2 ngày
PHASE_WORK = {
    0: {  # Ngày lẻ — sản xuất
        "phase": "SẢN XUẤT",
        "tasks": [
            ("Research", "Đọc lại outline + evidence quote của chủ đề hôm nay"),
            ("Script", "Viết kịch bản đầy đủ theo hook 3s + outline đã có"),
            ("Record", "Quay/ghi âm video long (8 phút mục tiêu)"),
            ("Chart", "Chuẩn bị chart XAUUSD thật cho các đoạn cần minh hoạ"),
            ("Handoff", "Gửi nguyên liệu + brief cho editor"),
        ],
    },
    1: {  # Ngày chẵn — hoàn thiện + đăng
        "phase": "HOÀN THIỆN & ĐĂNG",
        "tasks": [
            ("Edit check", "Kiểm tra bản dựng: hook 3-5s, cao trào 30/60/80%"),
            ("Thumbnail", "Làm 2 biến thể A/B theo concept trong DESIGN_BRIEF"),
            ("SEO", "Dán tiêu đề + mô tả + tag từ SEO_PACKAGES (chọn 1 trong 5 title)"),
            ("Upload", "Đăng thẳng, KHÔNG premiere/đặt lịch (kênh còn nhỏ)"),
            ("Cut Shorts", f"Cắt {SHORTS_PER_LONG} Short từ chính video long này"),
            ("Read-back", "Ghi số liệu sau 24h vào journal, so với video trước"),
        ],
    },
}

# Mốc kiểm tra — Alan yêu cầu "điểm kiểm tra đo được"
CHECKPOINTS = [
    (7, "Tuần 1", [
        "Đã đăng 3-4 video long?",
        "CTR trung bình ≥ 4%?",
        "%xem trung bình ≥ 35%?",
        "Comment rate > 0.05% (hiện tại 0.0111%)?",
        "Sub ròng dương (hiện tại -3)?",
    ]),
    (14, "Tuần 2", [
        "Đã đăng 6-7 video long?",
        "Có ít nhất 1 video vượt 500 view thật (đã lọc bot)?",
        "Video nào có %xem cao nhất — vì sao?",
        "Đã thử đổi thumbnail 1 video để test?",
        "Traffic bot đã lọc được chưa?",
    ]),
    (21, "Tuần 3", [
        "Đã đăng 10 video long?",
        "Video nào kéo sub nhiều nhất?",
        "Đã có video nào lên Suggested chưa?",
        "Thời gian edit trung bình 1 video là bao nhiêu?",
    ]),
    (30, "Tuần 4", [
        "Đã đăng 15 video long?",
        "Tổng view thật (đã lọc bot) so với baseline 4,700?",
        "Sub ròng 30 ngày?",
        "Đã có dữ liệu để chọn phân khúc mạnh nhất chưa?",
        "Nhịp 2 ngày/video có giữ được không — nếu không, nút cổ chai ở đâu?",
    ]),
]


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def load_csv(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=str, default="")
    args = ap.parse_args()

    plan = load_csv(STRAT / "EVERGREEN_PLAN.csv")
    seo = load_json(STRAT / "SEO_PACKAGES.json") or []
    thumbs = load_json(STRAT / "THUMBNAIL_CONCEPTS.json") or []
    rep = load_json(STRAT / "REPURPOSE_PACKAGES.json") or []
    segs = load_csv(STRAT / "AUDIENCE_SEGMENTS.csv")

    seo_by_topic = {p["topic"]: p for p in seo}
    th_by_topic = {t["topic"]: t for t in thumbs}
    rp_by_topic = {r["topic"]: r for r in rep}

    if not plan:
        print("✗ Thiếu EVERGREEN_PLAN.csv")
        return 1

    start = date.fromisoformat(args.start) if args.start else date.today() + timedelta(days=1)

    print(f"Nguồn: {len(plan)} chủ đề · {len(seo)} SEO · {len(thumbs)} thumbnail · "
          f"{len(rep)} repurpose · {len(segs)} phân khúc")
    print(f"Bắt đầu: {start} · nhịp {CYCLE_DAYS} ngày/1 video long + "
          f"{SHORTS_PER_LONG} Short")

    # ── Dựng lịch 30 ngày ───────────────────────────────────────────────────
    rows = []
    vid_i = 0
    for d in range(30):
        cur = start + timedelta(days=d)
        phase_idx = d % CYCLE_DAYS
        phase = PHASE_WORK[phase_idx]

        # Video nào đang làm
        topic = ""
        if vid_i < len(plan):
            topic = (plan[vid_i].get("topic") or "").strip()

        seo_p = seo_by_topic.get(topic, {})
        th_p = th_by_topic.get(topic, {})
        rp_p = rp_by_topic.get(topic, {})

        rows.append({
            "ngay": d + 1,
            "date": cur.isoformat(),
            "thu": cur.strftime("%a"),
            "phase": phase["phase"],
            "topic": topic if phase_idx == 0 else topic,
            "tuan": plan[vid_i].get("tuan", "") if vid_i < len(plan) else "",
            "title_goi_y": (seo_p.get("titles") or [{}])[0].get("title", ""),
            "keyword": plan[vid_i].get("keyword_chinh", "") if vid_i < len(plan) else "",
            "thumbnail_concept": th_p.get("primary", ""),
            "thumbnail_chu": ((th_p.get("concepts") or [{}])[0]).get("text_on_thumb", ""),
            "so_dinh_dang_phu": len(rp_p.get("formats", [])),
            "tasks": phase["tasks"] + [("Daily", t[1], t[2]) for t in DAILY_ALWAYS],
            "checkpoint": next((c[1] for c in CHECKPOINTS if c[0] == d + 1), ""),
        })

        # Sang video mới sau mỗi chu kỳ
        if phase_idx == CYCLE_DAYS - 1:
            vid_i += 1

    # ── CSV ─────────────────────────────────────────────────────────────────
    out_csv = STRAT / "PRODUCTION_30D.csv"
    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Ngày", "Date", "Thứ", "Pha", "Tuần", "Chủ đề", "Từ khoá",
                    "Tiêu đề gợi ý", "Thumbnail", "Chữ trên ảnh", "Việc chính"])
        for r in rows:
            w.writerow([r["ngay"], r["date"], r["thu"], r["phase"], r["tuan"],
                        r["topic"], r["keyword"], r["title_goi_y"],
                        r["thumbnail_concept"], r["thumbnail_chu"],
                        " | ".join(t[1] for t in r["tasks"][:5])])
    print(f"✓ {out_csv.relative_to(ROOT)}")

    # ── Markdown ────────────────────────────────────────────────────────────
    md = ["# CHECKLIST SẢN XUẤT 30 NGÀY", ""]
    md.append(f"**Bắt đầu:** {start}  ")
    md.append(f"**Nhịp:** {CYCLE_DAYS} ngày / 1 video long + {SHORTS_PER_LONG} Short  ")
    md.append(f"**Sinh:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ")
    md.append(f"**Nguồn:** {len(plan)} chủ đề đã plan · {len(seo)} gói SEO · "
              f"{len(thumbs)} concept thumbnail · {len(rep)} gói repurpose")
    md.append("")
    md.append("## Mục tiêu 30 ngày")
    md.append("")
    md.append("| Chỉ số | Hiện tại | Mục tiêu 30 ngày |")
    md.append("|--------|----------|------------------|")
    md.append("| Video long | ~0/tháng | **15 video** |")
    md.append("| Short | không đều | **45 Short** (3/video long) |")
    md.append("| Comment rate | 0.0111% | **> 0.05%** |")
    md.append("| Sub ròng | -3 | **dương** |")
    md.append("| %xem trung bình | 29% | **> 35%** |")
    md.append("| Nhịp sản xuất | — | **2 ngày/video, giữ đều** |")
    md.append("")
    md.append("## Việc lặp mỗi ngày (bất kể pha)")
    md.append("")
    for t, name, note in DAILY_ALWAYS:
        md.append(f"- [ ] **{t} — {name}** · {note}")
    md.append("")
    md.append("---")
    md.append("")

    for r in rows:
        cp = r["checkpoint"]
        marker = f"  🎯 **MỐC KIỂM TRA {cp}**" if cp else ""
        md.append(f"## Ngày {r['ngay']} — {r['date']} ({r['thu']}) · {r['phase']}{marker}")
        md.append("")
        if r["topic"]:
            md.append(f"**Chủ đề:** {r['topic']}  ")
            if r["title_goi_y"]:
                md.append(f"**Tiêu đề gợi ý:** {r['title_goi_y']}  ")
            if r["thumbnail_concept"]:
                md.append(f"**Thumbnail:** concept {r['thumbnail_concept']} · "
                          f"chữ `{r['thumbnail_chu']}`")
            md.append("")
        md.append("**Việc:**")
        md.append("")
        for t in r["tasks"]:
            if len(t) == 3 and t[0] == "Daily":
                md.append(f"- [ ] `{t[1]}` — {t[2]}")
            else:
                md.append(f"- [ ] **{t[0]}** — {t[1]}")
        md.append("")

        if cp:
            for c in CHECKPOINTS:
                if c[1] == cp:
                    md.append(f"### 🎯 Điểm kiểm tra {cp}")
                    md.append("")
                    for q in c[2]:
                        md.append(f"- [ ] {q}")
                    md.append("")
        md.append("---")
        md.append("")

    md.append("## Sau 30 ngày — đánh giá lại")
    md.append("")
    md.append("- [ ] Đạt 15 video long? Nếu không, nút cổ chai ở đâu?")
    md.append("- [ ] Chỉ số nào cải thiện, chỉ số nào không?")
    md.append("- [ ] Phân khúc nào phản hồi tốt nhất → dồn nội dung cho phân khúc đó")
    md.append("- [ ] Traffic bot đã xử lý xong chưa?")
    md.append("- [ ] Quyết định: giữ nhịp hay tăng lên 1 video/ngày?")
    md.append("")
    md.append("*Sinh bởi `scripts/build_production_checklist.py`.*")

    out_md = STRAT / "PRODUCTION_30D.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"✓ {out_md.relative_to(ROOT)}")

    # ── Excel ───────────────────────────────────────────────────────────────
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Lịch 30 ngày"
    ws.append(["Ngày", "Date", "Thứ", "Pha", "Tuần", "Chủ đề", "Tiêu đề gợi ý",
               "Thumbnail", "Chữ trên ảnh", "Việc chính", "Mốc KT"])
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for r in rows:
        ws.append([r["ngay"], r["date"], r["thu"], r["phase"], r["tuan"], r["topic"],
                   r["title_goi_y"], r["thumbnail_concept"], r["thumbnail_chu"],
                   " | ".join(t[1] for t in r["tasks"][:5]), r["checkpoint"]])
        if r["checkpoint"]:
            for c in ws[ws.max_row]:
                c.fill = PatternFill("solid", fgColor="FFF2CC")
                c.font = Font(bold=True)
    for i, w in enumerate([6, 11, 6, 16, 6, 26, 40, 11, 22, 60, 10], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"

    ws2 = wb.create_sheet("Checklist theo ngày")
    ws2.append(["Ngày", "Date", "Pha", "Việc", "Xong"])
    for c in ws2[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for r in rows:
        for t in r["tasks"]:
            label = t[2] if (len(t) == 3 and t[0] == "Daily") else t[1]
            who = "Daily" if (len(t) == 3 and t[0] == "Daily") else t[0]
            ws2.append([r["ngay"], r["date"], f"{r['phase']} / {who}", label, ""])
    for i, w in enumerate([6, 11, 26, 66, 8], 1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    ws3 = wb.create_sheet("Mốc kiểm tra")
    ws3.append(["Ngày", "Tuần", "Câu hỏi kiểm tra", "Đạt?"])
    for c in ws3[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for day, label, qs in CHECKPOINTS:
        for q in qs:
            ws3.append([day, label, q, ""])
    for i, w in enumerate([7, 10, 70, 9], 1):
        ws3.column_dimensions[get_column_letter(i)].width = w

    ws4 = wb.create_sheet("Mục tiêu")
    ws4.append(["Chỉ số", "Hiện tại", "Mục tiêu 30 ngày"])
    for c in ws4[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for row in [["Video long", "~0/tháng", "15 video"],
                ["Short", "không đều", "45 Short"],
                ["Comment rate", "0.0111%", "> 0.05%"],
                ["Sub ròng", "-3", "dương"],
                ["%xem trung bình", "29%", "> 35%"],
                ["Nhịp sản xuất", "—", "2 ngày/video"]]:
        ws4.append(row)
    for i, w in enumerate([22, 16, 22], 1):
        ws4.column_dimensions[get_column_letter(i)].width = w

    out_xlsx = REP / "AZZAM_PRODUCTION_30D.xlsx"
    REP.mkdir(parents=True, exist_ok=True)
    wb.save(out_xlsx)
    print(f"✓ {out_xlsx.relative_to(ROOT)}")

    # ── Word ────────────────────────────────────────────────────────────────
    from docx import Document

    doc = Document()
    doc.add_heading("CHECKLIST SẢN XUẤT 30 NGÀY", 0)
    doc.add_paragraph(f"Kênh @azzammastertradinggold · bắt đầu {start} · "
                      f"nhịp {CYCLE_DAYS} ngày/1 video long + {SHORTS_PER_LONG} Short")

    doc.add_heading("Mục tiêu 30 ngày", level=1)
    t = doc.add_table(rows=1, cols=3)
    t.style = "Light Grid Accent 1"
    for i, h in enumerate(["Chỉ số", "Hiện tại", "Mục tiêu"]):
        t.rows[0].cells[i].text = h
    for row in [["Video long", "~0/tháng", "15 video"],
                ["Short", "không đều", "45 Short"],
                ["Comment rate", "0.0111%", "> 0.05%"],
                ["Sub ròng", "-3", "dương"],
                ["%xem trung bình", "29%", "> 35%"]]:
        cells = t.add_row().cells
        for j, v in enumerate(row):
            cells[j].text = v

    doc.add_heading("Việc lặp mỗi ngày", level=1)
    for tm, name, note in DAILY_ALWAYS:
        doc.add_paragraph(f"{tm} — {name}: {note}", style="List Bullet")

    for r in rows:
        h = f"Ngày {r['ngay']} — {r['date']} · {r['phase']}"
        if r["checkpoint"]:
            h += f"  [MỐC KIỂM TRA {r['checkpoint']}]"
        doc.add_heading(h, level=1)
        if r["topic"]:
            doc.add_paragraph(f"Chủ đề: {r['topic']}")
            if r["title_goi_y"]:
                doc.add_paragraph(f"Tiêu đề: {r['title_goi_y']}")
        for t2 in r["tasks"]:
            label = t2[2] if (len(t2) == 3 and t2[0] == "Daily") else t2[1]
            doc.add_paragraph(f"☐ {label}", style="List Bullet")
        if r["checkpoint"]:
            for c in CHECKPOINTS:
                if c[1] == r["checkpoint"]:
                    for q in c[2]:
                        doc.add_paragraph(f"☐ {q}", style="List Bullet")

    out_docx = REP / "AZZAM_PRODUCTION_30D.docx"
    doc.save(out_docx)
    print(f"✓ {out_docx.relative_to(ROOT)}")

    print(f"\n30 ngày · {min(len(plan), 15)} video long · "
          f"{min(len(plan), 15)*SHORTS_PER_LONG} Short · 4 mốc kiểm tra")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

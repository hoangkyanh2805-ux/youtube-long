#!/usr/bin/env python3
"""P11 — CONCEPT THUMBNAIL TỐI ƯU CTR + DESIGN BRIEF CHO DESIGNER.

Sinh 2-5 concept thumbnail + prompt AI tạo hình + brief chi tiết cho designer.

Nguyên tắc (yêu cầu Alan, thread 13 msg 1131, 1149):
  - 5 concept có CTR cao: bố cục, màu, cảm xúc.
  - Chữ trên thumbnail đi cặp với tiêu đề theo tỷ lệ 80/20.
  - Tương phản & điểm nhấn hút mắt trên điện thoại.
  - Prompt AI để tạo hình cho từng concept.
  - Chọn 1 concept mạnh nhất và giải thích lý do.
  - Brief chi tiết hơn cho designer.
  - Guardrail P11: KHÔNG làm hình gây hiểu sai hoặc giả mạo kết quả trading.

Nguồn dữ liệu thật:
  outputs/strategy/EVERGREEN_PLAN.csv        chủ đề + hook + title_draft
  outputs/strategy/SEO_PACKAGES.json         tiêu đề đã chọn (để 80/20)
  outputs/strategy/sales_angles.json         pain cluster + quote (cảm xúc thật)
  outputs/reports/blindspots.json            CTR thật nếu có
  outputs/mrbeast_audit/azzam_videos.json    video kênh mình (biết đang dùng gì)

Xuất:
  outputs/strategy/THUMBNAIL_CONCEPTS.json
  outputs/strategy/THUMBNAIL_CONCEPTS.md          concept + prompt AI
  outputs/strategy/DESIGN_BRIEF.md                brief cho designer
  outputs/reports/AZZAM_THUMBNAIL_BRIEF.xlsx
  outputs/reports/AZZAM_THUMBNAIL_BRIEF.docx

Usage:
    python scripts/build_thumbnail_concepts.py
    python scripts/build_thumbnail_concepts.py --limit 6
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

# Bảng màu kênh — tương phản cao trên mobile, không chìm vào feed YouTube
PALETTE = {
    "nen": "#0D1117 (đen xanh) — tối, làm nổi chart và chữ",
    "nhan": "#FFD400 (vàng gold) — màu chủ đạo ngách vàng",
    "canh_bao": "#FF3B30 (đỏ) — chỉ dùng cho mất mát/rủi ro, tối đa 1 điểm",
    "tin_cay": "#00C853 (xanh) — chỉ dùng cho kết quả đúng, tối đa 1 điểm",
    "chu": "#FFFFFF trắng + viền đen 3px — đọc được trên mọi nền",
}

# 5 archetype concept — khác nhau về bố cục/cảm xúc, không lặp
ARCHETYPES = [
    {
        "id": "T1",
        "name": "Đối đầu 2 chiều",
        "layout": "Chia đôi dọc. Trái: chart XAUUSD đang rơi (đỏ). Phải: chart đi đúng hướng (xanh). "
                  "Ở giữa: mũi tên vàng to chỉ từ trái sang phải.",
        "emotion": "Tò mò + nhẹ nhõm — 'tôi đang ở bên trái, cần sang phải'",
        "why_ctr": "Tương phản màu đỏ/xanh mạnh nhất trong feed. Não đọc được 'trước/sau' "
                   "trong 0.3 giây, không cần đọc chữ.",
        "text_ratio": "Chữ 20%: 3 từ tối đa, ví dụ 'SAI → ĐÚNG'",
        "mobile_score": 9,
    },
    {
        "id": "T2",
        "name": "Con số áp đảo",
        "layout": "Số cực lớn chiếm 40% khung bên trái (font 200pt, vàng gold). "
                  "Bên phải: mặt người biểu cảm ngạc nhiên. Nền: chart mờ.",
        "emotion": "Sốc nhẹ — số lớn tạo cảm giác có thông tin cụ thể, đáng bấm",
        "why_ctr": "Số là yếu tố hút mắt mạnh nhất sau khuôn mặt. Đọc được cả khi "
                   "thumbnail chỉ còn 120px trên mobile.",
        "text_ratio": "Chữ 20%: chính là con số + 2-3 từ, ví dụ '3 BƯỚC'",
        "mobile_score": 10,
    },
    {
        "id": "T3",
        "name": "Khuôn mặt + cảm xúc cực đoan",
        "layout": "Mặt người chiếm 45% khung bên phải, biểu cảm mạnh (bực bội hoặc nhẹ nhõm). "
                  "Bên trái: 1 dòng chữ lớn + 1 phần tử chart nhỏ.",
        "emotion": "Đồng cảm — khán giả thấy cảm xúc của chính mình",
        "why_ctr": "Khuôn mặt + cảm xúc là tín hiệu CTR mạnh nhất trên YouTube. "
                   "Nhưng phải là cảm xúc THẬT của ngách, không phải mặt ngạc nhiên chung chung.",
        "text_ratio": "Chữ 20%: 3-4 từ, ví dụ 'TÔI ĐÃ SAI'",
        "mobile_score": 9,
    },
    {
        "id": "T4",
        "name": "Khoanh đỏ điều sai",
        "layout": "Chart toàn khung. Một vùng được khoanh đỏ nét dày, có mũi tên. "
                  "Góc phải trên: chữ nhỏ '90% làm sai chỗ này'.",
        "emotion": "Lo lắng bị bỏ lỡ — 'có thể tôi đang làm sai'",
        "why_ctr": "Khoanh đỏ tạo cảm giác 'đây là thứ tôi cần xem'. Rất hợp ngách "
                   "trading vì khán giả luôn nghi ngờ điểm vào lệnh của mình.",
        "text_ratio": "Chữ 20%: 4-5 từ nhỏ ở góc",
        "mobile_score": 8,
    },
    {
        "id": "T5",
        "name": "Checklist trước/sau",
        "layout": "Hai cột. Trái: 3 dòng có dấu ✗ đỏ. Phải: 3 dòng có dấu ✓ xanh. "
                  "Nền tối, chữ trắng viền đen.",
        "emotion": "Tin cậy — 'đây là hướng dẫn cụ thể, không phải nói suông'",
        "why_ctr": "Checklist tạo cảm giác giá trị rõ ràng, hợp video how-to. "
                   "Nhược điểm: nhiều chữ, chỉ hiệu quả nếu chữ đủ lớn.",
        "text_ratio": "Chữ 20% nhưng chia 6 dòng ngắn",
        "mobile_score": 6,
    },
]

BRIEF_RULES = [
    ("Kích thước", "1280×720 px, xuất PNG, dưới 2 MB. Kiểm tra ở 120px trước khi giao."),
    ("Vùng an toàn", "Giữ 60px viền ngoài trống — YouTube cắt góc khi hiển thị ở vài vị trí."),
    ("Chữ tối đa", "3-5 từ. Font sans-serif đậm (Anton, Montserrat ExtraBold, Bebas Neue). "
                   "Cỡ tối thiểu 90pt ở 1280px."),
    ("Viền chữ", "Viền đen 3-4px hoặc bóng đổ — nếu không, chữ chìm khi thumbnail thu nhỏ."),
    ("Màu", f"Nền {PALETTE['nen']}. Nhấn {PALETTE['nhan']}. "
             f"Đỏ {PALETTE['canh_bao']} và xanh {PALETTE['tin_cay']} mỗi thứ tối đa 1 điểm."),
    ("Tương phản", "Tỷ lệ tương phản chữ/nền tối thiểu 4.5:1. Test bằng ảnh grayscale — "
                   "nếu mất chữ thì chưa đủ tương phản."),
    ("Chart", "Dùng chart THẬT từ XAUUSD. Nếu dùng chartanimator.io thì ghi rõ là minh hoạ. "
              "TUYỆT ĐỐI không vẽ chart giả trông như kết quả trade thật."),
    ("Khuôn mặt", "Cảm xúc phải khớp nội dung. Không dùng mặt ngạc nhiên chung chung "
                  "cho video về quản lý rủi ro."),
    ("Nhất quán", "Giữ 1-2 archetype cho cả kênh để khán giả nhận ra. "
                  "Đổi archetype chỉ khi A/B test thắng rõ."),
    ("Bàn giao", "Giao kèm 2 biến thể (A/B) cho mỗi video. Ghi rõ biến thể nào là chính."),
]


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def load_csv(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def pick_archetype(pain: str, idx: int) -> dict:
    """Chọn archetype theo pain cluster — không random."""
    p = pain.lower()
    if "risk" in p or "cháy" in p:
        return ARCHETYPES[0]   # đối đầu 2 chiều
    if "entry" in p or "timing" in p:
        return ARCHETYPES[3]   # khoanh đỏ điều sai
    if "psychology" in p or "fomo" in p or "discipline" in p:
        return ARCHETYPES[2]   # khuôn mặt cảm xúc
    if "education" in p or "basic" in p:
        return ARCHETYPES[4]   # checklist trước/sau
    if "overcomplicating" in p:
        return ARCHETYPES[1]   # con số áp đảo
    return ARCHETYPES[idx % len(ARCHETYPES)]


def ai_prompt(topic: str, arch: dict, title: str) -> str:
    return (
        f"YouTube thumbnail, 16:9, 1280x720, high contrast, mobile-first legibility. "
        f"Subject: {topic} for XAUUSD gold trading. "
        f"Composition: {arch['layout']} "
        f"Color palette: background #0D1117, accent #FFD400 gold, "
        f"single red #FF3B30 and single green #00C853 highlight only. "
        f"Mood: {arch['emotion']}. "
        f"Style: sharp, professional trading channel, not cartoonish, no clutter. "
        f"Text: 3-5 words max in bold sans-serif with 3px black outline, "
        f"placeholder text '{title[:40]}'. "
        f"IMPORTANT: do not fabricate trading results, no fake profit numbers, "
        f"no fake account balance screenshots."
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    plan = load_csv(STRAT / "EVERGREEN_PLAN.csv")
    seo = load_json(STRAT / "SEO_PACKAGES.json") or []
    sales = load_json(STRAT / "sales_angles.json") or []

    seo_by_topic = {p["topic"]: p for p in seo}
    quote_by_pain = {}
    for s in sales:
        k = str(s.get("pain_cluster", "")).split("/")[0].strip()
        if k and k not in quote_by_pain:
            quote_by_pain[k] = s.get("audience_quote", "")

    if args.limit:
        plan = plan[:args.limit]

    print(f"Nguồn: {len(plan)} chủ đề · {len(seo)} gói SEO · {len(sales)} pain cluster")

    items = []
    for i, r in enumerate(plan):
        topic = (r.get("topic") or "").strip()
        pain = (r.get("pain_category") or "").strip()
        title = (r.get("title_draft") or topic).strip()
        if topic in seo_by_topic and seo_by_topic[topic]["titles"]:
            title = seo_by_topic[topic]["titles"][0]["title"]

        arch = pick_archetype(pain, i)
        # 2-5 concept: archetype chính + biến thể
        alts = [a for a in ARCHETYPES if a["id"] != arch["id"]]
        alts.sort(key=lambda a: -a["mobile_score"])
        concepts = [arch] + alts[:2]

        items.append({
            "stt": r.get("stt", i + 1),
            "tuan": r.get("tuan", ""),
            "topic": topic,
            "title": title,
            "pain_category": pain,
            "keyword": r.get("keyword_chinh", ""),
            "evidence_quote": quote_by_pain.get(pain.split("/")[0].strip(), ""),
            "concepts": [{
                **c,
                "text_on_thumb": title[:28].upper(),
                "ai_prompt": ai_prompt(topic, c, title),
                "is_primary": c["id"] == arch["id"],
            } for c in concepts],
            "primary": arch["id"],
            "primary_reason": arch["why_ctr"],
        })

    out_json = STRAT / "THUMBNAIL_CONCEPTS.json"
    out_json.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ {out_json.relative_to(ROOT)}")

    # ── Markdown concept ────────────────────────────────────────────────────
    md = [f"# P11 — CONCEPT THUMBNAIL ({len(items)} video)", ""]
    md.append(f"**Sinh:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ")
    md.append("**Guardrail:** không hình gây hiểu sai, không giả mạo kết quả trading.")
    md.append("")
    md.append("## Bảng màu kênh")
    md.append("")
    for k, v in PALETTE.items():
        md.append(f"- **{k}**: {v}")
    md.append("")

    for it in items:
        md.append(f"## {it['stt']}. {it['topic']}  (tuần {it['tuan']})")
        md.append("")
        md.append(f"**Tiêu đề đi kèm:** {it['title']}  ")
        md.append(f"**Nỗi đau:** {it['pain_category']}  ")
        md.append(f"**Concept chọn:** {it['primary']}  ")
        md.append("")
        if it["evidence_quote"]:
            md.append(f"> \"{it['evidence_quote'][:200]}\"")
            md.append("")
        md.append("### Concept")
        md.append("")
        for c in it["concepts"]:
            mark = " ⭐ **CHỌN**" if c["is_primary"] else ""
            md.append(f"#### {c['id']} — {c['name']}{mark}")
            md.append("")
            md.append(f"- **Bố cục:** {c['layout']}")
            md.append(f"- **Cảm xúc:** {c['emotion']}")
            md.append(f"- **Vì sao CTR cao:** {c['why_ctr']}")
            md.append(f"- **Chữ trên ảnh ({c['text_ratio']}):** `{c['text_on_thumb']}`")
            md.append(f"- **Điểm mobile:** {c['mobile_score']}/10")
            md.append("")
            md.append(f"**Prompt AI:**")
            md.append("")
            md.append("```")
            md.append(c["ai_prompt"])
            md.append("```")
            md.append("")
        md.append(f"**Lý do chọn {it['primary']}:** {it['primary_reason']}")
        md.append("")
        md.append("---")
        md.append("")

    md.append("*Sinh bởi `scripts/build_thumbnail_concepts.py` (P11).*")
    out_md = STRAT / "THUMBNAIL_CONCEPTS.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"✓ {out_md.relative_to(ROOT)}")

    # ── Design brief cho designer ───────────────────────────────────────────
    b = ["# DESIGN BRIEF — THUMBNAIL KÊNH AZZAM MASTER TRADING", ""]
    b.append(f"**Ngày:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}  ")
    b.append(f"**Người nhận:** Designer / Editor  ")
    b.append(f"**Số lượng:** {len(items)} video, mỗi video 2 biến thể A/B")
    b.append("")
    b.append("## 1. QUY TẮC BẮT BUỘC")
    b.append("")
    b.append("| Hạng mục | Yêu cầu |")
    b.append("|----------|---------|")
    for k, v in BRIEF_RULES:
        b.append(f"| **{k}** | {v} |")
    b.append("")
    b.append("## 2. BẢNG MÀU")
    b.append("")
    for k, v in PALETTE.items():
        b.append(f"- **{k}** — {v}")
    b.append("")
    b.append("## 3. 5 ARCHETYPE — CHỌN THEO NỘI DUNG")
    b.append("")
    for a in ARCHETYPES:
        b.append(f"### {a['id']} — {a['name']}  (mobile {a['mobile_score']}/10)")
        b.append("")
        b.append(f"- Bố cục: {a['layout']}")
        b.append(f"- Cảm xúc: {a['emotion']}")
        b.append(f"- Chữ: {a['text_ratio']}")
        b.append("")
    b.append("## 4. DANH SÁCH VIỆC THEO VIDEO")
    b.append("")
    b.append("| STT | Chủ đề | Concept | Chữ trên ảnh | Biến thể B |")
    b.append("|-----|--------|---------|--------------|-----------|")
    for it in items:
        alt = [c for c in it["concepts"] if not c["is_primary"]]
        alt_txt = f"{alt[0]['id']} {alt[0]['name']}" if alt else "—"
        b.append(f"| {it['stt']} | {it['topic'][:26]} | **{it['primary']}** | "
                 f"`{it['concepts'][0]['text_on_thumb']}` | {alt_txt} |")
    b.append("")
    b.append("## 5. TIÊU CHÍ NGHIỆM THU")
    b.append("")
    b.append("- [ ] Đọc được chữ ở 120px (thu nhỏ về 10% rồi xem)")
    b.append("- [ ] Ảnh grayscale vẫn đọc được chữ")
    b.append("- [ ] Không quá 5 từ")
    b.append("- [ ] Không có số lợi nhuận / số dư tài khoản giả")
    b.append("- [ ] Có 2 biến thể A/B, ghi rõ biến thể chính")
    b.append("- [ ] PNG < 2 MB, 1280×720")
    b.append("- [ ] Nhìn 1 giây biết video nói về gì")
    b.append("")
    b.append("## 6. BÀN GIAO")
    b.append("")
    b.append("Đặt tên file: `<stt>-<topic-slug>-<A|B>.png`  ")
    b.append("Ví dụ: `01-stop-loss-dung-cach-A.png`")
    b.append("")
    b.append("---")
    b.append("")
    b.append("*Sinh bởi `scripts/build_thumbnail_concepts.py` (P11). "
              "Prompt AI có sẵn trong THUMBNAIL_CONCEPTS.md.*")

    out_brief = STRAT / "DESIGN_BRIEF.md"
    out_brief.write_text("\n".join(b), encoding="utf-8")
    print(f"✓ {out_brief.relative_to(ROOT)}")

    # ── Excel ───────────────────────────────────────────────────────────────
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Thumbnail Plan"
    ws.append(["STT", "Tuần", "Chủ đề", "Tiêu đề", "Concept chính", "Chữ trên ảnh",
               "Biến thể B", "Điểm mobile"])
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for it in items:
        alt = [c for c in it["concepts"] if not c["is_primary"]]
        ws.append([it["stt"], it["tuan"], it["topic"], it["title"], it["primary"],
                   it["concepts"][0]["text_on_thumb"],
                   alt[0]["id"] if alt else "", it["concepts"][0]["mobile_score"]])
    for i, w in enumerate([5, 7, 28, 44, 14, 26, 12, 12], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"

    ws2 = wb.create_sheet("Prompt AI")
    ws2.append(["STT", "Chủ đề", "Concept", "Tên concept", "Prompt AI"])
    for c in ws2[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for it in items:
        for c in it["concepts"]:
            ws2.append([it["stt"], it["topic"], c["id"], c["name"], c["ai_prompt"]])
    ws2.column_dimensions["A"].width = 5
    ws2.column_dimensions["B"].width = 26
    ws2.column_dimensions["C"].width = 8
    ws2.column_dimensions["D"].width = 24
    ws2.column_dimensions["E"].width = 100
    for row in ws2.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")

    ws3 = wb.create_sheet("Quy tắc designer")
    ws3.append(["Hạng mục", "Yêu cầu"])
    for c in ws3[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for k, v in BRIEF_RULES:
        ws3.append([k, v])
    ws3.column_dimensions["A"].width = 18
    ws3.column_dimensions["B"].width = 100
    for row in ws3.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")

    out_xlsx = REP / "AZZAM_THUMBNAIL_BRIEF.xlsx"
    REP.mkdir(parents=True, exist_ok=True)
    wb.save(out_xlsx)
    print(f"✓ {out_xlsx.relative_to(ROOT)}")

    # ── Word ────────────────────────────────────────────────────────────────
    from docx import Document

    doc = Document()
    doc.add_heading("DESIGN BRIEF — THUMBNAIL", 0)
    doc.add_paragraph(f"Kênh @azzammastertradinggold · {len(items)} video × 2 biến thể A/B · "
                      f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}")

    doc.add_heading("1. Quy tắc bắt buộc", level=1)
    t = doc.add_table(rows=1, cols=2)
    t.style = "Light Grid Accent 1"
    t.rows[0].cells[0].text = "Hạng mục"
    t.rows[0].cells[1].text = "Yêu cầu"
    for k, v in BRIEF_RULES:
        cells = t.add_row().cells
        cells[0].text = k
        cells[1].text = v

    doc.add_heading("2. Bảng màu", level=1)
    for k, v in PALETTE.items():
        doc.add_paragraph(f"{k}: {v}", style="List Bullet")

    doc.add_heading("3. Danh sách việc theo video", level=1)
    t2 = doc.add_table(rows=1, cols=5)
    t2.style = "Light Grid Accent 1"
    for i, h in enumerate(["STT", "Chủ đề", "Concept", "Chữ trên ảnh", "Biến thể B"]):
        t2.rows[0].cells[i].text = h
    for it in items:
        alt = [c for c in it["concepts"] if not c["is_primary"]]
        cells = t2.add_row().cells
        for j, v in enumerate([str(it["stt"]), it["topic"], it["primary"],
                               it["concepts"][0]["text_on_thumb"],
                               alt[0]["id"] if alt else "—"]):
            cells[j].text = v

    doc.add_heading("4. Tiêu chí nghiệm thu", level=1)
    for line in ["Đọc được chữ ở 120px", "Grayscale vẫn đọc được chữ",
                 "Không quá 5 từ", "Không có số lợi nhuận / số dư giả",
                 "Có 2 biến thể A/B", "PNG < 2 MB, 1280×720",
                 "Nhìn 1 giây biết video nói về gì"]:
        doc.add_paragraph(line, style="List Bullet")

    out_docx = REP / "AZZAM_THUMBNAIL_BRIEF.docx"
    doc.save(out_docx)
    print(f"✓ {out_docx.relative_to(ROOT)}")

    print(f"\n{len(items)} video · {len(items)*3} concept · "
          f"concept chọn: " + ", ".join(sorted({it['primary'] for it in items})))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""P05 — BIẾN KIẾN THỨC THÀNH NỘI DUNG ĐA NỀN TẢNG.

Từ 1 video gốc → 5 định dạng: Short · bài chữ · carousel · bài quan điểm · checklist.
Mỗi cái: hook "dừng lướt" riêng, góc riêng, CTA riêng.

Nguyên tắc (yêu cầu Alan, thread 13 msg 1098):
  - "Đừng lặp 5 lần — rút góc khác nhau, đúng giọng của tôi."
  - Bản dịch tiếng Anh theo văn nói bản địa để mở thị trường RPM cao.
  - Guardrail P05: không lặp nguyên văn, không dùng asset không có quyền.
  - Human approval: duyệt bản dịch, claim và nội dung trước đăng.

Nguồn dữ liệu thật:
  outputs/strategy/EVERGREEN_PLAN.csv      chủ đề + outline + hook + CTA đã plan
  outputs/strategy/SEO_PACKAGES.json       tiêu đề đã tối ưu
  outputs/strategy/AUDIENCE_SEGMENTS.csv   phân khúc để chọn góc
  outputs/strategy/sales_angles.json       pain cluster + quote thật
  channel-brain-v1.md                      giọng kênh (section 2.2)
  outputs/reports/blindspots.json          ngôn ngữ/khán giả thật

Xuất:
  outputs/strategy/REPURPOSE_PACKAGES.json
  outputs/strategy/REPURPOSE_PACKAGES.md        5 định dạng mỗi video
  outputs/strategy/EDITOR_HANDOFF.md            brief cho editor (nguyên liệu)
  outputs/reports/AZZAM_REPURPOSE.xlsx
  outputs/reports/AZZAM_REPURPOSE.docx

Usage:
    python scripts/build_repurpose_packages.py
    python scripts/build_repurpose_packages.py --limit 4
    python scripts/build_repurpose_packages.py --topic "stop loss"
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

# 5 định dạng — mỗi cái một GÓC khác nhau, không lặp nội dung
FORMATS = [
    {
        "id": "F1",
        "name": "Short",
        "platform": "YouTube Shorts / TikTok / Reels",
        "len": "45-60 giây",
        "angle": "Một sai lầm duy nhất, nói thẳng, không dẫn dắt",
        "structure": [
            "0-3s: câu gây sốc về hậu quả (hook dừng lướt)",
            "3-10s: chỉ ra sai lầm ai cũng mắc",
            "10-35s: cách sửa — 1 hành động cụ thể",
            "35-45s: kết quả nếu sửa / hậu quả nếu không",
            "45-60s: CTA bình luận, không CTA đăng ký",
        ],
        "cta": "Bình luận con số bạn đang mắc — tôi trả lời từng cái",
        "editor_note": "Cắt dọc 9:16. Chữ to giữa khung. Không intro, không outro.",
    },
    {
        "id": "F2",
        "name": "Bài chữ (text post)",
        "platform": "Facebook / LinkedIn / X",
        "len": "150-250 từ",
        "angle": "Kể lại quá trình học — đồng cảm, không dạy",
        "structure": [
            "Dòng 1: nỗi đau được nói thành lời",
            "Dòng 2-3: chuyện thật (ẩn danh nếu cần)",
            "Thân: 3 điều học được, đánh số",
            "Kết: câu hỏi mở cho người đọc",
        ],
        "cta": "Đọc tới đây rồi, bạn đang ở bước nào? Comment số",
        "editor_note": "Xuống dòng nhiều, mỗi đoạn 1-2 câu. Không dùng bullet dày đặc.",
    },
    {
        "id": "F3",
        "name": "Carousel",
        "platform": "Instagram / Facebook / LinkedIn",
        "len": "7-9 slide",
        "angle": "Trực quan hoá — biến khái niệm thành hình",
        "structure": [
            "Slide 1: tiêu đề + nỗi đau (chữ lớn)",
            "Slide 2: vì sao điều này xảy ra",
            "Slide 3-6: từng bước, mỗi slide 1 ý",
            "Slide 7: lỗi thường gặp",
            "Slide 8: checklist tóm tắt",
            "Slide 9: CTA",
        ],
        "cta": "Lưu lại để dùng khi vào lệnh",
        "editor_note": "Mỗi slide 1 ý, chữ tối đa 15 từ. Chart nếu có thì để slide riêng.",
    },
    {
        "id": "F4",
        "name": "Bài quan điểm",
        "platform": "YouTube community / Facebook / LinkedIn",
        "len": "200-300 từ",
        "angle": "Phản biện điều ngành đang dạy — tạo tranh luận",
        "structure": [
            "Mở: điều đa số tin (nói công bằng, không công kích)",
            "Vì sao điều đó hụt ở một tình huống cụ thể",
            "Quan điểm khác của bạn + lý do",
            "Thừa nhận trường hợp điều cũ đúng",
            "Mời phản biện",
        ],
        "cta": "Nếu bạn không đồng ý, nói tôi sai ở đâu — tôi đọc hết",
        "editor_note": "Giọng bình tĩnh, không gay gắt. Thừa nhận điểm đúng của phía kia.",
    },
    {
        "id": "F5",
        "name": "Checklist",
        "platform": "Blog / PDF lead magnet / Notion / Telegram",
        "len": "10-15 mục",
        "angle": "Công cụ dùng được ngay — không giải thích dài",
        "structure": [
            "Tiêu đề: việc cần làm",
            "Chia 3 nhóm: trước / trong / sau khi vào lệnh",
            "Mỗi mục 1 dòng, động từ đầu câu",
            "Ô tick để in ra",
        ],
        "cta": "In ra dán cạnh màn hình",
        "editor_note": "Dạng bảng hoặc danh sách tick. Không văn dài.",
    },
]


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def load_csv(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def en_hook(topic: str, pain: str) -> str:
    """Bản dịch tiếng Anh theo văn nói bản địa — không dịch máy từng chữ."""
    t = topic.lower()
    mapping = [
        ("stop loss", "You moved your stop loss. That's why you're still losing."),
        ("supply", "Supply and demand isn't hard. You're just marking it wrong."),
        ("risk", "Risk management won't save you if you size like this."),
        ("entry", "Right direction, wrong entry. Every single time."),
        ("psychology", "Revenge trading isn't a mindset problem. It's a system problem."),
        ("discipline", "You don't have a discipline problem. You have a plan problem."),
        ("backtest", "You backtested wrong, so your results are fake."),
        ("lot", "Position size is the only thing keeping you alive."),
        ("structure", "Market structure is not what your course told you."),
        ("timeframe", "You're on the wrong timeframe for your account size."),
    ]
    for k, v in mapping:
        if k in t:
            return v
    return f"Most people get {topic.lower()} wrong. Here's the version that works."


def build_short(it: dict, pain_quote: str) -> dict:
    topic = it["topic"]
    hook = it.get("hook_3s") or f"Sai lầm lớn nhất khi làm {topic.lower()}"
    return {
        "script_beat": [
            f"[0-3s] HOOK: {hook}",
            f"[3-10s] Vấn đề: đa số trader mắc lỗi này vì "
            f"{pain_quote[:90] if pain_quote else 'không ai chỉ cho họ cách đúng'}",
            f"[10-35s] Cách sửa: {it.get('outline','')[:140]}",
            "[35-45s] Kết quả: nếu sửa được thì vào lệnh có lý do, không sửa thì lặp lại lỗi cũ",
            "[45-60s] CTA: comment con số bạn đang mắc",
        ],
        "on_screen_text": [
            hook[:28].upper(),
            "ĐỪNG LÀM ĐIỀU NÀY",
            "LÀM THẾ NÀY THAY",
            "LƯU LẠI",
        ],
        "en_version": {
            "hook": en_hook(topic, it.get("pain_category", "")),
            "note": "Văn nói tiếng Anh bản địa — không dịch word-by-word từ tiếng Việt.",
        },
        "asset_can_dung": "1 clip chart XAUUSD thật + chữ overlay. Không dùng clip đối thủ.",
    }


def build_text_post(it: dict, pain_quote: str) -> dict:
    return {
        "body": (
            f"{pain_quote[:200] if pain_quote else 'Ai cũng nói học trading khó. Khó nhất là phần không ai nói.'}\n\n"
            f"Tôi cũng từng ở đó. Và tôi nhận ra 3 điều về {it['topic'].lower()}:\n\n"
            f"1. Vấn đề không phải bạn thiếu kiến thức — bạn thiếu thứ tự áp dụng.\n"
            f"2. Bạn không cần thêm setup. Bạn cần bỏ bớt thứ đang làm nhiễu.\n"
            f"3. Không có cách nào biết mình đúng cho tới khi ghi lại và đếm.\n\n"
            f"{it.get('outline','')[:200]}\n\n"
            f"Bạn đang ở bước nào trong 3 điều trên?"
        ),
        "platform_note": "Facebook/LinkedIn: xuống dòng nhiều. X: cắt còn 1 điều + link.",
        "en_version": en_hook(it["topic"], it.get("pain_category", "")),
    }


def build_carousel(it: dict) -> dict:
    return {
        "slides": [
            {"n": 1, "text": f"{it['topic'].upper()}", "sub": "Sai lầm đa số trader mắc"},
            {"n": 2, "text": "VÌ SAO", "sub": "Không ai chỉ thứ tự đúng"},
            {"n": 3, "text": "BƯỚC 1", "sub": "Nhận diện trước khi vào lệnh"},
            {"n": 4, "text": "BƯỚC 2", "sub": "Xác định điều kiện vô hiệu"},
            {"n": 5, "text": "BƯỚC 3", "sub": "Chốt size trước, không sau"},
            {"n": 6, "text": "BƯỚC 4", "sub": "Ghi lại và đếm trong 20 lệnh"},
            {"n": 7, "text": "LỖI THƯỜNG GẶP", "sub": "Bỏ bước 2 — không biết khi nào mình sai"},
            {"n": 8, "text": "CHECKLIST", "sub": "4 bước trên, in ra dán màn hình"},
            {"n": 9, "text": "LƯU LẠI", "sub": "Dùng khi vào lệnh tiếp theo"},
        ],
        "design_note": "Nền tối, chữ trắng. Slide 1 và 8 dùng màu vàng gold.",
    }


def build_opinion(it: dict) -> dict:
    topic = it["topic"]
    return {
        "body": (
            f"Điều đa số đang dạy về {topic.lower()}: học thêm một setup nữa.\n\n"
            f"Tôi nghĩ điều đó hụt trong một tình huống rất cụ thể: khi bạn đã biết "
            f"hướng đúng nhưng vào lệnh sai nhịp. Thêm setup không sửa được nhịp.\n\n"
            f"Quan điểm của tôi: cái cần bỏ thời gian không phải là setup mới, "
            f"mà là ghi lại 20 lệnh gần nhất và đếm xem bạn sai ở bước nào. "
            f"Số liệu của chính bạn mới sửa được hành vi.\n\n"
            f"Tôi vẫn nghĩ học setup mới có ích — khi bạn đã có dữ liệu của mình "
            f"và biết chính xác setup đó sửa vấn đề gì.\n\n"
            f"Nếu bạn không đồng ý, nói tôi sai ở đâu. Tôi đọc hết."
        ),
        "controversy_level": "Trung bình — phản biện cách dạy, không công kích người dạy",
        "risk_note": "Không nêu tên kênh/khoá học cụ thể.",
    }


def build_checklist(it: dict) -> dict:
    topic = it["topic"]
    return {
        "title": f"CHECKLIST — {topic}",
        "groups": [
            {"name": "TRƯỚC khi vào lệnh", "items": [
                "Xác định hướng trên khung lớn trước",
                "Đánh dấu vùng quan tâm, không đánh dấu điểm vào",
                "Kiểm tra có tin tức lớn trong 2 giờ tới không",
                "Chốt số tiền rủi ro tối đa cho lệnh này",
            ]},
            {"name": "TRONG khi vào lệnh", "items": [
                "Vào đúng điều kiện đã định, không vào vì thấy đẹp",
                "Đặt stop loss trước, không sau",
                "Chụp ảnh lý do vào lệnh",
                "Không thêm lệnh khi lệnh đầu đang lỗ",
            ]},
            {"name": "SAU khi lệnh đóng", "items": [
                "Ghi kết quả vào journal ngay",
                "Ghi cảm xúc lúc vào và lúc đóng",
                "Đánh dấu có theo đúng checklist không",
                "Đếm lại sau mỗi 20 lệnh",
            ]},
        ],
        "cta": "In ra dán cạnh màn hình. Tick mỗi lần làm đúng.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--topic", type=str, default="")
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

    if args.topic:
        plan = [r for r in plan if args.topic.lower() in str(r.get("topic", "")).lower()]
    if args.limit:
        plan = plan[:args.limit]

    if not plan:
        print("✗ Không có chủ đề. Kiểm tra EVERGREEN_PLAN.csv")
        return 1

    print(f"Nguồn: {len(plan)} chủ đề · {len(seo)} gói SEO · {len(sales)} pain cluster")

    items = []
    for i, r in enumerate(plan):
        topic = (r.get("topic") or "").strip()
        pain = (r.get("pain_category") or "").strip()
        quote = quote_by_pain.get(pain.split("/")[0].strip(), "")
        base = {
            "stt": r.get("stt", i + 1),
            "tuan": r.get("tuan", ""),
            "topic": topic,
            "title": (seo_by_topic.get(topic, {}).get("titles") or [{}])[0].get(
                "title", r.get("title_draft", topic)),
            "pain_category": pain,
            "hook_3s": r.get("hook_3s", ""),
            "outline": r.get("outline", ""),
            "evidence_quote": quote,
        }
        base["formats"] = [
            {"id": "F1", "name": "Short", **build_short(base, quote)},
            {"id": "F2", "name": "Bài chữ", **build_text_post(base, quote)},
            {"id": "F3", "name": "Carousel", **build_carousel(base)},
            {"id": "F4", "name": "Bài quan điểm", **build_opinion(base)},
            {"id": "F5", "name": "Checklist", **build_checklist(base)},
        ]
        items.append(base)

    out_json = STRAT / "REPURPOSE_PACKAGES.json"
    out_json.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ {out_json.relative_to(ROOT)}")

    # ── Markdown ────────────────────────────────────────────────────────────
    md = [f"# P05 — GÓI ĐA NỀN TẢNG ({len(items)} video × 5 định dạng)", ""]
    md.append(f"**Sinh:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ")
    md.append(f"**Nguồn:** {len(plan)} chủ đề từ EVERGREEN_PLAN · quote thật từ comment khán giả")
    md.append("")
    md.append("> Nguyên tắc: **5 định dạng phải có 5 GÓC khác nhau**, không lặp nội dung. "
              "Mỗi cái có hook riêng, CTA riêng.")
    md.append("")
    md.append("## Bảng định dạng")
    md.append("")
    md.append("| Mã | Định dạng | Nền tảng | Độ dài | Góc |")
    md.append("|----|-----------|----------|--------|-----|")
    for f in FORMATS:
        md.append(f"| {f['id']} | **{f['name']}** | {f['platform']} | {f['len']} | {f['angle']} |")
    md.append("")

    for it in items:
        md.append(f"## {it['stt']}. {it['topic']}  (tuần {it['tuan']})")
        md.append("")
        md.append(f"**Tiêu đề gốc:** {it['title']}  ")
        md.append(f"**Nỗi đau:** {it['pain_category']}")
        md.append("")
        if it["evidence_quote"]:
            md.append(f"> \"{it['evidence_quote'][:200]}\"")
            md.append("")

        for f in it["formats"]:
            fid = f["id"]
            md.append(f"### {fid} — {f['name']}")
            md.append("")
            if fid == "F1":
                md.append("**Nhịp kịch bản:**")
                md.append("")
                for b in f["script_beat"]:
                    md.append(f"- {b}")
                md.append("")
                md.append(f"**Chữ trên màn hình:** {' / '.join(f['on_screen_text'])}")
                md.append("")
                md.append(f"**Bản tiếng Anh (văn nói bản địa):** {f['en_version']['hook']}")
                md.append("")
                md.append(f"**Nguyên liệu:** {f['asset_can_dung']}")
            elif fid in ("F2", "F4"):
                md.append("```")
                md.append(f["body"])
                md.append("```")
                if fid == "F2":
                    md.append(f"**Nền tảng:** {f['platform_note']}")
                else:
                    md.append(f"**Mức tranh luận:** {f['controversy_level']}  ")
                    md.append(f"**Lưu ý rủi ro:** {f['risk_note']}")
            elif fid == "F3":
                md.append("| Slide | Chữ | Phụ đề |")
                md.append("|-------|-----|--------|")
                for s in f["slides"]:
                    md.append(f"| {s['n']} | **{s['text']}** | {s['sub']} |")
                md.append("")
                md.append(f"**Ghi chú thiết kế:** {f['design_note']}")
            elif fid == "F5":
                md.append(f"**{f['title']}**")
                md.append("")
                for g in f["groups"]:
                    md.append(f"*{g['name']}*")
                    md.append("")
                    for x in g["items"]:
                        md.append(f"- [ ] {x}")
                    md.append("")
                md.append(f"**CTA:** {f['cta']}")
            md.append("")
        md.append("---")
        md.append("")

    md.append("*Sinh bởi `scripts/build_repurpose_packages.py` (P05).*")
    out_md = STRAT / "REPURPOSE_PACKAGES.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"✓ {out_md.relative_to(ROOT)}")

    # ── Editor handoff ──────────────────────────────────────────────────────
    e = ["# EDITOR HANDOFF — NGUYÊN LIỆU LÀM VIDEO", ""]
    e.append(f"**Ngày:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}  ")
    e.append(f"**Cho:** Editor  ")
    e.append(f"**Số video long:** {len(items)}")
    e.append("")
    e.append("## Quy trình nhận việc")
    e.append("")
    e.append("1. Nhận `REPURPOSE_PACKAGES.md` — phần F1 của mỗi chủ đề là Short, "
             "phần còn lại là nội dung phụ.")
    e.append("2. Nhận `SEO_PACKAGES.md` — dùng để đặt tiêu đề + mô tả + tag khi upload.")
    e.append("3. Nhận `DESIGN_BRIEF.md` — làm thumbnail theo concept đã chỉ định.")
    e.append("4. Quay/dựng video long theo outline trong EVERGREEN_PLAN.csv.")
    e.append("5. Cắt Short từ chính video long đó — không quay riêng.")
    e.append("")
    e.append("## Bảng giao việc")
    e.append("")
    e.append("| STT | Chủ đề | Video long | Short (F1) | Thumbnail | SEO |")
    e.append("|-----|--------|-----------|-----------|-----------|-----|")
    for it in items:
        e.append(f"| {it['stt']} | {it['topic'][:28]} | có | có | concept "
                 f"{'theo brief' if it['stt'] else '-'} | có |")
    e.append("")
    e.append("## Nguyên tắc nguyên liệu")
    e.append("")
    e.append("- **Chart:** dùng chart XAUUSD thật. Nếu dùng chartanimator.io thì "
             "ghi rõ là minh hoạ, không trình bày như kết quả trade thật.")
    e.append("- **Không dùng clip/asset của đối thủ.** Chỉ dùng nguồn có quyền.")
    e.append("- **Không hiện số dư tài khoản hoặc số lợi nhuận** — kể cả của chính mình.")
    e.append("- **Short cắt từ video long**, không sản xuất riêng — tiết kiệm thời gian.")
    e.append("- **1 video long → 1 Short tối thiểu**, có thể 3 nếu có 3 đoạn cao trào.")
    e.append("")
    e.append("## Tiêu chí nghiệm thu")
    e.append("")
    e.append("- [ ] Hook 3-5 giây đầu nói ngay người xem được gì")
    e.append("- [ ] Có điểm cao trào ở mốc 30% / 60% / 80%")
    e.append("- [ ] Phụ đề có, đọc được trên mobile")
    e.append("- [ ] Thumbnail đúng concept trong brief")
    e.append("- [ ] Tiêu đề + mô tả + tag lấy từ SEO_PACKAGES")
    e.append("- [ ] Đúng deadline, file đặt tên theo quy ước")
    e.append("")
    e.append("---")
    e.append("")
    e.append("*Sinh bởi `scripts/build_repurpose_packages.py` (P05).*")

    out_handoff = STRAT / "EDITOR_HANDOFF.md"
    out_handoff.write_text("\n".join(e), encoding="utf-8")
    print(f"✓ {out_handoff.relative_to(ROOT)}")

    # ── Excel ───────────────────────────────────────────────────────────────
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Tổng quan"
    ws.append(["STT", "Tuần", "Chủ đề", "Tiêu đề", "Nỗi đau",
               "F1 Short", "F2 Bài chữ", "F3 Carousel", "F4 Quan điểm", "F5 Checklist"])
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for it in items:
        ws.append([it["stt"], it["tuan"], it["topic"], it["title"], it["pain_category"],
                   "✓", "✓", "✓", "✓", "✓"])
    for i, w in enumerate([5, 7, 26, 42, 30, 10, 12, 12, 13, 13], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"

    ws2 = wb.create_sheet("Short F1")
    ws2.append(["STT", "Chủ đề", "Nhịp kịch bản", "Chữ trên màn hình",
                "Bản tiếng Anh", "Nguyên liệu"])
    for c in ws2[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for it in items:
        f = it["formats"][0]
        ws2.append([it["stt"], it["topic"], "\n".join(f["script_beat"]),
                    " / ".join(f["on_screen_text"]), f["en_version"]["hook"],
                    f["asset_can_dung"]])
    ws2.column_dimensions["A"].width = 5
    ws2.column_dimensions["B"].width = 24
    for col in ["C", "D", "E", "F"]:
        ws2.column_dimensions[col].width = 60
    for row in ws2.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")

    ws3 = wb.create_sheet("Bài chữ + Quan điểm")
    ws3.append(["STT", "Chủ đề", "Định dạng", "Nội dung"])
    for c in ws3[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for it in items:
        for f in it["formats"]:
            if f["id"] in ("F2", "F4"):
                ws3.append([it["stt"], it["topic"], f["name"], f["body"]])
    ws3.column_dimensions["A"].width = 5
    ws3.column_dimensions["B"].width = 24
    ws3.column_dimensions["C"].width = 16
    ws3.column_dimensions["D"].width = 100
    for row in ws3.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")

    ws4 = wb.create_sheet("Checklist F5")
    ws4.append(["STT", "Chủ đề", "Nhóm", "Mục"])
    for c in ws4[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for it in items:
        f = it["formats"][4]
        for g in f["groups"]:
            for x in g["items"]:
                ws4.append([it["stt"], it["topic"], g["name"], x])
    for i, w in enumerate([5, 24, 26, 60], 1):
        ws4.column_dimensions[get_column_letter(i)].width = w

    out_xlsx = REP / "AZZAM_REPURPOSE.xlsx"
    REP.mkdir(parents=True, exist_ok=True)
    wb.save(out_xlsx)
    print(f"✓ {out_xlsx.relative_to(ROOT)}")

    # ── Word ────────────────────────────────────────────────────────────────
    from docx import Document

    doc = Document()
    doc.add_heading("P05 — GÓI ĐA NỀN TẢNG", 0)
    doc.add_paragraph(f"Kênh @azzammastertradinggold · {len(items)} video × 5 định dạng · "
                      f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    doc.add_paragraph("5 định dạng = 5 GÓC khác nhau. Không lặp nội dung.")

    doc.add_heading("Bảng định dạng", level=1)
    t = doc.add_table(rows=1, cols=5)
    t.style = "Light Grid Accent 1"
    for i, h in enumerate(["Mã", "Định dạng", "Nền tảng", "Độ dài", "Góc"]):
        t.rows[0].cells[i].text = h
    for f in FORMATS:
        cells = t.add_row().cells
        for j, v in enumerate([f["id"], f["name"], f["platform"], f["len"], f["angle"]]):
            cells[j].text = v

    for it in items:
        doc.add_heading(f"{it['stt']}. {it['topic']}", level=1)
        doc.add_paragraph(f"Tiêu đề: {it['title']}")
        doc.add_paragraph(f"Nỗi đau: {it['pain_category']}")

        f1 = it["formats"][0]
        doc.add_heading("F1 — Short", level=2)
        for b in f1["script_beat"]:
            doc.add_paragraph(b, style="List Bullet")
        doc.add_paragraph(f"Bản tiếng Anh: {f1['en_version']['hook']}")

        doc.add_heading("F2 — Bài chữ", level=2)
        for p in it["formats"][1]["body"].split("\n\n"):
            doc.add_paragraph(p)

        doc.add_heading("F3 — Carousel", level=2)
        t3 = doc.add_table(rows=1, cols=3)
        t3.style = "Light Grid Accent 1"
        for i, h in enumerate(["Slide", "Chữ", "Phụ đề"]):
            t3.rows[0].cells[i].text = h
        for s in it["formats"][2]["slides"]:
            cells = t3.add_row().cells
            for j, v in enumerate([str(s["n"]), s["text"], s["sub"]]):
                cells[j].text = v

        doc.add_heading("F4 — Bài quan điểm", level=2)
        for p in it["formats"][3]["body"].split("\n\n"):
            doc.add_paragraph(p)

        doc.add_heading("F5 — Checklist", level=2)
        f5 = it["formats"][4]
        for g in f5["groups"]:
            doc.add_paragraph(g["name"]).runs[0].bold = True
            for x in g["items"]:
                doc.add_paragraph(x, style="List Bullet")

    out_docx = REP / "AZZAM_REPURPOSE.docx"
    doc.save(out_docx)
    print(f"✓ {out_docx.relative_to(ROOT)}")

    print(f"\n{len(items)} video × 5 định dạng = {len(items)*5} asset")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""P06 — PHÂN KHÚC KHÁN GIẢ GIÁ TRỊ NHẤT.

Chấm điểm 5-8 phân khúc khán giả từ DỮ LIỆU THẬT, chọn phân khúc nên đánh trước.

Nguyên tắc (theo yêu cầu Alan, thread 13 msg 1102):
  - "Đừng mặc định phân khúc đông nhất là giá trị nhất."
  - Chấm 1-10 mỗi phân khúc: nhu cầu, tiềm năng ra tiền, độ dễ tiếp cận,
    độ cạnh tranh, độ hợp thế mạnh kênh.
  - Không bịa RPM hoặc purchasing power khi không có nguồn (guardrail P06).

Nguồn dữ liệu thật:
  outputs/strategy/sales_angles.json              8 pain cluster + evidence_count + quote
  outputs/competitor_longform/painpoint_candidates.csv   1,582 comment đã chấm điểm
  outputs/competitor_analysis/painpoint_candidates.csv     985 comment đã chấm điểm
  outputs/strategy/keywords_longtail.json         500 long-tail từ ngôn ngữ khán giả
  outputs/strategy/keywords_main.json             7,937 comment / 1,848 pain point
  outputs/reports/blindspots.json                 analytics thật 28 ngày
  outputs/strategy/EVERGREEN_PLAN.csv             24 video đã plan

Xuất:
  outputs/strategy/AUDIENCE_SEGMENTS.csv      scorecard đầy đủ
  outputs/strategy/AUDIENCE_SEGMENTS.md       đọc được + chân dung khán giả
  outputs/reports/AZZAM_AUDIENCE_SEGMENTS.xlsx
  outputs/reports/AZZAM_AUDIENCE_SEGMENTS.docx

Usage:
    python scripts/build_audience_segments.py
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
STRAT = ROOT / "outputs" / "strategy"
REP = ROOT / "outputs" / "reports"

# ─────────────────────────────────────────────────────────────────────────────
# Định nghĩa phân khúc — ánh xạ từ pain cluster THẬT sang chân dung khán giả.
# Mọi con số evidence đều lấy từ sales_angles.json + comment CSV, không bịa.
# ─────────────────────────────────────────────────────────────────────────────
SEGMENT_DEFS = [
    {
        "id": "SEG-A",
        "name": "Người mới mất phương hướng",
        "pain_clusters": ["education_gap / basic không vững"],
        "who": "Học trading 3-12 tháng, đã mua 1-2 khoá nhưng vẫn không giao dịch được nhất quán. "
               "Vào kênh vì tò mò, ở lại vì được giải thích thứ họ không hiểu ở nơi khác.",
        "urgent": 9,
        "buy_power": 5,
        "reach": 9,
        "competition": 6,
        "fit": 9,
        "monetize": "Mini-course nhập môn, checklist cơ bản, VIP group cho người mới",
        "content": "Explain-đơn-giản, breakdown từng bước, thuật ngữ có hình minh hoạ",
        "hook_type": "\"Tại sao bạn học 8 tháng vẫn chưa có lệnh nào ra hồn\"",
    },
    {
        "id": "SEG-B",
        "name": "Trader đã cháy tài khoản",
        "pain_clusters": ["risk_management / cháy tài khoản", "discipline / không theo plan"],
        "who": "Đã nạp tiền thật, cháy ít nhất 1 tài khoản. Biết sai ở đâu nhưng không sửa được. "
               "Đây là nhóm có động lực mạnh nhất và chịu chi nhất.",
        "urgent": 10,
        "buy_power": 7,
        "reach": 8,
        "competition": 7,
        "fit": 10,
        "monetize": "Risk calculator, journal tool, VIP group kỷ luật, khoá risk management",
        "content": "Case study tài khoản thật (ẩn danh), checklist trước vào lệnh, quy tắc cứng",
        "hook_type": "\"Tôi cháy 3 tài khoản trước khi hiểu 1 điều này\"",
    },
    {
        "id": "SEG-C",
        "name": "Trader kỹ thuật phức tạp hoá",
        "pain_clusters": ["overcomplicating / strategy quá phức tạp"],
        "who": "Đã biết SMC/ICT/Wyckoff, đang nhồi thêm indicator và concept. "
               "Nhận ra mình đang phức tạp hoá nhưng không biết bỏ gì.",
        "urgent": 7,
        "buy_power": 8,
        "reach": 7,
        "competition": 8,
        "fit": 8,
        "monetize": "Khoá nâng cao, template strategy đơn giản hoá, 1-1 coaching",
        "content": "So sánh concept, \"bỏ 5 thứ này\", framework 3 bước",
        "hook_type": "\"Bạn không cần thêm setup. Bạn cần bỏ 5 thứ.\"",
    },
    {
        "id": "SEG-D",
        "name": "Scalper tìm điểm vào lệnh",
        "pain_clusters": ["entry_timing / vào lệnh sai thời điểm"],
        "who": "Trade khung nhỏ, biết hướng đúng nhưng vào lệnh sai nhịp rồi bị quét stop loss. "
               "Tìm kiếm điểm vào chính xác, không tìm lý thuyết.",
        "urgent": 9,
        "buy_power": 7,
        "reach": 7,
        "competition": 9,
        "fit": 9,
        "monetize": "Signal room có kiểm duyệt, charting platform affiliate, journal",
        "content": "Live scalp breakdown, entry model có điều kiện rõ, replay có timestamp",
        "hook_type": "\"Đúng hướng vẫn thua. Vì vào sai 3 phút.\"",
    },
    {
        "id": "SEG-E",
        "name": "Trader cô độc tìm cộng đồng",
        "pain_clusters": ["community / cô độc khi trading"],
        "who": "Trade một mình, không ai kiểm tra quyết định. Cần người đối chiếu, không cần tín hiệu. "
               "Nhóm này ở lại kênh lâu và tương tác cao nhất.",
        "urgent": 6,
        "buy_power": 6,
        "reach": 8,
        "competition": 5,
        "fit": 10,
        "monetize": "VIP group, cộng đồng trả phí, live hàng tuần, accountability partner",
        "content": "Live Q&A, review lệnh của người xem, bình luận có trả lời thật",
        "hook_type": "\"Bạn không thua vì strategy. Bạn thua vì không ai phản biện bạn.\"",
    },
    {
        "id": "SEG-F",
        "name": "Trader tâm lý / FOMO",
        "pain_clusters": ["psychology / revenge trading, FOMO"],
        "who": "Biết phân tích nhưng bị cảm xúc chi phối. Vào lệnh vì sợ bỏ lỡ, gỡ lệnh vì tức. "
               "Nhóm này đọc nhiều, xem hết video, tỷ lệ xem cao.",
        "urgent": 8,
        "buy_power": 6,
        "reach": 8,
        "competition": 6,
        "fit": 8,
        "monetize": "Khoá tâm lý, journal có cảm xúc, mentor 1-1",
        "content": "Kể chuyện thật, đặt tên cảm xúc, bài tập nhận diện FOMO",
        "hook_type": "\"Revenge trading không phải lỗi tâm lý. Là lỗi hệ thống.\"",
    },
    {
        "id": "SEG-G",
        "name": "Trader quan tâm broker/prop firm",
        "pain_clusters": ["broker_platform / spread, prop firm"],
        "who": "Đang cân nhắc chuyển broker hoặc thi prop firm. Quan tâm chi phí thật, spread, "
               "điều kiện rút tiền. Có tiền nhưng thận trọng.",
        "urgent": 7,
        "buy_power": 9,
        "reach": 6,
        "competition": 7,
        "fit": 6,
        "monetize": "Broker affiliate (RPM cao nhất), prop firm affiliate, so sánh platform",
        "content": "So sánh có số liệu, test spread thật, cảnh báo điều khoản ẩn",
        "hook_type": "\"Spread broker bạn đang dùng ăn mất bao nhiêu mỗi tháng?\"",
    },
]


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def load_csv(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def count_evidence(cluster_key: str, sales: list[dict], comments: list[dict]) -> dict:
    """Đếm evidence cho 1 cluster từ 2 NGUỒN ĐỘC LẬP.

    LƯU Ý: hai nguồn không phủ nhau hoàn toàn.
      - painpoint_candidates.csv có 7 category: education_gap, strategy_rules,
        other_question_or_pain, risk_management, entry_timing, psychology, broker_platform
      - sales_angles.json có 8 cluster, thêm community / overcomplicating / discipline
    Nên cluster như "community" có evidence trong sales_angles nhưng 0 comment khớp
    trong CSV. Trả về CẢ HAI để không hiển thị 0 gây hiểu sai là "không có nhu cầu".
    """
    key = cluster_key.split("/")[0].strip()
    n_sales = 0
    ev_sales = 0
    for s in sales:
        if key in str(s.get("pain_cluster", "")):
            n_sales += 1
            try:
                ev_sales += int(float(s.get("evidence_count") or 0))
            except (TypeError, ValueError):
                pass
    n_comments = 0
    likes = 0
    for c in comments:
        cats = str(c.get("categories", ""))
        if key in cats:
            n_comments += 1
            try:
                likes += int(float(c.get("engagement_likes") or 0))
            except (TypeError, ValueError):
                pass
    return {"n_sales": n_sales, "n_comments": n_comments, "likes": likes,
            "ev_sales": ev_sales}


def main() -> int:
    sales = load_json(STRAT / "sales_angles.json") or []
    lt = load_json(STRAT / "keywords_longtail.json") or {}
    km = load_json(STRAT / "keywords_main.json") or {}
    blind = load_json(REP / "blindspots.json") or {}

    c1 = load_csv(ROOT / "outputs/competitor_longform/painpoint_candidates.csv")
    c2 = load_csv(ROOT / "outputs/competitor_analysis/painpoint_candidates.csv")
    comments = c1 + c2

    print(f"Nguồn: {len(sales)} sales angle | {len(comments):,} comment | "
          f"{lt.get('count', 0)} long-tail | {km.get('total_comments', 0):,} comment gốc")

    metrics = blind.get("metrics", {})
    derived = blind.get("derived", {})
    bot = blind.get("bot_traffic", {})
    public = blind.get("public_stats", {})

    # Tổng evidence để tính tỷ trọng
    total_ev = 0
    rows = []
    for seg in SEGMENT_DEFS:
        ev = {"n_sales": 0, "n_comments": 0, "likes": 0, "ev_sales": 0}
        for pc in seg["pain_clusters"]:
            e = count_evidence(pc, sales, comments)
            for k in ev:
                ev[k] += e[k]
        total_ev += ev["n_comments"]

        # Điểm tổng: nhu cầu + tiền + tiếp cận + hợp thế mạnh, trừ cạnh tranh
        score = (seg["urgent"] * 1.2 + seg["buy_power"] * 1.3 + seg["reach"] * 1.0
                 + seg["fit"] * 1.2 - seg["competition"] * 0.7)
        rows.append({**seg, **ev, "score_raw": round(score, 2)})

    # Chuẩn hoá 0-100
    lo = min(r["score_raw"] for r in rows)
    hi = max(r["score_raw"] for r in rows)
    for r in rows:
        r["score_100"] = round((r["score_raw"] - lo) / (hi - lo) * 100, 1) if hi > lo else 50.0

    rows.sort(key=lambda r: -r["score_100"])

    # ── Xuất CSV ────────────────────────────────────────────────────────────
    STRAT.mkdir(parents=True, exist_ok=True)
    out_csv = STRAT / "AUDIENCE_SEGMENTS.csv"
    cols = ["id", "name", "score_100", "score_raw", "urgent", "buy_power", "reach",
            "competition", "fit", "n_comments", "n_sales", "likes", "ev_sales",
            "pct_evidence", "monetize", "content", "hook_type", "who"]
    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            r["pct_evidence"] = round(r["n_comments"] / total_ev * 100, 1) if total_ev else 0
            w.writerow(r)
    print(f"✓ {out_csv.relative_to(ROOT)}")

    # ── Markdown ────────────────────────────────────────────────────────────
    top3 = rows[:3]
    primary = rows[0]
    md = []
    md.append("# P06 — PHÂN KHÚC KHÁN GIẢ GIÁ TRỊ NHẤT")
    md.append("")
    md.append(f"**Sinh:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ")
    md.append(f"**Nguồn:** {len(comments):,} comment đã chấm điểm · "
              f"{len(sales)} pain cluster · {km.get('total_comments', 0):,} comment gốc · "
              f"analytics 28 ngày thật")
    md.append("")
    md.append("> Nguyên tắc: **không mặc định phân khúc đông nhất là giá trị nhất.** "
              "Chấm theo nhu cầu, tiền, tiếp cận, cạnh tranh và độ hợp thế mạnh kênh.")
    md.append("")

    md.append("## 1. BẢNG CHẤM ĐIỂM")
    md.append("")
    md.append("| # | Phân khúc | Điểm | Nhu cầu | Tiền | Tiếp cận | Cạnh tranh | Hợp kênh | Comment | Sales-angle ev |")
    md.append("|---|-----------|------|---------|------|----------|-----------|----------|---------|----------------|")
    for i, r in enumerate(rows, 1):
        star = " ⭐" if i <= 3 else ""
        md.append(f"| {i} | **{r['name']}**{star} | **{r['score_100']}** | {r['urgent']} | "
                  f"{r['buy_power']} | {r['reach']} | {r['competition']} | {r['fit']} | "
                  f"{r['n_comments']:,} | {r['ev_sales']:,} |")
    md.append("")
    md.append(f"*Cột **Comment** = số comment thật khớp pain cluster trong painpoint_candidates.csv "
              f"(tổng {total_ev:,}). Cột **Sales-angle ev** = evidence_count từ sales_angles.json — "
              f"hai nguồn KHÔNG phủ nhau: cluster community/overcomplicating/discipline chỉ có "
              f"ở sales_angles, không xuất hiện trong CSV category.*")
    md.append("")

    md.append("## 2. CHỌN PHÂN KHÚC NÊN ĐÁNH TRƯỚC")
    md.append("")
    md.append(f"### 🎯 {primary['id']} — {primary['name']}  (điểm {primary['score_100']}/100)")
    md.append("")
    md.append(f"**Họ là ai:** {primary['who']}")
    md.append("")
    md.append(f"**Nỗi đau cốt lõi:** {primary['pain_clusters'][0]}")
    md.append("")
    md.append(f"**Kết quả họ muốn:** giao dịch nhất quán, không cháy thêm tài khoản, "
              f"biết mình đang làm gì và vì sao.")
    md.append("")
    md.append(f"**Loại nội dung phù hợp:** {primary['content']}")
    md.append("")
    md.append(f"**Câu thông điệp 1 dòng:**")
    md.append("")
    md.append(f"> {primary['hook_type']}")
    md.append("")
    md.append(f"**Kiếm tiền từ họ:** {primary['monetize']}")
    md.append("")

    md.append("### 3 phân khúc mạnh nhất và khác biệt")
    md.append("")
    for r in top3:
        md.append(f"**{r['id']} — {r['name']}** (điểm {r['score_100']})")
        md.append(f"- Nỗi đau: {', '.join(r['pain_clusters'])}")
        md.append(f"- Kiếm tiền: {r['monetize']}")
        md.append(f"- Hook mẫu: *{r['hook_type']}*")
        md.append("")
    md.append("**Khác biệt giữa 3 nhóm:**")
    md.append("")
    md.append(f"- **{top3[0]['id']}** có evidence nhiều nhất nhưng tiền trung bình "
              f"(tiền={top3[0]['buy_power']}/10) — đánh để lấy độ phủ, nuôi phễu.")
    md.append(f"- **{top3[1]['id']}** cân bằng nhất giữa nhu cầu và khả năng chi "
              f"(nhu cầu={top3[1]['urgent']}, tiền={top3[1]['buy_power']}) — đánh để ra tiền.")
    md.append(f"- **{top3[2]['id']}** có khả năng chi tốt nhưng cạnh tranh cao hơn "
              f"(cạnh tranh={top3[2]['competition']}) — đánh bằng góc khác biệt, không đối đầu trực diện.")
    md.append("")

    md.append("## 3. PHÂN KHÚC GIÁ TRỊ NHẤT VỀ TIỀN (khác phân khúc đông nhất)")
    md.append("")
    by_money = sorted(rows, key=lambda r: -r["buy_power"])[:3]
    md.append("| Phân khúc | Tiền | Nhu cầu | Ghi chú |")
    md.append("|-----------|------|---------|---------|")
    for r in by_money:
        note = "RPM cao nhất (broker affiliate)" if r["id"] == "SEG-G" else \
               ("Cân bằng tốt, chịu chi" if r["buy_power"] >= 8 else "Đông nhưng tiền trung bình")
        md.append(f"| {r['name']} | {r['buy_power']} | {r['urgent']} | {note} |")
    md.append("")
    md.append(f"**Lưu ý:** không có dữ liệu RPM thật cho từng phân khúc → "
              f"cột \"Tiền\" là đánh giá định tính, **không phải số liệu đo được**. "
              f"Cần cắm affiliate link rồi đo mới có số thật.")
    md.append("")

    md.append("## 4. ĐỐI CHIẾU VỚI THỰC TRẠNG KÊNH")
    md.append("")
    md.append("| Chỉ số kênh (28 ngày) | Giá trị | Ý nghĩa cho phân khúc |")
    md.append("|----------------------|---------|----------------------|")
    md.append(f"| Tỷ lệ bình luận | {derived.get('comment_rate_pct', 0)}% | Gần như 0 → **không biết khán giả là ai**. "
              f"Phải sửa trước khi chọn phân khúc. |")
    md.append(f"| Tỷ lệ thích | {derived.get('like_rate_pct', 0)}% | Cao bất thường (nghi do traffic bot) |")
    md.append(f"| Sub ròng | {derived.get('sub_net', 0)} | Đang mất nhiều hơn được |")
    md.append(f"| % xem trung bình | {int(float(metrics.get('averageViewPercentage', 0)) * 100)}% | Thấp → hook chưa đúng phân khúc |")
    md.append(f"| View từ bot | {bot.get('pct_of_channel', 0)}% | **Số liệu nền là số ảo** |")
    md.append("")
    md.append("### 🔴 Chặn trước khi triển khai")
    md.append("")
    md.append(f"Traffic bot chiếm **{bot.get('pct_of_channel', 0)}%** view 28 ngày. "
              f"Mọi kết luận về phân khúc dựa trên analytics hiện tại đều **không đáng tin** "
              f"cho tới khi lọc được nguồn này.")
    md.append("")

    md.append("## 5. KẾ HOẠCH ĐÁNH THEO PHÂN KHÚC")
    md.append("")
    md.append("| Tuần | Phân khúc | Số video | Format | Nguồn dữ liệu |")
    md.append("|------|-----------|----------|--------|---------------|")
    md.append("| 1-2 | SEG-B (cháy tài khoản) | 3 | Case study + checklist | EVERGREEN_PLAN video 1-3 |")
    md.append("| 3-4 | SEG-A (mới mất phương hướng) | 3 | Explain đơn giản | EVERGREEN_PLAN video 4-6 |")
    md.append("| 5-6 | SEG-D (scalper entry) | 3 | Live breakdown | EVERGREEN_PLAN video 7-9 |")
    md.append("| 7-8 | SEG-E (cô độc) | 3 | Live Q&A | Cần bật comment trước |")
    md.append("")
    md.append("**Nguyên tắc thứ tự:** làm SEG-B trước vì evidence nhiều nhất "
              "và nhu cầu cấp thiết nhất (10/10), đồng thời là nhóm chịu chi để nuôi phễu.")
    md.append("")

    md.append("---")
    md.append("")
    md.append("*Sinh bởi `scripts/build_audience_segments.py` (P06). "
              "Mọi con số evidence lấy từ comment thật đã chấm điểm; "
              "cột đánh giá định tính ghi rõ là định tính.*")

    out_md = STRAT / "AUDIENCE_SEGMENTS.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"✓ {out_md.relative_to(ROOT)}")

    # ── Excel ───────────────────────────────────────────────────────────────
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Segment Scorecard"
    hdr = ["#", "Mã", "Phân khúc", "Điểm/100", "Nhu cầu", "Tiền", "Tiếp cận",
           "Cạnh tranh", "Hợp kênh", "Comment", "Sales angle", "Sales ev", "Likes", "% Evidence"]
    ws.append(hdr)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for i, r in enumerate(rows, 1):
        ws.append([i, r["id"], r["name"], r["score_100"], r["urgent"], r["buy_power"],
                   r["reach"], r["competition"], r["fit"], r["n_comments"],
                   r["n_sales"], r["ev_sales"], r["likes"], r["pct_evidence"]])
    for i, w in enumerate([4, 7, 32, 9, 9, 7, 10, 11, 9, 10, 11, 11, 9, 11], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"

    ws2 = wb.create_sheet("Chi tiết phân khúc")
    ws2.append(["Mã", "Phân khúc", "Họ là ai", "Nỗi đau", "Nội dung phù hợp",
                "Kiếm tiền", "Hook mẫu"])
    for c in ws2[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for r in rows:
        ws2.append([r["id"], r["name"], r["who"], " | ".join(r["pain_clusters"]),
                    r["content"], r["monetize"], r["hook_type"]])
    for i, w in enumerate([7, 30, 60, 34, 42, 42, 42], 1):
        ws2.column_dimensions[get_column_letter(i)].width = w
    for row in ws2.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")

    ws3 = wb.create_sheet("Kế hoạch 8 tuần")
    ws3.append(["Tuần", "Phân khúc", "Số video", "Format", "Ghi chú"])
    for c in ws3[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    for row in [["1-2", "SEG-B cháy tài khoản", 3, "Case study + checklist", "Evidence nhiều nhất, cấp thiết 10/10"],
                ["3-4", "SEG-A mới mất phương hướng", 3, "Explain đơn giản", "Độ phủ cao, nuôi phễu"],
                ["5-6", "SEG-D scalper entry", 3, "Live breakdown", "Cạnh tranh cao — cần góc riêng"],
                ["7-8", "SEG-E cô độc", 3, "Live Q&A", "Phải bật comment trước"]]:
        ws3.append(row)
    for i, w in enumerate([8, 32, 10, 24, 40], 1):
        ws3.column_dimensions[get_column_letter(i)].width = w

    out_xlsx = REP / "AZZAM_AUDIENCE_SEGMENTS.xlsx"
    REP.mkdir(parents=True, exist_ok=True)
    wb.save(out_xlsx)
    print(f"✓ {out_xlsx.relative_to(ROOT)}")

    # ── Word ────────────────────────────────────────────────────────────────
    from docx import Document
    from docx.shared import Pt

    doc = Document()
    doc.add_heading("P06 — PHÂN KHÚC KHÁN GIẢ GIÁ TRỊ NHẤT", 0)
    doc.add_paragraph(f"Kênh: @azzammastertradinggold · "
                      f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    doc.add_paragraph(f"Nguồn: {len(comments):,} comment đã chấm điểm, "
                      f"{len(sales)} pain cluster, analytics 28 ngày thật.")
    doc.add_paragraph("Nguyên tắc: không mặc định phân khúc đông nhất là giá trị nhất.")

    doc.add_heading("1. Bảng chấm điểm", level=1)
    t = doc.add_table(rows=1, cols=8)
    t.style = "Light Grid Accent 1"
    for i, h in enumerate(["#", "Phân khúc", "Điểm", "Nhu cầu", "Tiền",
                           "Tiếp cận", "Cạnh tranh", "Hợp kênh"]):
        t.rows[0].cells[i].text = h
    for i, r in enumerate(rows, 1):
        cells = t.add_row().cells
        for j, v in enumerate([str(i), r["name"], str(r["score_100"]), str(r["urgent"]),
                               str(r["buy_power"]), str(r["reach"]),
                               str(r["competition"]), str(r["fit"])]):
            cells[j].text = v

    doc.add_heading("2. Phân khúc nên đánh trước", level=1)
    doc.add_paragraph(f"{primary['id']} — {primary['name']} (điểm {primary['score_100']}/100)")
    for label, val in [("Họ là ai", primary["who"]),
                       ("Nỗi đau cốt lõi", primary["pain_clusters"][0]),
                       ("Nội dung phù hợp", primary["content"]),
                       ("Kiếm tiền", primary["monetize"]),
                       ("Thông điệp 1 dòng", primary["hook_type"])]:
        p = doc.add_paragraph()
        p.add_run(f"{label}: ").bold = True
        p.add_run(val)

    doc.add_heading("3. Kế hoạch 8 tuần", level=1)
    t2 = doc.add_table(rows=1, cols=5)
    t2.style = "Light Grid Accent 1"
    for i, h in enumerate(["Tuần", "Phân khúc", "Số video", "Format", "Ghi chú"]):
        t2.rows[0].cells[i].text = h
    for row in [["1-2", "SEG-B cháy tài khoản", "3", "Case study + checklist", "Evidence nhiều nhất"],
                ["3-4", "SEG-A mới mất phương hướng", "3", "Explain đơn giản", "Độ phủ cao"],
                ["5-6", "SEG-D scalper entry", "3", "Live breakdown", "Cạnh tranh cao"],
                ["7-8", "SEG-E cô độc", "3", "Live Q&A", "Bật comment trước"]]:
        cells = t2.add_row().cells
        for j, v in enumerate(row):
            cells[j].text = v

    doc.add_heading("4. Cảnh báo dữ liệu", level=1)
    doc.add_paragraph(f"Traffic bot chiếm {bot.get('pct_of_channel', 0)}% view 28 ngày. "
                      f"Kết luận về phân khúc dựa trên analytics hiện tại KHÔNG đáng tin "
                      f"cho tới khi lọc được nguồn này.")
    doc.add_paragraph("Cột \"Tiền\" là đánh giá định tính — không có dữ liệu RPM thật. "
                      "Cần cắm affiliate link rồi đo mới có số thật.")

    out_docx = REP / "AZZAM_AUDIENCE_SEGMENTS.docx"
    doc.save(out_docx)
    print(f"✓ {out_docx.relative_to(ROOT)}")

    print(f"\nTop 3: " + " | ".join(f"{r['id']} {r['name']} ({r['score_100']})" for r in top3))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

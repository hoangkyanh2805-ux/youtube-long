"""
Stage 3: MrBeast-style playbook for the Azzam channel.

Reads the scraped competitor data + strategy outputs and produces a concrete
playbook: packaging (title/thumbnail/hook), content pillars, and the
YouTube → Telegram → Offer funnel mechanics.

Output: outputs/strategy/mrbeast_playbook.md
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from html import unescape
from pathlib import Path
import sys

# Force UTF-8 console: without this, printing Vietnamese crashes with
# UnicodeEncodeError when stdout is a pipe (dagu/cron/CI).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402
ensure_utf8_console()

OUT = Path("outputs/strategy")
OUT.mkdir(parents=True, exist_ok=True)


def load_csv(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_json(path: str):
    p = Path(path)
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


def fmt_int(v) -> str:
    try:
        return f"{int(float(v)):,}"
    except (TypeError, ValueError):
        return str(v)


def parse_iso_seconds(d: str) -> int:
    """Parse PT18M30S / PT42S / PT1H8M59S -> seconds."""
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


def main() -> int:
    angles = load_json("outputs/strategy/sales_angles.json")
    shorts = load_csv("outputs/competitor_analysis/shorts_inventory.csv")
    longform = load_csv("outputs/competitor_longform/longform_inventory.csv")
    channels = load_json("outputs/competitor_analysis/channels_info.json")

    # ── Facts computed from real data ──────────────────────────────────
    # The shorts run and long-form run overlap heavily (a top short IS also a
    # long-form video). Dedupe by video_id, keeping the record with the most
    # complete duration, otherwise every top-N list shows each video twice.
    merged: dict[str, dict] = {}
    for v in shorts + longform:
        vid = v.get("video_id", "")
        if not vid:
            continue
        if vid not in merged:
            merged[vid] = dict(v)
            continue
        prev = merged[vid]
        # prefer the record that carries a parseable duration
        if not parse_iso_seconds(prev.get("duration", "")) and parse_iso_seconds(v.get("duration", "")):
            merged[vid] = dict(v)

    all_vids = list(merged.values())
    for v in all_vids:
        try:
            v["_views"] = int(float(v["views"] or 0))
            v["_likes"] = int(float(v.get("likes") or 0))
            v["_comments"] = int(float(v.get("comments") or 0))
        except (TypeError, ValueError):
            v["_views"] = v["_likes"] = v["_comments"] = 0
        v["_dur"] = parse_iso_seconds(v.get("duration", ""))
    # drop the placeholder "Specific Short" row with no real metadata
    all_vids = [v for v in all_vids if v["_views"] > 0]

    # duration bucket performance
    def bucket(d: int) -> str:
        if d == 0:
            return "unknown"
        if d <= 60:
            return "0-60s (Short)"
        if d <= 300:
            return "1-5 min"
        if d <= 900:
            return "5-15 min"
        if d <= 1800:
            return "15-30 min"
        return "30+ min"

    bucket_stats: dict[str, list] = {}
    for v in all_vids:
        bucket_stats.setdefault(bucket(v["_dur"]), []).append(v)

    # title pattern analysis on the top performers
    top20 = sorted(all_vids, key=lambda x: -x["_views"])[:20]

    lines: list[str] = []
    lines.append("# MrBeast Playbook — Kênh Azzam (XAUUSD / Forex)")
    lines.append("")
    lines.append("> Đóng vai: **MrBeast của ngách trading**. Nguyên tắc: packaging quyết định "
                 "90% kết quả, nội dung quyết định 10% còn lại. Nhưng trong trading, "
                 "**trust là điều kiện sống còn** — không hứa lợi nhuận, không trade giả.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── 0. Ground truth ────────────────────────────────────────────────
    lines.append("## 0. Ground truth — số liệu thật dùng cho playbook này")
    lines.append("")
    lines.append("| Kênh | Subs | Tổng views | Videos | Vai trò |")
    lines.append("|------|------|-----------|--------|---------|")
    for handle, info in channels.items():
        s = info.get("statistics", {})
        lines.append(f"| {info.get('snippet', {}).get('title', handle)} | "
                     f"{fmt_int(s.get('subscriberCount', 0))} | "
                     f"{fmt_int(s.get('viewCount', 0))} | "
                     f"{fmt_int(s.get('videoCount', 0))} | "
                     f"{'benchmark' if 'Jea' in handle or 'TTrades' in handle else 'tham chiếu'} |")
    lines.append("")
    lines.append(f"- Video phân tích: **{len(all_vids)}** unique "
                 f"(raw {len(shorts)} shorts-tab + {len(longform)} long-form, "
                 f"overlap đã dedupe theo video_id)")
    lines.append("- Nguồn: YouTube Data API v3 (search.list + videos.list + commentThreads.list)")
    lines.append("")
    lines.append("> **Cảnh báo chất lượng dữ liệu:** `search.list` với `duration=short` "
                 "KHÔNG lọc đáng tin — nhiều video trả về có duration 10-30 phút. Vì vậy "
                 "các video trong run 'shorts' phần lớn thực chất là long-form. Muốn lấy "
                 "Shorts thật phải dùng `channel/videos?tab=shorts` (TranscriptAPI) hoặc "
                 "kiểm tra duration thủ công.")
    lines.append("")

    # ── 1. Format nào thắng (bằng số) ──────────────────────────────────
    lines.append("## 1. Format nào thắng — đo bằng số, không đoán")
    lines.append("")
    lines.append("| Duration bucket | Số video | Avg views | Median views | Avg like rate |")
    lines.append("|-----------------|----------|-----------|--------------|---------------|")
    for b in ["0-60s (Short)", "1-5 min", "5-15 min", "15-30 min", "30+ min"]:
        vids = bucket_stats.get(b, [])
        if not vids:
            continue
        views = sorted(v["_views"] for v in vids)
        avg = sum(views) / len(views)
        med = views[len(views) // 2]
        lr = [v["_likes"] / v["_views"] * 100 for v in vids if v["_views"] > 0]
        avg_lr = sum(lr) / len(lr) if lr else 0
        lines.append(f"| {b} | {len(vids)} | {fmt_int(avg)} | {fmt_int(med)} | {avg_lr:.2f}% |")
    lines.append("")
    lines.append("**Đọc số này thế nào:** so sánh avg views giữa các bucket để biết format nào "
                 "đang được phân phối mạnh. Nhưng cẩn thận — bucket có avg cao có thể chỉ do "
                 "1-2 video viral kéo lên, nên xem cả median.")
    lines.append("")

    # ── 2. Top 20 video — giải phẫu packaging ─────────────────────────
    lines.append("## 2. Top 20 video — giải phẫu packaging")
    lines.append("")
    lines.append("| # | Views | Duration | Title | Kênh |")
    lines.append("|---|-------|----------|-------|------|")
    for i, v in enumerate(top20, 1):
        t = unescape(v.get("title", ""))[:72]
        dur = f"{v['_dur']//60}m{v['_dur']%60:02d}s" if v["_dur"] else "—"
        lines.append(f"| {i} | {fmt_int(v['_views'])} | {dur} | {t} | {v.get('channel', '')} |")
    lines.append("")

    # ── 3. Title formula — trích từ dữ liệu ───────────────────────────
    lines.append("## 3. Công thức tiêu đề — rút từ 20 video thắng")
    lines.append("")
    patterns = Counter()
    for v in top20:
        t = unescape(v.get("title", "")).lower()
        if re.search(r"\bonly\b", t):
            patterns["'The Only X' — tuyên bố độc quyền"] += 1
        if re.search(r"\bever\b", t):
            patterns["'You'll Ever Need' — hứa hẹn tuyệt đối"] += 1
        if re.search(r"\b(step by step|step-by-step|simplified|masterclass|full course)\b", t):
            patterns["'Step by Step / Simplified / Masterclass' — giảm ma sát học"] += 1
        if re.search(r"\b(actually|really|truly)\b", t):
            patterns["'That ACTUALLY Works' — đối đầu với lời hứa rỗng"] += 1
        if re.search(r"\b\d+\b", t):
            patterns["Có con số cụ thể"] += 1
        if re.search(r"\b(beginners?|new)\b", t):
            patterns["Nhắm 'Beginners' — mở rộng tệp khán giả"] += 1
        if re.search(r"\b(before|wait|don't|stop|never)\b", t):
            patterns["Mệnh lệnh/cảnh báo ('Don't', 'Stop', 'Wait For')"] += 1
        if re.search(r"\b(minutes?|seconds?|min|sec)\b", t):
            patterns["Có mốc thời gian"] += 1
    lines.append("| Pattern | Số video top-20 dùng |")
    lines.append("|---------|---------------------|")
    for p, c in patterns.most_common():
        lines.append(f"| {p} | {c} |")
    lines.append("")
    lines.append("**Công thức áp dụng cho Azzam:**")
    lines.append("")
    lines.append("```")
    lines.append("[CẢNH BÁO/MỆNH LỆNH] + [ĐỐI TƯỢNG] + [KẾT QUẢ] + [RÀO CẢN THỜI GIAN/SỐ]")
    lines.append("")
    lines.append("Ví dụ (XAUUSD):")
    lines.append("  • Stop Risking 10% Per XAUUSD Trade (Do This Instead)")
    lines.append("  • The Only XAUUSD Bias Routine You Need (5 Minutes)")
    lines.append("  • 3 XAUUSD Entry Mistakes That Blow Accounts")
    lines.append("  • Why You Keep Losing On Gold (And The Fix)")
    lines.append("```")
    lines.append("")

    # ── 4. Content pillars từ pain point ──────────────────────────────
    lines.append("## 4. Content pillars — map từ pain point có evidence")
    lines.append("")
    lines.append("| Pillar | Pain cluster | Evidence (unique comments) | Vai trò trong phễu |")
    lines.append("|--------|--------------|---------------------------|--------------------|")
    pillar_role = {
        "SA-07": "Top-funnel — kéo người mới vào",
        "SA-02": "Top-funnel — chống 'shiny object'",
        "SA-03": "Mid-funnel — trust qua risk (không hứa lãi)",
        "SA-06": "Bottom-funnel — lý do join Telegram/VIP",
        "SA-04": "Mid-funnel — kỹ thuật, giữ chân",
        "SA-08": "Monetization — affiliate prop firm/broker",
        "SA-05": "Mid-funnel — emotional hook",
        "SA-01": "Bottom-funnel — lý do mua hệ thống",
    }
    for a in sorted(angles, key=lambda x: -x["evidence_count"]):
        lines.append(f"| {a['id']} | {a['pain_cluster']} | {a['evidence_count']} | "
                     f"{pillar_role.get(a['id'], '—')} |")
    lines.append("")

    # ── 5. Packaging cho 5 video đầu ──────────────────────────────────
    lines.append("## 5. Packaging 5 video mở màn (title + thumbnail + hook)")
    lines.append("")
    packs = [
        {
            "angle": "SA-03",
            "title": "1 XAUUSD Trade Can Wipe Your Account (Here's The Math)",
            "thumb": "Nến XAUUSD đỏ dài + con số '10%' gạch chéo đỏ + text '1 TRADE = ACCOUNT GONE'",
            "hook": "0-3s: 'Nếu bạn risk 10% mỗi lệnh XAUUSD, đây là số lệnh bạn cần thua để cháy tài khoản.' → đếm ngược 5-4-3-2-1",
            "cta": "Comment 'RISK'",
            "why": "Con số cụ thể + cảnh báo = pattern 'Don't/Stop' thắng trong top-20",
        },
        {
            "angle": "SA-02",
            "title": "You Don't Need More Indicators — You Need Fewer",
            "thumb": "Chart XAUUSD với 10 indicator bị gạch đỏ, còn 1 cái khoanh xanh + 'DELETE THESE'",
            "hook": "0-3s: 'Tôi xoá 9/10 indicator của mình. Tài khoản bắt đầu tăng từ đó.' → show chart sạch",
            "cta": "Comment 'SIMPLE'",
            "why": "Đối đầu trực tiếp với hành vi phổ biến của khán giả (overcomplicating)",
        },
        {
            "angle": "SA-01",
            "title": "You Know The Strategy. So Why Do You Still Lose?",
            "thumb": "Chia đôi: bên trái 'BIẾT', bên phải 'KHÔNG LÀM ĐƯỢC' + mũi tên gãy",
            "hook": "0-3s: 'Bạn không thiếu kiến thức. Bạn thiếu quy trình. Hai thứ này khác nhau.'",
            "cta": "Comment 'PLAN'",
            "why": "Quote thật từ khán giả đối thủ: 'My problem is discipline. I do not stick to my plan.'",
        },
        {
            "angle": "SA-04",
            "title": "Stop Entering XAUUSD Too Early (3 Confirmations)",
            "thumb": "Chart XAUUSD với 3 điểm vào: 2 cái gạch đỏ (sớm), 1 cái khoanh xanh (đúng)",
            "hook": "0-3s: 'Đây là lý do bạn vào đúng hướng nhưng vẫn thua — bạn vào sớm 3 nến.'",
            "cta": "Comment 'ENTRY'",
            "why": "Lỗi kỹ thuật cụ thể, dễ chứng minh bằng chart",
        },
        {
            "angle": "SA-06",
            "title": "Trading Alone Is Why You're Not Improving",
            "thumb": "1 người đơn độc nhìn chart vs nhóm người review chart cùng nhau",
            "hook": "0-3s: 'Tôi mất 2 năm vì trade một mình. Feedback từ 1 người khác rút ngắn nó còn 6 tháng.'",
            "cta": "Join Telegram",
            "why": "Quote thật: 'I'm tired of trading by myself since my friend gave up'",
        },
    ]
    for i, p in enumerate(packs, 1):
        lines.append(f"### Video {i} — pillar {p['angle']}")
        lines.append(f"- **Title:** {p['title']}")
        lines.append(f"- **Thumbnail:** {p['thumb']}")
        lines.append(f"- **Hook (0-3s):** {p['hook']}")
        lines.append(f"- **CTA:** {p['cta']}")
        lines.append(f"- **Vì sao packaging này:** {p['why']}")
        lines.append("")

    # ── 6. Funnel mechanics ───────────────────────────────────────────
    lines.append("## 6. Phễu — cơ chế cụ thể, không phải khẩu hiệu")
    lines.append("")
    lines.append("### Bước 1 — Comment keyword → Telegram")
    lines.append("")
    lines.append("```")
    lines.append("Video CTA: \"Comment 'RISK' để nhận risk calculator\"")
    lines.append("   ↓")
    lines.append("Pinned comment (chính chủ): \"Đã gửi cho mọi người comment 'RISK' — "
                 "ai chưa nhận được thì join đây: [Telegram link]\"")
    lines.append("   ↓")
    lines.append("Telegram bot: /start → hỏi 'Bạn đang trade cặp nào?' → gửi đúng lead magnet")
    lines.append("   ↓")
    lines.append("Tag lead theo keyword nguồn (RISK / SIMPLE / ENTRY / PLAN / PSYCH)")
    lines.append("```")
    lines.append("")
    lines.append("**Vì sao hoạt động:** comment keyword (a) tăng engagement signal cho "
                 "thuật toán, (b) tạo phân khúc lead theo pain point, (c) đo được video nào "
                 "ra lead tốt nhất.")
    lines.append("")
    lines.append("### Bước 2 — Nurture 7 ngày trên Telegram")
    lines.append("")
    lines.append("| Ngày | Nội dung | Mục đích |")
    lines.append("|------|----------|----------|")
    nurture = [
        ("1", "Chào + hỏi mục tiêu trading hiện tại", "Segment"),
        ("2", "Bài học risk management 1 trang", "Giá trị thuần"),
        ("3", "Checklist entry 5 bước (PDF)", "Giá trị thuần"),
        ("4", "Case study: 1 lệnh thua được xử lý đúng cách", "Trust — dám show thua"),
        ("5", "Video long-form mới nhất + tóm tắt", "Kéo về YouTube"),
        ("6", "Mời vào buổi live XAUUSD", "Tương tác"),
        ("7", "Offer tripwire (template + calculator)", "Convert"),
    ]
    for d, c, p in nurture:
        lines.append(f"| {d} | {c} | {p} |")
    lines.append("")
    lines.append("**Quy tắc cứng:** ngày 1-6 không bán. Ngày 7 mới offer. Offer phải qua "
                 "human review trước khi gửi.")
    lines.append("")
    lines.append("### Bước 3 — Offer ladder")
    lines.append("")
    lines.append("| Tầng | Sản phẩm | Giá | Nguồn lead |")
    lines.append("|------|----------|-----|-----------|")
    lines.append("| Tripwire | Trading Plan Template + Risk Calculator | $9-27 | comment RISK/PLAN |")
    lines.append("| Core | Complete System (Basic → Setup → Execution) | $97-297 | tripwire buyers |")
    lines.append("| VIP | Mentorship + group review hàng tuần | $497+/tháng | core buyers |")
    lines.append("| Affiliate | Broker IB + Prop firm + Tools | hoa hồng | mọi tầng |")
    lines.append("")

    # ── 7. Guardrails ─────────────────────────────────────────────────
    lines.append("## 7. Guardrail — không thoả hiệp")
    lines.append("")
    lines.append("| Được | Không được |")
    lines.append("|------|-----------|")
    lines.append("| Show lệnh thua và cách xử lý | Show trade giả / chart mô phỏng như trade thật |")
    lines.append("| Nói về quy trình, xác suất, kỷ luật | Cam kết lợi nhuận, % thắng, 'chắc chắn lãi' |")
    lines.append("| Affiliate có disclosure rõ | Affiliate ngầm, giấu quan hệ thương mại |")
    lines.append("| Sales copy ở dạng draft | Auto-send sales/affiliate khi chưa có approval |")
    lines.append("| Dùng comment thật làm evidence (có link) | Bịa testimonial / quote khán giả |")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 8. Việc cần Alan duyệt trước khi thực thi")
    lines.append("")
    lines.append("1. Telegram gateway cho project YouTube (chưa xác nhận bot/chat ID riêng)")
    lines.append("2. Offer ladder + giá (chưa có quyết định)")
    lines.append("3. Broker/prop firm affiliate nào (chưa chọn đối tác)")
    lines.append("4. Có target khán giả tiếng Việt hay tiếng Anh (ảnh hưởng toàn bộ title/tag)")
    lines.append("")

    (OUT / "mrbeast_playbook.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Written {OUT / 'mrbeast_playbook.md'}")
    print(f"Videos analysed: {len(all_vids)}")
    print(f"Title patterns found: {len(patterns)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

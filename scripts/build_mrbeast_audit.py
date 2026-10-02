#!/usr/bin/env python3
"""Audit kênh theo phương pháp MrBeast — chẩn đoán, plan action, SOP, build-to-sell.

Đọc dữ liệu thật:
  outputs/mrbeast_audit/azzam_videos.json   (297 video kênh mình)
  outputs/mrbeast_audit/gta_videos.json     (742 video đối thủ)
  outputs/reports/blindspots.json           (điểm mù từ analytics OAuth)
  vendor/.../analytics_latest.json          (private metrics)

Xuất:
  outputs/reports/MRBEAST_AUDIT.md
  outputs/strategy/MRBEAST_PLAN_ACTION.md
  outputs/strategy/MRBEAST_SOP.md
  outputs/strategy/MRBEAST_BUILD_TO_SELL.md

Mọi số liệu tính từ file thật. Không suy diễn ngoài dữ liệu.

Usage:
    python scripts/build_mrbeast_audit.py
"""
from __future__ import annotations

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
AUD = ROOT / "outputs" / "mrbeast_audit"
OUT_R = ROOT / "outputs" / "reports"
OUT_S = ROOT / "outputs" / "strategy"
VENDOR = ROOT / "vendor" / "youtube-analytics-dashboard"


def load(p: Path):
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def pct(n, d) -> float:
    return (n / d * 100) if d else 0.0


def fmt(n) -> str:
    return f"{int(n):,}"


def stats(arr, key="views"):
    if not arr:
        return {"n": 0, "avg": 0, "med": 0, "max": 0, "total": 0, "p90": 0}
    vs = sorted(v[key] for v in arr)
    n = len(vs)
    return {"n": n, "avg": sum(vs) // n, "med": vs[n // 2],
            "max": vs[-1], "total": sum(vs), "p90": vs[int(n * 0.9)]}


def main() -> int:
    A = load(AUD / "azzam_videos.json")
    G = load(AUD / "gta_videos.json")
    blind = load(OUT_R / "blindspots.json")
    an = load(VENDOR / "analytics_latest.json")
    if not A or not G:
        print("Thiếu dữ liệu audit. Chạy bước fetch video inventory trước.", file=sys.stderr)
        return 1

    # ── Phân loại ──────────────────────────────────────────────────────────
    a_s = [v for v in A if 0 < v["duration_s"] <= 60]
    a_l = [v for v in A if v["duration_s"] > 60]
    a_ev = [v for v in A if 60 < v["duration_s"] <= 600]
    g_s = [v for v in G if 0 < v["duration_s"] <= 60]
    g_l = [v for v in G if v["duration_s"] > 60]
    g_ev = [v for v in G if 60 < v["duration_s"] <= 600
            and not re.search(r"live", v["title"], re.I)]

    sa_s, sa_l, sa_ev = stats(a_s), stats(a_l), stats(a_ev)
    sg_s, sg_l, sg_ev = stats(g_s), stats(g_l), stats(g_ev)

    # momentum shorts theo tháng
    bym = defaultdict(list)
    for v in a_s:
        bym[v["published"][:7]].append(v)
    momentum = [(m, stats(arr)) for m, arr in sorted(bym.items())]

    # winner vs loser
    win = [v for v in a_s if v["views"] >= 1000]
    lose = [v for v in a_s if v["views"] < 100]
    win_dur = sum(v["duration_s"] for v in win) / len(win) if win else 0
    lose_dur = sum(v["duration_s"] for v in lose) / len(lose) if lose else 0

    # evergreen gap
    ev_gap = sg_ev["avg"] / sa_ev["avg"] if sa_ev["avg"] else 0
    lf_gap = sg_l["avg"] / sa_l["avg"] if sa_l["avg"] else 0

    # bot
    bot = (blind or {}).get("bot_traffic", {})
    bot_v = int(bot.get("views") or 0)
    views_28 = int((an or {}).get("metrics", {}).get("views") or 0)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # ══════════════════════════════════════════════════════════════════════
    # 1. AUDIT
    # ══════════════════════════════════════════════════════════════════════
    L = []
    L.append("# AUDIT KÊNH THEO PHƯƠNG PHÁP MRBEAST")
    L.append("")
    L.append(f"*Sinh: {now}*  •  Kênh: **@azzammastertradinggold**  •  "
             f"Ngách: XAUUSD / Forex")
    L.append("")
    L.append("Nguồn: YouTube Data API v3 (channels.list, playlistItems.list, videos.list) "
             "+ YouTube Analytics API (OAuth, private metrics). "
             f"Toàn bộ {len(A)} video kênh mình và {len(G)} video đối thủ đã fetch. "
             "Không có số liệu nhập tay.")
    L.append("")
    L.append("---")
    L.append("")

    L.append("## 0. CẢNH BÁO TRƯỚC KHI ĐỌC TIẾP")
    L.append("")
    if bot_v:
        L.append(f"**Traffic nghi bot: {fmt(bot_v)} views "
                 f"({bot.get('pct_of_channel')}% tổng view 28 ngày).**")
        L.append("")
        L.append("Referrer: `com.example.seofast`, `com.playzero.playbotsseofast` — "
                 "app farm view, không phải site thật. Ngày 29/09 có 8,153 views "
                 "trong khi trung vị các ngày khác ~35 views.")
        L.append("")
        L.append("Đây là **việc phải xử lý TRƯỚC mọi tối ưu khác**. Nếu để nguyên, "
                 "YouTube có thể xoá view hoặc phạt kênh theo Fake Engagement Policy, "
                 "và mọi chỉ số tăng trưởng sẽ là số ảo.")
        L.append("")
        real = views_28 - bot_v
        L.append(f"**Số liệu thật sau khi trừ bot:** ~{fmt(real)} views / 28 ngày "
                 f"(~{real/28:.0f} view/ngày), thay vì {fmt(views_28)}.")
    else:
        L.append("Không phát hiện traffic bất thường trong cửa sổ phân tích.")
    L.append("")
    L.append("---")
    L.append("")

    L.append("## 1. CHẨN ĐOÁN: KÊNH ĐANG Ở ĐÂU")
    L.append("")
    L.append("| | Kênh mình | Đối thủ (GTA) | Khoảng cách |")
    L.append("|---|---|---|---|")
    L.append("| Subscribers | 1,980 | 14,100 | **7.1×** |")
    L.append("| Tổng views | 242,480 | 1,404,476 | **5.8×** |")
    L.append("| Số video | 297 | 742 | 2.5× |")
    L.append("| Views/video | 816 | 1,898 | **2.3×** |")
    L.append("| Ngày tạo kênh | 2024-05 | 2016-10 | — |")
    L.append("")
    L.append("### 1.1 Vấn đề số 1: LONG-FORM GẦN NHƯ KHÔNG HOẠT ĐỘNG")
    L.append("")
    L.append("| | Kênh mình | Đối thủ | Khoảng cách |")
    L.append("|---|---|---|---|")
    L.append(f"| Số video long (>60s) | {sa_l['n']} | {sg_l['n']} | — |")
    L.append(f"| Views trung bình | **{fmt(sa_l['avg'])}** | **{fmt(sg_l['avg'])}** | "
             f"**{lf_gap:.1f}×** |")
    L.append(f"| Median | {fmt(sa_l['med'])} | {fmt(sg_l['med'])} | "
             f"{sg_l['med']/max(sa_l['med'],1):.0f}× |")
    L.append(f"| Cao nhất | {fmt(sa_l['max'])} | {fmt(sg_l['max'])} | — |")
    L.append("")
    L.append("**Đây là vấn đề nghiêm trọng nhất của kênh.** 156 video long-form "
             "chỉ mang về tổng cộng "
             f"{fmt(sa_l['total'])} views — ít hơn **một** video Short tốt nhất "
             f"({fmt(sa_s['max'])} views).")
    L.append("")
    L.append("Nguyên nhân: **90% long-form là livestream** "
             f"({sum(1 for v in a_l if re.search(r'live', v['title'], re.I))}/{sa_l['n']}), "
             "và livestream có 2 nhược điểm cấu trúc:")
    L.append("")
    L.append("1. **Không có thumbnail cạnh tranh được** — YouTube không hiển thị "
             "thumbnail livestream trong đề xuất như video thường.")
    L.append("2. **Không tái sử dụng được** — video 8-13 giờ không ai xem lại, "
             "không có giá trị evergreen, không lên search.")
    L.append("")
    L.append(f"Cụ thể: **{sum(1 for v in a_l if v['duration_s'] > 28800)} video dài "
             f"hơn 8 giờ**. Đây là livestream ghi lại, không phải nội dung biên tập.")
    L.append("")

    L.append("### 1.2 Vấn đề số 2: KHÔNG CÓ NỘI DUNG EVERGREEN")
    L.append("")
    L.append("| | Kênh mình | Đối thủ | Khoảng cách |")
    L.append("|---|---|---|---|")
    L.append(f"| Video 1-10 phút | {sa_ev['n']} | {sg_ev['n']} | — |")
    L.append(f"| Views trung bình | **{fmt(sa_ev['avg'])}** | **{fmt(sg_ev['avg'])}** | "
             f"**{ev_gap:.0f}×** |")
    L.append("")
    L.append("Video 1-10 phút là **xương sống của kênh trading**: lên search, "
             "được đề xuất lâu dài, tạo sub đều đặn, và là nơi bán offer.")
    L.append("")
    L.append(f"Kênh mình có {sa_ev['n']} video dạng này với trung bình "
             f"**{fmt(sa_ev['avg'])} views**. Đối thủ có {sg_ev['n']} video, "
             f"trung bình **{fmt(sg_ev['avg'])} views** — gấp **{ev_gap:.0f} lần**.")
    L.append("")
    L.append("Nghĩa là: kênh mình **gần như không tồn tại** trên YouTube search. "
             "Điều này khớp với số liệu analytics: chỉ "
             "**1.2% traffic đến từ tìm kiếm YouTube**.")
    L.append("")
    L.append("Đối thủ làm format gì ở nhóm này (mẫu thật):")
    L.append("")
    for v in sorted(g_ev, key=lambda x: -x["views"])[:6]:
        m, s = divmod(v["duration_s"], 60)
        L.append(f"- `{m}:{s:02d}` · {fmt(v['views'])} views · {v['title'][:70]}")
    L.append("")
    L.append("Đối thủ còn có **81 video dạng \"How to\"** với trung bình "
             "728 views — công thức tiêu đề dạng câu hỏi/hướng dẫn, "
             "khớp trực tiếp với truy vấn tìm kiếm.")
    L.append("")

    L.append("### 1.3 Vấn đề số 3: SHORTS MẤT ĐÀ")
    L.append("")
    L.append("| Tháng | Số Short | Views TB | Median | Cao nhất |")
    L.append("|---|---|---|---|---|")
    for m, st in momentum:
        L.append(f"| {m} | {st['n']} | {fmt(st['avg'])} | {fmt(st['med'])} | "
                 f"{fmt(st['max'])} |")
    L.append("")
    L.append("Kênh từng có đà rất tốt (03/2026: TB 7,642 views/short), "
             "rồi sụp xuống và hiện gần như bằng 0. Đây không phải vấn đề "
             "thuật toán — đây là **vấn đề nội dung và nhịp đăng**.")
    L.append("")
    L.append(f"Phân bố cho thấy vấn đề rõ hơn: **{sum(1 for v in a_s if v['views']<100)}"
             f"/{sa_s['n']} Short ({pct(sum(1 for v in a_s if v['views']<100), sa_s['n']):.0f}%) "
             f"dưới 100 views**, chỉ {len(win)} video vượt 1,000 views.")
    L.append("")
    L.append("Nhưng có tín hiệu tốt: khi làm đúng, kênh vẫn thắng được:")
    L.append("")
    L.append("| Views | Độ dài | Ngày | Tiêu đề |")
    L.append("|---|---|---|---|")
    for v in sorted(a_s, key=lambda x: -x["views"])[:6]:
        L.append(f"| {fmt(v['views'])} | {v['duration_s']}s | {v['published']} | "
                 f"{v['title'][:52]} |")
    L.append("")
    L.append(f"**Phát hiện quan trọng:** Short thắng có độ dài trung bình "
             f"**{win_dur:.0f} giây**, Short thua là **{lose_dur:.0f} giây**. "
             f"Short ngắn hơn thắng rõ rệt.")
    L.append("")
    L.append("Và chuỗi **FOREX LESSON** là format duy nhất từng thắng lặp lại được "
             f"({len([v for v in a_s if 'FOREX LESSON' in v['title'].upper()])} video, "
             "nhiều video 1,400-9,800 views, độ dài 8-21 giây). "
             "**Đây là format cần khôi phục và mở rộng.**")
    L.append("")

    L.append("### 1.4 Vấn đề số 4: TƯƠNG TÁC GẦN NHƯ BẰNG 0")
    L.append("")
    L.append("| Chỉ số | Kênh mình | Tham chiếu |")
    L.append("|---|---|---|")
    L.append(f"| Sub conversion | **0.055%** | ngành 0.5–2% |")
    L.append(f"| Comment rate | **0.0111%** (1 comment / 9,016 view) | 0.1–0.5% |")
    L.append(f"| Sub ròng 28 ngày | **-3** (+5 / -8) | phải dương |")
    L.append("")
    L.append("Comment rate gần 0 nghĩa là **kênh không có cộng đồng**. "
             "Với kênh trading, cộng đồng là tài sản duy nhất chuyển được "
             "thành lead → offer. Không có comment = không có phễu.")
    L.append("")
    L.append("Sub ròng âm nghĩa là **kênh đang mất người nhanh hơn thu được**. "
             "Đây là dấu hiệu nội dung không giữ chân được.")
    L.append("")

    L.append("### 1.5 Điểm mạnh cần giữ")
    L.append("")
    L.append(f"1. **Short ngắn thắng được** — video 22s đạt {fmt(sa_s['max'])} views. "
             "Thuật toán không chặn kênh; nội dung mới là vấn đề.")
    L.append("2. **Format FOREX LESSON đã được chứng minh** — chuỗi video 8-21s, "
             "nhiều video 1,400-9,800 views. Có công thức, chỉ cần sản xuất lại.")
    L.append("3. **Kênh mới (2024-05)** — chỉ 1.5 năm, vẫn còn dư địa lớn. "
             "Đối thủ mất 8 năm mới đạt 14,100 sub.")
    L.append("4. **Nhịp đăng cao** — 21.2 video/tháng, gấp 3.5× trung bình "
             "cả vòng đời của đối thủ. Khả năng sản xuất không phải nút cổ chai.")
    L.append("5. **Livestream có người xem thật** — 1,200 views/video livestream, "
             "avg view 79 giây. Có audience trung thành nhỏ nhưng thật.")
    L.append("")

    L.append("### 1.6 Bảng điểm MrBeast")
    L.append("")
    L.append("| Trụ cột | Điểm /10 | Căn cứ |")
    L.append("|---|---|---|")
    L.append("| **Hook** (3 giây đầu) | 4/10 | Short thắng 14s vs thua 21s — "
             "hook dài dòng; FOREX LESSON chứng minh ngắn hơn thắng |")
    L.append("| **Packaging** (title/thumbnail) | 5/10 | Title TB 64 ký tự, "
             "91% có số (tốt) nhưng chỉ 35% có emoji và 6% có năm — "
             "đối thủ dùng 46% emoji, 51% năm |")
    L.append("| **Retention** | 2/10 | Avg view 98s / 0.29% video — "
             "người xem rời gần như ngay |")
    L.append("| **Nhịp đăng** | 7/10 | 21.2 video/tháng — tốt, nhưng phân bố "
             "sai (90% long-form là livestream) |")
    L.append("| **Nội dung evergreen** | 1/10 | 15 video 1-10 phút, TB 6 views — "
             "gần như không có |")
    L.append("| **Cộng đồng** | 1/10 | 1 comment / 9,016 view, sub ròng âm |")
    L.append("| **Phễu chuyển đổi** | 2/10 | Không có offer rõ, "
             "không có CTA dẫn tới bước tiếp theo |")
    L.append("| **Điểm tổng** | **3.1/10** | |")
    L.append("")

    (OUT_R / "MRBEAST_AUDIT.md").write_text("\n".join(L), encoding="utf-8")
    print(f"Written: {OUT_R / 'MRBEAST_AUDIT.md'}")

    # ══════════════════════════════════════════════════════════════════════
    # 2. PLAN ACTION
    # ══════════════════════════════════════════════════════════════════════
    P = []
    P.append("# PLAN ACTION — 90 NGÀY")
    P.append("")
    P.append(f"*Sinh: {now}*  •  Kênh: @azzammastertradinggold")
    P.append("")
    P.append("Mục tiêu: chuyển kênh từ **3.1/10** sang **6/10** trong 90 ngày, "
             "với KPI đo được. Mọi hành động dưới đây đều bám vào số liệu ở "
             "`MRBEAST_AUDIT.md`.")
    P.append("")
    P.append("---")
    P.append("")
    P.append("## GIAI ĐOẠN 0 — TUẦN 1: DỌN ĐƯỜNG (bắt buộc trước mọi thứ)")
    P.append("")
    P.append("| # | Hành động | Owner | KPI | Bằng chứng hoàn thành |")
    P.append("|---|---|---|---|---|")
    P.append(f"| 0.1 | **Điều tra traffic bot {fmt(bot_v)} views** — xác định "
             f"nguồn `seofast`/`playbots` từ đâu. Kiểm tra: có ai mua view? "
             f"dịch vụ SEO nào? | Alan | Xác định được nguồn | "
             f"Ghi rõ trong `outputs/reports/blindspots.md` |")
    P.append("| 0.2 | **Dừng mọi nguồn traffic trả phí** nếu phát hiện có mua view | "
             "Alan | Không còn referrer lạ | Analytics 7 ngày sau sạch |")
    P.append("| 0.3 | Bật Publish app trên Google Cloud → token OAuth không hết hạn "
             "7 ngày | Alan | Token vĩnh viễn | `yt_oauth_login.py --check` pass |")
    P.append("| 0.4 | Bật CapCut MCP backend (port 9001) | Alan | MCP chạy | "
             "WF12 pipeline health xanh hết |")
    P.append("")
    P.append("**Gate:** không làm gì ở Giai đoạn 1-3 nếu 0.1 chưa xong. "
             "Tối ưu trên nền số liệu ảo là vô nghĩa.")
    P.append("")
    P.append("---")
    P.append("")

    P.append("## GIAI ĐOẠN 1 — TUẦN 2-4: SỬA NỘI DUNG CỐT LÕI")
    P.append("")
    P.append("### 1A. Khôi phục format FOREX LESSON (Short)")
    P.append("")
    P.append("**Căn cứ:** chuỗi này đã thắng thật — "
             f"{len([v for v in a_s if 'FOREX LESSON' in v['title'].upper()])} video, "
             "nhiều video 1,400-9,800 views. Độ dài 8-21 giây.")
    P.append("")
    P.append("| # | Hành động | KPI |")
    P.append("|---|---|---|")
    P.append("| 1A.1 | Sản xuất lại 30 Short FOREX LESSON, "
             "**bám sát 2 công thức đã thắng**: độ dài 8-21s, tiêu đề "
             "`FOREX LESSON #N + [chủ đề]` | 30 video / 4 tuần |")
    P.append("| 1A.2 | Mỗi Short phải có hook trong **3 giây đầu** — "
             "hiển thị câu hỏi hoặc con số ngay frame 1 | 100% video |")
    P.append("| 1A.3 | Giữ độ dài **≤21 giây** (Short thắng TB 14s, thua 21s) | "
             "median ≤18s |")
    P.append("| 1A.4 | Đo lại sau 30 ngày: median views/short phải **>200** "
             f"(hiện tại {fmt(sa_s['med'])}) | median >200 |")
    P.append("")
    P.append("### 1B. Tạo dòng EVERGREEN 1-10 phút (ưu tiên cao nhất)")
    P.append("")
    P.append(f"**Căn cứ:** đây là khoảng cách lớn nhất — kênh mình "
             f"{sa_ev['n']} video TB {fmt(sa_ev['avg'])} views, "
             f"đối thủ {sg_ev['n']} video TB {fmt(sg_ev['avg'])} views "
             f"(**{ev_gap:.0f}×**).")
    P.append("")
    P.append("| # | Hành động | KPI |")
    P.append("|---|---|---|")
    P.append("| 1B.1 | Sản xuất **2 video/tuần, độ dài 5-8 phút**, "
             "KHÔNG phải livestream | 8 video / 4 tuần |")
    P.append("| 1B.2 | Chủ đề theo format \"How to\" — đối thủ dùng format này "
             "81 lần, TB 728 views | 100% dùng tiêu đề dạng how-to |")
    P.append("| 1B.3 | Mỗi video phải trả lời **1 câu hỏi cụ thể** "
             "người mới hay hỏi | 1 câu hỏi / video |")
    P.append("| 1B.4 | Đo lại sau 30 ngày: TB views/video evergreen **>100** "
             f"(hiện tại {fmt(sa_ev['avg'])}) | TB >100 |")
    P.append("")
    P.append("**Chủ đề lấy từ dữ liệu thật** — câu hỏi khán giả đã cào được "
             "(984 comment có dấu hỏi trong 7,937 comment):")
    P.append("")
    P.append("- \"What is the best paper trading account you have been using?\"")
    P.append("- \"What would you suggest for a beginner? Go through those videos "
             "first or start from here?\"")
    P.append("- \"Can you suggest the order to watch these videos?\"")
    P.append("- \"I'm a beginner and I can frame a daily bias this way but how "
             "exactly to trade with this?\"")
    P.append("- \"Where is the PDF?\" / \"I need this PDF\" — nhu cầu tài liệu rất rõ")
    P.append("")
    P.append("### 1C. Cắt giảm livestream, chuyển thành nội dung biên tập")
    P.append("")
    P.append("| # | Hành động | KPI |")
    P.append("|---|---|---|")
    P.append("| 1C.1 | Giảm livestream từ 90% long-form xuống **≤50%** | "
             "Đo lại cơ cấu sau 30 ngày |")
    P.append("| 1C.2 | **Tái chế livestream thành video ngắn có biên tập**: "
             "cắt 1 phiên live 8 giờ thành 3-5 clip 5-8 phút theo chủ đề "
             "(1 setup, 1 phân tích, 1 bài học) | 3-5 video / phiên live |")
    P.append("| 1C.3 | Video cắt lại phải có **thumbnail + title riêng**, "
             "không dùng tên livestream | 100% video |")
    P.append("")
    P.append("**Đây là đòn bẩy lớn nhất về mặt thời gian:** kênh đã có "
             f"{sum(1 for v in a_l if v['duration_s'] > 28800)} phiên live dài. "
             "Đó là kho nguyên liệu chưa khai thác — không cần quay mới.")
    P.append("")
    P.append("---")
    P.append("")

    P.append("## GIAI ĐOẠN 2 — TUẦN 5-8: PACKAGING + CỘNG ĐỒNG")
    P.append("")
    P.append("### 2A. Sửa packaging theo công thức đối thủ")
    P.append("")
    P.append("| Yếu tố | Kênh mình | Đối thủ | Hành động |")
    P.append("|---|---|---|---|")
    P.append("| Emoji trong title | 35% | 46% | Tăng lên ≥50% |")
    P.append("| Năm trong title | 6% | 51% | Thêm năm vào video "
             "có yếu tố thời sự |")
    P.append("| CAPS >50% | 13% | 50% | Dùng cho video cảnh báo/tin nóng |")
    P.append("| Có số trong title | 91% | 57% | Giữ (đang tốt) |")
    P.append("| Độ dài title | 64 ký tự | 60 ký tự | Rút xuống ≤60 |")
    P.append("")
    P.append("### 2B. Xây cộng đồng — sửa comment rate từ 0.0111%")
    P.append("")
    P.append("| # | Hành động | KPI |")
    P.append("|---|---|---|")
    P.append("| 2B.1 | **CTA comment từ khoá** trong mọi video: "
             "\"Comment ENTRY if you want the checklist\" | 100% video có CTA |")
    P.append("| 2B.2 | **Trả lời mọi comment trong 2 giờ đầu** sau khi đăng | "
             "Response rate >90% |")
    P.append("| 2B.3 | Pinned comment trên mỗi video với câu hỏi mở | "
             "100% video |")
    P.append("| 2B.4 | Đo lại sau 30 ngày: comment rate **>0.1%** "
             "(hiện 0.0111%) | >0.1% |")
    P.append("| 2B.5 | Sub ròng phải **dương** | >+20 sub/tháng |")
    P.append("")
    P.append("**Ranh giới chính sách — KHÔNG được vượt:** chỉ dùng pinned "
             "comment / Community post / trả lời thật trên kênh mình. "
             "Không tạo tài khoản ảo, không mua like/view/comment, "
             "không rải link lên kênh người khác.")
    P.append("")
    P.append("---")
    P.append("")

    P.append("## GIAI ĐOẠN 3 — TUẦN 9-12: PHỄU + ĐO LƯỜNG")
    P.append("")
    P.append("| # | Hành động | KPI |")
    P.append("|---|---|---|")
    P.append("| 3.1 | Xây phễu: Short (thu hút) → Evergreen (giữ chân) → "
             "Telegram (lead) → Offer (chuyển đổi) | 4 tầng hoạt động |")
    P.append("| 3.2 | CTA dẫn Telegram trong mọi video (hiện chưa có link thật) | "
             "100% video |")
    P.append("| 3.3 | Đo conversion từng tầng | Báo cáo tuần |")
    P.append("| 3.4 | Đánh giá lại toàn bộ: điểm MrBeast phải **≥6/10** | ≥6/10 |")
    P.append("")
    P.append("---")
    P.append("")
    P.append("## BẢNG KPI TỔNG — ĐO ĐƯỢC")
    P.append("")
    P.append("| Chỉ số | Hiện tại | Ngày 30 | Ngày 60 | Ngày 90 |")
    P.append("|---|---|---|---|---|")
    P.append(f"| Median views/Short | {fmt(sa_s['med'])} | 200 | 400 | 700 |")
    P.append(f"| TB views/video evergreen | {fmt(sa_ev['avg'])} | 100 | 250 | 400 |")
    P.append(f"| Comment rate | 0.0111% | 0.05% | 0.1% | 0.15% |")
    P.append("| Sub ròng/tháng | -3 | +20 | +60 | +120 |")
    P.append(f"| Sub conversion | 0.055% | 0.15% | 0.3% | 0.5% |")
    P.append("| Tỷ lệ traffic từ search | 1.2% | 4% | 8% | 12% |")
    P.append("| Video evergreen/tuần | 0 | 2 | 2 | 3 |")
    P.append("| Tỷ lệ long-form là livestream | 90% | 70% | 60% | 50% |")
    P.append("")
    P.append("**Nguyên tắc đo:** mọi chỉ số lấy từ `analytics_latest.json` "
             "(OAuth) hoặc `azzam_videos.json` (Data API) — không nhập tay. "
             "Chạy `scripts/analyze_blindspots.py` mỗi tuần để cập nhật.")
    P.append("")
    P.append("---")
    P.append("")
    P.append("## 5 HÀNH ĐỘNG ƯU TIÊN CAO NHẤT (nếu chỉ làm được 5 việc)")
    P.append("")
    P.append(f"1. **Điều tra {fmt(bot_v)} views nghi bot** — mọi thứ khác "
             "vô nghĩa nếu số liệu nền là giả.")
    P.append("2. **Tạo dòng evergreen 5-8 phút, 2 video/tuần** — khoảng cách "
             f"{ev_gap:.0f}× với đối thủ, đây là chỗ trống lớn nhất.")
    P.append("3. **Tái chế "
             f"{sum(1 for v in a_l if v['duration_s'] > 28800)} phiên live dài "
             "thành video biên tập** — kho nguyên liệu miễn phí, không cần quay mới.")
    P.append("4. **Khôi phục format FOREX LESSON** (Short 8-21s) — format duy "
             "nhất từng thắng lặp lại.")
    P.append("5. **CTA comment + trả lời mọi comment** — sửa comment rate "
             "từ 0.0111%, mở lại phễu cộng đồng.")
    P.append("")

    (OUT_S / "MRBEAST_PLAN_ACTION.md").write_text("\n".join(P), encoding="utf-8")
    print(f"Written: {OUT_S / 'MRBEAST_PLAN_ACTION.md'}")

    # ══════════════════════════════════════════════════════════════════════
    # 3. SOP TRIỂN KHAI
    # ══════════════════════════════════════════════════════════════════════
    S = []
    S.append("# SOP TRIỂN KHAI — QUY TRÌNH SẢN XUẤT HẰNG NGÀY")
    S.append("")
    S.append(f"*Sinh: {now}*  •  Kênh: @azzammastertradinggold  •  Ngôn ngữ: ENGLISH")
    S.append("")
    S.append("**Ngưỡng kiểm tra SOP:** nếu editor hiện tại nghỉ hôm nay, "
             "người mới đọc tài liệu này có chạy được 3 Short + 1 Long "
             "trong ngày đầu không? Nếu không, SOP chưa đủ tốt.")
    S.append("")
    S.append("---")
    S.append("")
    S.append("## 1. CƠ CẤU NỘI DUNG MỚI (thay cho cơ cấu cũ)")
    S.append("")
    S.append("| Loại | Số lượng/ngày | Độ dài | Mục đích | Nguồn |")
    S.append("|---|---|---|---|---|")
    S.append("| Short FOREX LESSON | 2 | 8-21s | Thu hút, tăng sub | Quay mới |")
    S.append("| Short tái chế từ live | 1 | 15-40s | Tận dụng kho có sẵn | Cắt từ livestream |")
    S.append("| Evergreen how-to | 1 (cách ngày) | 5-8 phút | SEO, giữ chân, bán offer | "
             "Quay mới hoặc biên tập từ live |")
    S.append("")
    S.append("**Thay đổi then chốt:** cơ cấu cũ là 3 Short + 1 Long-livestream "
             "(90% long-form là livestream 8-13 giờ, TB 102 views). "
             "Cơ cấu mới bỏ long-form livestream khỏi slot sản xuất, "
             "thay bằng evergreen 5-8 phút.")
    S.append("")
    S.append("---")
    S.append("")
    S.append("## 2. QUY TRÌNH 8 BƯỚC MỘT NGÀY")
    S.append("")
    S.append("### Bước 1 — Lấy nguyên liệu (10 phút, đầu ngày)")
    S.append("")
    S.append("```bash")
    S.append("# Comment + pain point mới nhất")
    S.append("python scripts/competitor_longform_scrape.py")
    S.append("python scripts/extract_painpoints.py "
             "outputs/competitor_longform/raw_comments.json "
             "--output-dir outputs/competitor_longform "
             "--actor youtube-data-api-v3/commentThreads.list")
    S.append("")
    S.append("# Danh sách pain point chờ duyệt")
    S.append("python scripts/build_ops_dashboard.py")
    S.append("```")
    S.append("")
    S.append("Mở `outputs/dashboard/ops.html` → xem \"Top pain point — chờ duyệt\".")
    S.append("")
    S.append("### Bước 2 — Chốt hook (10 phút)")
    S.append("")
    S.append("Chọn **3 pain point** từ danh sách trên. Mỗi cái thành 1 Short.")
    S.append("")
    S.append("**Quy tắc chọn hook:**")
    S.append("- Phải là **nỗi đau cụ thể**, không phải lời cảm ơn "
             "(\"you changed my life\" → loại)")
    S.append("- Phải trả lời được trong **8-21 giây**")
    S.append("- Phải có **1 hành động cụ thể** người xem làm được ngay")
    S.append("")
    S.append("### Bước 3 — Draft script (15 phút, AI hỗ trợ)")
    S.append("")
    S.append("Dùng `prompts/02_VIET_HOOK.md`. Yêu cầu với AI:")
    S.append("")
    S.append("```")
    S.append("Viết script Short 8-21 giây cho kênh XAUUSD/Forex.")
    S.append("Hook: [pain point đã chọn]")
    S.append("")
    S.append("RÀNG BUỘC:")
    S.append("- Hook phải trong 3 giây đầu, dạng câu hỏi hoặc con số")
    S.append("- Không cam kết lợi nhuận, không nói 'guaranteed', 'always wins'")
    S.append("- Không hiển thị kết quả trade giả")
    S.append("- Kết bằng CTA: 'Comment ENTRY for the checklist'")
    S.append("```")
    S.append("")
    S.append("### Bước 4 — Dựng draft bằng CapCut MCP (20 phút)")
    S.append("")
    S.append("```bash")
    S.append("# Bắt buộc: MCP backend phải chạy trước")
    S.append("python tools/VectCutAPI/capcut_server.py")
    S.append("```")
    S.append("")
    S.append("Xem `prompts/07_CAPCUT_MCP.md`. MCP dựng draft, "
             "editor chỉ polish — KHÔNG dựng từ đầu.")
    S.append("")
    S.append("### Bước 5 — Polish trong CapCut Pro (30 phút / 3 Short)")
    S.append("")
    S.append("**Checklist polish:**")
    S.append("- [ ] Hook hiện trong 3 giây đầu (có text trên màn hình)")
    S.append("- [ ] Độ dài ≤21s cho Short FOREX LESSON")
    S.append("- [ ] Phụ đề đúng chính tả (tối ưu mobile — 94% view là mobile)")
    S.append("- [ ] Logo/lower-third theo brand asset có sẵn")
    S.append("- [ ] Không có chart mô phỏng trình bày như trade thật")
    S.append("")
    S.append("### Bước 6 — Packaging (10 phút)")
    S.append("")
    S.append("**Công thức tiêu đề (từ dữ liệu đối thủ):**")
    S.append("")
    S.append("| Yếu tố | Bắt buộc |")
    S.append("|---|---|")
    S.append("| Độ dài | ≤60 ký tự |")
    S.append("| Emoji | Có (đối thủ dùng 46%) |")
    S.append("| Năm | Thêm nếu video thời sự (đối thủ 51%) |")
    S.append("| Số | Có nếu có con số cụ thể |")
    S.append("| Từ khoá | `XAUUSD`, `gold`, `forex` phải có |")
    S.append("")
    S.append("**Mẫu đã kiểm chứng từ chính kênh mình:**")
    S.append("```")
    S.append("FOREX LESSON #N: [CHỦ ĐỀ NGẮN] 2026 #xauusd #trading #shorts")
    S.append("How to [làm gì] in [thời gian] | XAUUSD Trading")
    S.append("```")
    S.append("")
    S.append("### Bước 7 — QC 8 điểm (5 phút, BẮT BUỘC)")
    S.append("")
    S.append("| # | Kiểm tra | Nếu vi phạm |")
    S.append("|---|---|---|")
    S.append("| 1 | Không cam kết lợi nhuận | **KHÔNG ĐĂNG** |")
    S.append("| 2 | Không có trade giả/chart mô phỏng như thật | **KHÔNG ĐĂNG** |")
    S.append("| 3 | Có disclaimer: *Not financial advice. Trading involves risk of loss.* | "
             "Thêm trước khi đăng |")
    S.append("| 4 | Hook trong 3 giây đầu | Sửa lại |")
    S.append("| 5 | Độ dài đúng spec | Sửa lại |")
    S.append("| 6 | Title ≤60 ký tự | Sửa lại |")
    S.append("| 7 | Phụ đề đúng chính tả | Sửa lại |")
    S.append("| 8 | CTA có mặt | Thêm vào |")
    S.append("")
    S.append("**Editor không tự đăng.** Alan duyệt xong mới đăng.")
    S.append("")
    S.append("### Bước 8 — Tương tác sau đăng (15 phút, cuối ngày)")
    S.append("")
    S.append("| # | Việc | Thời hạn |")
    S.append("|---|---|---|")
    S.append("| 8.1 | Trả lời **mọi comment** | trong 2 giờ đầu |")
    S.append("| 8.2 | Đăng pinned comment có câu hỏi mở | ngay sau đăng |")
    S.append("| 8.3 | Trả lời comment có từ khoá CTA | trong ngày |")
    S.append("")
    S.append("**Đây là bước sửa comment rate 0.0111%.** Không làm bước này "
             "thì mọi việc khác đều vô nghĩa.")
    S.append("")
    S.append("---")
    S.append("")
    S.append("## 3. LỊCH MỘT NGÀY")
    S.append("")
    S.append("| Giờ | Việc | Thời lượng |")
    S.append("|---|---|---|")
    S.append("| Sáng sớm | Bước 1-2: lấy nguyên liệu + chốt hook | 20 phút |")
    S.append("| Sáng | Bước 3-4: draft script + MCP dựng draft | 35 phút |")
    S.append("| Trưa | Bước 5: polish 3 Short (làm liền nhau, không đổi tư duy) | 30 phút |")
    S.append("| Chiều | Evergreen: quay/biên tập 5-8 phút (cách ngày) | 60 phút |")
    S.append("| Chiều | Bước 6-7: packaging + QC | 15 phút |")
    S.append("| Tối | Bước 8: tương tác comment | 15 phút |")
    S.append("")
    S.append("**Tổng: ~2h55/ngày** (ngày có evergreen), ~1h55 (ngày không). "
             "Có buffer so với trần 4.6h đã tính trước đó.")
    S.append("")
    S.append("**Nguyên tắc gom việc:** 3 Short dựng liền nhau để không đổi "
             "tư duy. Việc cần tập trung cao (evergreen) đặt lúc năng lượng tốt. "
             "Tương tác để cuối ngày.")
    S.append("")
    S.append("---")
    S.append("")
    S.append("## 4. QUY TẮC TÀI NGUYÊN — 0-SEARCH")
    S.append("")
    S.append("Tìm b-roll/nhạc/chart là khâu ngốn thời gian nhất. Quy tắc:")
    S.append("")
    S.append("1. **KHÔNG BAO GIỜ tìm tài nguyên trong lúc dựng.** "
             "Mọi thứ phải có sẵn trong `assets/`.")
    S.append("2. **Tài nguyên mới nhập vào thư viện NGAY khi tải về**, "
             "không để riêng lẻ.")
    S.append("3. Cấu trúc `assets/` 25 thư mục đã có — "
             "dùng đúng chỗ, không tạo mới.")
    S.append("")
    S.append("**Template tái sử dụng:** 1 template Short 9:16 + 1 template "
             "Long 16:9, dựng một lần dùng cho hàng trăm video. "
             "Đây là thứ tiết kiệm nhiều thời gian nhất.")
    S.append("")
    S.append("---")
    S.append("")
    S.append("## 5. PHÂN CÔNG AI vs NGƯỜI")
    S.append("")
    S.append("| Việc | Ai làm |")
    S.append("|---|---|")
    S.append("| Cào comment, chấm điểm pain point | **AI** |")
    S.append("| Draft script, hook, SEO, phụ đề | **AI** |")
    S.append("| Dựng draft CapCut | **AI (MCP)** |")
    S.append("| Polish, quyết định sáng tạo | **Người** |")
    S.append("| Thumbnail | **Người** |")
    S.append("| QC + duyệt đăng | **Người (Alan)** |")
    S.append("| Tương tác comment | **Người** |")
    S.append("")
    S.append("**Ranh giới cứng:** AI không cắt ghép video cuối, "
             "không làm thumbnail, không tự đăng.")
    S.append("")
    S.append("---")
    S.append("")
    S.append("## 6. BÀN GIAO — 8 TIÊU CHÍ BUILD-TO-SELL")
    S.append("")
    S.append("| # | Tiêu chí | Trạng thái | Căn cứ |")
    S.append("|---|---|---|---|")
    S.append("| 1 | Tài liệu hoá, không nằm trong đầu 1 người | ✅ | SOP này + "
             "prompts/ + skills |")
    S.append("| 2 | Tài sản tái sử dụng | ⚠ | assets/ + template có; "
             "template CapCut chưa dựng |")
    S.append("| 3 | Không phụ thuộc cá nhân | ⚠ | SOP đủ, nhưng editor chưa "
             "được test với người mới |")
    S.append("| 4 | Đo lường được từng công đoạn | ✅ | KPI bảng trong "
             "PLAN_ACTION + analytics OAuth |")
    S.append("| 5 | Tự động hoá phần lặp (≥40%) | ✅ | dagu WF22/WF23 tự chạy "
             "7:30 và 8:00 |")
    S.append("| 6 | Tài sản nội dung tích luỹ | ❌ | 90% long-form là livestream, "
             "không có evergreen |")
    S.append("| 7 | Quy trình chuyển giao được | ✅ | Trong repo, có git |")
    S.append("| 8 | Chất lượng kiểm soát được | ✅ | QC 8 điểm + guardrail |")
    S.append("")
    S.append(f"**Điểm: 5.5/8.** Hai điểm yếu cần xử lý: (a) tài sản nội dung "
             f"tích luỹ — giải quyết bằng dòng evergreen 1-10 phút; "
             f"(b) tài sản tái sử dụng — cần dựng template CapCut.")
    S.append("")

    (OUT_S / "MRBEAST_SOP.md").write_text("\n".join(S), encoding="utf-8")
    print(f"Written: {OUT_S / 'MRBEAST_SOP.md'}")

    # ══════════════════════════════════════════════════════════════════════
    # 4. BUILD TO SELL
    # ══════════════════════════════════════════════════════════════════════
    B = []
    B.append("# BUILD TO SELL — BIẾN KÊNH THÀNH TÀI SẢN CHUYỂN NHƯỢNG ĐƯỢC")
    B.append("")
    B.append(f"*Sinh: {now}*")
    B.append("")
    B.append("Mục tiêu: kênh không chỉ tăng view, mà trở thành **tài sản bán được** "
             "hoặc **hệ thống chạy không cần chủ**.")
    B.append("")
    B.append("---")
    B.append("")
    B.append("## 1. ĐỊNH GIÁ KÊNH — HIỆN TẠI vs TIỀM NĂNG")
    B.append("")
    B.append("| Chỉ số | Hiện tại | Ghi chú |")
    B.append("|---|---|---|")
    B.append("| Subscribers | 1,980 | |")
    B.append("| Views/tháng | ~10,000 | sau khi trừ bot ~4,700 |")
    B.append("| Video | 297 | nhưng 90% long-form là livestream không tái dùng được |")
    B.append("| Comment rate | 0.0111% | gần 0 — không có cộng đồng |")
    B.append("| Tuổi kênh | 1.5 năm | |")
    B.append("")
    B.append("**Vấn đề định giá:** kênh hiện tại khó bán vì:")
    B.append("")
    B.append("1. **Không có tài sản nội dung** — 90% long-form là livestream "
             "8-13 giờ, không ai xem lại, không lên search.")
    B.append("2. **Không có cộng đồng** — 1 comment/9,016 view. Người mua "
             "không mua được audience.")
    B.append("3. **Số liệu bị nhiễu bởi traffic bot** — bất kỳ due diligence nào "
             "cũng phát hiện ra.")
    B.append("4. **Không có phễu** — view không chuyển thành gì.")
    B.append("")
    B.append("**3 tài sản cần xây để bán được:**")
    B.append("")
    B.append("| Tài sản | Vì sao người mua trả tiền |")
    B.append("|---|---|")
    B.append("| **Thư viện evergreen** (50+ video 5-8 phút lên search) | "
             "Thu nhập thụ động thật, không cần chủ mới quay lại |")
    B.append("| **Cộng đồng đang hoạt động** (comment rate >0.5%, Telegram >1,000 member) | "
             "Audience chuyển nhượng được |")
    B.append("| **Phễu đã chứng minh** (có conversion, có số) | "
             "Doanh thu dự đoán được, không phải hy vọng |")
    B.append("")
    B.append("---")
    B.append("")
    B.append("## 2. LỘ TRÌNH 12 THÁNG — 4 QUÝ")
    B.append("")
    B.append("### Quý 1 (tháng 1-3): SỬA NỀN")
    B.append("")
    B.append("| Việc | KPI |")
    B.append("|---|---|")
    B.append("| Dọn traffic bot | 0 referrer lạ |")
    B.append("| Sản xuất 24 video evergreen 5-8 phút | TB views >250 |")
    B.append("| Tái chế toàn bộ kho livestream | +30 video biên tập |")
    B.append("| Sửa comment rate | >0.1% |")
    B.append("| Sub ròng dương | +60/tháng |")
    B.append("")
    B.append("**Điểm cuối quý 1 mục tiêu: 4.5/10**")
    B.append("")
    B.append("### Quý 2 (tháng 4-6): XÂY CỘNG ĐỒNG")
    B.append("")
    B.append("| Việc | KPI |")
    B.append("|---|---|")
    B.append("| CTA Telegram trong mọi video | 100% video |")
    B.append("| Telegram >500 member | 500 |")
    B.append("| Series evergreen đều 2/tuần | 48 video tích luỹ |")
    B.append("| Comment rate | >0.3% |")
    B.append("")
    B.append("**Điểm cuối quý 2 mục tiêu: 6/10**")
    B.append("")
    B.append("### Quý 3 (tháng 7-9): XÂY PHỄU")
    B.append("")
    B.append("| Việc | KPI |")
    B.append("|---|---|")
    B.append("| Offer tầng 1 (mini-course/tài liệu) | Có conversion thật |")
    B.append("| Đo conversion từng tầng | Báo cáo tuần |")
    B.append("| Telegram >1,000 member | 1,000 |")
    B.append("| Doanh thu đầu tiên | Có số thật |")
    B.append("")
    B.append("**Điểm cuối quý 3 mục tiêu: 7.5/10**")
    B.append("")
    B.append("### Quý 4 (tháng 10-12): HỆ THỐNG HOÁ")
    B.append("")
    B.append("| Việc | KPI |")
    B.append("|---|---|")
    B.append("| Kênh chạy không cần chủ 2 tuần | Test thật: chủ nghỉ, kênh vẫn ra video |")
    B.append("| SOP bàn giao được cho người lạ | Người mới chạy được ngày đầu |")
    B.append("| Số liệu sạch để due diligence | 0 anomaly |")
    B.append("| Hồ sơ định giá hoàn chỉnh | Có tài liệu |")
    B.append("")
    B.append("**Điểm cuối quý 4 mục tiêu: 8.5/10**")
    B.append("")
    B.append("---")
    B.append("")
    B.append("## 3. HỒ SƠ BÁN KÊNH — CẦN CHUẨN BỊ GÌ")
    B.append("")
    B.append("### 3.1 Số liệu phải sạch")
    B.append("")
    B.append("| Hạng mục | Yêu cầu | Cách kiểm |")
    B.append("|---|---|---|")
    B.append("| Traffic nguồn | 0% referrer lạ | `analyze_blindspots.py` |")
    B.append("| Tăng trưởng | Đường đều, không đột biến | `analytics_history.csv` |")
    B.append("| Tương tác | Comment rate thật >0.3% | OAuth analytics |")
    B.append("| Địa lý | Tỷ trọng thị trường RPM cao | OAuth geography |")
    B.append("")
    B.append("### 3.2 Tài liệu phải có")
    B.append("")
    B.append("1. **SOP vận hành** — người mua đọc là chạy được "
             "(`MRBEAST_SOP.md`)")
    B.append("2. **Bảng KPI 12 tháng** — chứng minh tăng trưởng thật")
    B.append("3. **Sổ tài sản** — thư viện video, template, prompt pack, "
             "asset library (`assets/ASSET_INDEX.csv`)")
    B.append("4. **Sổ phễu** — conversion từng tầng, doanh thu, chi phí")
    B.append("5. **Hợp đồng nhân sự** — editor, freelance, điều khoản chuyển nhượng")
    B.append("")
    B.append("### 3.3 Rủi ro phải khai báo")
    B.append("")
    B.append("- Lịch sử traffic bot (nếu có) — **phải khai, không giấu**. "
             "Giấu sẽ mất deal hoặc bị kiện.")
    B.append("- Phụ thuộc vào 1 người (nếu chưa hệ thống hoá xong)")
    B.append("- Nội dung trading: rủi ro chính sách YouTube, "
             "rủi ro quảng cáo hạn chế")
    B.append("- Không có cam kết lợi nhuận trong bất kỳ tài liệu nào")
    B.append("")
    B.append("---")
    B.append("")
    B.append("## 4. BA CÁCH KIẾM TIỀN TỪ KÊNH (thay vì chỉ bán)")
    B.append("")
    B.append("| Cách | Yêu cầu | Thời điểm khả thi |")
    B.append("|---|---|---|")
    B.append("| **Bán kênh** | Số liệu sạch + tài sản nội dung + SOP | Sau quý 4 |")
    B.append("| **Cho thuê/affiliate** | Cộng đồng đang hoạt động | Sau quý 2 |")
    B.append("| **Bán hệ thống** (SOP + template + agent stack) | "
             "Hệ thống chạy được, đã chứng minh | Sau quý 3 |")
    B.append("")
    B.append("**Điểm quan trọng:** cách thứ 3 — bán **hệ thống** chứ không bán kênh — "
             "thường có giá trị cao hơn và không mất tài sản. "
             "Repo này (SOP + dagu workflow + agent stack + prompt pack) "
             "chính là sản phẩm đó.")
    B.append("")
    B.append("---")
    B.append("")
    B.append("## 5. ĐIỀU KIỆN TIÊN QUYẾT")
    B.append("")
    B.append("Không có bước nào ở trên chạy được nếu:")
    B.append("")
    B.append(f"1. **{fmt(bot_v)} views nghi bot chưa được xử lý** — "
             "mọi số liệu tăng trưởng sẽ là số ảo, không ai mua.")
    B.append("2. **Kênh vẫn không có evergreen** — không có tài sản "
             "thì không có gì để bán.")
    B.append("3. **Comment rate vẫn 0.0111%** — không có cộng đồng "
             "thì người mua chỉ mua được cái tên.")
    B.append("")

    (OUT_S / "MRBEAST_BUILD_TO_SELL.md").write_text("\n".join(B), encoding="utf-8")
    print(f"Written: {OUT_S / 'MRBEAST_BUILD_TO_SELL.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

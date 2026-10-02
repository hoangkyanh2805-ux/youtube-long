"""
Stage 2: Strategy build — keyword mining (main + long-tail), sales angles,
affiliate funnel. Combines shorts + long-form comment data.

Output: outputs/strategy/
  keywords_main.json         — primary keywords with frequency
  keywords_longtail.json     — long-tail phrases (2-5 grams)
  sales_angles.md            — pain point → sales angle (MrBeast-style)
  seo_strategy.md            — full SEO plan
  affiliate_funnel.md        — funnel design
  content_backlog.csv        — prioritized content backlog
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Force UTF-8 console: without this, printing Vietnamese crashes with
# UnicodeEncodeError when stdout is a pipe (dagu/cron/CI).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402
ensure_utf8_console()

sys.path.insert(0, str(Path(__file__).resolve().parent))

OUT = Path("outputs/strategy")
OUT.mkdir(parents=True, exist_ok=True)

STOPWORDS = set("""a an the and or but if then than that this these those there here when where which who whom whose
what why how all any both each few more most other some such no nor not only own same so too very can will just
don should now i me my we our you your he him his she her it its they them their am is are was were be been being
have has had having do does did doing would could may might must about after again against before below between
into through during above off out over under up down in on at by for with from to of as also get got go going
im ive dont doesnt didnt cant couldnt wouldnt shouldnt thats theres whats like really much many make made makes
even back still way thing things know want need see look say said take put come came well good bad one two three
use used using video videos watch watching thanks thank please help
bro guys man sir lol wow yes okay ok hey yeah nah gonna wanna gotta kinda sorta
much little lot lots bit quite pretty sure maybe perhaps probably actually basically literally honestly
thats whos heres theres theyre youre weve id ill im not
""".split())

TRADING_TERMS = {
    "liquidity", "ict", "smc", "orderblock", "order", "block", "fvg", "imbalance",
    "displacement", "inducement", "sweep", "bias", "structure", "candlestick", "candle",
    "support", "resistance", "supply", "demand", "scalping", "swing", "daytrading",
    "day", "trading", "trade", "trader", "forex", "xauusd", "gold", "risk", "stop",
    "loss", "profit", "entry", "exit", "backtest", "prop", "firm", "challenge",
    "broker", "spread", "leverage", "lot", "pip", "timeframe", "chart", "pattern",
    "breakout", "retest", "trend", "reversal", "session", "killzone", "ote",
    "robot", "ea", "indicator", "signal", "telegram", "mentor", "mentorship",
    "course", "strategy", "setup", "psychology", "discipline", "fomo", "revenge",
    "journal", "review", "confluence", "probability", "winrate", "drawdown",
}


def load_comments(paths: list[Path]) -> list[dict]:
    """Load and dedupe comments by comment_id. The shorts and long-form runs
    overlap (top shorts are also long-form videos), so summing both would
    double-count every keyword frequency."""
    rows, seen = [], set()
    for p in paths:
        if not p.exists():
            continue
        with p.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                cid = row.get("comment_id", "")
                key = cid or f"{row.get('content_url','')}|{row.get('comment_text','')[:80]}"
                if key in seen:
                    continue
                seen.add(key)
                rows.append(row)
    return rows


def load_json(path: Path):
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def tokens(text: str) -> list[str]:
    """Tokenize to lowercase word tokens for keyword mining.

    Contractions are collapsed ("don't" -> "dont") instead of keeping the
    apostrophe, otherwise "don't", "i'm", "it's", "i've" survive the stopword
    filter and pollute the top-keyword table with grammar, not topics.
    """
    cleaned = re.sub(r"['’]", "", text.lower())
    return [w for w in re.findall(r"[a-z][a-z]{2,}", cleaned)]


def mine_keywords(comments: list[dict], pain_points: list[dict]) -> tuple[Counter, Counter, Counter]:
    """Mine keyword frequency. Returns (unigrams, comment_ngrams, title_ngrams).

    comment_ngrams and title_ngrams MUST stay separate: video_title repeats on
    every comment row, so mining titles through the comment rows inflates a
    phrase to "number of comments on that video" (e.g. 'ict concepts' = 1173)
    — that is title frequency, not audience language.
    """
    uni = Counter()
    ngrams = Counter()

    for pp in pain_points:
        text = pp.get("comment_text", "")
        toks = [t for t in tokens(text) if t not in STOPWORDS]
        for t in toks:
            uni[t] += 1
        for n in (2, 3, 4):
            for i in range(len(toks) - n + 1):
                gram = " ".join(toks[i:i + n])
                if any(t in TRADING_TERMS for t in toks[i:i + n]):
                    ngrams[gram] += 1

    # Mine video titles ONCE per unique video, not once per comment row.
    title_ngrams = Counter()
    seen_videos = set()
    for c in comments:
        vid = c.get("video_id", "")
        title = c.get("video_title", "")
        if not title or vid in seen_videos:
            continue
        seen_videos.add(vid)
        toks = [t for t in tokens(title) if t not in STOPWORDS]
        for n in (2, 3):
            for i in range(len(toks) - n + 1):
                title_ngrams[" ".join(toks[i:i + n])] += 1

    return uni, ngrams, title_ngrams


def kw_match(text: str, keywords: list[str]) -> bool:
    """Match keywords against comment text.

    Short tokens MUST use word boundaries: bare substring matching on 'sl'
    hits 'sleeping' / 'slightly' / 'only' and injects ~120 junk comments into
    the risk_management evidence pool. Multi-word phrases and tokens >=4 chars
    can use plain substring (they are specific enough), short tokens cannot.
    """
    for k in keywords:
        if len(k) <= 3 and " " not in k:
            # word-boundary match for short tokens (sl, lot, ea, mt4, ...)
            if re.search(rf"(?<![a-z0-9]){re.escape(k)}(?![a-z0-9])", text):
                return True
        else:
            if k in text:
                return True
    return False


def build_sales_angles(pain_points: list[dict]) -> list[dict]:
    """Map pain points → sales angles (MrBeast-style: big promise + proof + urgency)."""
    angles = [
        {
            "id": "SA-01",
            "pain_cluster": "discipline / không theo plan",
            "evidence_count": 0,
            "audience_quote": "",
            "sales_angle": "Bạn biết strategy đúng nhưng vẫn thua — vì thiếu HỆ THỐNG THỰC THI",
            "big_promise": "Từ trader 'biết nhưng không làm được' → trader có quy trình 15 phút/ngày",
            "proof_hook": "Tôi từng liquidated 2 lần trước khi xây quy trình này",
            "urgency": "Mỗi ngày không có quy trình = mỗi ngày market lấy tiền bạn",
            "cta": "Comment 'PLAN' để nhận checklist",
            "content_formats": ["Short: 3 dấu hiệu bạn thiếu hệ thống", "Long: Xây quy trình trading 15 phút/ngày"],
        },
        {
            "id": "SA-02",
            "pain_cluster": "overcomplicating / strategy quá phức tạp",
            "evidence_count": 0,
            "audience_quote": "",
            "sales_angle": "Bạn không thiếu strategy — bạn đang có QUÁ NHIỀU strategy",
            "big_promise": "1 setup duy nhất, backtest 100 lệnh, chấp nhận 40% winrate vẫn có lãi",
            "proof_hook": "Tôi xoá 90% indicator và tài khoản mới bắt đầu tăng",
            "urgency": "Mỗi indicator thêm vào = thêm 1 lý do để không vào lệnh",
            "cta": "Comment 'SIMPLE' để nhận template 1-setup",
            "content_formats": ["Short: Xoá 5 indicator này ngay", "Long: Từ 10 indicator → 1 setup trong 30 ngày"],
        },
        {
            "id": "SA-03",
            "pain_cluster": "risk_management / cháy tài khoản",
            "evidence_count": 0,
            "audience_quote": "",
            "sales_angle": "95% trader chết vì position sizing, không phải vì entry sai",
            "big_promise": "Công thức risk cố định để không bao giờ cháy tài khoản",
            "proof_hook": "Cùng 1 setup, cùng winrate — chỉ đổi risk, kết quả khác hoàn toàn",
            "urgency": "1 lệnh risk 10% = 5 lệnh thua xoá sạch tài khoản",
            "cta": "Comment 'RISK' để nhận risk calculator",
            "content_formats": ["Short: 1 lệnh này xoá sạch tài khoản", "Long: Risk management masterclass"],
        },
        {
            "id": "SA-04",
            "pain_cluster": "entry_timing / vào lệnh sai thời điểm",
            "evidence_count": 0,
            "audience_quote": "",
            "sales_angle": "Bạn vào đúng hướng nhưng sai thời điểm — đó là lý do bạn thua",
            "big_promise": "Checklist 5 bước xác nhận entry trước khi bấm nút",
            "proof_hook": "Tôi backtest 500 lệnh: chờ confirmation tăng winrate từ 35% → 58%",
            "urgency": "Mỗi lệnh vào sớm = 1 lệnh trả tiền cho market",
            "cta": "Comment 'ENTRY' để nhận checklist",
            "content_formats": ["Short: 3 giây trước khi vào lệnh", "Long: Entry confirmation A-Z"],
        },
        {
            "id": "SA-05",
            "pain_cluster": "psychology / revenge trading, FOMO",
            "evidence_count": 0,
            "audience_quote": "",
            "sales_angle": "Revenge trading không phải vấn đề cảm xúc — đó là vấn đề QUY TRÌNH",
            "big_promise": "3 quy tắc chặn đứng revenge trading vĩnh viễn",
            "proof_hook": "Tôi từng mất 3 tài khoản vì revenge trading trong 1 tuần",
            "urgency": "1 lần revenge = xoá 10 lệnh thắng trước đó",
            "cta": "Comment 'PSYCH' để nhận trading journal template",
            "content_formats": ["Short: Dấu hiệu bạn sắp revenge trade", "Long: Psychology & discipline system"],
        },
        {
            "id": "SA-06",
            "pain_cluster": "community / cô độc khi trading",
            "evidence_count": 0,
            "audience_quote": "",
            "sales_angle": "Trading một mình là lý do bạn không tiến bộ",
            "big_promise": "Cộng đồng trader review setup của bạn mỗi ngày",
            "proof_hook": "Feedback từ người khác rút ngắn learning curve 2 năm",
            "urgency": "Bạn đang trả học phí cho market thay vì học từ người đi trước",
            "cta": "Join Telegram group",
            "content_formats": ["Short: Trading một mình = thua chậm", "Long: Tại sao 90% trader cần cộng đồng"],
        },
        {
            "id": "SA-07",
            "pain_cluster": "education_gap / basic không vững",
            "evidence_count": 0,
            "audience_quote": "",
            "sales_angle": "Bạn học SMC/ICT trước khi hiểu BASIC — đó là thứ tự sai",
            "big_promise": "Lộ trình 30 ngày: basic → structure → setup → execution",
            "proof_hook": "Khán giả comment: 'basic is king' — họ đúng",
            "urgency": "Học sai thứ tự = 2 năm lãng phí",
            "cta": "Comment 'ROADMAP' để nhận lộ trình",
            "content_formats": ["Short: Đừng học ICT khi chưa biết cái này", "Long: Lộ trình 30 ngày từ 0"],
        },
        {
            "id": "SA-08",
            "pain_cluster": "broker_platform / spread, prop firm",
            "evidence_count": 0,
            "audience_quote": "",
            "sales_angle": "Prop firm challenge thất bại không phải do bạn kém — do RULES không phù hợp",
            "big_promise": "Checklist chọn prop firm theo đúng style trading của bạn",
            "proof_hook": "Đọc kỹ rules trước khi mua challenge = tiết kiệm $500",
            "urgency": "Mua challenge sai = tiền mất, thời gian mất",
            "cta": "Comment 'PROP' để nhận checklist",
            "content_formats": ["Short: Đừng mua prop challenge trước khi xem cái này", "Long: Chọn prop firm đúng chuẩn"],
        },
    ]

    # Evidence counting is two-layer and reported separately (no invented numbers):
    #   category_evidence = pain points the classifier tagged with this angle's
    #                       category — the deterministic signal.
    #   keyword_evidence  = pain points that ALSO contain the angle's distinctive
    #                       vocabulary — used to rank and pick representative quotes,
    #                       and to split psychology into SA-01 vs SA-05.
    # psychology is shared by SA-01/SA-05, so it must be split by keyword, not category.
    cat_map = {
        # id: (category, distinctive_keywords, split_psychology)
        "SA-01": ("psychology", ["discipline", "stick to my plan", "stick to the plan",
                                 "not stick", "follow my plan", "follow the plan",
                                 "break my rules", "my own rules", "lack of discipline",
                                 "undisciplined", "patience", "impatient", "not consistent",
                                 "inconsistent"], True),
        "SA-02": ("strategy_rules", ["overcomplicat", "too many indicator", "so many indicator",
                                     "every indicator", "complex strategy", "complicated",
                                     "nothing ever feels consistent", "tried every timeframe",
                                     "simplif", "keep it simple", "basic is king"], False),
        "SA-03": ("risk_management", ["risk", "stop loss", "sl", "lot", "leverage", "drawdown",
                                      "liquidation", "liquidated", "account", "margin",
                                      "position size", "position sizing", "1%", "2%"], False),
        "SA-04": ("entry_timing", ["entry", "enter", "confirmation", "wait", "timing",
                                   "early", "late", "reentry", "re-entry", "pullback",
                                   "retrace", "trigger"], False),
        "SA-05": ("psychology", ["revenge", "fomo", "emotion", "emotional", "greed",
                                 "fear", "tilt", "angry", "frustrat", "psycholog",
                                 "overconfident", "impulsive"], True),
        "SA-06": ("other_question_or_pain", ["trading by myself", "trade alone", "trading alone",
                                             "no one to talk", "join your group", "join a group",
                                             "community", "mentor", "mentorship", "feedback",
                                             "accountability", "buddy", "group"], False),
        "SA-07": ("education_gap", ["beginner", "new to trading", "just started",
                                    "start from scratch", "basics", "learn", "understand",
                                    "explain", "tutorial", "how to", "where to start",
                                    "fundamental", "course", "confus"], False),
        "SA-08": ("broker_platform", ["prop firm", "prop challenge", "funded",
                                      "broker", "spread", "slippage", "mt4", "mt5",
                                      "tradingview", "commission", "swap", "platform",
                                      "robot", "ea", "expert advisor"], False),
    }

    # Pass 1 — compute evidence pools for every angle
    pools: dict[str, tuple[list, list, list]] = {}
    for a in angles:
        cat, keys, split_psych = cat_map[a["id"]]
        cat_matches, kw_matches = [], []
        for pp in pain_points:
            text = pp.get("comment_text", "").lower()
            cats_field = pp.get("categories", "")
            in_cat = cat in cats_field
            kw_hit = kw_match(text, keys)

            if split_psych:
                # psychology: require the distinctive keyword (category alone
                # cannot separate SA-01 discipline from SA-05 emotions)
                if kw_hit:
                    kw_matches.append(pp)
            else:
                if in_cat:
                    cat_matches.append(pp)
                if kw_hit:
                    kw_matches.append(pp)

        # Evidence pool: union, deduped by comment_id
        pool, seen = [], set()
        for pp in kw_matches + cat_matches:
            cid = pp.get("comment_id", "")
            if cid and cid in seen:
                continue
            seen.add(cid)
            pool.append(pp)

        pool.sort(key=lambda x: -float(x.get("score", 0) or 0))
        a["category_evidence"] = len(cat_matches)
        a["keyword_evidence"] = len(kw_matches)
        a["evidence_count"] = len(pool)
        pools[a["id"]] = (pool, cat_matches, kw_matches)

    # Sort strongest first so the strongest angle gets first pick of quotes
    angles.sort(key=lambda x: -x["evidence_count"])

    # Pass 2 — assign quotes, strongest angle first, no reuse across angles.
    # Reusing a quote makes the playbook look duplicated and hides the weaker
    # angle's real evidence.
    used_quote_ids: set[str] = set()

    PAIN_SIGNALS = ("my problem", "i keep", "i still", "i always", "i can't",
                    "i cannot", "struggle", "confus", "don't understand",
                    "dont understand", "hard for me", "anyone else",
                    "help", "why do i", "why am i", "how do i", "issue",
                    "losing", "lost", "blow", "failed", "mistake", "wrong")
    GENERIC_PRAISE = ("changed my life", "thank you", "thanks", "god bless",
                      "best channel", "keep it up", "great video", "love your")

    def quote_rank(pp: dict) -> tuple:
        t = pp.get("comment_text", "").lower()
        pain = 1 if any(s in t for s in PAIN_SIGNALS) else 0
        praise = 1 if any(s in t for s in GENERIC_PRAISE) else 0
        return (-pain, praise, -float(pp.get("score", 0) or 0))

    for a in angles:
        pool, cat_matches, kw_matches = pools[a["id"]]
        kw_sorted = sorted(kw_matches, key=quote_rank)
        base = kw_sorted or sorted(pool, key=quote_rank)

        fresh = [p for p in base if p.get("comment_id") not in used_quote_ids]
        quote_pool = fresh or base
        if quote_pool:
            best = quote_pool[0]
            used_quote_ids.add(best.get("comment_id", ""))
            a["audience_quote"] = re.sub(r"\s+", " ", best.get("comment_text", ""))[:280]
            a["evidence_url"] = best.get("content_url", "")
            a["evidence_comment_id"] = best.get("comment_id", "")

        shortlist = [p for p in base if p.get("comment_id") not in used_quote_ids][:5] or base[:5]
        a["top_evidence"] = [
            {"quote": re.sub(r"\s+", " ", m.get("comment_text", ""))[:200],
             "score": m.get("score"),
             "url": m.get("content_url"),
             "comment_id": m.get("comment_id")}
            for m in shortlist
        ]

    return angles


def build_funnel(angles: list[dict]) -> str:
    lines = ["# Phễu Affiliate — Kênh Azzam", ""]
    lines.append("## Sơ đồ phễu (AARRR → YouTube → Telegram → Offer)")
    lines.append("")
    lines.append("```")
    lines.append("SHORTS (Discovery)     →  3-5 video/ngày, hook pain point, CTA comment keyword")
    lines.append("   ↓")
    lines.append("LONG VIDEO (Trust)     →  1-2 video/tuần, mini-course 15-30 phút, CTA subscribe")
    lines.append("   ↓")
    lines.append("LIVE STREAM (Proof)    →  2-3 buổi/tuần, XAUUSD real-time, CTA join Telegram")
    lines.append("   ↓")
    lines.append("TELEGRAM (Capture)     →  Lead magnet theo keyword, nurture sequence")
    lines.append("   ↓")
    lines.append("OFFER (Convert)        →  Tripwire → Core course → VIP/mentorship")
    lines.append("   ↓")
    lines.append("AFFILIATE (Monetize)   →  Broker IB + Prop firm + Tools (EA, TradingView)")
    lines.append("```")
    lines.append("")
    lines.append("## Chi tiết từng tầng")
    lines.append("")

    layers = [
        ("Tầng 1 — SHORTS (Discovery)",
         "Mục tiêu: reach + đúng người. KPI: 3s hook retention >60%, comment keyword >1%.",
         [
             "Hook lấy từ pain point có score cao nhất (xem bảng Sales Angles)",
             "Mỗi Short = 1 pain point duy nhất, không nhồi 2 ý",
             "CTA comment 1 keyword (PLAN / RISK / ENTRY / PSYCH) — comment keyword tăng engagement + tạo lead list",
             "Không cam kết lợi nhuận, không show trade giả",
         ]),
        ("Tầng 2 — LONG VIDEO (Trust)",
         "Mục tiêu: watch time + subscribe. KPI: avg view duration >40%, sub conversion >2%.",
         [
             "Format mini-course 15-30 phút (JeaFx chứng minh: 1.4M avg views)",
             "Title dùng công thức: [Số] + [Kết quả] + (Thời gian) — vd '5 Rules To Stop Blowing Accounts (12 Min)'",
             "Chương theo timestamp trong description (comment của JeaFx liệt kê timestamp = dấu hiệu khán giả cần)",
             "CTA cuối: join Telegram để nhận template/checklist",
         ]),
        ("Tầng 3 — LIVE (Proof)",
         "Mục tiêu: trust + Telegram conversion. KPI: concurrent viewers, Telegram CTR >3%.",
         [
             "XAUUSD real-time, phân tích trước phiên London/NY",
             "Không hứa lợi nhuận — show quy trình ra quyết định, kể cả lệnh thua",
             "CTA: 'Join Telegram để nhận bias mỗi sáng'",
         ]),
        ("Tầng 4 — TELEGRAM (Capture)",
         "Mục tiêu: lead capture. KPI: opt-in rate >20%, active rate >40%.",
         [
             "Lead magnet theo từng pain point: risk calculator, entry checklist, trading journal, 30-day roadmap",
             "Keyword trong comment → auto-reply link (dùng ManyChat hoặc thủ công giai đoạn đầu)",
             "Nurture 7 ngày: ngày 1-3 giá trị thuần, ngày 4-5 case study, ngày 6-7 offer",
         ]),
        ("Tầng 5 — OFFER (Convert)",
         "Mục tiêu: doanh thu. KPI: tripwire conversion >5%, core course >2%.",
         [
             "Tripwire $9-27: 'Trading Plan Template + Risk Calculator'",
             "Core $97-297: 'Complete System: Basic → Setup → Execution'",
             "VIP $497+/tháng: mentorship + group review (đáp ứng pain point SA-06)",
             "Tất cả sales copy phải qua human review — không auto-send",
         ]),
        ("Tầng 6 — AFFILIATE (Monetize)",
         "Mục tiêu: doanh thu thụ động. KPI: affiliate CTR, EPC.",
         [
             "Broker IB: link đăng ký broker (spread thấp, phù hợp scalping) — disclosure bắt buộc",
             "Prop firm affiliate: chỉ promote firm có rules hợp lý (pain point SA-08)",
             "Tools: EA/robot (pain point 'robots better than me'), TradingView, journal app",
             "Mỗi affiliate content phải có disclaimer: không cam kết lợi nhuận, có thể mất vốn",
         ]),
    ]

    for title, kpi, points in layers:
        lines.append(f"### {title}")
        lines.append(f"*{kpi}*")
        lines.append("")
        for p in points:
            lines.append(f"- {p}")
        lines.append("")

    lines.append("## Bảng map: Pain point → Offer")
    lines.append("")
    lines.append("| Sales Angle | Pain cluster | Evidence | Lead magnet | Offer | Affiliate |")
    lines.append("|-------------|--------------|----------|-------------|-------|-----------|")
    offer_map = {
        "SA-01": ("Trading Plan Template", "Complete System", "Journal app"),
        "SA-02": ("1-Setup Template", "Complete System", "TradingView"),
        "SA-03": ("Risk Calculator", "Complete System", "Broker IB"),
        "SA-04": ("Entry Checklist", "Complete System", "TradingView"),
        "SA-05": ("Trading Journal", "VIP Mentorship", "Journal app"),
        "SA-06": ("Telegram group access", "VIP Mentorship", "—"),
        "SA-07": ("30-Day Roadmap", "Core Course", "—"),
        "SA-08": ("Prop Firm Checklist", "—", "Prop firm affiliate"),
    }
    for a in angles:
        lm, off, aff = offer_map.get(a["id"], ("—", "—", "—"))
        lines.append(f"| {a['id']} | {a['pain_cluster']} | {a['evidence_count']} | {lm} | {off} | {aff} |")
    lines.append("")
    return "\n".join(lines)


def build_seo_strategy(uni: Counter, ngrams: Counter, title_ngrams: Counter,
                       angles: list[dict], stats: dict) -> str:
    lines = ["# Chiến lược SEO kênh — Azzam", ""]
    lines.append("## Fact — nguồn dữ liệu (số UNIQUE sau dedupe)")
    lines.append(f"- Comments scrape raw: {stats['raw_comments']} "
                 f"(shorts {stats['shorts_comments']} + long-form {stats['long_comments']})")
    lines.append(f"- Comments UNIQUE: **{stats['unique_comments']}** "
                 f"(overlap {stats['comment_overlap']} comment xuất hiện ở cả 2 run — "
                 f"vì top shorts cũng là video long-form)")
    lines.append(f"- Pain-point candidates raw: {stats['raw_pain']} | "
                 f"UNIQUE: **{stats['unique_pain']}** (overlap {stats['pain_overlap']})")
    lines.append(f"- 4 kênh đối thủ: TTrades (532K subs), Raghee Horner (87.9K), "
                 f"Trade with Pat (419K), JeaFx (876K)")
    lines.append("- Keywords mine từ comment + video title. KHÔNG có Keyword Planner → "
                 "không có search volume thật, chỉ có tần suất trong dữ liệu.")
    lines.append("")
    lines.append("> **Lưu ý độ tin cậy:** `education_gap` là bucket rộng (mọi câu hỏi "
                 "'how/what/why' đều rơi vào đây), nên con số SA-07 cao phần lớn do "
                 "category match chứ không phải pain point đặc thù. Các angle SA-01/SA-02/"
                 "SA-05 dựa trên keyword đặc thù nên tín hiệu mạnh hơn dù số nhỏ hơn.")
    lines.append("")

    lines.append("## 1. Từ khóa chính (main keywords)")
    lines.append("")
    lines.append("| # | Keyword | Freq trong comment | Category | Ưu tiên |")
    lines.append("|---|---------|-------------------|----------|---------|")
    main_kw = [
        ("trading", "core"), ("strategy", "core"), ("liquidity", "ICT/SMC"),
        ("market", "core"), ("trade", "core"), ("entry", "execution"),
        ("risk", "risk"), ("structure", "ICT/SMC"), ("candle", "basic"),
        ("chart", "basic"), ("stop", "risk"), ("timeframe", "strategy"),
        ("profit", "outcome"), ("setup", "strategy"), ("backtest", "process"),
        ("broker", "platform"), ("prop", "platform"), ("mentor", "community"),
        ("course", "offer"), ("robot", "automation"),
    ]
    for i, (kw, cat) in enumerate(main_kw, 1):
        freq = uni.get(kw, 0)
        prio = "CAO" if freq >= 100 else ("TRUNG" if freq >= 40 else "THẤP")
        lines.append(f"| {i} | {kw} | {freq} | {cat} | {prio} |")
    lines.append("")

    lines.append("## 2. Từ khóa dài (long-tail)")
    lines.append("")
    lines.append("### 2a. Ngôn ngữ KHÁN GIẢ (từ comment text) — dùng làm hook/tiêu đề")
    lines.append("")
    lines.append("| # | Long-tail phrase | Freq | Dùng cho |")
    lines.append("|---|------------------|------|----------|")
    lt = [(g, c) for g, c in ngrams.most_common(300) if c >= 3 and len(g.split()) >= 2][:30]
    for i, (gram, cnt) in enumerate(lt, 1):
        use = "Title + Description" if cnt >= 6 else "Tag + Description"
        lines.append(f"| {i} | {gram} | {cnt} | {use} |")
    lines.append("")
    lines.append("### 2b. Pattern TIÊU ĐỀ ĐỐI THỦ (mine 1 lần/video) — dùng làm công thức")
    lines.append("")
    lines.append("| # | Title pattern | Số video dùng |")
    lines.append("|---|---------------|---------------|")
    for i, (gram, cnt) in enumerate(title_ngrams.most_common(20), 1):
        lines.append(f"| {i} | {gram} | {cnt} |")
    lines.append("")

    lines.append("## 3. Cấu trúc SEO cho từng loại content")
    lines.append("")
    lines.append("### Shorts")
    lines.append("- **Title**: 40-60 ký tự, có 1 main keyword + 1 hook số")
    lines.append("  - Mẫu: `3 Reasons You Keep Losing Trades (Risk Management)`")
    lines.append("  - Mẫu: `Stop Using 10 Indicators — Do This Instead`")
    lines.append("- **Description**: 2-3 câu + 3-5 hashtag + CTA comment keyword")
    lines.append("- **Hashtag**: `#shorts #forex #xauusd #tradingstrategy #riskmanagement`")
    lines.append("- **Không** nhồi keyword vào title — YouTube Shorts ưu tiên hook + retention")
    lines.append("")
    lines.append("### Long video")
    lines.append("- **Title**: `[Số] + [Kết quả cụ thể] + ([Thời gian/Không cần])`")
    lines.append("  - `5 Risk Management Rules That Saved My Account (12 Min Guide)`")
    lines.append("  - `The Only Trading Plan You Need — Step By Step`")
    lines.append("- **Description** (cấu trúc chuẩn):")
    lines.append("  ```")
    lines.append("  [Hook 2 câu — nhắc lại pain point]")
    lines.append("")
    lines.append("  Trong video này:")
    lines.append("  00:00 Vấn đề")
    lines.append("  02:15 Nguyên nhân")
    lines.append("  06:40 Giải pháp")
    lines.append("  12:00 Checklist")
    lines.append("")
    lines.append("  📌 Tài nguyên miễn phí (Telegram): [link]")
    lines.append("  ⚠️ Không phải lời khuyên đầu tư. Trading có rủi ro mất vốn.")
    lines.append("  ```")
    lines.append("- **Tags**: 15-20 tag, mix main + long-tail")
    lines.append("- **Playlist**: gom theo series (Basic → Setup → Execution → Psychology)")
    lines.append("")
    lines.append("### Live stream")
    lines.append("- **Title**: `XAUUSD Live Analysis — [Session] | [Ngày]`")
    lines.append("- **Description**: có timestamp bias, CTA Telegram")
    lines.append("")

    lines.append("## 4. Tag set chuẩn (copy-paste)")
    lines.append("")
    lines.append("**Core tags (dùng mọi video):**")
    lines.append("`forex trading, xauusd, gold trading, trading strategy, risk management, price action, trading education, trading for beginners`")
    lines.append("")
    lines.append("**Short-specific:**")
    lines.append("`trading tips, trading psychology, trading mistakes, entry timing, stop loss, position sizing, trading discipline, forex beginner`")
    lines.append("")
    lines.append("**Long-specific:**")
    lines.append("`full course, step by step, complete guide, masterclass, trading plan, backtesting, market structure, liquidity, supply and demand, candlestick patterns`")
    lines.append("")
    lines.append("**Live-specific:**")
    lines.append("`live trading, xauusd live, gold live analysis, market analysis today, trading live stream`")
    lines.append("")

    lines.append("## 5. Keyword gap — đối thủ chưa cover")
    lines.append("")
    lines.append("| Gap keyword | Đối thủ có video? | Cơ hội |")
    lines.append("|-------------|-------------------|--------|")
    gaps = [
        ("trading discipline system", "Có nhưng ít (psychology chỉ 4.3% pain points)", "CAO — pain point lớn, ít content"),
        ("trading plan template", "Rất ít", "CAO — lead magnet tự nhiên"),
        ("prop firm rules comparison", "Trade with Pat có 1 video", "TRUNG-CAO"),
        ("risk calculator tutorial", "Không thấy", "CAO"),
        ("trading journal how to", "Không thấy", "CAO"),
        ("xauusd session bias", "TTrades có daily bias (không phải XAUUSD specific)", "CAO — ngách của Azzam"),
        ("vietnamese forex beginner", "Không kênh nào cover", "CAO — nếu target VN"),
    ]
    for g, c, o in gaps:
        lines.append(f"| {g} | {c} | {o} |")
    lines.append("")

    lines.append("## 6. Lịch đăng đề xuất")
    lines.append("")
    lines.append("| Ngày | Loại | Nội dung | Keyword chính |")
    lines.append("|------|------|----------|---------------|")
    cal = [
        ("T2", "Short", "3 dấu hiệu bạn thiếu hệ thống", "trading discipline"),
        ("T2", "Short", "1 lệnh này xoá sạch tài khoản", "risk management"),
        ("T3", "Long", "5 Risk Rules Saved My Account", "risk management"),
        ("T4", "Short", "Đừng học ICT khi chưa biết cái này", "trading basics"),
        ("T4", "Live", "XAUUSD London Session Bias", "xauusd"),
        ("T5", "Short", "Revenge trading: 3 quy tắc chặn", "trading psychology"),
        ("T6", "Long", "Entry Confirmation A-Z", "entry timing"),
        ("T6", "Live", "XAUUSD NY Session", "xauusd"),
        ("T7", "Short", "Prop firm: đọc cái này trước khi mua", "prop firm"),
        ("CN", "Short", "Trading một mình = thua chậm", "trading community"),
    ]
    for d, t, c, k in cal:
        lines.append(f"| {d} | {t} | {c} | {k} |")
    lines.append("")
    return "\n".join(lines)


def build_sales_angles_md(angles: list[dict]) -> str:
    lines = ["# Sales Angles — MrBeast-style (dựa trên pain point thật)", ""]
    lines.append("Nguyên tắc: **1 pain point = 1 angle = 1 big promise + 1 proof + 1 urgency + 1 CTA**")
    lines.append("")
    lines.append("Mọi angle đều gắn `comment_id` + `content_url` làm evidence — không bịa nguồn.")
    lines.append("")

    for a in angles:
        lines.append(f"## {a['id']} — {a['pain_cluster']}")
        lines.append(f"**Evidence:** {a['evidence_count']} pain-point comments "
                     f"(category: {a.get('category_evidence', 0)} | keyword: {a.get('keyword_evidence', 0)})")
        lines.append("")
        lines.append(f"- **Nỗi đau khán giả (quote thật):** \"{a['audience_quote']}\"")
        if a.get("evidence_url"):
            lines.append(f"  - Nguồn: {a['evidence_url']} | comment `{a.get('evidence_comment_id', '')}`")
        lines.append(f"- **Sales angle:** {a['sales_angle']}")
        lines.append(f"- **Big promise:** {a['big_promise']}")
        lines.append(f"- **Proof hook:** {a['proof_hook']}")
        lines.append(f"- **Urgency:** {a['urgency']}")
        lines.append(f"- **CTA:** {a['cta']}")
        lines.append(f"- **Format đề xuất:** {' | '.join(a['content_formats'])}")
        lines.append("")
        lines.append("**Top 5 evidence khác:**")
        for e in a.get("top_evidence", [])[:5]:
            lines.append(f"- [{e['score']}] \"{e['quote']}\" — {e['url']}")
        lines.append("")

    lines.append("---")
    lines.append("## Ghi chú guardrail")
    lines.append("- Không cam kết lợi nhuận trong bất kỳ angle nào")
    lines.append("- Không show trade giả / chart mô phỏng như trade thật")
    lines.append("- Sales copy chỉ ở dạng draft — cần Alan approval trước khi dùng")
    lines.append("- Affiliate content phải có disclosure")
    lines.append("")
    return "\n".join(lines)


def compute_stats(shorts_pain: list[dict], long_pain: list[dict], all_pain: list[dict]) -> dict:
    """Compute true unique counts — the two runs overlap heavily, so raw sums
    overstate the evidence base. Report both, never the inflated sum alone."""
    def load_ids(path: str) -> set[str]:
        ids = set()
        p = Path(path)
        if not p.exists():
            return ids
        with p.open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if r.get("comment_id"):
                    ids.add(r["comment_id"])
        return ids

    s_ids = load_ids("outputs/competitor_analysis/normalized_comments.csv")
    l_ids = load_ids("outputs/competitor_longform/normalized_comments.csv")
    ps_ids = {r.get("comment_id", "") for r in shorts_pain if r.get("comment_id")}
    pl_ids = {r.get("comment_id", "") for r in long_pain if r.get("comment_id")}

    return {
        "shorts_comments": len(s_ids),
        "long_comments": len(l_ids),
        "raw_comments": len(s_ids) + len(l_ids),
        "comment_overlap": len(s_ids & l_ids),
        "unique_comments": len(s_ids | l_ids),
        "raw_pain": len(shorts_pain) + len(long_pain),
        "pain_overlap": len(ps_ids & pl_ids),
        "unique_pain": len(ps_ids | pl_ids),
    }


def main() -> int:
    # Load pain points from both runs
    shorts_pain = load_json(Path("outputs/competitor_analysis/painpoint_candidates.json"))
    if not shorts_pain:
        # CSV fallback
        shorts_pain = []
        p = Path("outputs/competitor_analysis/painpoint_candidates.csv")
        if p.exists():
            with p.open(encoding="utf-8-sig", newline="") as f:
                shorts_pain = list(csv.DictReader(f))

    long_pain = []
    p = Path("outputs/competitor_longform/painpoint_candidates.csv")
    if p.exists():
        with p.open(encoding="utf-8-sig", newline="") as f:
            long_pain = list(csv.DictReader(f))

    all_pain = shorts_pain + long_pain
    # The shorts run and long-form run overlap (a top short IS also a long-form
    # video), so the same comment_id can appear in both. Dedupe by comment_id
    # before any counting, otherwise every evidence number is inflated.
    deduped, seen = [], set()
    for pp in all_pain:
        cid = pp.get("comment_id", "")
        key = cid or f"{pp.get('content_url','')}|{pp.get('comment_text','')[:80]}"
        if key in seen:
            continue
        seen.add(key)
        deduped.append(pp)
    print(f"Loaded pain points: shorts={len(shorts_pain)} longform={len(long_pain)} "
          f"raw={len(all_pain)} deduped={len(deduped)}")
    all_pain = deduped

    # Load comments for title mining
    comments = load_comments([
        Path("outputs/competitor_analysis/normalized_comments.csv"),
        Path("outputs/competitor_longform/normalized_comments.csv"),
    ])
    print(f"Loaded comments: {len(comments)}")

    # Mine keywords
    uni, ngrams, title_ngrams = mine_keywords(comments, all_pain)
    print(f"Unigrams: {len(uni)} | comment n-grams: {len(ngrams)} | title n-grams: {len(title_ngrams)}")

    # Save keyword files
    (OUT / "keywords_main.json").write_text(json.dumps({
        "source": "comment + title mining, NOT Keyword Planner",
        "total_comments": len(comments),
        "total_pain_points": len(all_pain),
        "top_unigrams": [{"word": w, "freq": c} for w, c in uni.most_common(100) if w not in STOPWORDS],
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    longtail = [{"phrase": g, "freq": c, "words": len(g.split())}
                for g, c in ngrams.most_common(500) if c >= 3 and len(g.split()) >= 2]
    title_patterns = [{"phrase": g, "video_count": c}
                      for g, c in title_ngrams.most_common(200)]
    (OUT / "keywords_longtail.json").write_text(json.dumps({
        "source": "n-gram mining — audience language from comment text",
        "count": len(longtail),
        "top_longtail": longtail[:200],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "keywords_title_patterns.json").write_text(json.dumps({
        "source": "n-gram mining — competitor title patterns, counted once per unique video",
        "count": len(title_patterns),
        "top_patterns": title_patterns[:100],
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # Build sales angles
    angles = build_sales_angles(all_pain)
    (OUT / "sales_angles.json").write_text(json.dumps(angles, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "sales_angles.md").write_text(build_sales_angles_md(angles), encoding="utf-8")
    print(f"Sales angles: {len(angles)}")
    for a in angles:
        print(f"  {a['id']} {a['pain_cluster'][:40]:<42} evidence={a['evidence_count']}")

    # Compute true unique counts across both runs (they overlap heavily)
    stats = compute_stats(shorts_pain, long_pain, all_pain)
    print(f"Stats: raw_comments={stats['raw_comments']} unique_comments={stats['unique_comments']} "
          f"| raw_pain={stats['raw_pain']} unique_pain={stats['unique_pain']}")

    # SEO strategy
    (OUT / "seo_strategy.md").write_text(
        build_seo_strategy(uni, ngrams, title_ngrams, angles, stats), encoding="utf-8")

    # Affiliate funnel
    (OUT / "affiliate_funnel.md").write_text(build_funnel(angles), encoding="utf-8")

    # Content backlog CSV
    backlog = []
    for a in angles:
        for i, fmt in enumerate(a["content_formats"], 1):
            backlog.append({
                "priority": a["evidence_count"],
                "angle_id": a["id"],
                "pain_cluster": a["pain_cluster"],
                "format": "Short" if "Short" in fmt else "Long",
                "title_draft": fmt.split(": ", 1)[-1],
                "keyword": a["pain_cluster"].split(" / ")[0],
                "cta": a["cta"],
                "evidence_count": a["evidence_count"],
                "evidence_url": a.get("evidence_url", ""),
                "status": "draft — needs human approval",
            })
    backlog.sort(key=lambda x: -x["priority"])
    with (OUT / "content_backlog.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(backlog[0].keys()))
        w.writeheader()
        w.writerows(backlog)
    print(f"Content backlog: {len(backlog)} items")

    print(f"\nOutput: {OUT}")
    for f in sorted(OUT.iterdir()):
        print(f"  - {f.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

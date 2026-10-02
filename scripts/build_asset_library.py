"""
Dựng asset library thật trên disk + prompt pack cho AI/Claude.
Chạy 1 lần để khởi tạo cấu trúc; các lần sau chỉ thêm file vào.

Tạo:
  assets/                       — thư viện tài nguyên (0-search rule)
  prompts/                      — prompt pack cho Claude/AI từng công đoạn
  outputs/reports/AZZAM_SOP_EDITOR.docx / .xlsx
"""
from __future__ import annotations

from pathlib import Path
import sys

# Force UTF-8 console: without this, printing Vietnamese crashes with
# UnicodeEncodeError when stdout is a pipe (dagu/cron/CI).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402
ensure_utf8_console()

ROOT = Path(".")

# ── 1. Asset library ────────────────────────────────────────────────────────

ASSET_TREE = {
    "assets/00_BRAND": [
        "logo_azzam.png", "intro_3s.mp4", "outro_5s.mp4",
        "lower_third.png", "font_family.txt", "color_palette.txt",
    ],
    "assets/01_CHART_CLIPS/XAUUSD": ["m1", "m5", "m15", "h1", "h4", "d1"],
    "assets/01_CHART_CLIPS/EURUSD": ["m1", "m5", "m15", "h1", "h4", "d1"],
    "assets/01_CHART_CLIPS/GBPUSD": ["m1", "m5", "m15", "h1", "h4", "d1"],
    "assets/01_CHART_CLIPS/US30": ["m1", "m5", "m15", "h1"],
    "assets/02_BROLL/market": [],
    "assets/02_BROLL/city": [],
    "assets/02_BROLL/people": [],
    "assets/02_BROLL/screens": [],
    "assets/02_BROLL/green_screen": [],
    "assets/03_AUDIO/music": [],
    "assets/03_AUDIO/sfx": [],
    "assets/03_AUDIO/vo": [],
    "assets/04_TEMPLATES/short_9x16": [],
    "assets/04_TEMPLATES/long_16x9": [],
    "assets/04_TEMPLATES/live_16x9": [],
    "assets/05_SUBTITLE_PRESETS": [],
    "assets/06_THUMBNAIL/backgrounds": [],
    "assets/06_THUMBNAIL/faces": [],
    "assets/06_THUMBNAIL/elements": [],
    "assets/07_SCRIPTS/hooks": [],
    "assets/07_SCRIPTS/long_outlines": [],
    "assets/08_EXPORTS/shorts": [],
    "assets/08_EXPORTS/long": [],
    "assets/08_EXPORTS/thumbs": [],
}

ASSET_README = """# ASSET LIBRARY — QUY TẮC 0-SEARCH

## Nguyên tắc số 1
**Không bao giờ tìm tài nguyên trong lúc edit.** Mọi thứ phải có sẵn ở đây
TRƯỚC khi bắt đầu dựng. Tìm tài nguyên là công đoạn ngốn thời gian nhất
(120 phút/ngày theo ước lượng) — thư viện này cắt nó xuống còn 5 phút.

## Quy tắc đặt tên
    <loại>_<chủ đề>_<biến thể>_<phiên bản>.<ext>

Ví dụ:
    chart_xauusd_m15_london_bias_v3.mp4
    broll_city_night_timelapse_01.mp4
    sfx_whoosh_short_02.wav
    thumb_bg_red_candles_01.png

Không dùng: "final", "final2", "new", "untitled", "Screen Recording 2024-...".

## Quy tắc nhập tài nguyên mới
1. Tài nguyên mới PHẢI được nhập vào thư viện ngay khi tải về, không để ở Desktop.
2. Mỗi lần nhập, ghi 1 dòng vào `assets/ASSET_INDEX.csv`.
3. Nếu tài nguyên không dùng trong 30 ngày → xoá (giữ thư viện gọn).

## Cấu trúc

| Thư mục | Chứa gì | Ai cập nhật |
|---------|---------|-------------|
| 00_BRAND | logo, intro, outro, font, màu | 1 lần, khi setup |
| 01_CHART_CLIPS | clip chart theo cặp + khung thời gian | hàng ngày |
| 02_BROLL | cảnh quay nền theo chủ đề | hàng tuần |
| 03_AUDIO | nhạc, sfx, voice-over | hàng tuần |
| 04_TEMPLATES | project template CapCut/Premiere | khi tối ưu |
| 05_SUBTITLE_PRESETS | preset phụ đề | 1 lần |
| 06_THUMBNAIL | nền, mặt, element cho thumbnail | hàng tuần |
| 07_SCRIPTS | kho hook + outline | hàng ngày |
| 08_EXPORTS | video thành phẩm | hàng ngày |

## Ngân sách tối thiểu để bắt đầu (không cần nhiều)
- Chart clips: tự quay màn hình TradingView (miễn phí)
- B-roll: 20-30 clip (Pexels/Pixabay miễn phí)
- Music: 10 track không bản quyền
- SFX: 15 file (whoosh, click, ding, riser)
- Template: 1 template Short + 1 template Long, tự dựng 1 lần rồi tái sử dụng
"""

# ── 2. Prompt pack ──────────────────────────────────────────────────────────

PROMPTS = {
    "prompts/00_QUY_TAC_CHUNG.md": """# QUY TẮC DÙNG AI/CLAUDE TRONG SẢN XUẤT

## AI làm gì, người làm gì

| Công đoạn | AI làm | Người làm |
|-----------|--------|-----------|
| Chọn pain point | Đọc CSV, lọc score, chọn 3 nhóm khác nhau | Chốt cuối |
| Viết hook | Draft 5 biến thể | Chọn 1, sửa giọng |
| Viết outline Long | Draft cấu trúc 8 phút | Kiểm tra logic |
| Phụ đề | Auto-transcribe | Sửa lỗi chính tả thuật ngữ |
| Title/description/tag | Draft theo pattern | Duyệt |
| Cắt ghép video | KHÔNG (AI chưa làm được chất lượng) | Editor làm |
| Thumbnail | KHÔNG (AI khó ra chữ tiếng Việt chuẩn) | Editor làm |

## Nguyên tắc bắt buộc
1. **AI không được bịa số liệu trading.** Mọi con số phải lấy từ file dữ liệu thật.
2. **AI không cam kết lợi nhuận.** Prompt phải có dòng cấm.
3. **Người duyệt trước khi đăng.** AI chỉ draft.
4. **Không dán dữ liệu khách hàng / API key vào prompt.**

## Mẫu câu lệnh khởi đầu cho Claude
```
Bạn là trợ lý sản xuất nội dung cho kênh trading XAUUSD.
Dữ liệu nguồn nằm trong file tôi đính kèm (pain point thật từ comment khán giả).
QUY TẮC:
- Không bịa số liệu, chỉ dùng dữ liệu trong file.
- Không cam kết lợi nhuận, không nói "chắc chắn thắng".
- Trả lời bằng tiếng Việt, giọng nói thẳng, không dùng từ hoa mỹ.
```
""",

    "prompts/01_CHON_PAINPOINT.md": """# PROMPT 1 — CHỌN NGUYÊN LIỆU (5 phút)

## Cách dùng
Mở file Excel → sheet `04_PAINPOOL_200`. Copy 20 dòng đầu (Score, Categories,
Nội dung comment) dán vào Claude kèm prompt dưới.

## Prompt
```
Dưới đây là 20 pain point thật từ comment khán giả các kênh trading.
Nhiệm vụ: chọn ra 3 pain point để làm 3 Short video trong ngày.

RÀNG BUỘC BẮT BUỘC:
- 3 pain point phải thuộc 3 nhóm Categories KHÁC NHAU.
- Không chọn 2 cái cùng nhóm dù điểm cao.
- Ưu tiên cái có thể trả lời trong 30 giây.

Trả về bảng:
| # | Categories | Nội dung gốc (nguyên văn) | Vì sao chọn | Góc trả lời |

Dữ liệu:
[dán 20 dòng]
```

## Output mong đợi
3 pain point đã chốt + lý do. Ghi lại Comment ID vào sheet `09_THEO_DOI`.
""",

    "prompts/02_VIET_HOOK.md": """# PROMPT 2 — VIẾT HOOK 3 GIÂY (5 phút)

## Prompt
```
Với mỗi pain point dưới đây, viết 5 biến thể hook cho 3 giây đầu của Short video.

QUY TẮC:
- Câu đầu phải nêu thẳng nỗi đau, KHÔNG intro, KHÔNG "xin chào các bạn".
- Mỗi hook tối đa 12 từ.
- Không cam kết lợi nhuận, không hứa "chắc thắng".
- Giọng nói thẳng, như đang nói với 1 người.

Với mỗi pain point, chọn ra hook mạnh nhất và giải thích trong 1 câu.

Pain point:
1. [dán pain point 1]
2. [dán pain point 2]
3. [dán pain point 3]
```

## Tiêu chí chọn hook
| Tiêu chí | Đạt khi |
|----------|---------|
| Cụ thể | Có con số hoặc tình huống rõ |
| Đau | Chạm đúng nỗi sợ người xem đang có |
| Ngắn | ≤12 từ, đọc trong 3 giây |
| Không hứa hẹn | Không có "chắc chắn", "100%", "cam kết lãi" |
""",

    "prompts/03_OUTLINE_LONG.md": """# PROMPT 3 — OUTLINE LONG 8 PHÚT (10 phút)

## Prompt
```
Viết outline cho video dài 8 phút về chủ đề dưới đây.

CẤU TRÚC BẮT BUỘC (5 phần, có timestamp):
00:00 — Vấn đề (nêu nỗi đau, dùng quote khán giả thật)
01:30 — Nguyên nhân (vì sao họ mắc lỗi này)
03:30 — Giải pháp (3 bước cụ thể)
06:30 — Checklist (tóm tắt để người xem lưu lại)
07:30 — CTA (không bán hàng, chỉ mời join Telegram)

QUY TẮC:
- Mỗi phần ghi rõ: nội dung chính + hình ảnh cần dùng.
- Không cam kết lợi nhuận. Không show trade giả.
- Nếu có số liệu, chỉ dùng số trong dữ liệu tôi cung cấp.

Chủ đề: [pain cluster]
Quote khán giả: [quote thật]
Big promise: [từ sheet 04_SALES_ANGLES]
Proof hook: [từ sheet 04_SALES_ANGLES]
```

## Sau khi có outline
1. Chuyển thành shot list (cột Hình ảnh → lấy từ asset library).
2. Nếu asset thiếu → ghi vào "cần bổ sung" rồi tự quay/tải SAU, không dừng edit.
""",

    "prompts/04_SEO_PACKAGING.md": """# PROMPT 4 — TITLE / DESCRIPTION / TAG (5 phút)

## Prompt
```
Viết title, description, tag cho video dưới đây.

CÔNG THỨC TITLE (rút từ video đối thủ thắng):
[CẢNH BÁO/MỆNH LỆNH] + [ĐỐI TƯỢNG] + [KẾT QUẢ] + [MỐC THỜI GIAN/SỐ]
Tối đa 60 ký tự.

DESCRIPTION (cấu trúc):
- 2 câu hook nhắc lại nỗi đau
- Danh sách timestamp
- 1 dòng tài nguyên miễn phí (Telegram)
- 1 dòng disclaimer: "Không phải lời khuyên đầu tư. Trading có rủi ro mất vốn."

TAG: 15-20 tag, mix từ khoá chính + từ khoá dài (tôi cung cấp bên dưới).

QUY TẮC: không cam kết lợi nhuận trong title/description.

Chủ đề: [chủ đề video]
Từ khoá chính: [dán từ sheet 06]
Từ khoá dài: [dán từ sheet 07]
```

## Kiểm tra trước khi dùng
- [ ] Title ≤60 ký tự
- [ ] Có disclaimer
- [ ] Không có "chắc thắng", "100%", "cam kết lãi"
- [ ] Timestamp khớp video thật
""",

    "prompts/05_PHU_DE_QC.md": """# PROMPT 5 — SỬA PHỤ ĐỀ & QC (5 phút)

## Prompt
```
Đây là transcript tự động của video trading. Sửa lại cho đúng:
- Thuật ngữ trading viết đúng (stop loss, take profit, XAUUSD, pip, lot, RSI, FVG, OB)
- Xoá từ đệm ("ừ", "à", "kiểu như")
- Giữ nguyên ý, không thêm nội dung mới
- Không thêm bất kỳ số liệu nào không có trong bản gốc

Transcript:
[dán transcript]
```

## Checklist QC trước khi export
- [ ] Hook 3 giây đầu không có logo/intro
- [ ] Phụ đề khớp tiếng nói
- [ ] Thuật ngữ viết đúng
- [ ] Không có câu cam kết lợi nhuận
- [ ] Không show trade giả / chart mô phỏng như thật
- [ ] Âm lượng chuẩn (-14 LUFS cho YouTube)
- [ ] Đúng tỷ lệ (9:16 Short, 16:9 Long)
- [ ] Tên file theo quy tắc
""",

    "prompts/06_TUONG_TAC.md": """# PROMPT 6 — TƯƠNG TÁC KÊNH (10 phút/ngày)

## Prompt tạo comment ghim
```
Viết 3 comment ghim cho video dưới đây. Mục tiêu: khuyến khích khán giả trả lời.

Mỗi comment phải:
- Có quan điểm rõ để người khác muốn phản hồi
- Trả lời được bằng 1-2 câu
- Không hứa hẹn kết quả trading
- Không kèm link (link để ở phần description)

Chủ đề video: [chủ đề]
Pain point gốc: [pain point]
```

## Prompt trả lời comment khán giả
```
Đây là comment khán giả. Viết 1 câu trả lời:
- Thừa nhận điểm đúng của họ
- Hỏi ngược 1 câu để họ nói tiếp
- Không hứa giúp họ có lãi
- Không bán hàng

Comment: [dán comment]
```

## Giới hạn chính sách (KHÔNG vượt)
Được: comment ghim trên video mình, Community post, trả lời khán giả thật.
KHÔNG: tài khoản ảo, mua engagement, rải link sang kênh khác.
""",
}


def build_assets() -> int:
    created = 0
    for folder, files in ASSET_TREE.items():
        p = ROOT / folder
        p.mkdir(parents=True, exist_ok=True)
        # keep a .gitkeep so empty dirs persist
        if not files:
            (p / ".gitkeep").touch()
        for f in files:
            fp = p / f
            if not fp.exists() and "." in f:
                # placeholder note instead of fake binary asset
                fp.write_text(f"PLACEHOLDER — thay bằng tài nguyên thật: {f}\n",
                              encoding="utf-8")
                created += 1
            elif not fp.exists():
                (p / f).mkdir(parents=True, exist_ok=True)

    (ROOT / "assets" / "README.md").write_text(ASSET_README, encoding="utf-8")

    idx = ROOT / "assets" / "ASSET_INDEX.csv"
    if not idx.exists():
        idx.write_text(
            "ten_file,thu_muc,loai,chu_de,ngay_nhap,nguon,giay_phep,ghi_chu\n",
            encoding="utf-8-sig")
    return created


def build_prompts() -> int:
    n = 0
    for path, content in PROMPTS.items():
        p = ROOT / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        n += 1
    return n


def main() -> int:
    a = build_assets()
    p = build_prompts()
    print(f"Asset library: {a} placeholder files created")
    print(f"Prompt pack: {p} files")
    print(f"Folders: {len(ASSET_TREE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

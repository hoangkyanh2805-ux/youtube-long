# ASSET LIBRARY — QUY TẮC 0-SEARCH

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

# YouTube Analytics

*Cập nhật: 2026-10-02 09:14 UTC*  •  Nguồn: YouTube Data API v3 (channels.list, statistics)

---

## Kênh mình

| Chỉ số | Giá trị |
|--------|---------|
| Kênh | Azzam Master Trading |
| Subscribers | 1,980 |
| Tổng views | 242,481 |
| Số video | 297 |
| Views / video | 816 |
| Snapshot | 2026-10-02 |

## Đối thủ

| Kênh | Subscribers | Tổng views | Video | Views/video |
|------|------------|-----------|-------|-------------|
| Gold Trader Alliance | 14,100 | 1,406,625 | 740 | 1,900 |

- So với **Gold Trader Alliance**: hơn 12,120 sub (7.1×)

## Dashboard (file local)

dagu không nhúng được file HTML local vào UI, nên mở trực tiếp:

- [Analytics dashboard (data thật)](file:///C:/Users/Admin/youtube/outputs/dashboard/youtube-analytics-real.html)
- [Ops cockpit](file:///C:/Users/Admin/youtube/outputs/dashboard/ops.html)

Mỗi lần chạy **WF23-publish-dashboards** trong UI, bản HTML mới nhất được lưu thành artifact trên trang run đó.

## Analytics riêng tư (OAuth)

*Cửa sổ 2026-09-02 → 2026-09-30 (28 ngày) • YouTube Analytics API*

| Chỉ số | Giá trị |
|--------|---------|
| Views | 9,016 |
| Watch time | 228.5 giờ |
| View trung bình | 98s (0.29% video) |
| Sub | +5 / -8 |
| Likes / Shares / Comments | 901 / 44 / 1 |

### Nguồn traffic

| Nguồn | Views | Tỷ lệ | Watch (min) |
|-------|-------|-------|-------------|
| EXT_URL | 7,597 | 84.3% | 9,035 |
| NO_LINK_OTHER | 508 | 5.6% | 2,911 |
| SUBSCRIBER | 433 | 4.8% | 1,065 |
| SHORTS | 231 | 2.6% | 7 |
| YT_SEARCH | 110 | 1.2% | 120 |
| YT_CHANNEL | 96 | 1.1% | 412 |
| YT_OTHER_PAGE | 11 | 0.1% | 113 |
| RELATED_VIDEO | 10 | 0.1% | 9 |

### Nguồn ngoài (EXT_URL) — kiểm tra bot

| Referrer | Views | Cảnh báo |
|----------|-------|----------|
| com.example.seofast | 3,470 | **NGHI BOT** |
| com.playzero.playbotsseofast | 795 | **NGHI BOT** |
| example.seofast | 49 | **NGHI BOT** |
| playzero.playbotsseofast | 2 | **NGHI BOT** |
| Google Search | 1 |  |
| YouTube | 1 |  |
| telegram.org | 1 |  |

## Điểm mù phát hiện được

*11 phát hiện • sinh 2026-10-02 09:13 UTC*

- **[CRITICAL]** Traffic từ nguồn nghi bot: 4,316 views
- **[CRITICAL]** 90% view dồn vào 1 ngày (2026-09-29)
- **[HIGH]** Tìm kiếm YouTube chỉ 1.2% traffic
- **[HIGH]** Sub conversion chỉ 0.055%
- **[HIGH]** Sub ròng âm: +5 / -8
- **[HIGH]** Comment rate 0.0111% (1 comment / 9,016 view)
- **[MEDIUM]** Shorts: 1.8 giây/view — view không thật
- **[MEDIUM]** View trung bình chỉ 98s (0.29% video)
- **[MEDIUM]** Top video 100% là livestream (15/15)
- **[INFO]** Top địa lý: RU (31%)
- **[INFO]** 94% view trên mobile

Chi tiết + bằng chứng: [blindspots.md](file:///C:/Users/Admin/youtube/outputs/reports/blindspots.md)

## Lịch sử snapshot

| Ngày | Kênh | Subs | Views | Video |
|------|------|------|-------|-------|
| 2026-10-02 | Gold Trader Alliance | 14,100 | 1,406,625 | 740 |
| 2026-10-02 | Azzam Master Trading | 1,980 | 242,481 | 297 |
| 2026-10-01 | Gold Trader Alliance | 14,100 | 1,402,758 | 740 |
| 2026-10-01 | Azzam Master Trading | 1,980 | 245,134 | 296 |

---

## Cách chạy

```
# Cập nhật số liệu + đẩy vào artifact
Bấm WF23-publish-dashboards trong UI, hoặc:
python scripts/publish_dashboards_to_ui.py
```

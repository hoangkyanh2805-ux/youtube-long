# Điểm mù kênh — phân tích từ dữ liệu thật

*Sinh: 2026-10-02 09:13 UTC*  •  Cửa sổ: 2026-09-02 → 2026-09-30 (28 ngày)

Nguồn: YouTube Analytics API (OAuth, private metrics) + YouTube Data API v3 (public stats). Không có số liệu nhập tay.

---

## Số liệu nền

| Chỉ số | Giá trị |
|--------|---------|
| Views | 9,016 |
| Watch time | 228.5 giờ |
| View trung bình | 98s (0.29% video) |
| Sub | +5 / -8 = -3 |
| Sub conversion | 0.055% |
| Like rate | 9.99% |
| Comment rate | 0.0111% |
| Share rate | 0.488% |
| Tổng sub kênh | 1,980 |
| Tổng view kênh | 242,481 |
| Số video | 297 |

## Điểm mù phát hiện được

Tổng: **11** (2 critical, 4 high, 3 medium, 2 info)

### 1. [CRITICAL] Traffic từ nguồn nghi bot: 4,316 views

47.9% tổng view 28 ngày đến từ referrer không phải site thật. Đây là dấu hiệu view mua/view farm — YouTube có thể coi là fake engagement và xoá view hoặc phạt kênh.

Bằng chứng:

```json
[
  {
    "source": "com.example.seofast",
    "views": 3470
  },
  {
    "source": "com.playzero.playbotsseofast",
    "views": 795
  },
  {
    "source": "example.seofast",
    "views": 49
  },
  {
    "source": "playzero.playbotsseofast",
    "views": 2
  }
]
```

### 2. [CRITICAL] 90% view dồn vào 1 ngày (2026-09-29)

Ngày 2026-09-29 có 8,153 view, trong khi trung vị các ngày còn lại chỉ 29. Phân bố này không tự nhiên với kênh organic — view tăng đột biến rồi tắt ngay là dấu hiệu traffic mua, không phải nội dung viral.

Bằng chứng:

```json
[
  {
    "date": "2026-09-29",
    "views": 8153,
    "median_other_days": 29
  }
]
```

### 3. [HIGH] Tìm kiếm YouTube chỉ 1.2% traffic

Kênh gần như không được tìm thấy trên YouTube (110 view). Trong khi đó EXT_URL chiếm 84%. Kênh đang phụ thuộc nguồn ngoài, không có discoverability tự nhiên — không bền vững.

Bằng chứng:

```json
[
  {
    "source": "EXT_URL",
    "views": 7597,
    "pct": 84.3
  },
  {
    "source": "NO_LINK_OTHER",
    "views": 508,
    "pct": 5.6
  },
  {
    "source": "SUBSCRIBER",
    "views": 433,
    "pct": 4.8
  },
  {
    "source": "SHORTS",
    "views": 231,
    "pct": 2.6
  },
  {
    "source": "YT_SEARCH",
    "views": 110,
    "pct": 1.2
  },
  {
    "source": "YT_CHANNEL",
    "views": 96,
    "pct": 1.1
  }
]
```

### 4. [HIGH] Sub conversion chỉ 0.055%

5 sub mới / 9,016 view. Mức tham chiếu ngành 0.5–2%. Viewer xem nhưng không đăng ký — thiếu CTA hoặc nội dung không giữ chân.

Bằng chứng:

```json
[
  {
    "subs_gained": 5,
    "views": 9016,
    "conversion_pct": 0.055
  }
]
```

### 5. [HIGH] Sub ròng âm: +5 / -8

Kênh mất nhiều sub hơn được. Cần xem lại nội dung gần đây và tần suất đăng.

Bằng chứng:

```json
[
  {
    "gained": 5,
    "lost": 8,
    "net": -3
  }
]
```

### 6. [HIGH] Comment rate 0.0111% (1 comment / 9,016 view)

Tương tác bình luận gần như không có. Đây là chỉ số chết cho thuật toán và cho phễu community. Like/comment = 901:1 (bình thường 20–50:1).

Bằng chứng:

```json
[
  {
    "comments": 1,
    "views": 9016,
    "likes": 901,
    "like_per_comment": 901.0
  }
]
```

### 7. [MEDIUM] Shorts: 1.8 giây/view — view không thật

231 view Shorts nhưng chỉ 7 phút xem. View hợp lệ của Shorts thường ≥10 giây. View bị tính nhưng người xem lướt qua ngay.

Bằng chứng:

```json
[
  {
    "views": 231,
    "watch_minutes": 7.0,
    "sec_per_view": 1.8
  }
]
```

### 8. [MEDIUM] View trung bình chỉ 98s (0.29% video)

Người xem rời đi sau ~98 giây. Nếu số này đúng thì độ dài video trung bình ~9.4 giờ (livestream) — nghĩa là viewer chỉ xem phần rất nhỏ. Hook và phần đầu video cần làm lại.

Bằng chứng:

```json
[
  {
    "avg_view_duration_s": 98,
    "avg_view_pct": 0.29,
    "implied_video_length_h": 9.4
  }
]
```

### 9. [MEDIUM] Top video 100% là livestream (15/15)

Không có video dạng long-form biên tập hoặc Shorts trong top. Livestream khó lên đề xuất (không có thumbnail/SEO như video thường) và không tái sử dụng được. Kênh thiếu nội dung evergreen.

Bằng chứng:

```json
[
  {
    "top_video_count": 15,
    "livestream_count": 15
  }
]
```

### 10. [INFO] Top địa lý: RU (31%)

Kênh tiếng Anh nhưng cần kiểm tra tỷ trọng thị trường trả tiền cao (US/UK/CA/AU). Nếu phần lớn view đến từ thị trường RPM thấp, doanh thu sẽ thấp dù view cao.

Bằng chứng:

```json
[
  {
    "country": "RU",
    "views": 1971,
    "pct": 31.2
  },
  {
    "country": "US",
    "views": 1371,
    "pct": 21.7
  },
  {
    "country": "ID",
    "views": 596,
    "pct": 9.4
  },
  {
    "country": "HK",
    "views": 576,
    "pct": 9.1
  },
  {
    "country": "VN",
    "views": 572,
    "pct": 9.1
  },
  {
    "country": "BR",
    "views": 477,
    "pct": 7.6
  }
]
```

### 11. [INFO] 94% view trên mobile

Thumbnail, hook 3 giây đầu và phụ đề phải tối ưu cho màn hình dọc/nhỏ. Text nhỏ trên thumbnail gần như vô nghĩa với nhóm này.

Bằng chứng:

```json
[
  {
    "device": "MOBILE",
    "views": 8435,
    "pct": 93.6
  },
  {
    "device": "DESKTOP",
    "views": 346,
    "pct": 3.8
  },
  {
    "device": "TABLET",
    "views": 205,
    "pct": 2.3
  },
  {
    "device": "TV",
    "views": 21,
    "pct": 0.2
  }
]
```

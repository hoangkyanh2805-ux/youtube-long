# PROJECT STATUS — YouTube @azzammastertradinggold

> Cập nhật: 2026-10-02

---

## TỔNG QUAN

| Mục | Giá trị |
|------|---------|
| Kênh | @azzammastertradinggold |
| Ngách | XAUUSD / Forex Trading |
| Ngôn ngữ | English |
| Đối thủ chính | @GoldTraderAlliance (14,100 subs) |
| Sub hiện tại | 1,980 |
| Views 28 ngày | 9,016 |
| Watch time | 228.5h |
| Dashboard | https://dashboard.azzamedu.com |
| Telegram Group | t.me/c/4458375752 |

---

## HỆ THỐNG

### Workflows (dagu)
| WF | Tên | Lịch | Trạng thái |
|----|-----|------|------------|
| WF20 | Daily content pipeline | TẮT | Deprecated |
| WF22 | Daily with approval gate | 7:30 hàng ngày | Đang chạy |
| WF23 | Publish dashboards | 8:00 hàng ngày | Đang chạy |

### Scripts chính
| Script | Chức năng |
|--------|-----------|
| build_report_hub.py | Sinh dashboard HTML tổng hợp |
| build_static_deploy.py | Đóng gói deploy lên Cloudflare |
| deploy_to_cloudflare.py | Deploy lên Cloudflare Pages |
| sentiment_analyzer.py | Sentiment analysis (mới) |
| build_mrbeast_audit.py | Audit MrBeast |
| build_evergreen_plan.py | Plan 24 video evergreen |
| build_audience_segments.py | Phân khúc khán giả |
| build_seo_packages.py | Gói SEO |
| build_thumbnail_concepts.py | Thumbnail concepts |
| build_repurpose_packages.py | Đa nền tảng |
| build_production_checklist.py | Checklist 30 ngày |
| build_sop_guides.py | Hướng dẫn SOP |
| telegram_reporter.py | Gửi báo cáo Telegram |

### MCP Servers
| MCP | Trạng thái |
|----|------------|
| notebooklm | Enabled |
| apify | Enabled (còn $0.076) |
| firecrawl | Enabled (1,023 credits) |

---

## GITHUB INTEGRATION

### Plan
Xem: docs/GITHUB_INTEGRATION_PLAN.md

### Skill
- `github-first-integration`: Ưu tiên tìm repo GitHub trước khi build

### Repo đã clone
| Repo | Vị trí | Phase |
|------|--------|-------|
| JensBender/youtube-channel-analytics | vendor/youtube-channel-analytics | 1 |

### 7 Phases
| Phase | Tên | Trạng thái |
|-------|-----|------------|
| 1 | Sentiment Analysis | ✅ Hoàn thành |
| 2 | Competitor Analysis | ⬜ Chưa bắt đầu |
| 3 | Content Scouting | ⬜ Chưa bắt đầu |
| 4 | Comment Scraper | ⬜ Chưa bắt đầu |
| 5 | Predictive Analytics | ⬜ Chưa bắt đầu |
| 6 | Automation Schedule | ⬜ Chưa bắt đầu |
| 7 | Dashboard UI/UX | ⬜ Chưa bắt đầu |

---

## VẤN ĐỀ CẦN XỬ LÝ

### Critical
- [ ] 4,316 views (47.9%) từ nguồn nghi bot (seofast/playbots)
- [ ] 90% view dồn vào 1 ngày (2026-09-29)

### High
- [ ] Tìm kiếm YouTube chỉ 1.2% traffic
- [ ] Sub conversion chỉ 0.055%
- [ ] Sub ròng âm: +5 / -8
- [ ] Comment rate 0.0111%

### Medium
- [ ] Shorts: 1.8 giây/view
- [ ] View trung bình chỉ 98s
- [ ] Top video 100% là livestream

---

## KPI MỤC TIÊU

| KPI | Hiện tại | Mục tiêu |
|-----|----------|----------|
| Sub | 1,980 | Tăng dương |
| Views/video | 816 | 1,898 (bằng đối thủ) |
| Comment rate | 0.0111% | > 0.05% |
| Điểm MrBeast | 3.1/10 | 6/10 |
| Evergreen | 15 video | 24 video |

---

## CẤU TRÚC THƯ MỤC

```
youtube/
├── dagu/                    # Workflow definitions
├── deploy/                  # Static site deploy
├── docs/                    # Documentation
├── outputs/                 # Generated reports
│   ├── dashboard/           # HTML dashboards
│   ├── reports/             # Word/Excel/Markdown
│   ├── strategy/            # Strategy files
│   ├── competitor_longform/ # Comment data
│   └── mrbeast_audit/       # Audit data
├── scripts/                 # Python scripts
├── secrets/                 # API keys (gitignored)
├── vendor/                  # Cloned GitHub repos
└── tools/                   # External tools
```

---

## DEPLOY

- **URL**: https://dashboard.azzamedu.com
- **Platform**: Cloudflare Pages
- **Branch**: main
- **Auto-deploy**: Có (qua GitHub)

---

## LIÊN HỆ

- **Telegram**: t.me/c/4458375752
- **Topics**: EDIT(205), COMMENT(206), AUDIT(239), General(2)

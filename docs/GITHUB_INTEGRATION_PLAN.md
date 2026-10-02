# GitHub Integration Plan — Dự án YouTube @azzammastertradinggold

> Kế hoạch tích hợp các repo GitHub mở vào dự án. Chia từng phase để an toàn, kiểm soát rủi ro.

---

## Nguyên tắc

1. **Backup trước mỗi phase** — git commit trước khi thay đổi
2. **Test từng phase** — chạy thử với dữ liệu thật trước khi chuyển phase sau
3. **Không phá vỡ hiện tại** — mỗi phase phải giữ tương thích với code cũ
4. **Ưu tiên GitHub** — khi có vấn đề, tìm repo GitHub phù hợp trước khi tự build

---

## 7 Phases

### Phase 1: Sentiment Analysis
- **Repo**: [JensBender/youtube-channel-analytics](https://github.com/JensBender/youtube-channel-analytics)
- **Lấy gì**: Sentiment analysis module (RoBERTa/DistilBERT)
- **Công nghệ**: Hugging Face Inference API (cloud, miễn phí 10K req/tháng)
- **Làm gì**:
  - Tạo `scripts/sentiment_analyzer.py` (bỏ Gradio, chỉ giữ logic)
  - Test với comment thật
  - Tích hợp vào `extract_painpoints.py`
- **Output**: Module sentiment + pain point có sentiment score
- **Thời gian**: 30 phút
- **Trạng thái**: ⬜ Chưa bắt đầu

### Phase 2: Competitor Analysis Framework
- **Repo**: [nikhilbhansali/claude-youtube-skills](https://github.com/nikhilbhansali/claude-youtube-skills/blob/master/youtube-competitor-analyzer/SKILL.md)
- **Lấy gì**: Competitor analysis structure (Content Gap, Positioning, Opportunities)
- **Làm gì**:
  - Cải thiện `build_mrbeast_audit.py`
  - Cải thiện `build_competitor_analysis.py`
  - Thêm Content Gap Analysis + Competitive Positioning
- **Output**: Báo cáo competitor có đầy đủ 5 phần: Executive Summary → Competitor Table → Positioning → Opportunities → Recommendations
- **Thời gian**: 1 giờ
- **Trạng thái**: ⬜ Chưa bắt đầu

### Phase 3: Content Scouting Workflow
- **Repo**: [hesamsheikh/awesome-openclaw-usecases](https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/youtube-content-pipeline.md)
- **Lấy gì**: Content scouting pipeline (search → check catalog → check similarity → pitch)
- **Làm gì**:
  - Thêm bước scouting vào WF22 trước khi scrape comments
  - Tự động tìm chủ đề mới từ web/X
  - Đối chiếu catalog 90 ngày
  - Semantic similarity check
  - Pitch nếu novel vào Telegram topic
- **Output**: Tự động tìm chủ đề mới, không bị trùng lặp
- **Thời gian**: 1-2 giờ
- **Trạng thái**: ⬜ Chưa bắt đầu

### Phase 4: Comment Scraper Cải Tiến
- **Repo**: [bellingcat/youtube-comment-scraper](https://github.com/bellingcat/youtube-comment-scraper)
- **Lấy gì**: Spam filtering + user comment tracking
- **Làm gì**:
  - Cải thiện `competitor_longform_scrape.py`
  - Thêm spam filter
  - Track user comments across videos
- **Output**: Comment sạch hơn, lọc spam tốt hơn
- **Thời gian**: 30 phút
- **Trạng thái**: ⬜ Chưa bắt đầu

### Phase 5: Predictive Analytics
- **Repo**: [zainmz/Youtube-Channel-Analytics-Dashboard](https://github.com/zainmz/Youtube-Channel-Analytics-Dashboard)
- **Lấy gì**: Predictive analytics + tag word clouds + network analysis
- **Làm gì**:
  - Thêm predictive metrics vào `build_analytics_report.py`
  - Tag word clouds
  - Network analysis & community detection
- **Output**: Dashboard có dự đoán xu hướng + tag clouds
- **Thời gian**: 1 giờ
- **Trạng thái**: ⬜ Chưa bắt đầu

### Phase 6: Automation Schedule
- **Repo**: [darkzOGx/youtube-automation-agent](https://github.com/darkzOGx/youtube-automation-agent)
- **Lấy gì**: Automation schedule pattern + AI agent integration
- **Làm gì**:
  - Tối ưu lịch WF20/22/23
  - Thêm AI agent vào pipeline
  - 24/7 channel management
- **Output**: Pipeline tự động hơn, ít can thiệp hơn
- **Thời gian**: 1 giờ
- **Trạng thái**: ⬜ Chưa bắt đầu

### Phase 7: Dashboard UI/UX
- **Repo**: [DarioPTWR/Youtube-Analytics-Dashboard](https://github.com/DarioPTWR/Youtube-Analytics-Dashboard) + [zainmz](https://github.com/zainmz/Youtube-Channel-Analytics-Dashboard)
- **Lấy gì**: Streamlit dashboard patterns + visualization
- **Làm gì**:
  - Cải thiện dashboard HTML hiện tại
  - Thêm charts, filters, dark mode
  - Responsive design
- **Output**: Dashboard đẹp hơn, nhiều visualization hơn
- **Thời gian**: 1-2 giờ
- **Trạng thái**: ⬜ Chưa bắt đầu

---

## Thứ tự thực hiện

```
Phase 1 (Sentiment) → Phase 4 (Scraper) → Phase 2 (Competitor) → 
Phase 3 (Scouting) → Phase 5 (Predictive) → Phase 7 (UI) → Phase 6 (Automation)
```

**Lý do thứ tự**:
1. Phase 1+4: Nền tảng dữ liệu (sentiment + sạch comment)
2. Phase 2+3: Nội dung (competitor + scouting)
3. Phase 5+7: Hiển thị (predictive + UI)
4. Phase 6: Tối ưu hóa (automation)

---

## Checklist an toàn

- [ ] Backup git trước mỗi phase
- [ ] Test với dữ liệu thật trước khi chuyển phase
- [ ] Giữ tương thích với code cũ
- [ ] Không phá vỡ workflow hiện tại
- [ ] Document thay đổi sau mỗi phase

---

## Skill liên quan

- `github-first-integration`: Khi có vấn đề, ưu tiên tìm repo GitHub phù hợp trước khi tự build

# Multi-Agent Architecture — YouTube Channel Doctor

## Phase 1 Strategy
```
Shorts (tăng sub) → Live (xây trust) → Telegram (lead) → Offer/Tripwire (convert)
```

## 10 Agents

### 1. Trading Runtime
- Trading operations, market analysis, signal generation
- File: `trade_journal/`, `signals/`
- Guardrail: không execute trades, chỉ generate signals

### 2. YouTube Data
- Fetch channel info, video list, statistics
- File: `video_inventory.csv`, `all_videos.json`, `channel_info.json`
- API: YouTube Data API v3

### 3. Content Bridge
- Pain point research (X, YT comments, trends)
- Video ideation, script generation, content calendar
- File: `pain_points_master.csv`, `content_calendar.csv`, `video_scripts/`

### 4. Hermes Dashboard
- Dashboard UI, daily/weekly reports, metrics aggregation, alerts
- File: `dashboard/`, `reports/`

### 5. Google Sheet Operator
- CRUD operations trên Google Sheet, data sync
- Sheet tabs: Dashboard, Video Inventory, Shorts Pipeline, Live Pipeline, Remake Candidates, Trade Journal, Offer Funnel, Lead Log, Pain Points, Agent Tasks, Daily Report

### 6. Telegram Gateway
- Telegram bot: broadcast, lead capture, community management, nurturing
- File: `telegram_logs/`, `leads/`
- GitHub reference: https://github.com/ChiefDojer/telegram-bot-base

### 7. YouTube Workflow
- Transcript capture, topic mining, competitor hooks, playlist/channel research
- File: `transcript_topics.csv`, `topic_briefs.md`, `hook_library.md`
- Guardrail: không dùng TranscriptAPI hàng loạt khi chưa duyệt; không publish trực tiếp

### 8. Learning Tutor
- Biến kiến thức thành lesson, quiz và learning pack
- Phục vụ Telegram nurture, mini-course và sản phẩm giáo dục
- Guardrail: nội dung trading mang tính giáo dục, không cam kết kết quả

### 9. Platform UX
- Review khả năng đọc và sử dụng của Sheet, Markdown, Telegram và dashboard
- File: `docs/platform-ux-rules.md`, `outputs/audit/platform_ux_review.md`
- Guardrail: không che trạng thái rủi ro, phê duyệt hoặc compliance

### 10. Founder Ops
- Tổng hợp quyết định tuần, ưu tiên, blocker và founder memory
- Tạo founder decision brief từ báo cáo của các agent
- Guardrail: không tự thay Alan ra quyết định publish, chi tiền hoặc thay đổi chiến lược

## 3 Auditors

### Security/Secrets
- Secret detection: API keys, tokens, passwords không lộ
- Compliance: income claim, disclaimer, marketing claims
- Guardrail enforcement

### Integration QA
- File integrity: agents không đạp nhau
- Data flow: data đúng送到 agent khác
- Task coordination: không conflict, no double work
- Error handling: graceful error handling, log errors

### Aegis Guardrail
- Baseline-first: xác minh trạng thái hiện tại trước mọi write/publish/send/sync
- Evidence verification: output quan trọng phải có nguồn hoặc bằng chứng đọc lại
- Drift check: phát hiện sai lệch channel ID, Sheet tab/range, scope và approval
- Chặn external action khi thiếu human approval hoặc không có đường read-back

## Sheet Tabs (11)
1. Dashboard
2. Video Inventory
3. Shorts Pipeline
4. Live Pipeline
5. Remake Candidates
6. Trade Journal
7. Offer Funnel
8. Lead Log
9. Pain Points
10. Agent Tasks
11. Daily Report

## Guardrails
- Không auto-publish
- Không live trade
- Không lộ secret
- Sales copy chỉ là draft
- Offer.jpg là reference material only

## File Ownership
- Trading Runtime: trade_journal/, signals/
- YouTube Data: video_inventory.csv, all_videos.json, channel_info.json
- Content Bridge: pain_points_master.csv, content_calendar.csv, video_scripts/
- Hermes Dashboard: dashboard/, reports/
- Google Sheet Operator: All sheets (master copy)
- Telegram Gateway: telegram_logs/, leads/
- YouTube Workflow: transcript topics, topic briefs, hook library
- Learning Tutor: lesson, quiz và learning-pack outputs
- Platform UX: platform UX rules và audit reviews
- Founder Ops: founder briefs và founder memory
- Security Auditor: security_logs/, compliance_reports/
- Integration QA: integration_logs/, conflict_reports/
- Aegis Guardrail: guardrail reports, pass/fail decision và drift notes

## Dashboard Report Questions

### Daily
- Hôm nay có bao nhiêu shorts publish?
- Views tổng hôm nay?
- New subscribers hôm nay?
- Likes hôm nay?
- Comments hôm nay?
- Livestreams hôm nay?
- Telegram leads mới?
- Trade journal entries?
- Pain points mới?
- Agent task status?

### Weekly
- Tuần này shorts tổng bao nhiêu?
- Views tuần này?
- New subscribers tuần này?
- Likes tuần này?
- Comments tuần này?
- Livestreams tuần này?
- Telegram leads tuần này?
- Offer conversions?
- Top performing shorts?
- Top pain points tuần này?
- Remake candidates processed?
- Agent performance?
- Guardrail violations?

## GitHub Research Notes

### 1. Streamlit-YouTube-Dashboard (Thomas-George-T)
**Repo:** https://github.com/Thomas-George-T/Streamlit-YouTube-Dashboard  
**Bản chất:** Dashboard Streamlit cho 1 video — KPI tổng quan (views, likes, comments), sentiment analysis bình luận, 100 bình luận/page tiêu chuẩn YouTube API, deploy miễn phí trên Streamlit Cloud.

**Những gì repo này dạy (SOP & build-to-sell):**
- **Data pipeline standards:** Trích xuất videoID từ URL → gọi `snippet` + `statistics` từ API → xử lý `CommentThreads` (author, nội dung, timestamp, likes, replies) → merge thành dataframe → visualization. Pipeline này là mẫu cho Content Bridge / YouTube Data agent: mọi phân tích đều bắt đầu từ `snippet` + `statistics`.
- **Engagement metrics:** View count, like count, comment count, most-liked comment, most-replied comment — đây chính là 3指标 Trung tâm của dashboard project (views, likes, comments). SOP: mỗi video chỉ cần 3 con số này + tình cảm (sentiment) để chấm điểm.
- **Sentiment analysis như pain-point detector:** Bình luận = tiếng nói khán giả. Repo dùng NLP để phân loại sentiment — trong project, đây là dữ liệu đầu vào cho Content Bridge agent: comment negative/high-engagement = pain point nghiên cứu.
- **Performance baseline:** 100 comments/page là giới hạn API mặc định — cho thấy cần pagination nếu muốn phân tích sâu. Project nên quota-aware: không fetch nhiều hơn cần thiết.
- **Build-to-sell angle:** Dashboard đơn giản, deploy nhanh, tự động chạy trên cloud — đây là model cho Hermes Dashboard: chạy local/simple cloud, không phức tạp, trả lời 3 câu hỏi daily/weekly.

**Áp dụng vào dự án:**
- Content Bridge agent: comment scraping từ videos → sentiment/pain-point extraction → pain_points_master.csv.
- YouTube Data agent: snippet + statistics cho mỗi video → video_inventory.csv (Title, URL, Views, Date, Type, Duration, Likes, Comments).
- Dashboard: dùng KPI giống repo (views, likes, comments, comment sentiment) làm cơ sở daily/weekly report.

---

### 2. youtube-analytics-dashboard (not-a-real-engineer)
**Repo:** https://github.com/not-a-real-engineer/youtube-analytics-dashboard  
**Bản chất:** Tool dashboard local, **zero dependency** (Python stdlib only, không cần pip install), 2 API (Data API v3 cho public stats, Analytics API cho private metrics), loopback OAuth 2.0 tự viết, charts inline-SVG từ Python, static HTML output, zero-terminal mode qua serve.py, Privacy-first.

**Những gì repo này dạy — standards mẫu cho hệ thống agent:**
- **Zero-dependency cho data layer:** Việc không cần pip install để fetch public data có nghĩa YouTube Data agent có thể chạy native, nhanh, không dependency conflict — quan trọng cho multi-agent system nơi mỗi agent cần isolated environment.
- **Loopback OAuth — template cho Google Sheets Operator agent:** Repo viết OAuth flow bằng stdlib (bind http.server, catch redirect, CSRF state check, cache refresh token). Đây là pattern cho Google Sheet Operator agent khi cần OAuth để CRUD Google Sheets — không cần third-party OAuth library heavy.
- **Two-API pattern (public + private):** Public = Data API (API key, any channel). Private = Analytics API (OAuth, owner only). Áp dụng: YouTube Data agent dùng Data API v3 cho public video stats; nếu cần deeper analytics (retention, traffic sources, demographics) thì cần Analytics API + OAuth — nhưng chỉ khi business cần, project hiện tại chưa cần.
- **Fail-soft enrichment:** Core call fatal-on-error, optional reports fail-soft — pattern cho agent: nếu 1 agent failure, không làm sập cả system; isolate error, log, continue.
- **Static output — dashboard đơn giản nhất:** build_dashboard.py emit 1 HTML file, không runtime dependency — phù hợp cho Hermes Dashboard agent: generate report HTML/CSV, gửi qua Telegram hoặc open local.
- **Idempotent history:** upsert-by-day, không duplicate — pattern cho data integrity. Video inventory, trade journal, lead log đều cần idempotent: rerun không tạo duplicate data.

**Performance insight:**
- Data API: 10,000 units/day free, `channels.list` = 1 unit → tracking nhiều channels rất rẻ. Project tracking 2 channels (self + opposition) tiêu tốn ~2-10 units/day → negligible.
- Analytics API: cần OAuth, higher quota cost — chỉ dùng khi cần deeper data (retention, traffic sources).

**Build-to-sell angle:**
- "No SaaS, no subscription, data never leaves machine" — đây là selling point cho Hermes Dashboard: local, privacy-first, không gửi data ra ngoài.
- Single HTML dashboard, không cần server — phù hợp cho phase 1 (MVP), sau này có thể upgrade lên Streamlit/FastAPI.

**Áp dụng vào dự án:**
- YouTube Data agent: dùng pattern này — stdlib cho data fetch, idempotent upsert history, fail-soft cho optional metrics.
- Google Sheet Operator agent: dùng loopback OAuth pattern cho Google Sheets API.
- Dashboard: output static HTML/CSV, Telegram gateway gửi link/screenshot.

---

### 3. yt-analytics-hub / Creatorscope (sasank-in)
**Repo:** https://github.com/sasank-in/yt-analytics-hub (đổi tên khỏi creatorscope)  
**Bản chất:** FastAPI backend + vanilla JS/Tailwind/Chart.js frontend, SQLite/PostgreSQL, nhiều tính năng analytics nâng cao: engagement rate, CTR proxy, view outliers, RPM-based earnings estimate, publishing cadence, weekday/hour pattern, title-length impact, channel health score 0-100, power-law decay fit, earnings cone ±30%, composite ranking top-5.

**Những gì repo này dạy — advanced analytics SOP:**
- **Idempotent channel search với TTL:** Re-search trong 24h trả cached row — tránh waste quota. Áp dụng: YouTube Data agent search channel lần đầu, cache 24h, không refetch trừ khi cần.
- **Quota-aware pagination:** `search.list` cho top videos = 100 units/call, `playlistItems.list` = 1 unit. project cần quota budget: 2 channels × 50 videos = ~200 units cho top videos, gần như không đáng kể so với 10,000/day.
- **Rate limiting:** Per-IP rate limit trên các endpoint (30-60/minute) — pattern cho Telegram Gateway agent khi broadcast nhiều user: không spam, rate-limit messages.
- **Decoupled video analysis:** Video search không side-effect trigger channel detail charts — architectural principle: agent tasks phải isolated, không cross-contaminate. Content Bridge agent làm pain-point research không nên trigger YouTube Data agent fetch trừ khi cần.
- **Human-friendly error messages:** `_humanize_error()` translate HTTP error thành readable message — pattern cho agent error handling: mỗi agent trả về error message readable cho user, không raw stack trace.
- **Idempotent upsert:** database.py upsert-by-key — pattern cho data integrity trong semua agent-owned files.

**Advanced metrics học được (áp dụng làm dashboard metrics):**
- Engagement rate = (likes + comments) / views — project có sẵn likes/comments/views trong video_inventory.csv → tính engagement rate cho mỗi video, flag outlier (high/low).
- CTR proxy = views / impressions (cần Analytics API) — không dùng được với Data API alone.
- View outliers: identifying videos far above/below expected — Content Bridge dùng để chọn remake candidates (underperform → remake).
- Publishing cadence/ weekday-hour pattern: YouTube Data agent có thể calculate từ publish timestamps → gợi ý best time to publish.
- Channel health score (0-100): composite của subs growth, view trend, engagement rate, comment rate — Hermes Dashboard có thể tính weekly.

**Build-to-sell angle:**
- Self-hosted, local-first, no SaaS — selling point tương tự #2.
- Docker + Caddy HTTPS — production-ready deployment pattern cho Telegram Gateway agent (bot chạy service, có HTTPS webhook).
- FastAPI + Pydantic + SQLAlchemy — production backend stack cho Google Sheet Operator agent (nếu cần REST API cho sheet sync).

**Áp dụng vào dự án:**
- Content Bridge agent: dùng advanced metrics (engagement rate, view outliers, publish pattern) để chọn remake candidates và optimal publish time.
- Hermes Dashboard: tính channel health score weekly, view outliers, engagement rate trend.
- Telegram Gateway agent: rate-limit messages, fail-soft error handling, human-friendly error messages.
- Google Sheet Operator agent: idempotent upsert pattern cho sheet sync.

---

### 4. Telegram Bot Base (ChiefDojer)
**Repo:** https://github.com/ChiefDojer/telegram-bot-base  
**Bản chất:** Production-ready Telegram bot template: Aiogram v3 (async Python), Docker, Azure deployment (VM + ACI + App Service), CI/CD GitHub Actions, unit tests với pytest + coverage, modular handlers, timezone support, logging.

**Những gì repo này dạy — Telegram Gateway agent SOP:**
- **Aiogram v3 — async framework:** Telegram Gateway agent nên dùng Aiogram v3 (async) để xử lý multiple message concurrently — quan trọng khi broadcast nhiều user.
- **Modular handler architecture:** handlers.py separate from main.py — pattern cho agent: command handlers (/diagnose, /remake, /painpoints, /report, /next) mỗi cái 1 function/module, dễ maintain.
- **Docker + compose — production deployment:** Dockerfile + docker-compose.yml — Telegram Gateway agent deploy như Docker container, dễ scaling, easy backup.
- **CI/CD — test trước deploy:** GitHub Actions run pytest trước khi deploy — pattern cho agent: ogni agent change phải pass integration QA audit trước khi deploy.
- **Unit tests — test coverage:** 32 tests trong project, pytest-cov — Telegram Gateway agent cần test coverage cho commands, error handling, rate limiting.
- **Timezone support:** pytz cho date/time — Telegram Gateway sends reports với correct local time (UTC+7).
- **Long polling vs webhook:** Default long polling, webhook optional — project dùng long polling for simplicity, webhook khi production.

**Performance insight:**
- Docker memory limit (compose config) — Telegram Gateway agent cần resource limit để không eat toàn bộ system resource.
- Azure VM/ACI/App Service — 3 deployment option, project có thể dùng Azure VM (cheap) hoặc local Docker.

**Build-to-sell angle:**
- "Production-ready" — selling point cho Telegram Gateway: không phải toy project, deploy được production.
- CI/CD pipeline — selling point cho Integration QA: automated test trước deploy.
- Modular, testable — selling point cho maintainability: dễ add command mới.

**Áp dụng vào dự án:**
- Telegram Gateway agent: dùng Aiogram v3, modular handlers, Docker deployment, CI/CD, unit tests.
- Integration QA auditor: CI/CD pipeline check Telegram Gateway agent tests pass trước khi deploy.

---

### 5. Google YouTube Analytics & Reporting API Code Samples
**Repo:** https://developers.google.com/youtube/reporting/v1/code_samples  
**Bản质:** Official Google code samples cho YouTube Analytics API (query reports) và YouTube Reporting API (create/retrieve bulk reports). Languages: Java, JavaScript, PHP, Python. Samples: retrieve daily channel statistics, create reporting job, retrieve reports.

**Những gì repo này dạy:**
- **YouTube Analytics API — deeper data:** Data API v3 chỉ có public data (views, likes, comments, subscribers). Analytics API có private data: watch time, retention, traffic sources, search terms, geography, devices, audience demographics — cần OAuth.
- **Reporting API — scheduled bulk reports:** Tạo scheduling job để Google tự export data định kỳ (ngày/week/month), sau đó retrieve — phù hợp cho large-scale analytics, project hiện tại chưa cần.
- **Two API distinction rõ ràng:** Data API = public, API key. Analytics API = private, OAuth. Reporting API = scheduled bulk export. Project cần phân biệt rõ để quota management.

**Áp dụng vào dự án:**
- Hiện tại: chỉ cần Data API v3 (public data) — YouTube Data agent dùng API key.
- Nếu cần deeper analytics (retention, traffic, demographics): thêm Analytics API + OAuth — nhưng phase 1 không cần.
- Reporting API: không cần phase 1.

---

## Cross-Cutting Lessons — SOP, Performance, Build-to-Sell cho dự án

### SOP standards từ 5 repo
1. **Data pipeline:** URL → videoID → snippet + statistics → process → dataframe → visualization/report. Áp dụng cho YouTube Data agent, Content Bridge agent.
2. **Idempotent data fetch:** Cache TTL (24h), upsert-by-key, không duplicate. Áp dụng cho tất cả agent-owned data files.
3. **Fail-soft error handling:** Core call fatal, optional fail-soft, human-friendly error messages. Áp dụng cho tất cả agent.
4. **Quota awareness:** Track quota usage, optimize API call cost. Áp dụng cho YouTube Data agent (Data API units) + Telegram Gateway (rate limit).
5. **Modular agent design:** Mỗi agent 1 responsibility, file ownership rõ ràng, isolated tasks. Áp dụng cho 10 agents + 3 auditors.
6. **CI/CD + test trước deploy:** Integration QA auditor verify agent tests pass trước khi deploy. Áp dụng cho Telegram Gateway agent (prototype), sau đó cho tất cả agent.

### Performance standards
1. **YouTube Data API quota:** 10,000 units/day free. Project 2 channels × ~50 videos = ~200 units → negligible. Nhưng cần track để không exceed quota.
2. **API call optimization:** Dùng `playlistItems.list` (1 unit) cho video list, không dùng `search.list` (100 units) trừ khi cần search by keyword. Áp dụng cho YouTube Data agent.
3. **Telegram bot rate limit:** Limit broadcast rate để không spam users, không bị Telegram ban. Áp dụng cho Telegram Gateway agent.
4. **Data storage efficiency:** CSV/JSON lightweight, không cần database phức tạp phase 1. Áp dụng cho data files.

### Build-to-sell standards
1. **Local-first, privacy-first:** Không SaaS, không gửi data ra ngoài (trừ Telegram gateway broadcast). Selling point cho Hermes Dashboard, Google Sheet Operator.
2. **Self-contained output:** Static HTML/CSV dashboard, không cần runtime server. Selling point cho Hermes Dashboard phase 1.
3. **Production-ready deployment:** Docker, CI/CD, test coverage — Telegram Gateway agent model, sau này scale cho tất cả agent.
4. **Clear value proposition:** Dashboard trả lời daily/weekly questions 구체적으로 — selling point cho Hermes Dashboard.
5. **Modular, extendable:** Mỗi agent independent, dễ add/remove, dễ scale. Selling point cho multi-agent system overall.

---

## ZeroPointRepo YouTube Skills (TransciptAPI)

**Repo:** https://github.com/ZeroPointRepo/youtube-skills  
**Bản chất:** 12 skills YouTube cho AI agents — transcript, search, channels, playlists, captions, subtitles — chạy qua TranscriptAPI (khác với YouTube Data API v3). Hỗ trợ Hermes Agent, OpenClaw, Claude Code, Cursor, Codex, v.v.

**12 skills:**
- youtube-full (chính): transcripts + search + channels + playlists
- transcript: video transcript với timestamps
- youtube-search: search videos + channels
- youtube-channels: browse uploads, get latest, resolve @handles
- youtube-playlist: fetch all videos từ playlist
- youtube-api: YouTube API access không cần Google quota
- video-transcript, captions, subtitles, yt, transcriptapi: variants

**Install cho Hermes:**
```
hermes skills install skills-sh/ZeroPointRepo/youtube-skills/skills/youtube-full
```

**API key setup:** Signup transcriptapi.com → free 100 credits → key `sk_...` → lưu vào Hermes secret store qua `required_environment_variables: TRANSCRIPT_API_KEY` trong skill frontmatter.

**So sánh với YouTube Data API v3 hiện tại:**
- YouTube Data API v3: free 10,000 units/day, API key, lấy snippet+statistics, không lấy transcript
- TranscriptAPI (ZeroPointRepo): 100 credits free, key `sk_...`, lấy transcript + captions, search, channel browse — nhanh, không quota hassle, không cần OAuth

**Khi nào dùng cái nào:**
- YouTube Data API: khi cần views, likes, comments, subscribers, publish date, duration — data metrics cho dashboard, video inventory
- TranscriptAPI: khi cần transcript/captions từ video — cho Content Bridge agent research nội dung, pain point từ transcript, script generation

**Áp dụng vào dự án:**
- Content Bridge agent: dùng youtube-full skill để fetch transcript videos viral đối thủ → phân tích nội dung, pain point, hook structure → làm nguyên liệu video
- YouTube Data agent: vẫn dùng YouTube Data API v3 cho stats (views, likes, comments) — không conflict
- Hermes secret store: thêm TRANSCRIPT_API_KEY vào .env.example

**Build-to-sell angle:**
- "TranscriptAPI — 15M+ transcripts/month, 99.9% uptime" — selling point cho Content Bridge: không phải YouTube API quota-limited, nhanh, reliable
- "No yt-dlp, no headless browsers, no binaries" — selling point: nhẹ, thân thiện cloud, không bị YouTube block IP

---

| Repo | Loại | Application vào dự án | Build-to-sell value |
|------|------|----------------------|---------------------|
| Streamlit-YouTube-Dashboard | Streamlit dashboard cho 1 video, sentiment analysis | Content Bridge: comment → pain point; YouTube Data: snippet+stats pipeline; Dashboard: KPI views/likes/comments | Simple dashboard, deploy nhanh, sentiment-based pain-point detection |
| youtube-analytics-dashboard | Local zero-dep dashboard, loopback OAuth, static HTML, fail-soft | YouTube Data agent: stdlib fetch, idempotent history, fail-soft; Google Sheet Operator: loopback OAuth pattern; Dashboard: static HTML output | Privacy-first, no SaaS, no dependency, local-only data |
| yt-analytics-hub (Creatorscope) | FastAPI + SQLite, advanced analytics (engagement rate, CTR proxy, view outliers, health score, RPM estimate) | Content Bridge: engagement rate, view outliers, publish cadence → remake candidates; Hermes Dashboard: health score, trends; Telegram Gateway: rate limit, human-friendly errors | Production backend stack, self-hosted, Docker + HTTPS deployment |
| Telegram Bot Base (ChiefDojer) | Aiogram v3, Docker, Azure, CI/CD, pytest, modular handlers | Telegram Gateway agent: full reference implementation — async, modular, Docker deploy, CI/CD, test coverage, timezone | Production-ready bot, testable, CI/CD, modular — scaling-ready |
| Google YouTube Analytics/Reporting API samples | Official samples cho Analytics API (private) + Reporting API (scheduled) | Reference cho deep analytics (retention, traffic, demographics) — nhưng phase 1 không cần | Official Google reference — reliable, future upgrade path |

---

## Phase 1 Strategy Details

### Shorts (tăng sub)
- 3-5/ngày
- Pain point-driven content
- Hook 3 giây đầu strong
- CTA: Subscribe + Comment keyword

### Live (xây trust)
- 2-3/ngày
- XAUUSD trading real-time
- Title: giá trị proposition + hook
- CTA: Subscribe, join Telegram

### Telegram (lead)
- Lead capture từ YouTube subscriber
- Nurturing messages
- Offer promotion (sau human review)

### Offer/Tripwire (convert)
- Mini-course, VIP Signal, Edu Course
- Convert Telegram leads thành buyers

# RUN-20261001-WF02-comment-painpoint-scrape

- Goal: Thu thập comments trading qua YouTube Data API v3 → pain-point CSV làm nguyên liệu Shorts trả lời comment
- Workflow: WF02
- Automation level: L1 (external read, free API)
- Owner: youtube_workflow
- Supporting agents: content_bridge, security, aegis_guardrail
- Status: COMPLETE (local artifacts only)
- Inputs: data/processed/video_inventory_api.csv, data/processed/comment_videos_input.csv, long-tail keyword queries
- Missing inputs: NONE
- Tools allowed: YouTube Data API v3 (commentThreads.list, search.list), Python scripts
- Tools prohibited: YouTube publish, Telegram broadcast, Sheet write, trade execution
- Guardrail result: PASS — no secrets in output, no external write, no profit claims
- Human approval required: YES cho việc dùng data vào backlog/publish
- Human approval status: PENDING (data đã sẵn sàng, chờ Alan review)
- Output paths: outputs/painpoints/master/painpoints_master.csv
- External action: NONE (chỉ đọc API công khai)
- External action read-back: N/A (read-only)
- Feedback destination: Channel Brain, Prompt Registry
- Next owner/action: content_bridge review + chọn top pain point cho Shorts

## Plan

1. Verify token/API access
2. Scrape comments theo 2 chế độ: inventory CSV + long-tail keyword search
3. Normalize + lọc spam + lọc domain relevance
4. Extract pain-point candidates có scoring
5. Aggregate vào master CSV + gán góc Short trả lời comment
6. Human review trước khi đưa vào backlog

## Evidence and Sources

- YouTube Data API v3 `commentThreads.list` (1 unit/call, free)
- YouTube Data API v3 `search.list` (100 units/call)
- Apify actor `streamers/youtube-comments-scraper`: THẤT BẠI — tài khoản chỉ còn $0.076, lỗi 402 not-enough-usage-to-run-paid-actor
- Kênh đối thủ: @GoldTraderAlliance (UCdS8VXFlNvVohM09qzZGCkA)

## Results

- 8 runs (6 keyword queries + 2 inventory runs)
- 5,731 comments thô từ 6 keyword runs; 43 video nguồn unique
- 1,204 pain point unique sau dedupe + lọc spam + lọc domain
- Phân bố: strategy_rules 315, risk_management 275, education_gap 273,
  other_question_or_pain 152, entry_timing 108, broker_platform 60, psychology 21
- Quota dùng: ~648 units (6 keyword runs × 108) + 20 units (inventory runs) ≈ 668 / 10,000 units/ngày
- Spam còn lại: 0

## Validation

- Command: `py -3 -m pytest tests/ -q`
- Result: 58 passed
- Command: `python scripts/aggregate_painpoints.py --input-dir outputs/painpoints --output-dir outputs/painpoints/master`
- Result: 1,204 unique pain points written

## Approval Log

- 2026-10-01: Apify paid actor run — BLOCKED (insufficient Apify balance, $0.076 remaining)
- 2026-10-01: Chuyển sang YouTube Data API v3 (free) — không cần approval cho read-only public data
- 2026-10-01: PENDING — chờ Alan review master CSV trước khi promote vào Shorts backlog

## Feedback

- Apify actor trả phí là blocker thật (balance $0.076). YouTube Data API v3 thay thế hoàn toàn cho comment scraping, miễn phí và đủ dùng.
- Search theo `order=viewCount` kéo video viral không liên quan → phải dùng `order=relevance` + domain relevance gate.
- `.env` có BOM ở dòng đầu → key đầu tiên bị che. Phải đọc bằng `utf-8-sig`.
- Reply của chính chủ kênh phải bị loại khỏi pain-point (không phải tiếng nói khán giả).

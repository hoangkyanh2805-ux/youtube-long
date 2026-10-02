# AI Workflow Blueprint — YouTube Operating System

**Project:** `@azzammastertradinggold`  
**Đối thủ chính:** `@GoldTraderAlliance`  
**Công thức bắt buộc:**

```text
PROBLEM → OUTCOME → TRIGGER → INPUT → AI PROCESS → TOOLS
→ GUARDRAILS → HUMAN REVIEW → OUTPUT → FEEDBACK
```

Tài liệu này biến P01–P17 từ các prompt riêng lẻ thành workflow lặp lại được. Prompt là năng lực; workflow mới là quy trình tạo kết quả.

---

## 1. Workflow Contract

Mọi workflow trong dự án phải khai báo đủ các trường sau:

1. **Problem — Why:** Vấn đề lặp lại, chậm, tốn chi phí hoặc dễ sai nào cần giải quyết?
2. **Outcome — What:** Kết quả cuối phải trông như thế nào và dùng để làm gì?
3. **Trigger — When:** Điều gì khởi động workflow: yêu cầu thủ công, lịch, file mới, video mới hay metric alert?
4. **Inputs — What data:** AI cần tài liệu, URL, API data, business rule, mẫu cũ và context nào?
5. **AI Process — Steps:** `Research → Analyze → Process → Create → Review`.
6. **Tools — Systems:** API, file, database, Sheet, TranscriptAPI, ChartAnimator, Telegram hoặc MCP nào được phép dùng?
7. **Guardrails — Rules:** AI được tự làm gì, bị cấm làm gì và khi nào phải dừng?
8. **Human Review — Approval:** Ai duyệt, duyệt ở bước nào và duyệt cái gì?
9. **Output — Result:** File, report, script, video package hoặc queue nào được bàn giao?
10. **Feedback — Improve:** Metric và phản hồi nào được đưa về Channel Brain, Prompt Registry hoặc Founder Memory?

### Trạng thái workflow

```text
DRAFT → READY → RUNNING → PENDING_APPROVAL → COMPLETE → MEASURED → IMPROVED
```

Không được đánh dấu `COMPLETE` nếu chưa có output thật. Không được đánh dấu `MEASURED` nếu chưa có dữ liệu sau thực thi.

---

## 2. Mức tự động hóa và quyền hạn

### L0 — Gợi ý

- AI chỉ đề xuất kế hoạch hoặc nội dung.
- Không tạo file và không tác động hệ thống bên ngoài.

### L1 — Read-only automation

- Được đọc API, transcript, file và dữ liệu công khai.
- Được phân tích và tạo báo cáo local.
- Không được sửa Sheet, publish hoặc gửi tin.

### L2 — Local production

- Được tạo script, CSV, Markdown, brief và asset package trong workspace.
- Phải ghi owner, nguồn và trạng thái.
- Không được tự gửi ra ngoài.

### L3 — External action có phê duyệt

- Publish video, sửa Sheet, broadcast Telegram, trả lời bình luận nhạy cảm, thay title/thumbnail hoặc gửi sales/affiliate content.
- Chỉ thực hiện sau human approval.
- Sau thao tác phải đọc lại đúng target và lưu bằng chứng.

### L4 — Cấm tự động

- Execute trade.
- Cam kết lợi nhuận.
- Tạo hoặc trình bày kết quả trading giả.
- Seeding giả danh người xem.
- Xóa dữ liệu lớn hoặc sửa cấu trúc Sheet không có approval.
- Lộ API key, token, password hoặc dữ liệu riêng tư.

---

# 3. Các workflow vận hành chính

## WF01 — New Topic → Published Video → Measured Result

### Problem

Ý tưởng, research, script, SEO, thumbnail và editor đang rời rạc; dễ thiếu đầu vào, trễ deadline và không biết video thắng/thua vì đâu.

### Outcome

Một `publish-ready package` hoàn chỉnh gồm:

- Approved topic brief.
- Script đã duyệt.
- Visual/chart brief.
- Video master và source files.
- Thumbnail variants.
- SEO/upload package.
- Measurement plan sau đăng.

### Trigger

- Alan duyệt một topic trong backlog; hoặc
- Topic mới được thêm vào content calendar và chuyển trạng thái `APPROVED`.

### Inputs

- P01 Channel Brain.
- P02 audience research.
- P06 audience segment.
- P07 keyword/competitor gap.
- Topic, keyword, format và target duration.
- Brand guide và asset library.

### AI Process

```text
Research topic
→ Verify demand/evidence
→ Select angle
→ Generate brief
→ Write script
→ Fact/claim check
→ Create editor handoff
→ Generate SEO + thumbnail brief
→ QA package
→ Human approval
```

### Tools

- YouTube Data API v3.
- TranscriptAPI khi đã cấu hình và được phép dùng credit.
- Channel Brain và Prompt Registry.
- File workspace/Google Sheet.
- ChartAnimator/TradingView cho chart asset.
- Phần mềm edit do Editor sử dụng.

### Agents và Prompt

- `youtube_data`: P07.
- `youtube_workflow`: P02.
- `content_bridge`: P03, P08, P09, P10, P11.
- Editor: P15.
- `platform_ux`: mobile/readability review.
- `integration_qa` + `aegis_guardrail`: pre-publish gate.

### Guardrails

- Không bịa volume, kết quả trade hoặc tỷ lệ thắng.
- Chart mô phỏng phải được ghi rõ.
- Không dùng asset không có quyền.
- Không auto-publish.

### Human Review

Alan duyệt ba gate:

1. Topic/angle.
2. Script/claim.
3. Final video/thumbnail/upload package.

### Output

- `outputs/content/<video_id>/topic-brief.md`
- `outputs/content/<video_id>/script.md`
- `outputs/content/<video_id>/editor-brief.md`
- `outputs/content/<video_id>/seo-package.md`
- Master video, thumbnail và source files do Editor bàn giao.

### Feedback

Sau khi có dữ liệu, P04 phân tích phễu. Insight được chuyển về:

- Channel Brain: insight bền vững.
- Prompt Registry: lỗi/quy trình cần sửa.
- Founder Memory: quyết định và bài học chiến lược.

### Success Criteria

- Tất cả đầu ra bắt buộc tồn tại.
- Claim có nguồn hoặc được gắn nhãn mô phỏng/ý kiến.
- Ba approval gate đã pass.
- Video sau đăng có measurement record; không tự đặt ngưỡng CTR/retention khi chưa có baseline thật.

---

## WF02 — Competitor/Keyword → Priority Content Backlog

### Problem

Nghiên cứu đối thủ thủ công tốn thời gian; keyword, transcript, comment và video inventory không được nối thành backlog có ưu tiên.

### Outcome

Một backlog có bằng chứng gồm keyword, audience pain point, competitor coverage, content angle và mức ưu tiên.

### Trigger

- Review hàng tuần/tháng; hoặc
- Alan yêu cầu kiểm tra một đối thủ/keyword mới; hoặc
- Backlog sắp hết topic đã duyệt.

### Inputs

- Kênh mình: `@azzammastertradinggold`.
- Đối thủ chính: `@GoldTraderAlliance`.
- Keyword sheet.
- Video metadata, transcript và comments có thật.
- Channel Brain hiện hành.

### AI Process

```text
Verify channel identity
→ Fetch metadata/inventory
→ Fetch selected transcripts/comments
→ Extract hooks, pain points and coverage
→ Match keyword to competitor content
→ Detect gaps
→ Rank backlog
→ Evidence review
```

### Tools

- YouTube Data API v3.
- TranscriptAPI.
- Sheet/file parser.
- Local CSV/JSON/Markdown.

### Agents và Prompt

- `youtube_data`: inventory và metrics.
- `youtube_workflow`: transcript/topic/hook extraction.
- `content_bridge`: P06, P07, P08.
- `security` + `integration_qa`: source và schema check.

### Guardrails

- Luôn báo số video thực fetch được so với `videoCount` công khai.
- Không biến substring match thành kết luận semantic chắc chắn.
- Không dùng paid credits hàng loạt khi chưa duyệt.

### Human Review

Alan duyệt top backlog trước khi chuyển sang WF01.

### Output

- Competitor inventory.
- Keyword-gap report.
- Hook library.
- Priority content backlog.

### Feedback

So sánh hiệu suất video đã sản xuất với giả thuyết ban đầu để tăng/giảm trọng số keyword, angle và segment.

### Success Criteria

- Channel ID/handle đúng.
- Mọi keyword và competitor claim có nguồn.
- Backlog có owner, priority và status.

---

## WF03 — Long Video → Shorts + Remake + Thumbnail Assets

### Problem

Một video dài chưa được tái sử dụng tối đa; Editor thiếu cut list, chart brief và tiêu chuẩn bàn giao.

### Outcome

Một asset package gồm Shorts, remake variants, chart animation và thumbnail variants, nếu nguyên liệu đủ chất lượng.

### Trigger

- Video dài master đã được duyệt; hoặc
- Video cũ được chọn làm remake candidate.

### Inputs

- Master video/script/transcript.
- Retention data nếu có.
- Brand guide.
- Chart/setup brief.
- CTA và target platform.

### AI Process

```text
Analyze transcript and structure
→ Identify standalone moments
→ Rank clips by hook/value
→ Rewrite short hooks
→ Build cut list
→ Build ChartAnimator brief
→ Build thumbnail brief
→ Editor production
→ QA mobile/copyright/claim
```

### Tools

- Transcript/cut-list processing.
- ChartAnimator.
- TradingView khi cần dữ liệu/chart context.
- CapCut, Premiere Pro hoặc DaVinci Resolve.
- Canva/Photoshop hoặc công cụ thiết kế được duyệt.

### Agents và Prompt

- `youtube_workflow`: tìm đoạn và cấu trúc.
- `content_bridge`: P05, P11, P15.
- Editor người thật: dựng và bàn giao.
- `platform_ux`: kiểm tra khả năng xem trên mobile.
- `aegis_guardrail`: claim, copyright và simulation label.

### Guardrails

- Không sao chép video đối thủ.
- Không ép đủ 3–5 Shorts nếu video không có đủ đoạn độc lập.
- Không trình bày chart mô phỏng như trade thật.
- Không dùng nhạc/footage không rõ quyền.

### Human Review

Duyệt master Short, remake concept và thumbnail trước đăng.

### Output

- Shorts 9:16.
- Remake variants.
- Chart animation/source.
- Thumbnail variants/source.
- Asset manifest và quyền sử dụng.

### Feedback

Lưu completion rate, retention, CTR và revision notes để cải thiện cut rule, subtitle style và thumbnail system.

### Success Criteria

- Hook rõ trên mobile.
- Subtitle không che UI.
- File nguồn và asset manifest đầy đủ.
- Không có claim/copyright issue chưa xử lý.

---

## WF04 — Upload → Funnel Diagnosis → Optimization

### Problem

Đăng video xong chỉ nhìn view; không biết video rớt ở hiển thị, click hay giữ chân.

### Outcome

Upload sạch, measurement record và action đúng nấc phễu.

### Trigger

- Video chuyển trạng thái `READY_TO_PUBLISH`.
- Measurement windows do Alan/Channel Manager đặt.
- Metric alert hoặc yêu cầu review thủ công.

### Inputs

- Final video, thumbnail, title, description và playlist plan.
- Analytics/Studio data thực sau đăng.
- Baseline cùng format/topic nếu có.

### AI Process

```text
Pre-publish checklist
→ Human publish
→ Read-back target
→ Collect analytics
→ Diagnose impressions/CTR/views/retention
→ Recommend one controlled change
→ Human approval
→ Apply change
→ Measure again
```

### Tools

- YouTube Studio/Analytics.
- YouTube Data API cho public metrics.
- Dashboard và Sheet/file log.

### Agents và Prompt

- P04, P10, P14.
- `youtube_data` + `hermes_dashboard`.
- `integration_qa` + `aegis_guardrail`.

### Guardrails

- Không gọi Data API public là retention/CTR private.
- Không đổi đồng thời quá nhiều biến khi cần học nguyên nhân.
- Không auto-publish hoặc tự đổi video public.

### Human Review

Duyệt publish và mọi thay đổi title/thumbnail/description quan trọng.

### Output

- Upload checklist.
- Publish/read-back record.
- Funnel diagnosis.
- Optimization action và experiment log.

### Feedback

Cập nhật winning title/thumbnail/hook pattern khi có đủ evidence; không generalize từ một video.

### Success Criteria

- Target publish đúng kênh.
- Read-back thành công.
- Chẩn đoán dựa trên đủ dữ liệu hiện có.
- Mỗi thay đổi có hypothesis và kết quả đo lại.

---

## WF05 — Comment → Reply → Audience Insight → New Content

### Problem

Bình luận không được phản hồi nhất quán và insight khán giả bị mất.

### Outcome

Reply queue đúng giọng kênh, escalation queue và pain points được chuyển thành content input.

### Trigger

- Bình luận mới; hoặc
- Ca kiểm tra cộng đồng; hoặc
- Video vừa publish và cần theo dõi phản hồi.

### Inputs

- Comment thật.
- Channel Brain/voice guide.
- FAQ, escalation rules và approved CTA.

### AI Process

```text
Fetch/read comments
→ Classify question/positive/objection/spam/risk
→ Draft reply
→ Escalate sensitive items
→ Human review when required
→ Reply
→ Extract recurring pain point
→ Send insight to Content Bridge
```

### Tools

- YouTube comment interface/API khi được cấp quyền.
- Telegram community tools.
- Local reply queue và pain-point file.

### Agents và Prompt

- P04, P16.
- `telegram_gateway` + Community Assistant.
- `content_bridge` nhận insight.
- `security` kiểm tra claim và link.

### Guardrails

- Không spam, seeding giả hoặc giả danh Alan.
- Không đưa signal hoặc cam kết lợi nhuận.
- Không tự ý gửi affiliate/Telegram link.
- Không xóa phản hồi tiêu cực hợp lệ.

### Human Review

Khiếu nại, claim lợi nhuận, pháp lý, thanh toán, sales CTA và xung đột phải được duyệt.

### Output

- Reply queue.
- Escalation list.
- FAQ/pain-point update.
- Content ideas từ comments.

### Feedback

Đo response quality, escalation rate và số pain point chuyển thành video; tránh tối ưu theo số reply đơn thuần.

### Success Criteria

- Bình luận được phân loại đúng schema.
- Nội dung nhạy cảm không bị auto-reply.
- Insight được chuyển đúng owner.

---

## WF06 — Audience → Lead → Offer → Revenue Learning

### Problem

View/subscriber không được nối thành lead và offer có đo lường; hoạt động monetization dễ trở thành spam hoặc claim quá mức.

### Outcome

Một funnel có disclosure, approval, tracking và feedback về product-market fit.

### Trigger

- Nội dung/lead magnet đã được Alan duyệt.
- Campaign hoặc offer window được mở thủ công.

### Inputs

- Audience segment.
- Approved offer/product.
- Lead magnet.
- CTA, disclosure và pricing đã duyệt.
- Lead/conversion data thật.

### AI Process

```text
Match audience pain point to offer
→ Draft lead magnet/CTA
→ Compliance review
→ Human approval
→ Publish/send
→ Track lead and conversion
→ Analyze objection and drop-off
→ Improve offer/content
```

### Tools

- Telegram Gateway.
- Google Sheet/local lead log.
- Email/payment platform khi được kết nối và phê duyệt.
- Dashboard.

### Agents và Prompt

- P12, P13.
- `founder_ops`, `learning_tutor`, `telegram_gateway`, `hermes_dashboard`.
- `security` + `aegis_guardrail`.

### Guardrails

- Sales copy chỉ là draft.
- Affiliate disclosure bắt buộc khi áp dụng.
- Không bịa revenue, conversion hoặc testimonial.
- Không broadcast khi chưa duyệt.

### Human Review

Alan duyệt offer, pricing, sales copy, audience, channel và thời điểm gửi.

### Output

- Approved funnel package.
- Lead log.
- Campaign/read-back record.
- Revenue report chỉ dùng dữ liệu thật.

### Feedback

Objection, conversion và refund/complaint data quay lại audience research, product curriculum và content plan.

### Success Criteria

- Approval và disclosure đầy đủ.
- Lead/conversion có source attribution khi data hỗ trợ.
- Không có claim không được chứng minh.

---

## WF07 — Weekly Review → Learning → Workflow Improvement

### Problem

Agent có thể lặp lỗi, prompt bị thay đổi không kiểm soát và bài học không được đưa trở lại hệ thống.

### Outcome

Một weekly operating review xác định điều gì thắng, điều gì sai, workflow nào cần sửa và ai chịu trách nhiệm.

### Trigger

- Cuối chu kỳ tuần; hoặc
- Lỗi lặp lại; hoặc
- Guardrail violation; hoặc
- Alan yêu cầu retrospective.

### Inputs

- Agent task logs.
- Video/content performance có thật.
- Error/conflict/security reports.
- Human feedback.
- Founder decisions.

### AI Process

```text
Collect evidence
→ Compare outcome with success criteria
→ Identify bottleneck/root cause
→ Propose workflow/prompt change
→ QA and human review
→ Apply local versioned change
→ Re-test
→ Keep only if improved
```

### Tools

- Dashboard reports.
- Prompt Registry.
- Channel Brain.
- Founder Memory.
- Integration, security và Aegis reports.

### Agents và Prompt

- P17.
- Hermes Orchestrator.
- `founder_ops`, `hermes_dashboard`.
- Ba Auditor.

### Guardrails

- Không self-modify prompt/SOP mà không log.
- Không giữ thay đổi nếu không có improvement evidence.
- Dừng sau hai vòng liên tiếp không cải thiện; giới hạn tối đa là safeguard, không phải tiêu chí thành công.

### Human Review

Alan duyệt thay đổi chiến lược, quyền, workflow hoặc external integration.

### Output

- Weekly decision brief.
- Improvement backlog.
- Versioned prompt/workflow change log.
- Assigned owners và deadline.

### Feedback

Bài học bền vững vào Skill/Channel Brain; quyết định điều hành vào Founder Memory; identity và hard rules mới được đưa vào `soul.md` khi thật sự áp dụng cho mọi task.

### Success Criteria

- Mỗi thay đổi có root cause, owner và evidence.
- Không để bài học chỉ nằm trong chat.
- Không mở rộng `soul.md` vượt giới hạn 18 dòng.

---

# 4. Workflow Router

Hermes Orchestrator định tuyến theo loại yêu cầu:

- **Nghiên cứu đối thủ/keyword/transcript:** WF02.
- **Sản xuất video mới:** WF01.
- **Cắt Shorts/remake/thumbnail:** WF03.
- **Upload và phân tích hiệu suất:** WF04.
- **Bình luận và cộng đồng:** WF05.
- **Lead, offer và doanh thu:** WF06.
- **Review/cải tiến hệ thống:** WF07.

Nếu một yêu cầu đi qua nhiều workflow, Orchestrator tạo dependency rõ ràng thay vì chạy tất cả cùng lúc.

---

# 5. Workflow Run Record — Template

```markdown
# RUN-[YYYYMMDD]-[WF-ID]-[SHORT-NAME]
- Workflow:
- Owner:
- Status:
- Problem:
- Desired outcome:
- Trigger:
- Inputs received:
- Missing inputs:
- AI process completed:
- Tools used:
- Evidence/source links:
- Guardrail result:
- Human approval required:
- Human approval status:
- Output paths/URLs:
- External action read-back:
- Metrics/checkpoint:
- Feedback/lesson:
- Next owner/action:
```

---

# 6. Definition of Done cho một Real Workflow

Một workflow chỉ được xem là “real” khi:

- Vấn đề và outcome rõ ràng.
- Trigger có thể nhận biết.
- Input schema cụ thể.
- Từng bước AI có owner.
- Tool và quyền được khai báo.
- Guardrail và điểm dừng tồn tại.
- Human approval đặt trước external action.
- Output thật đã được tạo.
- External action được read-back.
- Metric/feedback quay lại hệ thống để cải tiến.

Nếu thiếu bất kỳ phần nào, đó vẫn chỉ là **AI idea hoặc prompt**, chưa phải workflow vận hành.

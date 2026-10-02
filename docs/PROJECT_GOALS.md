# MỤC TIÊU & KỲ VỌNG DỰ ÁN — CHỐT TỪ LỜI ALAN

**Nguồn:** toàn bộ hội thoại Telegram thread 13 (`t.me/c/4458375752/13`),
session `20260930_204033_f886c7e4`, 53 tin nhắn user từ 30/09 → 02/10/2026.
**Sinh:** tự động từ session DB, không diễn giải thêm.

---

## 1. MỤC TIÊU KINH DOANH (Alan nói rõ nhất)

> *"vận hành dự án này theo tiêu chí SOP AI agent integration + Build-to-sell:
> hiệu suất để rõ ràng, nặng nhất là khâu edit tận dụng hết khả năng của agent,
> Claude vào dự án. **Mục tiêu 2 ngày 1 video long, tăng sub, like**"*

**3 nguồn thu nhập Alan liệt kê:**
1. **YPP** — ad revenue
2. **Affiliate** — broker, charting platform, journal
3. **Bán sản phẩm** — checklist, calculator, mini-course, VIP group, full course

**Nút cổ chai Alan xác định:** khâu **EDIT** — phải tận dụng hết khả năng agent.

---

## 2. 13 PROMPT PHÚC BANI — Alan yêu cầu ứng dụng TỪNG CÁI

Alan gửi lần lượt và yêu cầu *"ứng dụng nội dung, prompt vào dự án"*:

| # | Tên prompt | Nội dung cốt lõi |
|---|-----------|------------------|
| 01 | **Channel Brain** | File bộ não kênh: ngành/khán giả/nỗi đau, thế mạnh/giọng, mục tiêu/đối thủ/từ khoá. Không bịa dữ liệu |
| 02 | **Nghiên cứu ngách & khán giả** | Transcript + comment đối thủ → 5 nỗi đau lặp lại, câu hỏi chưa trả lời, 10 long-tail keyword, 5 khoảng trống đối thủ |
| 03 | **Lên ý tưởng → kịch bản** | Từ 1 chủ đề → 10 ý tưởng, title ≤60 ký tự, hook 8s, câu ngắn, khử "mùi AI" |
| 04 | **Tối ưu phễu & chăm khán giả** | Soi phễu **Hiển thị → CTR → %xem**, chỉ ra tụt ở nấc nào; sửa thumbnail/title (CTR) + mở đầu (%xem); 5 câu trả lời bình luận giữ chân. *Không kết luận chỉ dựa 1 chỉ số; thiếu dữ liệu thì nói rõ* |
| 05 | **Đa nền tảng** | 1 video → 5 định dạng: Short · bài chữ · carousel · bài quan điểm · checklist. Mỗi cái hook riêng, góc riêng, CTA riêng. Bản dịch tiếng Anh mở thị trường RPM cao |
| 06 | **Phân khúc khán giả giá trị nhất** | 5-8 phân khúc, chấm 1-10 (nhu cầu, tiềm năng tiền, dễ tiếp cận, cạnh tranh, hợp thế mạnh). *"Đừng mặc định phân khúc đông nhất là giá trị nhất"* |
| 07 | **Nghiên cứu đối thủ & từ khoá chủ lực** | 10 kênh đối thủ, điểm mạnh/yếu/khoảng trống, 5 từ khoá chủ lực, 20 long-tail |
| 08 | **30 ý tưởng video viral** | 30 ý tưởng + 2-3 title mẫu mỗi cái (tò mò/số/cảm xúc), đánh dấu 5 dễ lên đề xuất nhất, xếp thứ tự 30 ngày |
| 09 | **Kịch bản giữ chân** | Hook 15s đầu, bố cục có điểm "sóng cao", giọng tự nhiên không lộ mặt AI, CTA cuối, gợi ý hình ảnh từng đoạn |
| 10 | **SEO: title, mô tả, tag** | 5 title chuẩn SEO, mô tả 150-200 từ + timestamp, 15-20 tag mượn view đối thủ, 3 hashtag + khung giờ đăng |
| 11 | **Thumbnail bùng nổ CTR** | 5 concept (bố cục/màu/cảm xúc), chữ 80/20 với title, tương phản trên mobile, prompt AI tạo hình |
| 12 | **Kiếm tiền & nhân bản** | Nguồn thu, lộ trình bật kiếm tiền nhanh nhất, nhân bản đa ngôn ngữ, mô hình đội nhóm, kế hoạch 90 ngày |
| 13 | **Lộ trình 0 → mục tiêu** | Cột mốc theo tuần, việc theo ngày, bài tập ra sản phẩm thật, công cụ, điểm kiểm tra (CTR · %xem · sub · view) |

**Alan còn yêu cầu:** *"tổng hợp thành 1 checklist sản xuất 30 ngày (video + SEO + thumbnail + đăng bài)"*

---

## 3. KIẾN TRÚC HỆ THỐNG (Alan chỉ định cụ thể)

### Mô hình "1 brain, 1 workshop, 1 cockpit"

```
Hermes Agent  = Orchestrator / điều phối
                Nhận goal, chọn WF01-WF07, giữ nhịp, hỏi approval,
                KHÔNG tự sửa/publish/send nếu chưa duyệt.

Codex         = Builder / analyst / auditor trong repo
                Đọc docs, tạo plan, sửa file local khi được giao,
                chạy test/check, sinh report. Làm việc sâu trong repo.

VS Code       = cockpit / nơi Alan quan sát và chỉnh tay
                Xem diff, duyệt file, chạy terminal, kiểm soát thay đổi
                trước khi đẩy sang hệ thống ngoài.
```

### Source-of-Truth (Alan chỉ định rõ)

| File | Vai trò |
|------|---------|
| `docs/ai-workflow-blueprint.md` | **Workflow router chính** |
| `knowledge/prompt-registry.md` | **Prompt/capability router P01-P17** |
| `multi_agent_architecture.md` | **Agent ownership** |
| `docs/aegis-guardrail-checklist.md` | **Safety gate** |
| `soul.md` | Hermes bootstrap — **không giữ state dài** |

### Nhịp chạy chuẩn (Alan viết chính xác)

```
Goal → Pick WF → Create Run Record → Assign Agents → Produce Draft
→ Guardrail Check → Human Approval → External Action nếu có
→ Read-back → Feedback/Memory
```

### Cấp quyền L0-L4 (Alan định nghĩa)

| Mức | Được làm |
|-----|----------|
| **L0** | Hermes/Codex chỉ đề xuất |
| **L1** | Đọc file/API public, phân tích |
| **L2** | Tạo file local trong repo |
| **L3** | Sheet, Telegram, YouTube publish, title/thumbnail, sales CTA → **bắt buộc Alan duyệt** |
| **L4** | **CẤM tự động:** execute trade, claim lợi nhuận, seeding giả, lộ secret, xoá dữ liệu lớn |

### Multi-agent — "đừng để 10 agent chạy loạn"

Alan chỉ định agent nào cho workflow nào:
```
WF01: youtube_data, youtube_workflow, content_bridge, platform_ux, integration_qa, aegis_guardrail
WF02: youtube_data, youtube_workflow, content_bridge
WF03: youtube_workflow, content_bridge, Editor, platform_ux
WF04: youtube_data, hermes_dashboard, integration_qa, aegis_guardrail
```

### Alan yêu cầu cụ thể (msg 1264)

1. Thay `soul.md` bằng bản **18 dòng**
2. Đồng bộ `multi_agent_architecture.md` thành **10 Agent + 3 Auditor**
3. Tạo `prompt-registry.md` chứa **P01–P17**

---

## 4. 4 CÔNG VIỆC CHO AGENT (Alan liệt kê 4 lần, msg 1203-1216)

> *"con Agent dữ liệu làm content youtube, nguyên liệu làm ra edit video ngắn.
> remake video. Thành làm short và thumbnail. làm checklist tuyển dụng vị trí editor
> → list 4 công việc này ra cho tôi"*

1. **Agent dữ liệu** làm content YouTube
2. **Nguyên liệu** để edit video ngắn
3. **Remake video** → thành Short + thumbnail
4. **Checklist tuyển dụng** vị trí editor

**Bổ sung (msg 1220):** *"nhận script content làm video ngắn, thêm task cho ứng viên
nhận thêm kênh để comment tương tác tăng"*

**Nguồn nguyên liệu chart (msg 1222):** https://www.chartanimator.io/

**Yêu cầu cụ thể cho editor Hưng (msg 1229, 1231):**
*"gửi checklist và yêu cầu công việc cho Hưng xem như thế nào nhé, bạn làm được
thì nhận việc"* → *"rút ngắn gọn thành JD, checklist công việc cho editor Hưng"*

---

## 5. WORKFLOW BLUEPRINT (msg 1286, 1187)

Alan gửi công thức và yêu cầu áp vào dự án:

```
PROBLEM → OUTCOME → TRIGGER → INPUT → AI → TOOLS → REVIEW → OUTPUT → FEEDBACK
```

Chi tiết 10 bước:
```
🎯 Problem     → What are you actually solving?
📤 Outcome     → What should the final result look like?
⚡ Trigger     → What starts the process?
📥 Inputs      → What does AI need?
🧠 AI Process  → Research → Analyze → Create → Review
🔗 Tools       → APIs, files, databases, MCP
🛡 Guardrails  → What can AI do automatically?
👤 Human Review→ Where does approval happen?
📊 Output      → What exactly gets delivered?
🔄 Feedback    → How does the workflow improve?
```

> *"Stop asking: 'What can AI do?' Start asking: 'What repeatable workflow can AI redesign?'"*

---

## 6. AGENTIC AI — 9 NĂNG LỰC NỀN TẢNG (msg 1175, 1201)

Alan gửi infographic + phân tích, yêu cầu áp vào dự án:
Harness · Memory & State · Search & Content · Tích hợp hệ thống ·
Skill toolkits · Permission & Security · Evaluation & Learning ·
Multi-agent network · Centralized coordination

---

## 7. QUY TRÌNH UP VIDEO BÀI BẢN (msg 1173, 1199)

Alan gửi và yêu cầu chuyển thành prompt:
- **Hook 3-5 giây đầu** phải nói ngay "người xem được gì"
- **Cài điểm cao trào** để giữ qua mốc **30% – 60% – 80%**
- ***"%xem trung bình mới là thứ quyết định YouTube có đề xuất tiếp hay không — không phải lượt xem"***
- Cấu hình upload: đúng danh mục, ngôn ngữ, vị trí. Kênh mới **đừng premiere/đặt lịch** — đăng thẳng
- **Đăng đúng khung giờ quan trọng hơn đúng ngày** — chọn giờ cố định để thuật toán học quy luật

---

## 8. YÊU CẦU CÔNG CỤ (msg 1330, 1388)

> *"chạy được chưa, cần set up lệnh gì không qua hermes, rồi thêm tool **Apify**
> cào comment youtube, tiktok, social để lấy pain point chưa"*

---

## 9. NGUYÊN TẮC LÀM VIỆC ALAN NHẤN MẠNH

Từ chính lời Alan trong thread:

| Nguyên tắc | Nguồn |
|-----------|-------|
| **Không bịa số liệu** — thiếu thì nói rõ | msg 1106, 1001 |
| **Đọc hình rồi làm, đừng đoán** | msg 1074 (*"đọc hình đi rồi làm, chứ đoán j mày"*) |
| **Không kết luận chỉ dựa 1 chỉ số** | msg 1090 |
| **Đi từng prompt chi tiết** — mỗi prompt tương đương 1 agent | msg 999 |
| **Human approval trước mọi external action** | msg 1301 |
| **Không tự sửa sheet/publish/send khi chưa duyệt** | msg 1301 |

---

## 10. ĐỐI CHIẾU: ĐÃ CÓ GÌ / CÒN THIẾU GÌ

> **Đã verify thật ngày 02/10/2026** — mỗi dòng dưới đây có kiểm chứng bằng lệnh, không suy đoán.

### ✅ Đã có trong repo

| Yêu cầu | Trạng thái | Bằng chứng |
|---------|-----------|-----------|
| Prompt registry P01-P17 | ✅ **17/17** | `knowledge/prompt-registry.md` 13,755 B, grep thấy đủ P01→P17 |
| Multi-agent 10 Agent | ✅ **10 Agent** | `multi_agent_architecture.md` 24,411 B, 361 dòng |
| Workflow blueprint | ✅ | `docs/ai-workflow-blueprint.md` 19,369 B, 725 dòng |
| Aegis guardrail | ✅ | `docs/aegis-guardrail-checklist.md` 2,306 B |
| soul.md **18 dòng** | ✅ | `profiles/youtube/soul.md` — đúng 18 dòng có nội dung (msg 1264 đã xong) |
| Channel Brain | ⚠️ **ngoài repo** | `C:\Users\Admin\channel-brain-v1.md` — 206 dòng, đủ 5 section. **Chưa copy vào repo** |
| Prompt #02 nghiên cứu ngách | ✅ | `outputs/competitor_longform/`, `keywords_*.json` |
| Prompt #04 phễu + chăm khán giả | ✅ | `scripts/analyze_blindspots.py` → 11 điểm mù |
| Prompt #07 đối thủ + từ khoá | ✅ | `keywords_main/longtail/title_patterns.json` |
| Prompt #08 30 ý tưởng | ✅ | `outputs/strategy/content_backlog.csv` |
| Prompt #12 kiếm tiền | ✅ | `outputs/strategy/affiliate_funnel.md` |
| Prompt #13 lộ trình | ✅ | `outputs/strategy/MRBEAST_PLAN_ACTION.md` |
| Agent stack + dagu | ✅ | WF01-WF23, WF23 **14/14 succeeded** |
| Dashboard cho team | ✅ | https://dashboard.azzamedu.com (HTTP 200, HTTPS Google CA) |
| Google Drive | ✅ | 32 file / 6 thư mục |

### ❌ CÒN THIẾU — cần làm

| # | Yêu cầu | Trạng thái | Bằng chứng / Ghi chú |
|---|---------|-----------|---------------------|
| 1 | **Prompt #05 đa nền tảng** | ❌ **0 file** | Grep `repurpose/multiplatform/5_format` → không có script nào |
| 2 | **Prompt #06 phân khúc khán giả** | ❌ | 7 file khớp nhưng đều là `segment` kỹ thuật (CapCut/audio), không phải phân khúc khán giả |
| 3 | **Prompt #10 SEO generator** | ❌ | 12 file khớp chỉ là `seo_tags.json` của đối thủ (dữ liệu), chưa có generator |
| 4 | **Prompt #11 thumbnail concept** | ❌ **0 file** | Grep `thumbnail/design_brief` → không có |
| 5 | **Checklist sản xuất 30 ngày** | ❌ | Chỉ có checklist trading/guardrail, không có checklist sản xuất 30 ngày |
| 6 | **Apify bật lại** | ❌ **disabled** | `hermes mcp list` → `apify ✗ disabled` (Alan hỏi 2 lần: msg 1330, 1388) |
| 7 | **chartanimator.io** | ❌ | Chưa tích hợp (Alan yêu cầu msg 1222) |
| 8 | **Mục tiêu 2 ngày/1 video long** | ⚠️ | Chưa có workflow đạt nhịp này |
| 9 | **Git version control** | ❌ **không phải git repo** | `git rev-parse` → `fatal: not a git repository`. Alan yêu cầu VS Code làm cockpit *"xem diff, kiểm soát thay đổi"* — **không git thì không diff được** |
| 10 | **Traffic bot 4,316 views** | 🔴 | 47.9% view 28 ngày — chưa xử lý, chặn mọi tối ưu |

### 🔴 RỦI RO CAO NHẤT

**Repo không có version control.** Alan định vị VS Code là *"cockpit — mở repo, xem diff, duyệt file, kiểm soát thay đổi trước khi đẩy sang external systems"*. Không có git thì:
- Không xem được diff
- Không rollback được khi agent sửa sai
- Không có audit trail cho yêu cầu *"mỗi task phải có audit trail rõ ràng"*

**Khuyến nghị:** `git init` + commit baseline ngay, trước khi làm thêm bất cứ gì.

---

## 11. KPI ALAN ĐẶT RA

Từ chính lời Alan:

| Chỉ số | Mục tiêu | Nguồn |
|--------|----------|-------|
| **Nhịp video long** | 2 ngày / 1 video | msg 1167 |
| **Sub** | tăng | msg 1167 |
| **Like** | tăng | msg 1167 |
| **%xem** | "thứ quyết định độc giả" | msg 1173 |
| **CTR** | đo được, mốc kiểm tra | msg 1195 |
| **Thu nhập** | YPP + Affiliate + Sản phẩm | msg 1167 |
| **Hiệu suất** | giảm thời gian edit | msg 1167 |
| **Build-to-sell** | hệ thống bán được | msg 1167 |

---

## 12. ĐỊNH DẠNG OUTPUT ALAN MUỐN

- **Tiếng Việt** cho tài liệu nội bộ
- **Tiếng Anh** cho nội dung kênh (kênh tiếng Anh)
- **Word + Excel** cho báo cáo giao được (Alan đã quen nhận cả 2)
- **Link online** cho team mở được (không phải file local)
- **Phân tách rõ:** Fact / Inference / Recommendation / Missing Data

---

*Tài liệu này tổng hợp từ 53 tin nhắn của Alan trong thread 13.
Mọi mục tiêu đều trích nguyên văn — không suy diễn thêm.*

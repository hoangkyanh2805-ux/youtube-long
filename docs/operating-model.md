# Operating Model — 1 Brain, 1 Workshop, 1 Cockpit

## 1. Ba lớp vận hành

### Brain — Hermes Agent

Hermes là Orchestrator, không phải nơi giữ toàn bộ state dự án.

- Nhận goal từ Alan.
- Chọn một workflow chính trong `WF01–WF07`.
- Xác định automation level `L0–L4`.
- Tạo Run Record trước khi giao việc.
- Chỉ gọi những Agent cần cho workflow đó.
- Giữ dependency, status và approval gate.
- Không tự sửa hệ thống ngoài, publish hoặc send khi chưa được duyệt.
- Đưa feedback về đúng Source-of-Truth.

`soul.md` chỉ bootstrap identity và hard rules; không lưu project state dài hạn.

### Workshop — Codex

Codex là Builder/Analyst/Auditor làm việc sâu trong `C:\Users\Admin\youtube`.

- Đọc Source-of-Truth và Run Record.
- Kiểm tra input/missing input trước khi làm.
- Tạo plan và artifact local theo quyền L0–L2.
- Sửa file khi task đã giao rõ phạm vi.
- Chạy test, validator và read-back local.
- Gắn nguồn, missing data, owner và next action.
- Không chạy paid/bulk API hoặc external action khi chưa được duyệt.
- Không tự thay đổi workflow, architecture hoặc guardrail ngoài scope task.

### Cockpit — VS Code

VS Code là nơi Alan quan sát và kiểm soát bằng tay.

- Mở repo và xem diff.
- Đọc Run Record và output.
- Duyệt/reject script, backlog, asset, Sheet payload hoặc external action.
- Chạy terminal khi cần.
- Sửa tay khi business context không thể tự động hóa.
- Quyết định khi nào task được chuyển từ local output sang external system.

---

## 2. Source-of-Truth

Theo thứ tự chức năng:

1. `docs/ai-workflow-blueprint.md` — workflow router và contract `WF01–WF07`.
2. `knowledge/prompt-registry.md` — capability/prompt router `P01–P17`.
3. `multi_agent_architecture.md` — Agent ownership và integration boundaries.
4. `docs/aegis-guardrail-checklist.md` — safety gate và stop conditions.
5. `data/workflow_registry.csv` — machine-readable workflow registry.
6. `outputs/runs/` — task state, approval, output và feedback theo từng lần chạy.
7. `soul.md` của Hermes profile — bootstrap identity/hard rules; không phải project database.

Nếu tài liệu mâu thuẫn:

- Guardrail thắng convenience.
- Run Record không được nới quyền vượt Source-of-Truth.
- Số liệu mới phải có evidence; không ghi đè historical fact mà không version/source.
- Alan quyết định ngoại lệ và thay đổi chiến lược.

---

## 3. Protocol bắt buộc cho mọi task

```text
Goal
→ Pick WF
→ Set automation level
→ Create Run Record
→ Assign only required Agents
→ Produce local draft/artifact
→ Guardrail check
→ Human approval when required
→ External action if approved
→ Read-back exact target
→ Feedback/Memory update
```

### No Five, No Run

Không cho Agent bắt đầu nếu Run Record chưa có đủ năm trường:

1. `Workflow` — phải là `WF01–WF07`.
2. `Automation level` — phải là `L0–L4`.
3. `Owner` — một owner chịu trách nhiệm chính.
4. `Human approval required/status` — approval gate rõ ràng.
5. `Output paths` — đường dẫn dự kiến hoặc target cụ thể.

Ngoài năm trường trên, Run Record phải ghi Goal, Inputs, Missing inputs, Tools allowed, Guardrail result, Read-back và Feedback.

---

## 4. Automation Levels

### L0 — Propose only

Hermes/Codex chỉ đề xuất; không tạo artifact vận hành và không thay đổi file.

### L1 — Read and analyze

Được đọc file, API public và dữ liệu được cấp; tạo phân tích tạm thời/read-only.

### L2 — Local write

Được tạo/sửa file local trong `C:\Users\Admin\youtube` theo Run Record; phải test và ghi output path.

### L3 — Approved external action

Bao gồm:

- Google Sheet write/sync.
- Telegram send/broadcast.
- YouTube publish.
- Thay title/thumbnail/description trên video public.
- Sales CTA, affiliate placement hoặc offer launch.
- Paid/bulk API job.

Bắt buộc `Human approval status: APPROVED`, sau đó read-back exact target.

### L4 — Prohibited automation

- Execute trade.
- Claim/guarantee lợi nhuận.
- Seeding giả.
- Lộ secret.
- Xóa dữ liệu lớn/destructive rewrite.
- Làm giả trade, backtest, testimonial hoặc performance.

---

## 5. Workflow → Active Team

### WF01 — New Topic → Published Video

- `youtube_data`
- `youtube_workflow`
- `content_bridge`
- `platform_ux`
- `integration_qa`
- `aegis_guardrail`

### WF02 — Competitor/Keyword → Backlog

- `youtube_data`
- `youtube_workflow`
- `content_bridge`

Paid/bulk transcript cần approval trước khi gọi.

### WF03 — Long Video → Shorts/Remake/Thumbnail

- `youtube_workflow`
- `content_bridge`
- Editor người thật
- `platform_ux`

### WF04 — Upload → Funnel Optimization

- `youtube_data`
- `hermes_dashboard`
- `integration_qa`
- `aegis_guardrail`

Publish hoặc đổi metadata public là L3.

### WF05 — Comment → Audience Insight

- `telegram_gateway`
- Community Assistant
- `content_bridge`
- `security`

Reply nhạy cảm, sales CTA hoặc external send là L3.

### WF06 — Audience → Lead → Offer

- `founder_ops`
- `learning_tutor`
- `telegram_gateway`
- `security`

Pricing, launch, broadcast và affiliate placement là L3.

### WF07 — Weekly Review → Improvement

- Hermes Orchestrator
- `founder_ops`
- `hermes_dashboard`
- `security`
- `integration_qa`
- `aegis_guardrail`

---

## 6. Handoff Contract

### Hermes → Codex

Hermes phải cung cấp:

- Goal.
- WF-ID.
- Automation level.
- Owner và supporting Agents.
- Inputs/missing inputs.
- Output paths.
- Approval gate.
- Stop conditions.

### Codex → Hermes/Alan

Codex phải trả:

- Files changed/created.
- Test/validation result thật.
- Missing data và blocker.
- Guardrail result.
- External action cần approval hay không.
- Next action/owner.

### Alan/VS Code → Hermes

Alan trả một trong bốn quyết định:

- `APPROVED` — được chạy đúng external action đã mô tả.
- `REVISION_REQUIRED` — quay lại local draft.
- `REJECTED` — dừng task.
- `HOLD` — giữ artifact, không chạy tiếp.

Approval chỉ áp dụng cho đúng target, scope và payload trong Run Record; không phải quyền mở rộng.

---

## 7. Run Record Storage

Tên file chuẩn:

```text
outputs/runs/RUN-YYYYMMDD-WFNN-short-slug.md
```

Mỗi Run Record là state nhỏ, có thể audit và không phụ thuộc toàn bộ conversation history.

Validator:

```bash
python scripts/validate_run_record.py outputs/runs/RUN-YYYYMMDD-WFNN-short-slug.md
```

Kiểm tra tất cả Run Record:

```bash
python scripts/validate_run_record.py outputs/runs
```

---

## 8. Example Route — Competitor Backlog

Yêu cầu: “Làm backlog video từ đối thủ.”

### Hermes

- Route: `WF02`.
- Mode: `L1/L2`.
- Owner: `youtube_workflow`.
- Supporting: `youtube_data`, `content_bridge`.
- Approval: cần nếu gọi paid/bulk transcript.
- Output: competitor report, keyword gap, priority backlog.

### Codex

- Đọc input trong repo.
- Verify đúng `@azzammastertradinggold` và `@GoldTraderAlliance`.
- Tạo report local.
- Không gọi paid/bulk service khi chưa duyệt.
- Gắn source, missing data, owner và next action.

### Alan/VS Code

- Xem diff và report.
- Chọn top backlog.
- Nếu muốn sản xuất, tạo Run Record mới và chuyển sang `WF01`.

---

## 9. Definition of Done

Task hoàn thành khi:

- Run Record hợp lệ.
- Artifact thật tồn tại tại output path.
- Test/validator pass hoặc lỗi được ghi rõ.
- Guardrail result rõ ràng.
- L3 có approval và read-back.
- Feedback được đưa về đúng nơi.
- Không dùng chat hoặc `soul.md` làm project state dài hạn.

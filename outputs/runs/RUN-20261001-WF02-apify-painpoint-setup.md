# RUN-20261001-WF02-apify-painpoint-setup

- Goal: Thiết lập Apify MCP ở chế độ actor allowlist và pipeline local comments → pain-point candidates cho YouTube, TikTok, Instagram và Facebook.
- Workflow: WF02
- Automation level: L2
- Owner: youtube_data
- Supporting agents: youtube_workflow, content_bridge, integration_qa, aegis_guardrail
- Status: RUNNING
- Inputs: `docs/operating-model.md`; `docs/ai-workflow-blueprint.md`; yêu cầu của Alan; Apify MCP documentation.
- Missing inputs: `APIFY_TOKEN` chưa hiện diện trong project/profile environment; chưa có source URL/account list được duyệt; chưa có ngân sách/bulk-run approval.
- Tools allowed: Đọc file; tạo/sửa file local; cấu hình MCP local; chạy unit test; test kết nối không scrape; API public khi không phát sinh paid/bulk action.
- Tools prohibited: Chạy paid/bulk Actor; scrape nguồn riêng tư; publish; sửa Google Sheet; gửi Telegram; lưu token trong source/config/Run Record.
- Guardrail result: PASS_WITH_BLOCKER — được setup local; không được chạy Actor trước khi token và scope được duyệt.
- Human approval required: YES — trước mọi paid/bulk scrape và trước khi dùng dữ liệu cho outbound/publish.
- Human approval status: PENDING
- Output paths: `scripts/apify_mcp_launcher.py`; `scripts/extract_painpoints.py`; `data/schemas/social_comment.schema.json`; `docs/apify-painpoint-pipeline.md`; `tests/test_extract_painpoints.py`.
- External action: NONE — setup local only.
- External action read-back: NOT_REQUIRED — chưa có external write.
- Evidence: Sẽ ghi sau test và MCP registration.
- Feedback destination: `channel-brain-v1.md` chỉ sau human review; candidate backlog local trước.
- Next owner/action: Alan cung cấp token an toàn và duyệt platform/source/giới hạn Actor; Hermes chạy smoke scrape nhỏ sau approval. Tạo tool, registry, pipeline và test local; không scrape.

## Agent assignments

- youtube_data: MCP launcher, schema, normalization.
- content_bridge: pain-point candidate taxonomy/report.
- integration_qa: unit test và Run Record validator.
- aegis_guardrail: token, privacy, paid/bulk gate.

## Validation

- Command/check: Pending.
- Result: Pending.

## Approval log

- 2026-10-01 15:52 +07: Alan yêu cầu kiểm tra runtime và thêm Apify để cào comments/pain points; chưa phê duyệt paid/bulk scrape cụ thể.

## Feedback

- Pending after validation and first approved smoke run.

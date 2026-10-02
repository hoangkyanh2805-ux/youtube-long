# Azzam YouTube — Operating Cockpit

Trang điều khiển trung tâm. Mở dagu UI tại **http://127.0.0.1:8080** và chọn tab **Wiki**.

---

## Wiki pages

| Trang | Nội dung |
|-------|----------|
| **analytics** | Analytics riêng tư (OAuth) + traffic + nguồn bot + **11 điểm mù** + số liệu 2 kênh |
| **index** (trang này) | Nút bấm, topic Telegram, quy tắc, lệnh hay dùng |

---

## Bấm chạy nhanh

| Workflow | Việc nó làm | Lịch tự động |
|----------|-------------|--------------|
| **WF22-daily-with-approval-gate** | Cào comment → chấm điểm → gửi pain point chờ duyệt → **DỪNG chờ Alan duyệt** → duyệt xong gửi brief cho editor | **7:30 mỗi ngày** |
| **WF23-publish-dashboards** | Refresh analytics thật + ops cockpit → cập nhật Wiki | **8:00 mỗi ngày** |
| **WF20-daily-content-pipeline** | Bản không có approval gate (chạy thẳng) | 7:30 mỗi ngày |
| **WF21-weekly-review** | Rebuild báo cáo + tổng kết tuần | **9:00 thứ Hai** |
| **WF12-pipeline-health** | Kiểm tra MCP backend, dữ liệu, dashboard | chạy tay |
| **WF11-content-brief-to-editor** | Chỉ gửi brief sang topic EDIT | chạy tay |
| **WF10-daily-comment-to-approval** | Chỉ cào comment + báo cáo | chạy tay |

**Lưu ý:** WF20 và WF22 cùng lịch 7:30 — chỉ nên bật một. WF22 có approval gate (an toàn hơn).

---

## Approval gate hoạt động thế nào

Khi WF22 chạy tới bước duyệt, run có status **`waiting`**:

1. Vào dagu UI → thấy WF22 đang `waiting`
2. Mở run → đọc form duyệt
3. Chọn `decision = approve` hoặc `reject`, ghi chú nếu cần
4. Bấm complete → pipeline tiếp tục gửi brief cho editor
5. Hoặc dùng **push-back** để trả về bước rebuild kèm feedback

---

## 2 topic Telegram

| Topic | Thread | Ai dùng | Nhận gì |
|-------|--------|---------|---------|
| **COMMENT** | 206 | **Alan duyệt** | Top pain point mới + link nguồn → chốt content |
| **EDIT** | 205 | **Editor làm** | Brief 3 Short + 1 Long, hook, CTA, quy trình |
| GENERAL | 2 | Alan | Health pipeline + tổng kết tuần |

Luồng: **COMMENT (duyệt) → EDIT (làm)** → đăng → báo cáo về **GENERAL**.

---

## Dashboard

| Dashboard | Đường dẫn | Nội dung |
|-----------|-----------|----------|
| Analytics (data thật) | `outputs/dashboard/youtube-analytics-real.html` | Subs/views 2 kênh, watch time, retention, traffic, địa lý |
| Ops cockpit | `outputs/dashboard/ops.html` | Analytics + **điểm mù** + 7 kiểm tra + 3 topic + 8 bước + top pain + backlog |
| Snapshot JSON | `outputs/dashboard/analytics_snapshot.json` | Số liệu dạng máy đọc |
| Báo cáo Analytics + Điểm mù | `outputs/reports/AZZAM_ANALYTICS_DIEM_MU.docx` / `.xlsx` | Word (đọc) + Excel 10 sheet (lọc) |
| Báo cáo đối thủ & chiến lược | `outputs/reports/AZZAM_BAOCAO_PHAN_TICH_DOI_THU.docx` / `.xlsx` | SOP, sales angles, SEO |

dagu **không nhúng được HTML local vào UI** — số liệu nằm ở Wiki page **analytics**, file HTML mở trực tiếp bằng browser.

---

## 📊 Dashboard — LINK CỐ ĐỊNH

**Trang điểm vào duy nhất — mở được từ mọi nơi:**

```
🌐 https://dashboard.azzamedu.com
```

| Trang | Link |
|-------|------|
| **Report Hub (chính)** | https://dashboard.azzamedu.com |
| Ops cockpit | https://dashboard.azzamedu.com/ops.html |
| Analytics dashboard | https://dashboard.azzamedu.com/youtube-analytics-real.html |
| Evergreen plan (CSV) | https://dashboard.azzamedu.com/data/EVERGREEN_PLAN.csv |

**Báo cáo Word/Excel** → https://drive.google.com/drive/folders/1AzIiixGpZ4miW7ht7snpz7D5-4RZDycc

**Hạ tầng:** Cloudflare Pages (project `azzam-reports`) + CNAME `dashboard` ở iNET.
HTTPS: Google Trust Services, hết hạn 31/12/2026. Link **cố định**, không phụ thuộc máy nào.

**Local (chỉ máy Alan):** `outputs/dashboard/REPORT_HUB.html`

**Deploy:** `python scripts/deploy_to_cloudflare.py --apply` (nằm trong WF23, tự chạy 8:00/ngày)

---

## 🌱 Evergreen là gì — ưu tiên số 1

**Evergreen** = video còn mang view **nhiều tháng/năm sau khi đăng**. Khác Short
(hết view sau vài ngày) và livestream (chỉ có view lúc phát).

| | Short | Livestream | **Evergreen 5-8 phút** |
|---|---|---|---|
| Vòng đời view | 3-7 ngày | 1-2 giờ | **nhiều tháng/năm** |
| Nguồn view | Shorts feed | thông báo | **Search + đề xuất** |
| Tái dùng | không | không | **có** |
| Bán offer | kém | kém | **tốt** |
| Kênh mình | 141 video, median 46 | 141 video, TB 102 | **15 video, TB 6** |
| Đối thủ | 340, median 845 | 328, TB 2,873 | **31, TB 395** |

**Khoảng cách 66×** — và chỉ **1.2%** traffic kênh đến từ search YouTube.

**Kế hoạch: 24 video, 2/tuần × 12 tuần** — **18/24 chủ đề đối thủ CHƯA làm**.
Chủ đề lấy từ 500 long-tail phrase mine từ 7,937 comment thật.

| File | Nội dung |
|------|----------|
| `outputs/strategy/EVERGREEN_PLAN.csv` | 24 video, 18 cột (title, hook, outline, keyword, evidence) |
| `outputs/strategy/EVERGREEN_PLAN.md` | Chi tiết từng video |
| `outputs/reports/AZZAM_EVERGREEN_PLAN.docx` | Word |
| `outputs/reports/AZZAM_EVERGREEN_PLAN.xlsx` | 6 sheet: plan, từ khoá nguồn, pattern đối thủ, mẫu, lịch 12 tuần |

---

## ⚠ Cảnh báo đang mở — cần xử lý

**Traffic nghi bot:** 4,316 views (47.9% tổng view 28 ngày) đến từ referrer
`com.example.seofast` / `com.playzero.playbotsseofast` — không phải site thật.
Ngày 29/09 có 8,153 views trong khi trung vị các ngày khác chỉ ~35.

Đây là dấu hiệu **view mua/view farm**. YouTube có thể xoá view hoặc phạt kênh
theo Fake Engagement Policy. **Cần điều tra nguồn gốc trước khi làm gì khác.**

Chi tiết: Wiki page **analytics** → mục "Điểm mù", hoặc
`outputs/reports/blindspots.md`.

---

## 🧬 Audit MrBeast — điểm 3.1/10

Xem topic **AUDIT** (thread 239) trên Telegram, hoặc tài liệu trong repo:

| Tài liệu | Nội dung |
|----------|----------|
| `outputs/reports/MRBEAST_AUDIT.md` | Chẩn đoán: 4 vấn đề + điểm mạnh + bảng điểm |
| `outputs/strategy/MRBEAST_PLAN_ACTION.md` | Plan 90 ngày, 4 giai đoạn, bảng KPI |
| `outputs/strategy/MRBEAST_SOP.md` | SOP 8 bước hằng ngày + lịch + QC |
| `outputs/strategy/MRBEAST_BUILD_TO_SELL.md` | Lộ trình 12 tháng + hồ sơ bán kênh |
| `outputs/reports/AZZAM_MRBEAST_AUDIT.docx` | Word — 4 phần, 30 bảng |
| `outputs/reports/AZZAM_MRBEAST_AUDIT.xlsx` | Excel — 8 sheet |

**3 phát hiện quyết định:**

1. **Long-form gần như không hoạt động** — 156 video TB **102** views vs đối thủ
   400 video TB **2,523** views (**24.7×**). Nguyên nhân: 90% là livestream.
2. **Không có evergreen** — 15 video 1-10 phút TB **6** views vs đối thủ
   31 video TB **395** views (**66×**). Khớp với chỉ 1.2% traffic từ search.
3. **Tương tác bằng 0** — comment rate 0.0111%, sub ròng **-3**.

**5 hành động ưu tiên:**
1. Điều tra 4,316 views nghi bot (trước mọi thứ)
2. Evergreen 5-8 phút, 2 video/tuần
3. Tái chế 110 phiên live dài thành video biên tập
4. Khôi phục format FOREX LESSON (Short 8-21s)
5. CTA comment + trả lời mọi comment

---

## Số liệu hiện tại

Xem trang **analytics** để có số mới nhất. Tóm tắt:

**Kênh mình (28 ngày: 02/09 → 30/09):**
- Views: **9,016** · Watch time: **228.5 giờ** · View trung bình: **98s**
- Sub: **+5 / -8 = -3** (ròng âm) · Sub conversion: **0.055%** (ngành 0.5–2%)
- Likes **901** · Comments **1** · Comment rate **0.0111%**
- Tích luỹ: **1,980 subs** · 242,480 views · 297 video

**Đối thủ Gold Trader Alliance:** **14,100 subs** · 1,404,476 views · 740 video
(→ hơn kênh mình **7.1×** về sub)

**Nguồn dữ liệu:** YouTube Data API v3 (public) + YouTube Analytics API (OAuth, private)

**Pipeline:** Comment unique: **5,843** · Pain point: **1,259** · Sales angles: **8** ·
Content backlog: **16** · KPI: **3 Short + 1 Long 8 phút / ngày** (tiếng Anh)

---

## Quy tắc bắt buộc

1. **Guardrail chặn đăng:** không cam kết lợi nhuận, không trade giả. Vi phạm → không đăng.
2. **Telegram cần approval:** mọi lệnh gửi phải có `--approve APPROVE`.
3. **Editor không tự đăng** — Alan duyệt trước.
4. **Không dùng tài khoản ảo để seeding** — vi phạm Fake Engagement Policy, có thể bị xoá kênh.
5. **MCP backend phải chạy** trước khi dựng video: `python tools/VectCutAPI/capcut_server.py`

---

## Lệnh hay dùng

```
# Khởi động UI — BẮT BUỘC dùng script này
python scripts/start_dagu.py
python scripts/start_dagu.py --status
python scripts/start_dagu.py --stop

# Sync workflow mới vào UI
python scripts/sync_dagu_workflows.py

# Cập nhật số liệu + Wiki
python scripts/refresh_youtube_analytics_dashboard.py
python scripts/analyze_blindspots.py
python scripts/build_ops_dashboard.py
python scripts/build_analytics_report.py
python scripts/publish_dashboards_to_ui.py

# Gửi báo cáo tay
python scripts/telegram_reporter.py --report comment
python scripts/telegram_reporter.py --report content_brief
python scripts/telegram_reporter.py --report pipeline_health

# Gửi thật (cần approval)
python scripts/telegram_reporter.py --report content_brief --send --approve APPROVE
```

**Quan trọng:** luôn dùng `python scripts/start_dagu.py`. Flag `--dagu-home` **KHÔNG hoạt động** — chỉ biến môi trường `DAGU_HOME` mới redirect đúng data dir. Dùng sai sẽ khiến workflow kẹt ở `queued` mãi mãi.

---

## Còn thiếu

- [ ] Telegram community invite link (cho CTA trong video) — đang placeholder
- [ ] Master template CapCut (Short 9:16 + Long 16:9)
- [ ] Asset library đổ file thật (qua MCP driver Google)

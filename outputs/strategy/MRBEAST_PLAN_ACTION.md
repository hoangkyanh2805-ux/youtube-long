# PLAN ACTION — 90 NGÀY

*Sinh: 2026-10-02 09:27 UTC*  •  Kênh: @azzammastertradinggold

Mục tiêu: chuyển kênh từ **3.1/10** sang **6/10** trong 90 ngày, với KPI đo được. Mọi hành động dưới đây đều bám vào số liệu ở `MRBEAST_AUDIT.md`.

---

## GIAI ĐOẠN 0 — TUẦN 1: DỌN ĐƯỜNG (bắt buộc trước mọi thứ)

| # | Hành động | Owner | KPI | Bằng chứng hoàn thành |
|---|---|---|---|---|
| 0.1 | **Điều tra traffic bot 4,316 views** — xác định nguồn `seofast`/`playbots` từ đâu. Kiểm tra: có ai mua view? dịch vụ SEO nào? | Alan | Xác định được nguồn | Ghi rõ trong `outputs/reports/blindspots.md` |
| 0.2 | **Dừng mọi nguồn traffic trả phí** nếu phát hiện có mua view | Alan | Không còn referrer lạ | Analytics 7 ngày sau sạch |
| 0.3 | Bật Publish app trên Google Cloud → token OAuth không hết hạn 7 ngày | Alan | Token vĩnh viễn | `yt_oauth_login.py --check` pass |
| 0.4 | Bật CapCut MCP backend (port 9001) | Alan | MCP chạy | WF12 pipeline health xanh hết |

**Gate:** không làm gì ở Giai đoạn 1-3 nếu 0.1 chưa xong. Tối ưu trên nền số liệu ảo là vô nghĩa.

---

## GIAI ĐOẠN 1 — TUẦN 2-4: SỬA NỘI DUNG CỐT LÕI

### 1A. Khôi phục format FOREX LESSON (Short)

**Căn cứ:** chuỗi này đã thắng thật — 117 video, nhiều video 1,400-9,800 views. Độ dài 8-21 giây.

| # | Hành động | KPI |
|---|---|---|
| 1A.1 | Sản xuất lại 30 Short FOREX LESSON, **bám sát 2 công thức đã thắng**: độ dài 8-21s, tiêu đề `FOREX LESSON #N + [chủ đề]` | 30 video / 4 tuần |
| 1A.2 | Mỗi Short phải có hook trong **3 giây đầu** — hiển thị câu hỏi hoặc con số ngay frame 1 | 100% video |
| 1A.3 | Giữ độ dài **≤21 giây** (Short thắng TB 14s, thua 21s) | median ≤18s |
| 1A.4 | Đo lại sau 30 ngày: median views/short phải **>200** (hiện tại 46) | median >200 |

### 1B. Tạo dòng EVERGREEN 1-10 phút (ưu tiên cao nhất)

**Căn cứ:** đây là khoảng cách lớn nhất — kênh mình 15 video TB 6 views, đối thủ 31 video TB 395 views (**66×**).

| # | Hành động | KPI |
|---|---|---|
| 1B.1 | Sản xuất **2 video/tuần, độ dài 5-8 phút**, KHÔNG phải livestream | 8 video / 4 tuần |
| 1B.2 | Chủ đề theo format "How to" — đối thủ dùng format này 81 lần, TB 728 views | 100% dùng tiêu đề dạng how-to |
| 1B.3 | Mỗi video phải trả lời **1 câu hỏi cụ thể** người mới hay hỏi | 1 câu hỏi / video |
| 1B.4 | Đo lại sau 30 ngày: TB views/video evergreen **>100** (hiện tại 6) | TB >100 |

**Chủ đề lấy từ dữ liệu thật** — câu hỏi khán giả đã cào được (984 comment có dấu hỏi trong 7,937 comment):

- "What is the best paper trading account you have been using?"
- "What would you suggest for a beginner? Go through those videos first or start from here?"
- "Can you suggest the order to watch these videos?"
- "I'm a beginner and I can frame a daily bias this way but how exactly to trade with this?"
- "Where is the PDF?" / "I need this PDF" — nhu cầu tài liệu rất rõ

### 1C. Cắt giảm livestream, chuyển thành nội dung biên tập

| # | Hành động | KPI |
|---|---|---|
| 1C.1 | Giảm livestream từ 90% long-form xuống **≤50%** | Đo lại cơ cấu sau 30 ngày |
| 1C.2 | **Tái chế livestream thành video ngắn có biên tập**: cắt 1 phiên live 8 giờ thành 3-5 clip 5-8 phút theo chủ đề (1 setup, 1 phân tích, 1 bài học) | 3-5 video / phiên live |
| 1C.3 | Video cắt lại phải có **thumbnail + title riêng**, không dùng tên livestream | 100% video |

**Đây là đòn bẩy lớn nhất về mặt thời gian:** kênh đã có 110 phiên live dài. Đó là kho nguyên liệu chưa khai thác — không cần quay mới.

---

## GIAI ĐOẠN 2 — TUẦN 5-8: PACKAGING + CỘNG ĐỒNG

### 2A. Sửa packaging theo công thức đối thủ

| Yếu tố | Kênh mình | Đối thủ | Hành động |
|---|---|---|---|
| Emoji trong title | 35% | 46% | Tăng lên ≥50% |
| Năm trong title | 6% | 51% | Thêm năm vào video có yếu tố thời sự |
| CAPS >50% | 13% | 50% | Dùng cho video cảnh báo/tin nóng |
| Có số trong title | 91% | 57% | Giữ (đang tốt) |
| Độ dài title | 64 ký tự | 60 ký tự | Rút xuống ≤60 |

### 2B. Xây cộng đồng — sửa comment rate từ 0.0111%

| # | Hành động | KPI |
|---|---|---|
| 2B.1 | **CTA comment từ khoá** trong mọi video: "Comment ENTRY if you want the checklist" | 100% video có CTA |
| 2B.2 | **Trả lời mọi comment trong 2 giờ đầu** sau khi đăng | Response rate >90% |
| 2B.3 | Pinned comment trên mỗi video với câu hỏi mở | 100% video |
| 2B.4 | Đo lại sau 30 ngày: comment rate **>0.1%** (hiện 0.0111%) | >0.1% |
| 2B.5 | Sub ròng phải **dương** | >+20 sub/tháng |

**Ranh giới chính sách — KHÔNG được vượt:** chỉ dùng pinned comment / Community post / trả lời thật trên kênh mình. Không tạo tài khoản ảo, không mua like/view/comment, không rải link lên kênh người khác.

---

## GIAI ĐOẠN 3 — TUẦN 9-12: PHỄU + ĐO LƯỜNG

| # | Hành động | KPI |
|---|---|---|
| 3.1 | Xây phễu: Short (thu hút) → Evergreen (giữ chân) → Telegram (lead) → Offer (chuyển đổi) | 4 tầng hoạt động |
| 3.2 | CTA dẫn Telegram trong mọi video (hiện chưa có link thật) | 100% video |
| 3.3 | Đo conversion từng tầng | Báo cáo tuần |
| 3.4 | Đánh giá lại toàn bộ: điểm MrBeast phải **≥6/10** | ≥6/10 |

---

## BẢNG KPI TỔNG — ĐO ĐƯỢC

| Chỉ số | Hiện tại | Ngày 30 | Ngày 60 | Ngày 90 |
|---|---|---|---|---|
| Median views/Short | 46 | 200 | 400 | 700 |
| TB views/video evergreen | 6 | 100 | 250 | 400 |
| Comment rate | 0.0111% | 0.05% | 0.1% | 0.15% |
| Sub ròng/tháng | -3 | +20 | +60 | +120 |
| Sub conversion | 0.055% | 0.15% | 0.3% | 0.5% |
| Tỷ lệ traffic từ search | 1.2% | 4% | 8% | 12% |
| Video evergreen/tuần | 0 | 2 | 2 | 3 |
| Tỷ lệ long-form là livestream | 90% | 70% | 60% | 50% |

**Nguyên tắc đo:** mọi chỉ số lấy từ `analytics_latest.json` (OAuth) hoặc `azzam_videos.json` (Data API) — không nhập tay. Chạy `scripts/analyze_blindspots.py` mỗi tuần để cập nhật.

---

## 5 HÀNH ĐỘNG ƯU TIÊN CAO NHẤT (nếu chỉ làm được 5 việc)

1. **Điều tra 4,316 views nghi bot** — mọi thứ khác vô nghĩa nếu số liệu nền là giả.
2. **Tạo dòng evergreen 5-8 phút, 2 video/tuần** — khoảng cách 66× với đối thủ, đây là chỗ trống lớn nhất.
3. **Tái chế 110 phiên live dài thành video biên tập** — kho nguyên liệu miễn phí, không cần quay mới.
4. **Khôi phục format FOREX LESSON** (Short 8-21s) — format duy nhất từng thắng lặp lại.
5. **CTA comment + trả lời mọi comment** — sửa comment rate từ 0.0111%, mở lại phễu cộng đồng.

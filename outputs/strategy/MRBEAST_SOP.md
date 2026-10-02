# SOP TRIỂN KHAI — QUY TRÌNH SẢN XUẤT HẰNG NGÀY

*Sinh: 2026-10-02 08:57 UTC*  •  Kênh: @azzammastertradinggold  •  Ngôn ngữ: ENGLISH

**Ngưỡng kiểm tra SOP:** nếu editor hiện tại nghỉ hôm nay, người mới đọc tài liệu này có chạy được 3 Short + 1 Long trong ngày đầu không? Nếu không, SOP chưa đủ tốt.

---

## 1. CƠ CẤU NỘI DUNG MỚI (thay cho cơ cấu cũ)

| Loại | Số lượng/ngày | Độ dài | Mục đích | Nguồn |
|---|---|---|---|---|
| Short FOREX LESSON | 2 | 8-21s | Thu hút, tăng sub | Quay mới |
| Short tái chế từ live | 1 | 15-40s | Tận dụng kho có sẵn | Cắt từ livestream |
| Evergreen how-to | 1 (cách ngày) | 5-8 phút | SEO, giữ chân, bán offer | Quay mới hoặc biên tập từ live |

**Thay đổi then chốt:** cơ cấu cũ là 3 Short + 1 Long-livestream (90% long-form là livestream 8-13 giờ, TB 102 views). Cơ cấu mới bỏ long-form livestream khỏi slot sản xuất, thay bằng evergreen 5-8 phút.

---

## 2. QUY TRÌNH 8 BƯỚC MỘT NGÀY

### Bước 1 — Lấy nguyên liệu (10 phút, đầu ngày)

```bash
# Comment + pain point mới nhất
python scripts/competitor_longform_scrape.py
python scripts/extract_painpoints.py outputs/competitor_longform/raw_comments.json --output-dir outputs/competitor_longform --actor youtube-data-api-v3/commentThreads.list

# Danh sách pain point chờ duyệt
python scripts/build_ops_dashboard.py
```

Mở `outputs/dashboard/ops.html` → xem "Top pain point — chờ duyệt".

### Bước 2 — Chốt hook (10 phút)

Chọn **3 pain point** từ danh sách trên. Mỗi cái thành 1 Short.

**Quy tắc chọn hook:**
- Phải là **nỗi đau cụ thể**, không phải lời cảm ơn ("you changed my life" → loại)
- Phải trả lời được trong **8-21 giây**
- Phải có **1 hành động cụ thể** người xem làm được ngay

### Bước 3 — Draft script (15 phút, AI hỗ trợ)

Dùng `prompts/02_VIET_HOOK.md`. Yêu cầu với AI:

```
Viết script Short 8-21 giây cho kênh XAUUSD/Forex.
Hook: [pain point đã chọn]

RÀNG BUỘC:
- Hook phải trong 3 giây đầu, dạng câu hỏi hoặc con số
- Không cam kết lợi nhuận, không nói 'guaranteed', 'always wins'
- Không hiển thị kết quả trade giả
- Kết bằng CTA: 'Comment ENTRY for the checklist'
```

### Bước 4 — Dựng draft bằng CapCut MCP (20 phút)

```bash
# Bắt buộc: MCP backend phải chạy trước
python tools/VectCutAPI/capcut_server.py
```

Xem `prompts/07_CAPCUT_MCP.md`. MCP dựng draft, editor chỉ polish — KHÔNG dựng từ đầu.

### Bước 5 — Polish trong CapCut Pro (30 phút / 3 Short)

**Checklist polish:**
- [ ] Hook hiện trong 3 giây đầu (có text trên màn hình)
- [ ] Độ dài ≤21s cho Short FOREX LESSON
- [ ] Phụ đề đúng chính tả (tối ưu mobile — 94% view là mobile)
- [ ] Logo/lower-third theo brand asset có sẵn
- [ ] Không có chart mô phỏng trình bày như trade thật

### Bước 6 — Packaging (10 phút)

**Công thức tiêu đề (từ dữ liệu đối thủ):**

| Yếu tố | Bắt buộc |
|---|---|
| Độ dài | ≤60 ký tự |
| Emoji | Có (đối thủ dùng 46%) |
| Năm | Thêm nếu video thời sự (đối thủ 51%) |
| Số | Có nếu có con số cụ thể |
| Từ khoá | `XAUUSD`, `gold`, `forex` phải có |

**Mẫu đã kiểm chứng từ chính kênh mình:**
```
FOREX LESSON #N: [CHỦ ĐỀ NGẮN] 2026 #xauusd #trading #shorts
How to [làm gì] in [thời gian] | XAUUSD Trading
```

### Bước 7 — QC 8 điểm (5 phút, BẮT BUỘC)

| # | Kiểm tra | Nếu vi phạm |
|---|---|---|
| 1 | Không cam kết lợi nhuận | **KHÔNG ĐĂNG** |
| 2 | Không có trade giả/chart mô phỏng như thật | **KHÔNG ĐĂNG** |
| 3 | Có disclaimer: *Not financial advice. Trading involves risk of loss.* | Thêm trước khi đăng |
| 4 | Hook trong 3 giây đầu | Sửa lại |
| 5 | Độ dài đúng spec | Sửa lại |
| 6 | Title ≤60 ký tự | Sửa lại |
| 7 | Phụ đề đúng chính tả | Sửa lại |
| 8 | CTA có mặt | Thêm vào |

**Editor không tự đăng.** Alan duyệt xong mới đăng.

### Bước 8 — Tương tác sau đăng (15 phút, cuối ngày)

| # | Việc | Thời hạn |
|---|---|---|
| 8.1 | Trả lời **mọi comment** | trong 2 giờ đầu |
| 8.2 | Đăng pinned comment có câu hỏi mở | ngay sau đăng |
| 8.3 | Trả lời comment có từ khoá CTA | trong ngày |

**Đây là bước sửa comment rate 0.0111%.** Không làm bước này thì mọi việc khác đều vô nghĩa.

---

## 3. LỊCH MỘT NGÀY

| Giờ | Việc | Thời lượng |
|---|---|---|
| Sáng sớm | Bước 1-2: lấy nguyên liệu + chốt hook | 20 phút |
| Sáng | Bước 3-4: draft script + MCP dựng draft | 35 phút |
| Trưa | Bước 5: polish 3 Short (làm liền nhau, không đổi tư duy) | 30 phút |
| Chiều | Evergreen: quay/biên tập 5-8 phút (cách ngày) | 60 phút |
| Chiều | Bước 6-7: packaging + QC | 15 phút |
| Tối | Bước 8: tương tác comment | 15 phút |

**Tổng: ~2h55/ngày** (ngày có evergreen), ~1h55 (ngày không). Có buffer so với trần 4.6h đã tính trước đó.

**Nguyên tắc gom việc:** 3 Short dựng liền nhau để không đổi tư duy. Việc cần tập trung cao (evergreen) đặt lúc năng lượng tốt. Tương tác để cuối ngày.

---

## 4. QUY TẮC TÀI NGUYÊN — 0-SEARCH

Tìm b-roll/nhạc/chart là khâu ngốn thời gian nhất. Quy tắc:

1. **KHÔNG BAO GIỜ tìm tài nguyên trong lúc dựng.** Mọi thứ phải có sẵn trong `assets/`.
2. **Tài nguyên mới nhập vào thư viện NGAY khi tải về**, không để riêng lẻ.
3. Cấu trúc `assets/` 25 thư mục đã có — dùng đúng chỗ, không tạo mới.

**Template tái sử dụng:** 1 template Short 9:16 + 1 template Long 16:9, dựng một lần dùng cho hàng trăm video. Đây là thứ tiết kiệm nhiều thời gian nhất.

---

## 5. PHÂN CÔNG AI vs NGƯỜI

| Việc | Ai làm |
|---|---|
| Cào comment, chấm điểm pain point | **AI** |
| Draft script, hook, SEO, phụ đề | **AI** |
| Dựng draft CapCut | **AI (MCP)** |
| Polish, quyết định sáng tạo | **Người** |
| Thumbnail | **Người** |
| QC + duyệt đăng | **Người (Alan)** |
| Tương tác comment | **Người** |

**Ranh giới cứng:** AI không cắt ghép video cuối, không làm thumbnail, không tự đăng.

---

## 6. BÀN GIAO — 8 TIÊU CHÍ BUILD-TO-SELL

| # | Tiêu chí | Trạng thái | Căn cứ |
|---|---|---|---|
| 1 | Tài liệu hoá, không nằm trong đầu 1 người | ✅ | SOP này + prompts/ + skills |
| 2 | Tài sản tái sử dụng | ⚠ | assets/ + template có; template CapCut chưa dựng |
| 3 | Không phụ thuộc cá nhân | ⚠ | SOP đủ, nhưng editor chưa được test với người mới |
| 4 | Đo lường được từng công đoạn | ✅ | KPI bảng trong PLAN_ACTION + analytics OAuth |
| 5 | Tự động hoá phần lặp (≥40%) | ✅ | dagu WF22/WF23 tự chạy 7:30 và 8:00 |
| 6 | Tài sản nội dung tích luỹ | ❌ | 90% long-form là livestream, không có evergreen |
| 7 | Quy trình chuyển giao được | ✅ | Trong repo, có git |
| 8 | Chất lượng kiểm soát được | ✅ | QC 8 điểm + guardrail |

**Điểm: 5.5/8.** Hai điểm yếu cần xử lý: (a) tài sản nội dung tích luỹ — giải quyết bằng dòng evergreen 1-10 phút; (b) tài sản tái sử dụng — cần dựng template CapCut.

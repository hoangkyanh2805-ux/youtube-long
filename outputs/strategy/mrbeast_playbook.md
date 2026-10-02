# MrBeast Playbook — Kênh Azzam (XAUUSD / Forex)

> Đóng vai: **MrBeast của ngách trading**. Nguyên tắc: packaging quyết định 90% kết quả, nội dung quyết định 10% còn lại. Nhưng trong trading, **trust là điều kiện sống còn** — không hứa lợi nhuận, không trade giả.

---

## 0. Ground truth — số liệu thật dùng cho playbook này

| Kênh | Subs | Tổng views | Videos | Vai trò |
|------|------|-----------|--------|---------|
| TTrades | 532,000 | 44,045,219 | 544 | benchmark |
| Raghee Horner | 87,900 | 4,795,742 | 1,968 | tham chiếu |
| Trade with Pat | 419,000 | 20,044,654 | 421 | tham chiếu |
| JeaFx | 876,000 | 45,924,304 | 273 | benchmark |

- Video phân tích: **44** unique (raw 35 shorts-tab + 38 long-form, overlap đã dedupe theo video_id)
- Nguồn: YouTube Data API v3 (search.list + videos.list + commentThreads.list)

> **Cảnh báo chất lượng dữ liệu:** `search.list` với `duration=short` KHÔNG lọc đáng tin — nhiều video trả về có duration 10-30 phút. Vì vậy các video trong run 'shorts' phần lớn thực chất là long-form. Muốn lấy Shorts thật phải dùng `channel/videos?tab=shorts` (TranscriptAPI) hoặc kiểm tra duration thủ công.

## 1. Format nào thắng — đo bằng số, không đoán

| Duration bucket | Số video | Avg views | Median views | Avg like rate |
|-----------------|----------|-----------|--------------|---------------|
| 0-60s (Short) | 6 | 917,201 | 383,937 | 3.12% |
| 1-5 min | 2 | 3,178 | 4,901 | 5.25% |
| 5-15 min | 18 | 464,800 | 445,009 | 3.09% |
| 15-30 min | 15 | 933,420 | 665,139 | 3.15% |
| 30+ min | 3 | 1,285,365 | 1,230,143 | 2.85% |

**Đọc số này thế nào:** so sánh avg views giữa các bucket để biết format nào đang được phân phối mạnh. Nhưng cẩn thận — bucket có avg cao có thể chỉ do 1-2 video viral kéo lên, nên xem cả median.

## 2. Top 20 video — giải phẫu packaging

| # | Views | Duration | Title | Kênh |
|---|-------|----------|-------|------|
| 1 | 4,585,339 | 0m42s | 10 year FX Scalping Strategy in 42 seconds! #trading | Trade with Pat |
| 2 | 2,985,757 | 27m58s | Every Candlestick Tells a Story... Here's how to read them like a pro | JeaFx |
| 3 | 1,734,380 | 68m59s | Master Market Structure in 68 Minutes (Step-by-Step Course) | JeaFx |
| 4 | 1,695,547 | 15m55s | Always Wait For THIS Before Entering Trades (Candlestick Closures) | JeaFx |
| 5 | 1,631,244 | 18m30s | ICT Daily Bias - The Only Video You Will Ever Need! | TTrades |
| 6 | 1,624,514 | 20m08s | Liquidity + Structure = Profit | JeaFx |
| 7 | 1,301,153 | 25m12s | Master Liquidity Sweeps & Inducements (in 25 minutes) | JeaFx |
| 8 | 1,230,143 | 31m09s | Forex Trading For Beginners (FULL COURSE) | JeaFx |
| 9 | 1,123,876 | 10m59s | A+ ICT Entry Checklist - ICT Concepts | TTrades |
| 10 | 1,101,999 | 17m50s | The PERFECT ENTRY Strategy That Will 10x Your Results... | JeaFx |
| 11 | 929,829 | 29m49s | Ultimate Top Down Analysis Strategy (Step by Step) | JeaFx |
| 12 | 903,587 | 9m55s | Liquidity: Buyside & Sellside - ICT Concepts | TTrades |
| 13 | 891,574 | 40m03s | ULTIMATE Supply and Demand Masterclass (Beginner to Pro) | JeaFx |
| 14 | 733,179 | 7m32s | The ONLY Market Structure Lesson You'll EVER Need (Step by Step) | JeaFx |
| 15 | 689,042 | 11m38s | This Trading Tip Will Make You $$$ (Inducement) | JeaFx |
| 16 | 665,139 | 24m38s | The Ultimate Supply & Demand Trading Course (Become a Pro) | JeaFx |
| 17 | 556,963 | 18m24s | The 3 Step A+ Supply & Demand Strategy (That Actually Works) | Trade with Pat |
| 18 | 543,888 | 14m58s | Order Blocks Simplified - ICT Concepts | TTrades |
| 19 | 512,161 | 0m28s | Don’t BUY Prop Firm Trading Challenges ❌ #forex | Trade with Pat |
| 20 | 484,219 | 12m41s | 3 Best Forex Robots for 2026 that ACTUALLY Work | Trade with Pat |

## 3. Công thức tiêu đề — rút từ 20 video thắng

| Pattern | Số video top-20 dùng |
|---------|---------------------|
| 'Step by Step / Simplified / Masterclass' — giảm ma sát học | 6 |
| Có con số cụ thể | 5 |
| Có mốc thời gian | 3 |
| 'The Only X' — tuyên bố độc quyền | 2 |
| 'You'll Ever Need' — hứa hẹn tuyệt đối | 2 |
| Nhắm 'Beginners' — mở rộng tệp khán giả | 2 |
| 'That ACTUALLY Works' — đối đầu với lời hứa rỗng | 2 |
| Mệnh lệnh/cảnh báo ('Don't', 'Stop', 'Wait For') | 1 |

**Công thức áp dụng cho Azzam:**

```
[CẢNH BÁO/MỆNH LỆNH] + [ĐỐI TƯỢNG] + [KẾT QUẢ] + [RÀO CẢN THỜI GIAN/SỐ]

Ví dụ (XAUUSD):
  • Stop Risking 10% Per XAUUSD Trade (Do This Instead)
  • The Only XAUUSD Bias Routine You Need (5 Minutes)
  • 3 XAUUSD Entry Mistakes That Blow Accounts
  • Why You Keep Losing On Gold (And The Fix)
```

## 4. Content pillars — map từ pain point có evidence

| Pillar | Pain cluster | Evidence (unique comments) | Vai trò trong phễu |
|--------|--------------|---------------------------|--------------------|
| SA-07 | education_gap / basic không vững | 718 | Top-funnel — kéo người mới vào |
| SA-02 | overcomplicating / strategy quá phức tạp | 382 | Top-funnel — chống 'shiny object' |
| SA-03 | risk_management / cháy tài khoản | 324 | Mid-funnel — trust qua risk (không hứa lãi) |
| SA-06 | community / cô độc khi trading | 250 | Bottom-funnel — lý do join Telegram/VIP |
| SA-04 | entry_timing / vào lệnh sai thời điểm | 226 | Mid-funnel — kỹ thuật, giữ chân |
| SA-08 | broker_platform / spread, prop firm | 113 | Monetization — affiliate prop firm/broker |
| SA-05 | psychology / revenge trading, FOMO | 62 | Mid-funnel — emotional hook |
| SA-01 | discipline / không theo plan | 43 | Bottom-funnel — lý do mua hệ thống |

## 5. Packaging 5 video mở màn (title + thumbnail + hook)

### Video 1 — pillar SA-03
- **Title:** 1 XAUUSD Trade Can Wipe Your Account (Here's The Math)
- **Thumbnail:** Nến XAUUSD đỏ dài + con số '10%' gạch chéo đỏ + text '1 TRADE = ACCOUNT GONE'
- **Hook (0-3s):** 0-3s: 'Nếu bạn risk 10% mỗi lệnh XAUUSD, đây là số lệnh bạn cần thua để cháy tài khoản.' → đếm ngược 5-4-3-2-1
- **CTA:** Comment 'RISK'
- **Vì sao packaging này:** Con số cụ thể + cảnh báo = pattern 'Don't/Stop' thắng trong top-20

### Video 2 — pillar SA-02
- **Title:** You Don't Need More Indicators — You Need Fewer
- **Thumbnail:** Chart XAUUSD với 10 indicator bị gạch đỏ, còn 1 cái khoanh xanh + 'DELETE THESE'
- **Hook (0-3s):** 0-3s: 'Tôi xoá 9/10 indicator của mình. Tài khoản bắt đầu tăng từ đó.' → show chart sạch
- **CTA:** Comment 'SIMPLE'
- **Vì sao packaging này:** Đối đầu trực tiếp với hành vi phổ biến của khán giả (overcomplicating)

### Video 3 — pillar SA-01
- **Title:** You Know The Strategy. So Why Do You Still Lose?
- **Thumbnail:** Chia đôi: bên trái 'BIẾT', bên phải 'KHÔNG LÀM ĐƯỢC' + mũi tên gãy
- **Hook (0-3s):** 0-3s: 'Bạn không thiếu kiến thức. Bạn thiếu quy trình. Hai thứ này khác nhau.'
- **CTA:** Comment 'PLAN'
- **Vì sao packaging này:** Quote thật từ khán giả đối thủ: 'My problem is discipline. I do not stick to my plan.'

### Video 4 — pillar SA-04
- **Title:** Stop Entering XAUUSD Too Early (3 Confirmations)
- **Thumbnail:** Chart XAUUSD với 3 điểm vào: 2 cái gạch đỏ (sớm), 1 cái khoanh xanh (đúng)
- **Hook (0-3s):** 0-3s: 'Đây là lý do bạn vào đúng hướng nhưng vẫn thua — bạn vào sớm 3 nến.'
- **CTA:** Comment 'ENTRY'
- **Vì sao packaging này:** Lỗi kỹ thuật cụ thể, dễ chứng minh bằng chart

### Video 5 — pillar SA-06
- **Title:** Trading Alone Is Why You're Not Improving
- **Thumbnail:** 1 người đơn độc nhìn chart vs nhóm người review chart cùng nhau
- **Hook (0-3s):** 0-3s: 'Tôi mất 2 năm vì trade một mình. Feedback từ 1 người khác rút ngắn nó còn 6 tháng.'
- **CTA:** Join Telegram
- **Vì sao packaging này:** Quote thật: 'I'm tired of trading by myself since my friend gave up'

## 6. Phễu — cơ chế cụ thể, không phải khẩu hiệu

### Bước 1 — Comment keyword → Telegram

```
Video CTA: "Comment 'RISK' để nhận risk calculator"
   ↓
Pinned comment (chính chủ): "Đã gửi cho mọi người comment 'RISK' — ai chưa nhận được thì join đây: [Telegram link]"
   ↓
Telegram bot: /start → hỏi 'Bạn đang trade cặp nào?' → gửi đúng lead magnet
   ↓
Tag lead theo keyword nguồn (RISK / SIMPLE / ENTRY / PLAN / PSYCH)
```

**Vì sao hoạt động:** comment keyword (a) tăng engagement signal cho thuật toán, (b) tạo phân khúc lead theo pain point, (c) đo được video nào ra lead tốt nhất.

### Bước 2 — Nurture 7 ngày trên Telegram

| Ngày | Nội dung | Mục đích |
|------|----------|----------|
| 1 | Chào + hỏi mục tiêu trading hiện tại | Segment |
| 2 | Bài học risk management 1 trang | Giá trị thuần |
| 3 | Checklist entry 5 bước (PDF) | Giá trị thuần |
| 4 | Case study: 1 lệnh thua được xử lý đúng cách | Trust — dám show thua |
| 5 | Video long-form mới nhất + tóm tắt | Kéo về YouTube |
| 6 | Mời vào buổi live XAUUSD | Tương tác |
| 7 | Offer tripwire (template + calculator) | Convert |

**Quy tắc cứng:** ngày 1-6 không bán. Ngày 7 mới offer. Offer phải qua human review trước khi gửi.

### Bước 3 — Offer ladder

| Tầng | Sản phẩm | Giá | Nguồn lead |
|------|----------|-----|-----------|
| Tripwire | Trading Plan Template + Risk Calculator | $9-27 | comment RISK/PLAN |
| Core | Complete System (Basic → Setup → Execution) | $97-297 | tripwire buyers |
| VIP | Mentorship + group review hàng tuần | $497+/tháng | core buyers |
| Affiliate | Broker IB + Prop firm + Tools | hoa hồng | mọi tầng |

## 7. Guardrail — không thoả hiệp

| Được | Không được |
|------|-----------|
| Show lệnh thua và cách xử lý | Show trade giả / chart mô phỏng như trade thật |
| Nói về quy trình, xác suất, kỷ luật | Cam kết lợi nhuận, % thắng, 'chắc chắn lãi' |
| Affiliate có disclosure rõ | Affiliate ngầm, giấu quan hệ thương mại |
| Sales copy ở dạng draft | Auto-send sales/affiliate khi chưa có approval |
| Dùng comment thật làm evidence (có link) | Bịa testimonial / quote khán giả |

---

## 8. Việc cần Alan duyệt trước khi thực thi

1. Telegram gateway cho project YouTube (chưa xác nhận bot/chat ID riêng)
2. Offer ladder + giá (chưa có quyết định)
3. Broker/prop firm affiliate nào (chưa chọn đối tác)
4. Có target khán giả tiếng Việt hay tiếng Anh (ảnh hưởng toàn bộ title/tag)

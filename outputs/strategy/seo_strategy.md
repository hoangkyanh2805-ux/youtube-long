# Chiến lược SEO kênh — Azzam

## Fact — nguồn dữ liệu (số UNIQUE sau dedupe)
- Comments scrape raw: 11125 (shorts 4389 + long-form 6736)
- Comments UNIQUE: **7937** (overlap 3188 comment xuất hiện ở cả 2 run — vì top shorts cũng là video long-form)
- Pain-point candidates raw: 2567 | UNIQUE: **1848** (overlap 719)
- 4 kênh đối thủ: TTrades (532K subs), Raghee Horner (87.9K), Trade with Pat (419K), JeaFx (876K)
- Keywords mine từ comment + video title. KHÔNG có Keyword Planner → không có search volume thật, chỉ có tần suất trong dữ liệu.

> **Lưu ý độ tin cậy:** `education_gap` là bucket rộng (mọi câu hỏi 'how/what/why' đều rơi vào đây), nên con số SA-07 cao phần lớn do category match chứ không phải pain point đặc thù. Các angle SA-01/SA-02/SA-05 dựa trên keyword đặc thù nên tín hiệu mạnh hơn dù số nhỏ hơn.

## 1. Từ khóa chính (main keywords)

| # | Keyword | Freq trong comment | Category | Ưu tiên |
|---|---------|-------------------|----------|---------|
| 1 | trading | 547 | core | CAO |
| 2 | strategy | 332 | core | CAO |
| 3 | liquidity | 97 | ICT/SMC | TRUNG |
| 4 | market | 276 | core | CAO |
| 5 | trade | 360 | core | CAO |
| 6 | entry | 106 | execution | CAO |
| 7 | risk | 127 | risk | CAO |
| 8 | structure | 73 | ICT/SMC | TRUNG |
| 9 | candle | 128 | basic | CAO |
| 10 | chart | 105 | basic | CAO |
| 11 | stop | 90 | risk | TRUNG |
| 12 | timeframe | 50 | strategy | TRUNG |
| 13 | profit | 72 | outcome | TRUNG |
| 14 | setup | 77 | strategy | TRUNG |
| 15 | backtest | 15 | process | THẤP |
| 16 | broker | 15 | platform | THẤP |
| 17 | prop | 33 | platform | THẤP |
| 18 | mentor | 49 | community | TRUNG |
| 19 | course | 30 | offer | THẤP |
| 20 | robot | 24 | automation | THẤP |

## 2. Từ khóa dài (long-tail)

### 2a. Ngôn ngữ KHÁN GIẢ (từ comment text) — dùng làm hook/tiêu đề

| # | Long-tail phrase | Freq | Dùng cho |
|---|------------------|------|----------|
| 1 | stop loss | 43 | Title + Description |
| 2 | supply demand | 36 | Title + Description |
| 3 | market structure | 33 | Title + Description |
| 4 | risk management | 29 | Title + Description |
| 5 | daily bias | 23 | Title + Description |
| 6 | swing trading | 21 | Title + Description |
| 7 | trading strategy | 20 | Title + Description |
| 8 | started trading | 19 | Title + Description |
| 9 | paper trading | 15 | Title + Description |
| 10 | prop firms | 15 | Title + Description |
| 11 | support resistance | 13 | Title + Description |
| 12 | prop firm | 12 | Title + Description |
| 13 | every day | 12 | Title + Description |
| 14 | order block | 12 | Title + Description |
| 15 | orb strategy | 11 | Title + Description |
| 16 | candle candle | 10 | Title + Description |
| 17 | chart examples | 10 | Title + Description |
| 18 | learning trade | 9 | Title + Description |
| 19 | stop losses | 9 | Title + Description |
| 20 | liquidity sweep | 9 | Title + Description |
| 21 | trading without | 9 | Title + Description |
| 22 | trade trade | 8 | Title + Description |
| 23 | trading years | 8 | Title + Description |
| 24 | minute scalping | 8 | Title + Description |
| 25 | per day | 8 | Title + Description |
| 26 | money trading | 8 | Title + Description |
| 27 | break structure | 8 | Title + Description |
| 28 | trading real | 8 | Title + Description |
| 29 | trading journey | 8 | Title + Description |
| 30 | ict concepts | 8 | Title + Description |

### 2b. Pattern TIÊU ĐỀ ĐỐI THỦ (mine 1 lần/video) — dùng làm công thức

| # | Title pattern | Số video dùng |
|---|---------------|---------------|
| 1 | ict concepts | 8 |
| 2 | step step | 4 |
| 3 | market structure | 3 |
| 4 | scalping strategy | 3 |
| 5 | simplified ict | 2 |
| 6 | simplified ict concepts | 2 |
| 7 | trading beginners | 2 |
| 8 | ever step | 2 |
| 9 | ever step step | 2 |
| 10 | trading strategy | 2 |
| 11 | ict daily | 1 |
| 12 | daily bias | 1 |
| 13 | bias ever | 1 |
| 14 | ict daily bias | 1 |
| 15 | daily bias ever | 1 |
| 16 | ict entry | 1 |
| 17 | entry checklist | 1 |
| 18 | checklist ict | 1 |
| 19 | ict entry checklist | 1 |
| 20 | entry checklist ict | 1 |

## 3. Cấu trúc SEO cho từng loại content

### Shorts
- **Title**: 40-60 ký tự, có 1 main keyword + 1 hook số
  - Mẫu: `3 Reasons You Keep Losing Trades (Risk Management)`
  - Mẫu: `Stop Using 10 Indicators — Do This Instead`
- **Description**: 2-3 câu + 3-5 hashtag + CTA comment keyword
- **Hashtag**: `#shorts #forex #xauusd #tradingstrategy #riskmanagement`
- **Không** nhồi keyword vào title — YouTube Shorts ưu tiên hook + retention

### Long video
- **Title**: `[Số] + [Kết quả cụ thể] + ([Thời gian/Không cần])`
  - `5 Risk Management Rules That Saved My Account (12 Min Guide)`
  - `The Only Trading Plan You Need — Step By Step`
- **Description** (cấu trúc chuẩn):
  ```
  [Hook 2 câu — nhắc lại pain point]

  Trong video này:
  00:00 Vấn đề
  02:15 Nguyên nhân
  06:40 Giải pháp
  12:00 Checklist

  📌 Tài nguyên miễn phí (Telegram): [link]
  ⚠️ Không phải lời khuyên đầu tư. Trading có rủi ro mất vốn.
  ```
- **Tags**: 15-20 tag, mix main + long-tail
- **Playlist**: gom theo series (Basic → Setup → Execution → Psychology)

### Live stream
- **Title**: `XAUUSD Live Analysis — [Session] | [Ngày]`
- **Description**: có timestamp bias, CTA Telegram

## 4. Tag set chuẩn (copy-paste)

**Core tags (dùng mọi video):**
`forex trading, xauusd, gold trading, trading strategy, risk management, price action, trading education, trading for beginners`

**Short-specific:**
`trading tips, trading psychology, trading mistakes, entry timing, stop loss, position sizing, trading discipline, forex beginner`

**Long-specific:**
`full course, step by step, complete guide, masterclass, trading plan, backtesting, market structure, liquidity, supply and demand, candlestick patterns`

**Live-specific:**
`live trading, xauusd live, gold live analysis, market analysis today, trading live stream`

## 5. Keyword gap — đối thủ chưa cover

| Gap keyword | Đối thủ có video? | Cơ hội |
|-------------|-------------------|--------|
| trading discipline system | Có nhưng ít (psychology chỉ 4.3% pain points) | CAO — pain point lớn, ít content |
| trading plan template | Rất ít | CAO — lead magnet tự nhiên |
| prop firm rules comparison | Trade with Pat có 1 video | TRUNG-CAO |
| risk calculator tutorial | Không thấy | CAO |
| trading journal how to | Không thấy | CAO |
| xauusd session bias | TTrades có daily bias (không phải XAUUSD specific) | CAO — ngách của Azzam |
| vietnamese forex beginner | Không kênh nào cover | CAO — nếu target VN |

## 6. Lịch đăng đề xuất

| Ngày | Loại | Nội dung | Keyword chính |
|------|------|----------|---------------|
| T2 | Short | 3 dấu hiệu bạn thiếu hệ thống | trading discipline |
| T2 | Short | 1 lệnh này xoá sạch tài khoản | risk management |
| T3 | Long | 5 Risk Rules Saved My Account | risk management |
| T4 | Short | Đừng học ICT khi chưa biết cái này | trading basics |
| T4 | Live | XAUUSD London Session Bias | xauusd |
| T5 | Short | Revenge trading: 3 quy tắc chặn | trading psychology |
| T6 | Long | Entry Confirmation A-Z | entry timing |
| T6 | Live | XAUUSD NY Session | xauusd |
| T7 | Short | Prop firm: đọc cái này trước khi mua | prop firm |
| CN | Short | Trading một mình = thua chậm | trading community |

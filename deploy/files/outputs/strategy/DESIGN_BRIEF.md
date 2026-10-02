# DESIGN BRIEF — THUMBNAIL KÊNH AZZAM MASTER TRADING

**Ngày:** 2026-10-02  
**Người nhận:** Designer / Editor  
**Số lượng:** 24 video, mỗi video 2 biến thể A/B

## 1. QUY TẮC BẮT BUỘC

| Hạng mục | Yêu cầu |
|----------|---------|
| **Kích thước** | 1280×720 px, xuất PNG, dưới 2 MB. Kiểm tra ở 120px trước khi giao. |
| **Vùng an toàn** | Giữ 60px viền ngoài trống — YouTube cắt góc khi hiển thị ở vài vị trí. |
| **Chữ tối đa** | 3-5 từ. Font sans-serif đậm (Anton, Montserrat ExtraBold, Bebas Neue). Cỡ tối thiểu 90pt ở 1280px. |
| **Viền chữ** | Viền đen 3-4px hoặc bóng đổ — nếu không, chữ chìm khi thumbnail thu nhỏ. |
| **Màu** | Nền #0D1117 (đen xanh) — tối, làm nổi chart và chữ. Nhấn #FFD400 (vàng gold) — màu chủ đạo ngách vàng. Đỏ #FF3B30 (đỏ) — chỉ dùng cho mất mát/rủi ro, tối đa 1 điểm và xanh #00C853 (xanh) — chỉ dùng cho kết quả đúng, tối đa 1 điểm mỗi thứ tối đa 1 điểm. |
| **Tương phản** | Tỷ lệ tương phản chữ/nền tối thiểu 4.5:1. Test bằng ảnh grayscale — nếu mất chữ thì chưa đủ tương phản. |
| **Chart** | Dùng chart THẬT từ XAUUSD. Nếu dùng chartanimator.io thì ghi rõ là minh hoạ. TUYỆT ĐỐI không vẽ chart giả trông như kết quả trade thật. |
| **Khuôn mặt** | Cảm xúc phải khớp nội dung. Không dùng mặt ngạc nhiên chung chung cho video về quản lý rủi ro. |
| **Nhất quán** | Giữ 1-2 archetype cho cả kênh để khán giả nhận ra. Đổi archetype chỉ khi A/B test thắng rõ. |
| **Bàn giao** | Giao kèm 2 biến thể (A/B) cho mỗi video. Ghi rõ biến thể nào là chính. |

## 2. BẢNG MÀU

- **nen** — #0D1117 (đen xanh) — tối, làm nổi chart và chữ
- **nhan** — #FFD400 (vàng gold) — màu chủ đạo ngách vàng
- **canh_bao** — #FF3B30 (đỏ) — chỉ dùng cho mất mát/rủi ro, tối đa 1 điểm
- **tin_cay** — #00C853 (xanh) — chỉ dùng cho kết quả đúng, tối đa 1 điểm
- **chu** — #FFFFFF trắng + viền đen 3px — đọc được trên mọi nền

## 3. 5 ARCHETYPE — CHỌN THEO NỘI DUNG

### T1 — Đối đầu 2 chiều  (mobile 9/10)

- Bố cục: Chia đôi dọc. Trái: chart XAUUSD đang rơi (đỏ). Phải: chart đi đúng hướng (xanh). Ở giữa: mũi tên vàng to chỉ từ trái sang phải.
- Cảm xúc: Tò mò + nhẹ nhõm — 'tôi đang ở bên trái, cần sang phải'
- Chữ: Chữ 20%: 3 từ tối đa, ví dụ 'SAI → ĐÚNG'

### T2 — Con số áp đảo  (mobile 10/10)

- Bố cục: Số cực lớn chiếm 40% khung bên trái (font 200pt, vàng gold). Bên phải: mặt người biểu cảm ngạc nhiên. Nền: chart mờ.
- Cảm xúc: Sốc nhẹ — số lớn tạo cảm giác có thông tin cụ thể, đáng bấm
- Chữ: Chữ 20%: chính là con số + 2-3 từ, ví dụ '3 BƯỚC'

### T3 — Khuôn mặt + cảm xúc cực đoan  (mobile 9/10)

- Bố cục: Mặt người chiếm 45% khung bên phải, biểu cảm mạnh (bực bội hoặc nhẹ nhõm). Bên trái: 1 dòng chữ lớn + 1 phần tử chart nhỏ.
- Cảm xúc: Đồng cảm — khán giả thấy cảm xúc của chính mình
- Chữ: Chữ 20%: 3-4 từ, ví dụ 'TÔI ĐÃ SAI'

### T4 — Khoanh đỏ điều sai  (mobile 8/10)

- Bố cục: Chart toàn khung. Một vùng được khoanh đỏ nét dày, có mũi tên. Góc phải trên: chữ nhỏ '90% làm sai chỗ này'.
- Cảm xúc: Lo lắng bị bỏ lỡ — 'có thể tôi đang làm sai'
- Chữ: Chữ 20%: 4-5 từ nhỏ ở góc

### T5 — Checklist trước/sau  (mobile 6/10)

- Bố cục: Hai cột. Trái: 3 dòng có dấu ✗ đỏ. Phải: 3 dòng có dấu ✓ xanh. Nền tối, chữ trắng viền đen.
- Cảm xúc: Tin cậy — 'đây là hướng dẫn cụ thể, không phải nói suông'
- Chữ: Chữ 20% nhưng chia 6 dòng ngắn

## 4. DANH SÁCH VIỆC THEO VIDEO

| STT | Chủ đề | Concept | Chữ trên ảnh | Biến thể B |
|-----|--------|---------|--------------|-----------|
| 1 | Stop Loss đúng cách | **T1** | `STOP LOSS ĐÚNG CÁCH — 3 BƯỚC` | T2 Con số áp đảo |
| 2 | Supply & Demand zone | **T2** | `SUPPLY & DEMAND ZONE — 3 BƯỚ` | T1 Đối đầu 2 chiều |
| 3 | Market Structure | **T5** | `MARKET STRUCTURE — 3 BƯỚC CH` | T2 Con số áp đảo |
| 4 | Risk Management cho tài kh | **T1** | `TẠI SAO BẠN VẪN THUA VỚI RIS` | T2 Con số áp đảo |
| 5 | Daily Bias | **T5** | `DAILY BIAS — 3 BƯỚC CHO NGƯỜ` | T2 Con số áp đảo |
| 6 | Swing Trading | **T1** | `SWING TRADING — 3 BƯỚC CHO N` | T2 Con số áp đảo |
| 7 | Paper Trading — bắt đầu an | **T5** | `PAPER TRADING — BẮT ĐẦU AN T` | T2 Con số áp đảo |
| 8 | Prop Firm: nên hay không | **T3** | `PROP FIRM: NÊN HAY KHÔNG — 3` | T2 Con số áp đảo |
| 9 | Order Block | **T4** | `ORDER BLOCK — 3 BƯỚC CHO NGƯ` | T2 Con số áp đảo |
| 10 | Liquidity Sweep | **T4** | `LIQUIDITY SWEEP — 3 BƯỚC CHO` | T2 Con số áp đảo |
| 11 | Scalping 1 phút | **T4** | `SCALPING 1 PHÚT — 3 BƯỚC CHO` | T2 Con số áp đảo |
| 12 | Entry Model — vào lệnh đún | **T4** | `ENTRY MODEL — VÀO LỆNH ĐÚNG ` | T2 Con số áp đảo |
| 13 | Trading mà không có hướng  | **T5** | `TRADING MÀ KHÔNG CÓ HƯỚNG DẪ` | T2 Con số áp đảo |
| 14 | Vì sao trader thua | **T3** | `VÌ SAO TRADER THUA — 3 BƯỚC ` | T2 Con số áp đảo |
| 15 | ICT Concepts đơn giản hoá | **T5** | `ICT CONCEPTS ĐƠN GIẢN HOÁ — ` | T2 Con số áp đảo |
| 16 | Support & Resistance thật | **T5** | `SUPPORT & RESISTANCE THẬT — ` | T2 Con số áp đảo |
| 17 | Trading Journal — nhật ký  | **T3** | `TRADING JOURNAL — NHẬT KÝ LỆ` | T2 Con số áp đảo |
| 18 | Bắt đầu trading từ 0 | **T5** | `BẮT ĐẦU TRADING TỪ 0 — 3 BƯỚ` | T2 Con số áp đảo |
| 19 | Candle — đọc nến đúng | **T5** | `CANDLE — ĐỌC NẾN ĐÚNG — 3 BƯ` | T2 Con số áp đảo |
| 20 | Timeframe nào cho người mớ | **T5** | `TIMEFRAME NÀO CHO NGƯỜI MỚI ` | T2 Con số áp đảo |
| 21 | Số lệnh mỗi ngày | **T1** | `SỐ LỆNH MỖI NGÀY — 3 BƯỚC CH` | T2 Con số áp đảo |
| 22 | Tâm lý khi thua liên tiếp | **T3** | `TÂM LÝ KHI THUA LIÊN TIẾP — ` | T2 Con số áp đảo |
| 23 | XAUUSD vs Forex pairs | **T3** | `XAUUSD VS FOREX PAIRS — 3 BƯ` | T2 Con số áp đảo |
| 24 | Lộ trình 90 ngày | **T5** | `LỘ TRÌNH 90 NGÀY — 3 BƯỚC CH` | T2 Con số áp đảo |

## 5. TIÊU CHÍ NGHIỆM THU

- [ ] Đọc được chữ ở 120px (thu nhỏ về 10% rồi xem)
- [ ] Ảnh grayscale vẫn đọc được chữ
- [ ] Không quá 5 từ
- [ ] Không có số lợi nhuận / số dư tài khoản giả
- [ ] Có 2 biến thể A/B, ghi rõ biến thể chính
- [ ] PNG < 2 MB, 1280×720
- [ ] Nhìn 1 giây biết video nói về gì

## 6. BÀN GIAO

Đặt tên file: `<stt>-<topic-slug>-<A|B>.png`  
Ví dụ: `01-stop-loss-dung-cach-A.png`

---

*Sinh bởi `scripts/build_thumbnail_concepts.py` (P11). Prompt AI có sẵn trong THUMBNAIL_CONCEPTS.md.*
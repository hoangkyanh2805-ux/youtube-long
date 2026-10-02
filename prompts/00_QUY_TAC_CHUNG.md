# QUY TẮC DÙNG AI/CLAUDE TRONG SẢN XUẤT

## AI làm gì, người làm gì

| Công đoạn | AI làm | Người làm |
|-----------|--------|-----------|
| Chọn pain point | Đọc CSV, lọc score, chọn 3 nhóm khác nhau | Chốt cuối |
| Viết hook | Draft 5 biến thể | Chọn 1, sửa giọng |
| Viết outline Long | Draft cấu trúc 8 phút | Kiểm tra logic |
| Phụ đề | Auto-transcribe | Sửa lỗi chính tả thuật ngữ |
| Title/description/tag | Draft theo pattern | Duyệt |
| Cắt ghép video | KHÔNG (AI chưa làm được chất lượng) | Editor làm |
| Thumbnail | KHÔNG (AI khó ra chữ tiếng Việt chuẩn) | Editor làm |

## Nguyên tắc bắt buộc
1. **AI không được bịa số liệu trading.** Mọi con số phải lấy từ file dữ liệu thật.
2. **AI không cam kết lợi nhuận.** Prompt phải có dòng cấm.
3. **Người duyệt trước khi đăng.** AI chỉ draft.
4. **Không dán dữ liệu khách hàng / API key vào prompt.**

## Mẫu câu lệnh khởi đầu cho Claude
```
Bạn là trợ lý sản xuất nội dung cho kênh trading XAUUSD.
Dữ liệu nguồn nằm trong file tôi đính kèm (pain point thật từ comment khán giả).
QUY TẮC:
- Không bịa số liệu, chỉ dùng dữ liệu trong file.
- Không cam kết lợi nhuận, không nói "chắc chắn thắng".
- Trả lời bằng tiếng Việt, giọng nói thẳng, không dùng từ hoa mỹ.
```

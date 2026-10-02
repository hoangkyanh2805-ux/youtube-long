# PROMPT 1 — CHỌN NGUYÊN LIỆU (5 phút)

## Cách dùng
Mở file Excel → sheet `04_PAINPOOL_200`. Copy 20 dòng đầu (Score, Categories,
Nội dung comment) dán vào Claude kèm prompt dưới.

## Prompt
```
Dưới đây là 20 pain point thật từ comment khán giả các kênh trading.
Nhiệm vụ: chọn ra 3 pain point để làm 3 Short video trong ngày.

RÀNG BUỘC BẮT BUỘC:
- 3 pain point phải thuộc 3 nhóm Categories KHÁC NHAU.
- Không chọn 2 cái cùng nhóm dù điểm cao.
- Ưu tiên cái có thể trả lời trong 30 giây.

Trả về bảng:
| # | Categories | Nội dung gốc (nguyên văn) | Vì sao chọn | Góc trả lời |

Dữ liệu:
[dán 20 dòng]
```

## Output mong đợi
3 pain point đã chốt + lý do. Ghi lại Comment ID vào sheet `09_THEO_DOI`.

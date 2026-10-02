"""
So sánh dagu vs Windmill cho bối cảnh thật của Alan + danh sách câu hỏi quyết định.

Writes:
  outputs/reports/DECISION_dagu_vs_windmill.docx
  outputs/reports/DECISION_dagu_vs_windmill.xlsx
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

OUT = Path("outputs/reports")
OUT.mkdir(parents=True, exist_ok=True)

# ── Số liệu máy (đo thật, không đoán) ───────────────────────────────────────
MACHINE = [
    ("CPU", "Intel Core i3-12100F, 4 cores", "Khá yếu cho việc chạy VM song song"),
    ("RAM", "16 GB (17.0 GB đo được)", "Đang chạy Chrome + Edge + CapCut"),
    ("Ổ C:", "237.6 GB total — còn trống 28.7 GB (12%)", "CẢNH BÁO: rất chật"),
    ("Ổ G:", "15 GB — còn trống 6 GB (40%)", "Không đủ cho Docker"),
    ("Docker", "CHƯA CÀI (có trên winget 4.93.0)", "Blocker của Windmill"),
    ("WSL2", "Ubuntu, WSL 2, đang Stopped", "Nền cho Docker Desktop"),
    ("Tiến trình", "365 process đang chạy", "Máy đã khá tải"),
]

# ── Chi phí thật của Docker/Windmill ────────────────────────────────────────
DOCKER_COST = [
    ("Docker Desktop (installer)", "~1.0 GB", "Cài đặt"),
    ("WSL2 Ubuntu VM (đang có)", "~1.5-3 GB", "Đã tồn tại, sẽ phình khi dùng"),
    ("Docker Desktop VM disk", "~2-4 GB", "Tăng dần theo thời gian"),
    ("Windmill images (app + worker)", "~2-3 GB", "Kéo từ registry"),
    ("Postgres image + data", "~0.5-1 GB", "Bắt buộc cho Windmill"),
    ("TỔNG THÊM", "~7-12 GB", "Trên ổ C: còn 28.7 GB → còn ~17-22 GB"),
]

# ── So sánh năng lực ────────────────────────────────────────────────────────
COMPARE = [
    ("UI bấm chạy workflow", "Có — đang chạy tại :8080", "Có — UI đẹp hơn, nhiều tính năng hơn"),
    ("Xem logs", "Có — log từng step, lưu file", "Có — log + streaming"),
    ("Xem history", "Có — dag-runs, trạng thái từng lần", "Có — history đầy đủ hơn"),
    ("Agent điều khiển được", "CÓ — MCP tích hợp sẵn (3 tools: dagu_read, dagu_change, dagu_execute)",
     "Có — qua API, không có MCP sẵn"),
    ("App builder (tự dựng UI)", "Không", "Có"),
    ("Approval UI native", "Không — dùng guardrail script + Telegram topic", "Có"),
    ("Script Python/Bash/TS", "Có — chạy trực tiếp", "Có — native, có editor trong web"),
    ("Scheduler", "Có — đã bật", "Có"),
    ("Cài đặt", "XONG — 1 binary, không phụ thuộc", "Cần Docker + Postgres"),
    ("Tài nguyên tiêu tốn", "~50 MB RAM khi chạy", "VM 2-4 GB RAM + 7-12 GB disk"),
    ("Xung đột với CapCut Pro", "Không", "CÓ — VM chiếm RAM khi editor đang dựng video"),
    ("Số workflow hiện có", "12 WF, 3 đã chạy thành công", "Phải viết lại / chuyển đổi"),
    ("Rủi ro ổ C: đầy", "Không", "Cao — chỉ còn 28.7 GB (12%)"),
    ("Thời gian để dùng được", "0 — đã dùng được ngay", "2-4 giờ cài + cấu hình + chuyển WF"),
]

# ── Năng lực MCP của dagu (phát hiện mới) ───────────────────────────────────
DAGU_MCP = [
    ("dagu_read", "Đọc DAG spec, wiki, chi tiết dag-run, logs, list view",
     "Agent tự đọc trạng thái workflow, không cần Alan mở UI"),
    ("dagu_change", "Validate và áp dụng thay đổi DAG YAML (có mode=preview trước mode=apply)",
     "Agent sửa workflow an toàn: xem trước rồi mới áp dụng"),
    ("dagu_execute", "start / enqueue / retry / stop một DAG",
     "Agent tự chạy hoặc retry workflow — đúng thứ Alan muốn"),
]

# ── Câu hỏi cho Alan ────────────────────────────────────────────────────────
QUESTIONS = [
    ("Q1", "Máy tính này có phải máy editor dùng CapCut Pro hàng ngày không?",
     "Nếu CÓ → Docker VM sẽ tranh RAM với CapCut khi dựng video → nghiêng về giữ dagu",
     "Có / Không / Máy khác"),
    ("Q2", "Bạn có cần 'App builder' (tự dựng UI riêng cho từng workflow) không?",
     "Nếu KHÔNG → dagu đủ. Nếu CÓ → Windmill là lựa chọn duy nhất có tính năng này",
     "Có / Không / Chưa biết"),
    ("Q3", "Approval hiện tại qua Telegram topic (EDIT/COMMENT) đã đủ chưa?",
     "Nếu ĐỦ → không cần Windmill. Nếu muốn duyệt ngay trong UI → Windmill",
     "Đủ / Chưa đủ / Muốn cả hai"),
    ("Q4", "Bạn chấp nhận ổ C: còn ~17-22 GB sau khi cài Docker chứ?",
     "Còn 12% hiện tại đã chật; cài Docker còn ~7-9%. Rủi ro Windows chậm/đầy",
     "Chấp nhận / Không / Sẽ dọn ổ trước"),
    ("Q5", "Bạn có sẵn sàng bỏ 2-4 giờ để cài Docker + Postgres + chuyển 12 workflow không?",
     "dagu đã chạy; Windmill phải viết lại workflow sang định dạng mới",
     "Sẵn sàng / Không / Chỉ khi thật cần"),
    ("Q6", "Mục tiêu cuối là gì: vận hành kênh, hay bán hệ thống (build-to-sell)?",
     "Nếu BÁN hệ thống → Windmill UI đẹp hơn để demo. Nếu VẬN HÀNH → dagu đủ và nhẹ hơn",
     "Vận hành / Bán hệ thống / Cả hai"),
    ("Q7", "Editor có cần tự bấm chạy workflow không, hay chỉ Alan?",
     "Nếu chỉ Alan → dagu đủ. Nếu editor cũng dùng → Windmill phân quyền tốt hơn",
     "Chỉ Alan / Cả editor / Chưa rõ"),
    ("Q8", "Bạn muốn agent (Claude/Codex) tự điều khiển workflow không?",
     "dagu ĐÃ có MCP sẵn (dagu_read/change/execute) → làm được ngay, không cần Windmill",
     "Có / Không"),
    ("Q9", "Ngân sách hạ tầng hàng tháng?",
     "Windmill self-host = miễn phí nhưng tốn tài nguyên máy. Cloud có phí",
     "0đ (self-host) / Có ngân sách / Chưa rõ"),
    ("Q10", "Nếu giữ dagu, bạn có muốn tôi làm thêm gì để tiện hơn không?",
     "Ví dụ: dashboard gộp vào UI, thêm nút bấm, tự động chạy theo lịch",
     "Mô tả mong muốn"),
]

# ── Khuyến nghị ─────────────────────────────────────────────────────────────
RECOMMEND = [
    ("Giữ dagu", "Đã chạy, 12 WF sẵn sàng, MCP tích hợp, không tốn tài nguyên, ổ C: an toàn",
     "Đây là khuyến nghị mặc định"),
    ("Chỉ cân nhắc Windmill khi", "Cần app builder HOẶC bán hệ thống cần UI đẹp để demo "
     "HOẶC dọn được ổ C: còn ≥50 GB", "Điều kiện rõ ràng"),
    ("Không cài Docker ngay", "Ổ C: chỉ còn 28.7 GB (12%) — cài Docker còn ~7-9%, "
     "rủi ro cho cả Windows lẫn CapCut", "Blocker kỹ thuật thật"),
]


def build_docx() -> Path:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt, RGBColor

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10.5)
    st.paragraph_format.space_after = Pt(4)

    t = doc.add_heading("QUYẾT ĐỊNH: dagu HAY WINDMILL", level=0)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s = doc.add_paragraph()
    s.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = s.add_run("So sánh theo bối cảnh thật — kèm câu hỏi cần Alan trả lời")
    r.bold = True
    r.font.size = Pt(11)
    m = doc.add_paragraph()
    m.alignment = WD_ALIGN_PARAGRAPH.CENTER
    m.add_run(f"{date.today().isoformat()} • Dự án YouTube @azzammastertradinggold").italic = True
    doc.add_paragraph()

    def table(headers, rows, sizes=None):
        tb = doc.add_table(rows=len(rows) + 1, cols=len(headers))
        tb.style = "Light Grid Accent 1"
        for j, h in enumerate(headers):
            c = tb.cell(0, j)
            c.text = h
            for p in c.paragraphs:
                for run in p.runs:
                    run.bold = True
                    run.font.size = Pt(9.5)
        for i, row in enumerate(rows, 1):
            for j, v in enumerate(row):
                c = tb.cell(i, j)
                c.text = str(v)
                for p in c.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(9)
        doc.add_paragraph()

    # Kết luận trước
    doc.add_heading("KẾT LUẬN NGẮN", level=1)
    p = doc.add_paragraph()
    pr = p.add_run("GIỮ DAGU. Không cài Docker/Windmill lúc này.")
    pr.bold = True
    pr.font.size = Pt(13)
    pr.font.color.rgb = RGBColor(0x06, 0x76, 0x47)
    doc.add_paragraph(
        "Ba lý do quyết định: (1) ổ C: chỉ còn 28.7 GB — Docker + Windmill + Postgres "
        "sẽ lấy thêm 7-12 GB, đẩy ổ xuống ~7-9% và rủi ro cho cả Windows lẫn CapCut; "
        "(2) dagu ĐÃ có MCP tích hợp sẵn nên agent điều khiển được — lợi thế lớn nhất "
        "của Windmill không còn độc quyền; (3) dagu đang chạy, 12 workflow sẵn sàng, "
        "3 workflow đã chạy thành công — Windmill phải viết lại toàn bộ."
    )
    doc.add_paragraph()

    # Số liệu máy
    doc.add_heading("1. SỐ LIỆU MÁY (đo thật)", level=1)
    table(["Hạng mục", "Giá trị đo được", "Ý nghĩa"], [list(x) for x in MACHINE])

    # Chi phí Docker
    doc.add_heading("2. CHI PHÍ THẬT NẾU CÀI DOCKER + WINDMILL", level=1)
    table(["Thành phần", "Dung lượng", "Ghi chú"], [list(x) for x in DOCKER_COST])
    p = doc.add_paragraph()
    pr = p.add_run("Đây là blocker kỹ thuật thật, không phải lo xa.")
    pr.bold = True
    pr.font.color.rgb = RGBColor(0xB0, 0x30, 0x60)
    doc.add_paragraph()

    # So sánh
    doc.add_heading("3. SO SÁNH NĂNG LỰC", level=1)
    table(["Tiêu chí", "dagu (đang chạy)", "Windmill (chưa cài)"], [list(x) for x in COMPARE])

    # MCP
    doc.add_heading("4. PHÁT HIỆN QUAN TRỌNG — dagu CÓ MCP TÍCH HỢP", level=1)
    doc.add_paragraph(
        "Kiểm tra thật: dagu 2.18.1 mở MCP server tại /mcp với 3 tool. "
        "Nghĩa là agent (Claude Code / Codex) điều khiển được workflow — "
        "đúng thứ mà Windmill được cho là có lợi thế."
    )
    table(["Tool", "Làm được gì", "Ý nghĩa cho dự án"], [list(x) for x in DAGU_MCP])
    doc.add_paragraph()

    # Câu hỏi
    doc.add_heading("5. CÂU HỎI CẦN ALAN TRẢ LỜI", level=1)
    doc.add_paragraph("Trả lời theo mã Q1-Q10. Càng trả lời đủ, quyết định càng chính xác.")
    doc.add_paragraph()
    for qid, q, why, opts in QUESTIONS:
        p = doc.add_paragraph()
        pr = p.add_run(f"{qid}. {q}")
        pr.bold = True
        d = doc.add_paragraph()
        d.paragraph_format.left_indent = Pt(20)
        dr = d.add_run(f"→ Vì sao quan trọng: {why}")
        dr.italic = True
        dr.font.size = Pt(9)
        dr.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        o = doc.add_paragraph()
        o.paragraph_format.left_indent = Pt(20)
        orr = o.add_run(f"→ Trả lời: {opts}")
        orr.font.size = Pt(9)
        orr.font.color.rgb = RGBColor(0x17, 0x5C, 0xD3)
    doc.add_paragraph()

    # Khuyến nghị
    doc.add_heading("6. KHUYẾN NGHỊ", level=1)
    table(["Khuyến nghị", "Lý do", "Điều kiện"], [list(x) for x in RECOMMEND])

    doc.add_heading("7. NẾU SAU NÀY VẪN MUỐN WINDMILL", level=1)
    for txt in [
        "Dọn ổ C: còn tối thiểu 50 GB trống trước khi cài.",
        "Cài Docker Desktop qua winget: winget install Docker.DockerDesktop",
        "Chạy Windmill bằng Docker Compose (app + worker + Postgres).",
        "Chuyển 12 workflow sang định dạng Windmill (Python script hoặc flow).",
        "Giữ dagu song song trong 2 tuần để so sánh trước khi bỏ hẳn.",
    ]:
        doc.add_paragraph(txt, style="List Number")

    path = OUT / "DECISION_dagu_vs_windmill.docx"
    doc.save(path)
    return path


def build_xlsx() -> Path:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    HF = PatternFill("solid", fgColor="1F3864")
    HFONT = Font(bold=True, color="FFFFFF", size=10)
    TFONT = Font(bold=True, size=14, color="1F3864")
    NFONT = Font(italic=True, size=9, color="555555")
    THIN = Side(style="thin", color="BFBFBF")
    BD = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
    GOOD = PatternFill("solid", fgColor="D9F2E3")
    WARN = PatternFill("solid", fgColor="FDE7E7")

    wb = Workbook()
    used = [False]

    def sheet(name, title, note, headers, rows, widths=None, wrap=None, color=None):
        if not used[0]:
            ws = wb.active
            used[0] = True
        else:
            ws = wb.create_sheet(name)
        ws.title = name
        ws["A1"] = title
        ws["A1"].font = TFONT
        ws["A2"] = note
        ws["A2"].font = NFONT
        hr = 4
        for j, h in enumerate(headers, 1):
            c = ws.cell(row=hr, column=j, value=h)
            c.fill = HF
            c.font = HFONT
            c.border = BD
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for i, row in enumerate(rows, hr + 1):
            for j, v in enumerate(row, 1):
                c = ws.cell(row=i, column=j, value=v)
                c.border = BD
                c.font = Font(size=10)
                c.alignment = Alignment(vertical="top",
                                        wrap_text=(headers[j - 1] in (wrap or set())))
                if color and (i - hr - 1) < len(color) and color[i - hr - 1]:
                    c.fill = color[i - hr - 1]
        for j, h in enumerate(headers, 1):
            L = get_column_letter(j)
            if widths and h in widths:
                ws.column_dimensions[L].width = widths[h]
            else:
                longest = len(str(h))
                for row in rows[:200]:
                    if j - 1 < len(row):
                        longest = max(longest, len(str(row[j - 1])))
                ws.column_dimensions[L].width = min(max(longest + 2, 10), 62)
        if rows:
            ws.auto_filter.ref = f"A{hr}:{get_column_letter(len(headers))}{hr + len(rows)}"
        ws.freeze_panes = ws.cell(row=hr + 1, column=1)
        return ws

    # 01 KẾT LUẬN
    ws = wb.active
    ws.title = "01_KET_LUAN"
    ws["A1"] = "KẾT LUẬN: GIỮ DAGU — KHÔNG CÀI DOCKER/WINDMILL LÚC NÀY"
    ws["A1"].font = Font(bold=True, size=14, color="067647")
    ws["A2"] = f"Cập nhật {date.today().isoformat()} • Dựa trên số liệu đo thật từ máy"
    ws["A2"].font = NFONT
    rows = [
        ["1", "Ổ C: chỉ còn 28.7 GB (12%)", "Docker + Windmill + Postgres lấy thêm 7-12 GB → còn ~7-9%",
         "Blocker kỹ thuật thật"],
        ["2", "dagu ĐÃ có MCP tích hợp", "dagu_read / dagu_change / dagu_execute — agent điều khiển được",
         "Lợi thế của Windmill không còn độc quyền"],
        ["3", "dagu đang chạy, 12 WF sẵn sàng", "3 workflow đã chạy thành công, 0 phút setup",
         "Windmill phải viết lại toàn bộ"],
        ["4", "Máy 4 core / 16 GB, 365 process", "Docker VM 2-4 GB RAM sẽ tranh với CapCut Pro khi dựng video",
         "Xung đột với công cụ sản xuất chính"],
    ]
    hr = 4
    for j, h in enumerate(["#", "Lý do", "Chi tiết", "Loại"], 1):
        c = ws.cell(row=hr, column=j, value=h)
        c.fill = HF; c.font = HFONT; c.border = BD
        c.alignment = Alignment(horizontal="center", wrap_text=True)
    for i, row in enumerate(rows, hr + 1):
        for j, v in enumerate(row, 1):
            c = ws.cell(row=i, column=j, value=v)
            c.border = BD; c.font = Font(size=10)
            c.alignment = Alignment(vertical="top", wrap_text=True)
            c.fill = GOOD
    for j, w in enumerate([5, 34, 62, 40], 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = "A5"
    used[0] = True

    # 02 MÁY
    sheet("02_MAY_TINH", "SỐ LIỆU MÁY (đo thật)",
          "Đo bằng shutil.disk_usage + wmic, không ước lượng",
          ["Hạng mục", "Giá trị đo được", "Ý nghĩa"],
          [list(x) for x in MACHINE],
          widths={"Hạng mục": 18, "Giá trị đo được": 46, "Ý nghĩa": 44},
          wrap={"Giá trị đo được", "Ý nghĩa"})

    # 03 CHI PHÍ DOCKER
    colors = [None, None, None, None, None, WARN]
    sheet("03_CHI_PHI_DOCKER", "CHI PHÍ THẬT NẾU CÀI DOCKER + WINDMILL",
          "Ổ C: còn 28.7 GB. Sau khi cài còn ~17-22 GB → 7-9% dung lượng trống.",
          ["Thành phần", "Dung lượng", "Ghi chú"],
          [list(x) for x in DOCKER_COST],
          widths={"Thành phần": 34, "Dung lượng": 16, "Ghi chú": 54},
          wrap={"Ghi chú"}, color=colors)

    # 04 SO SÁNH
    sheet("04_SO_SANH", "SO SÁNH NĂNG LỰC",
          "Cột dagu là trạng thái thật đã kiểm chứng. Cột Windmill là tài liệu chính thức.",
          ["Tiêu chí", "dagu (đang chạy)", "Windmill (chưa cài)"],
          [list(x) for x in COMPARE],
          widths={"Tiêu chí": 26, "dagu (đang chạy)": 52, "Windmill (chưa cài)": 50},
          wrap={"dagu (đang chạy)", "Windmill (chưa cài)"})

    # 05 MCP
    sheet("05_DAGU_MCP", "dagu CÓ MCP TÍCH HỢP (phát hiện mới)",
          "Test thật: POST http://127.0.0.1:8080/mcp → initialize OK → tools/list trả 3 tool.",
          ["Tool", "Làm được gì", "Ý nghĩa cho dự án"],
          [list(x) for x in DAGU_MCP],
          widths={"Tool": 18, "Làm được gì": 56, "Ý nghĩa cho dự án": 52},
          wrap={"Làm được gì", "Ý nghĩa cho dự án"})

    # 06 CÂU HỎI
    rows = [[qid, q, why, opts, ""] for qid, q, why, opts in QUESTIONS]
    sheet("06_CAU_HOI", "CÂU HỎI CẦN ALAN TRẢ LỜI",
          "Điền vào cột cuối. Trả lời đủ Q1-Q10 → quyết định chính xác.",
          ["Mã", "Câu hỏi", "Vì sao quan trọng", "Lựa chọn gợi ý", "TRẢ LỜI CỦA ALAN"],
          rows,
          widths={"Mã": 6, "Câu hỏi": 46, "Vì sao quan trọng": 52,
                  "Lựa chọn gợi ý": 28, "TRẢ LỜI CỦA ALAN": 26},
          wrap={"Câu hỏi", "Vì sao quan trọng", "Lựa chọn gợi ý"})

    # 07 KHUYẾN NGHỊ
    sheet("07_KHUYEN_NGHI", "KHUYẾN NGHỊ",
          "Điều kiện để đổi quyết định được ghi rõ.",
          ["Khuyến nghị", "Lý do", "Điều kiện"],
          [list(x) for x in RECOMMEND],
          widths={"Khuyến nghị": 26, "Lý do": 60, "Điều kiện": 34},
          wrap={"Lý do", "Điều kiện"})

    path = OUT / "DECISION_dagu_vs_windmill.xlsx"
    wb.save(path)
    return path


def main() -> int:
    d = build_docx()
    x = build_xlsx()
    print(f"Questions: {len(QUESTIONS)}")
    print(f"Comparison rows: {len(COMPARE)}")
    for p in (d, x):
        print(f"Saved: {p.resolve()}  ({p.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

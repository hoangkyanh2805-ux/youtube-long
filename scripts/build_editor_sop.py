"""
SOP chi tiết cho đội edit 1 người (long + short + tương tác) + tích hợp AI/Claude.
Tính hiệu suất thật, tiêu chí build-to-sell.

Writes:
  outputs/reports/AZZAM_SOP_EDITOR.docx
  outputs/reports/AZZAM_SOP_EDITOR.xlsx
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

# Force UTF-8 console: without this, printing Vietnamese crashes with
# UnicodeEncodeError when stdout is a pipe (dagu/cron/CI).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402
ensure_utf8_console()

OUT = Path("outputs/reports")
OUT.mkdir(parents=True, exist_ok=True)

KPI = {"shorts": 3, "long": 1, "long_min": 8}

# ── Thời gian: truyền thống vs có SOP (phút) ────────────────────────────────
TIME_ROWS = [
    ("1. Chọn nguyên liệu", 30, 5, "Agent lọc từ 04_PAINPOOL_200, chọn 3 nhóm khác nhau"),
    ("2. Viết script", 60, 15, "Claude draft từ prompt 02/03, người sửa giọng"),
    ("3. Tìm tài nguyên", 120, 5, "Thư viện assets/ có sẵn — quy tắc 0-search"),
    ("4. Cắt ghép 3 Short", 180, 66, "Template Short 9:16, 22 phút/cái"),
    ("5. Cắt ghép Long 8 phút", 240, 100, "Template Long 16:9, có sẵn timeline mẫu"),
    ("6. Text / graphic / phụ đề", 90, 25, "AI auto-subtitle + preset có sẵn"),
    ("7. Audio + color", 45, 10, "Preset LUT + audio chain lưu sẵn"),
    ("8. Export + QC", 45, 20, "Preset export + checklist QC"),
    ("9. Tương tác kênh", 45, 30, "Comment ghim từ sheet 05, trả lời khán giả"),
]

# ── Lịch 1 ngày ─────────────────────────────────────────────────────────────
DAY_PLAN = [
    ("07:30", "08:00", "30'", "Chuẩn bị", "Chọn 3 pain point + 1 pillar Long. "
     "Claude draft hook + outline.", "3 pain point chốt, script nháp"),
    ("08:00", "08:20", "20'", "Duyệt script", "Sửa giọng, chốt hook 3 giây, "
     "chốt outline 5 phần", "Script final"),
    ("08:20", "08:40", "20'", "Chuẩn bị tài nguyên", "Mở asset library, "
     "copy chart clip + b-roll + nhạc + sfx vào timeline", "Timeline có sẵn tài nguyên"),
    ("08:40", "09:50", "70'", "Dựng Short 1-3", "3 Short, mỗi cái ~22 phút. "
     "Template có sẵn, chỉ thay nội dung", "3 Short export nháp"),
    ("09:50", "10:05", "15'", "Nghỉ", "—", "—"),
    ("10:05", "11:45", "100'", "Dựng Long 8 phút", "Theo outline 5 phần, "
     "dùng chart clip đã chuẩn bị", "Long export nháp"),
    ("11:45", "12:15", "30'", "Nghỉ trưa", "—", "—"),
    ("12:15", "12:45", "30'", "Phụ đề + text", "AI transcribe → sửa thuật ngữ → "
     "burn-in theo preset", "Phụ đề hoàn chỉnh"),
    ("12:45", "12:55", "10'", "Audio + color", "Áp preset, chuẩn hoá -14 LUFS", "Audio/color xong"),
    ("12:55", "13:15", "20'", "Export + QC", "Chạy checklist QC 8 điểm", "4 file final"),
    ("13:15", "13:35", "20'", "Packaging", "Title/desc/tag từ prompt 04, "
     "thumbnail 3 yếu tố", "Metadata + thumbnail"),
    ("13:35", "14:00", "25'", "Đăng + tương tác", "Đăng theo lịch, ghim comment, "
     "trả lời khán giả", "Đã đăng + comment ghim"),
    ("14:00", "14:30", "30'", "Buffer", "Việc phát sinh, bổ sung asset thiếu, "
     "học tool mới", "—"),
]

# ── Phân bổ tài nguyên ──────────────────────────────────────────────────────
RESOURCE_ROWS = [
    ("Máy tính", "1 máy đủ dựng video", "RAM ≥16GB, GPU rời nếu render 4K",
     "Bắt buộc", "Không dùng máy yếu — render sẽ là bottleneck"),
    ("Phần mềm dựng", "CapCut (miễn phí) hoặc Premiere", "CapCut đủ cho Short; "
     "Premiere nếu muốn template mạnh", "Bắt buộc", "Chọn 1, không đổi giữa chừng"),
    ("Template Short", "1 template 9:16", "Tự dựng 1 lần, tái sử dụng vô hạn",
     "Bắt buộc", "Đây là thứ tiết kiệm nhiều thời gian nhất"),
    ("Template Long", "1 template 16:9", "Có sẵn timeline 5 phần theo outline chuẩn",
     "Bắt buộc", "Dựng 1 lần, dùng mãi"),
    ("Asset library", "25 thư mục theo ASSET_TREE", "Xem assets/README.md",
     "Bắt buộc", "Quy tắc 0-search: không tìm tài nguyên trong lúc dựng"),
    ("AI/Claude", "1 tài khoản Claude", "Draft script, hook, SEO, sửa phụ đề",
     "Nên có", "Không dùng để cắt ghép — chất lượng chưa đạt"),
    ("Chart recording", "TradingView + OBS", "Tự quay clip chart mọi khung thời gian",
     "Bắt buộc", "Quay 1 buổi/tuần đủ dùng cả tuần"),
    ("Nhạc + SFX", "10 track + 15 sfx không bản quyền", "Pexels/Pixabay/YouTube Audio Library",
     "Bắt buộc", "Phải không bản quyền — tránh claim"),
    ("B-roll", "20-30 clip", "Pexels/Pixabay miễn phí",
     "Nên có", "Phân loại theo 02_BROLL/*"),
    ("Lưu trữ", "Ổ cứng ≥1TB hoặc cloud", "Video thô rất nặng",
     "Bắt buộc", "Backup hàng tuần, không để mất project"),
]

# ── Build-to-sell ───────────────────────────────────────────────────────────
BTS_ROWS = [
    ("Tài liệu hoá", "Mọi quy trình đều có file SOP, không nằm trong đầu 1 người",
     "Người mới đọc SOP làm được việc trong 2 ngày", "Có SOP + prompt pack + template"),
    ("Tài sản tái sử dụng", "Template, asset library, prompt pack dùng lại vô hạn",
     "Thời gian/ngày giảm ≥60% so với làm thủ công", "14.25h → 4.6h (giảm 68%)"),
    ("Không phụ thuộc cá nhân", "Bất kỳ editor nào đọc SOP cũng chạy được",
     "Thay người không gián đoạn sản xuất", "SOP + checklist QC + naming rule"),
    ("Đo lường được", "Mỗi công đoạn có thời gian mục tiêu và KPI",
     "Biết ngay khâu nào đang chậm", "Sheet 01/02 trong file Excel"),
    ("Tự động hoá phần lặp", "AI làm script/hook/SEO/phụ đề — không làm phần sáng tạo cốt lõi",
     "≥40% công đoạn có AI hỗ trợ", "Prompt pack 6 file"),
    ("Tài sản nội dung tích luỹ", "Video cũ thành kho nguyên liệu, không bỏ đi",
     "Video cũ vẫn kéo view và lead", "Playlist + remake candidate"),
    ("Quy trình chuyển giao được", "Toàn bộ nằm trong repo, version-controlled",
     "Bán/chuyển giao kèm hệ thống chạy được", "Repo + SOP + asset + prompt"),
    ("Chất lượng kiểm soát được", "Checklist QC cố định, không phụ thuộc cảm hứng",
     "Tỷ lệ video phải sửa lại <10%", "Checklist 8 điểm trong SOP"),
]

# ── Workflow AI integration ─────────────────────────────────────────────────
AI_ROWS = [
    ("Chọn pain point", "Agent đọc CSV, lọc score, chọn 3 nhóm khác nhau",
     "prompts/01_CHON_PAINPOINT.md", "5 phút", "Người chốt cuối"),
    ("Viết hook", "Claude draft 5 biến thể/cái, chọn mạnh nhất",
     "prompts/02_VIET_HOOK.md", "5 phút", "Người sửa giọng"),
    ("Outline Long", "Claude draft 5 phần có timestamp",
     "prompts/03_OUTLINE_LONG.md", "10 phút", "Người kiểm tra logic"),
    ("SEO/packaging", "Claude draft title/desc/tag theo pattern",
     "prompts/04_SEO_PACKAGING.md", "5 phút", "Người duyệt"),
    ("Phụ đề", "AI transcribe → Claude sửa thuật ngữ",
     "prompts/05_PHU_DE_QC.md", "10 phút", "Người spot-check"),
    ("Tương tác", "Claude draft comment ghim + trả lời",
     "prompts/06_TUONG_TAC.md", "10 phút", "Người duyệt trước khi đăng"),
    ("Cắt ghép video", "KHÔNG dùng AI — chất lượng chưa đạt",
     "—", "—", "Editor làm tay theo template"),
    ("Thumbnail", "KHÔNG dùng AI — chữ tiếng Việt dễ sai",
     "—", "—", "Editor làm tay theo template"),
]

# ── Checklist QC ────────────────────────────────────────────────────────────
QC_ROWS = [
    ("Hook", "3 giây đầu nêu thẳng nỗi đau, không logo/intro", "Bắt buộc"),
    ("Phụ đề", "Khớp tiếng nói, thuật ngữ viết đúng", "Bắt buộc"),
    ("Guardrail", "Không cam kết lợi nhuận, không trade giả", "Bắt buộc — chặn đăng"),
    ("Tỷ lệ", "9:16 cho Short, 16:9 cho Long", "Bắt buộc"),
    ("Âm lượng", "Chuẩn hoá -14 LUFS", "Bắt buộc"),
    ("Tên file", "Theo quy tắc <loại>_<chủ đề>_<biến thể>_<version>", "Bắt buộc"),
    ("Metadata", "Title ≤60 ký tự, có disclaimer, timestamp khớp", "Bắt buộc"),
    ("Nguồn pain point", "Comment ID ghi vào sheet 09_THEO_DOI", "Bắt buộc"),
]

# ── Rủi ro ──────────────────────────────────────────────────────────────────
RISK_ROWS = [
    ("1 người ốm/nghỉ", "Sản xuất dừng hoàn toàn",
     "Quay trước 2 ngày buffer; SOP đủ để người khác chạy thay", "Cao"),
    ("Template bị lỗi sau update phần mềm", "Mất thời gian dựng lại",
     "Backup project template; không update phần mềm giữa tuần", "Trung bình"),
    ("AI draft sai số liệu trading", "Đăng thông tin sai, mất uy tín",
     "Prompt cấm bịa số; người verify mọi con số", "Cao"),
    ("Asset vi phạm bản quyền", "Video bị claim, mất doanh thu",
     "Chỉ dùng nhạc/b-roll miễn phí có giấy phép rõ; ghi vào ASSET_INDEX", "Cao"),
    ("Kiệt sức vì khối lượng 4 video/ngày", "Chất lượng giảm, bỏ cuộc",
     "Giữ buffer 204 phút/ngày; 1 ngày/tuần chỉ làm Long + tương tác", "Cao"),
    ("Phụ thuộc 1 người", "Không bán/chuyển giao được",
     "Tài liệu hoá toàn bộ (build-to-sell); mọi thứ trong repo", "Cao"),
]


# ── DOCX ────────────────────────────────────────────────────────────────────

def build_docx() -> Path:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt, RGBColor

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10.5)
    st.paragraph_format.space_after = Pt(4)

    t = doc.add_heading("SOP ĐỘI EDIT — 1 NGƯỜI VẬN HÀNH 3 SHORT + 1 LONG/NGÀY", level=0)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s = doc.add_paragraph()
    s.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = s.add_run("Kênh @azzammastertradinggold  •  Ngách XAUUSD / Forex")
    r.bold = True
    r.font.size = Pt(12)
    m = doc.add_paragraph()
    m.alignment = WD_ALIGN_PARAGRAPH.CENTER
    m.add_run(f"Ngày lập: {date.today().isoformat()}  •  "
              "Vai trò: MrBeast niche trading").italic = True
    doc.add_paragraph()

    def table(headers, rows, widths_note=None):
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

    # 1. Vấn đề
    doc.add_heading("1. VẤN ĐỀ CẦN GIẢI", level=1)
    doc.add_paragraph(
        "Một editor phải làm 3 Short + 1 Long 8 phút + tương tác kênh mỗi ngày. "
        "Nếu làm theo cách thông thường, khối lượng này mất khoảng 14,25 giờ — "
        "không khả thi với 1 người. Nút cổ chai lớn nhất là TÌM TÀI NGUYÊN "
        "(120 phút/ngày) và CẮT GHÉP (420 phút/ngày)."
    )
    p = doc.add_paragraph()
    pr = p.add_run(
        "Mục tiêu của SOP: đưa tổng thời gian xuống dưới 5 giờ/ngày bằng 3 đòn: "
        "(a) thư viện tài nguyên sẵn có — quy tắc 0-search, (b) template tái sử dụng, "
        "(c) AI lo phần chữ (script, hook, SEO, phụ đề)."
    )
    pr.bold = True
    doc.add_paragraph()

    # 2. Hiệu suất
    doc.add_heading("2. TÍNH HIỆU SUẤT — TRƯỚC VÀ SAU SOP", level=1)
    rows = [[a, f"{b} phút", f"{c} phút", f"{b-c} phút", d] for a, b, c, d in TIME_ROWS]
    total_trad = sum(x[1] for x in TIME_ROWS)
    total_sop = sum(x[2] for x in TIME_ROWS)
    rows.append(["TỔNG", f"{total_trad} phút", f"{total_sop} phút",
                 f"{total_trad-total_sop} phút", ""])
    rows.append(["", f"{total_trad/60:.2f} giờ", f"{total_sop/60:.2f} giờ",
                 f"giảm {(1-total_sop/total_trad)*100:.0f}%", ""])
    table(["Công đoạn", "Truyền thống", "Có SOP", "Tiết kiệm", "Cách đạt được"], rows)

    p = doc.add_paragraph()
    pr = p.add_run(
        f"Kết luận khả thi: {total_sop/60:.1f} giờ/ngày cho 1 người, còn "
        f"{(8 - total_sop/60)*60:.0f} phút buffer cho việc phát sinh. "
        "Con số này chỉ đạt được nếu tuân thủ đúng 3 điều kiện: thư viện tài nguyên "
        "phải có sẵn TRƯỚC khi dựng, template phải dựng 1 lần rồi tái sử dụng, "
        "và AI phải draft xong phần chữ trước khi bắt đầu cắt."
    )
    pr.bold = True
    doc.add_paragraph()

    # 3. Lịch ngày
    doc.add_heading("3. LỊCH MỘT NGÀY (14:30 kết thúc, có buffer)", level=1)
    table(["Bắt đầu", "Kết thúc", "Thời lượng", "Công đoạn", "Việc cụ thể", "Output"],
          [list(x) for x in DAY_PLAN])
    doc.add_paragraph(
        "Nguyên tắc xếp lịch: gom việc giống nhau lại (3 Short dựng liền nhau để "
        "không phải đổi tư duy), đặt phần cần tập trung cao (dựng Long) vào lúc "
        "năng lượng tốt nhất, để tương tác kênh cuối ngày vì không cần tập trung sâu."
    )
    doc.add_paragraph()

    # 4. Tài nguyên
    doc.add_heading("4. PHÂN BỔ TÀI NGUYÊN", level=1)
    table(["Hạng mục", "Cần gì", "Chi tiết", "Mức độ", "Ghi chú"],
          [list(x) for x in RESOURCE_ROWS])
    doc.add_paragraph(
        "Không cần đầu tư lớn để bắt đầu. Thứ tốn kém nhất không phải thiết bị mà "
        "là THỜI GIAN DỰNG TEMPLATE lần đầu — dựng 1 lần, dùng cho hàng trăm video."
    )
    doc.add_paragraph()

    # 5. Asset library
    doc.add_heading("5. THƯ VIỆN TÀI NGUYÊN — QUY TẮC 0-SEARCH", level=1)
    doc.add_paragraph(
        "Đã dựng sẵn cấu trúc 25 thư mục tại assets/ (xem assets/README.md). "
        "Quy tắc số 1: KHÔNG BAO GIỜ tìm tài nguyên trong lúc dựng. Mọi thứ phải "
        "có sẵn trước. Tài nguyên mới phải nhập vào thư viện ngay khi tải về, "
        "không để ở Desktop."
    )
    table(["Thư mục", "Chứa gì", "Tần suất cập nhật"],
          [["00_BRAND", "logo, intro, outro, font, màu", "1 lần khi setup"],
           ["01_CHART_CLIPS", "clip chart theo cặp + khung thời gian", "hàng ngày"],
           ["02_BROLL", "cảnh quay nền theo chủ đề", "hàng tuần"],
           ["03_AUDIO", "nhạc, sfx, voice-over", "hàng tuần"],
           ["04_TEMPLATES", "project template Short/Long/Live", "khi tối ưu"],
           ["05_SUBTITLE_PRESETS", "preset phụ đề", "1 lần"],
           ["06_THUMBNAIL", "nền, mặt, element thumbnail", "hàng tuần"],
           ["07_SCRIPTS", "kho hook + outline đã dùng", "hàng ngày"],
           ["08_EXPORTS", "video thành phẩm", "hàng ngày"]])
    doc.add_paragraph()
    p = doc.add_paragraph()
    pr = p.add_run("Quy tắc đặt tên: <loại>_<chủ đề>_<biến thể>_<phiên bản>.<ext>")
    pr.bold = True
    doc.add_paragraph("Ví dụ: chart_xauusd_m15_london_bias_v3.mp4")
    doc.add_paragraph("Không dùng: final, final2, new, untitled, Screen Recording 2024-...")
    doc.add_paragraph()

    # 6. AI integration
    doc.add_heading("6. TÍCH HỢP AI / CLAUDE VÀO WORKFLOW", level=1)
    doc.add_paragraph(
        "Đã tạo prompt pack 7 file tại prompts/ — copy-paste trực tiếp vào Claude. "
        "Nguyên tắc: AI làm phần CHỮ, người làm phần HÌNH. AI chưa đủ tốt để cắt "
        "ghép video hoặc làm thumbnail tiếng Việt."
    )
    table(["Công đoạn", "AI làm gì", "File prompt", "Thời gian", "Người duyệt"],
          [list(x) for x in AI_ROWS])
    doc.add_paragraph()
    p = doc.add_paragraph()
    pr = p.add_run("3 quy tắc bắt buộc khi dùng AI:")
    pr.bold = True
    doc.add_paragraph("1. AI không được bịa số liệu trading — mọi con số phải từ file dữ liệu thật.", style="List Number")
    doc.add_paragraph("2. AI không cam kết lợi nhuận — prompt phải có dòng cấm.", style="List Number")
    doc.add_paragraph("3. Người duyệt trước khi đăng — AI chỉ draft, không tự publish.", style="List Number")
    doc.add_paragraph()

    # 7. QC
    doc.add_heading("7. CHECKLIST QC TRƯỚC KHI ĐĂNG", level=1)
    table(["Hạng mục", "Tiêu chí", "Mức độ"], [list(x) for x in QC_ROWS])
    doc.add_paragraph(
        "Mục 'Guardrail' là điều kiện CHẶN ĐĂNG: nếu video có cam kết lợi nhuận "
        "hoặc show trade giả, không được đăng dù mọi thứ khác đạt."
    )
    doc.add_paragraph()

    # 8. Build to sell
    doc.add_heading("8. TIÊU CHÍ BUILD-TO-SELL", level=1)
    doc.add_paragraph(
        "Hệ thống này được thiết kế để CHUYỂN GIAO ĐƯỢC, không phụ thuộc một cá nhân. "
        "Nếu sau này muốn bán kênh, thuê thêm người, hoặc nhân bản sang ngách khác, "
        "mọi thứ cần thiết đã nằm trong repo."
    )
    table(["Tiêu chí", "Nghĩa là", "Ngưỡng đo được", "Bằng chứng trong hệ thống"],
          [list(x) for x in BTS_ROWS])
    doc.add_paragraph()
    p = doc.add_paragraph()
    pr = p.add_run("Kiểm tra build-to-sell: ")
    pr.bold = True
    p.add_run(
        "nếu editor hiện tại nghỉ hôm nay, một người mới đọc SOP này có thể chạy "
        "được 3 Short + 1 Long trong ngày đầu tiên không? Nếu câu trả lời là không, "
        "SOP chưa đủ tốt."
    )
    doc.add_paragraph()

    # 9. Rủi ro
    doc.add_heading("9. RỦI RO VÀ CÁCH XỬ LÝ", level=1)
    table(["Rủi ro", "Hậu quả", "Cách xử lý", "Mức độ"],
          [list(x) for x in RISK_ROWS])
    doc.add_paragraph()

    # 10. Việc cần duyệt
    doc.add_heading("10. VIỆC CẦN ALAN DUYỆT TRƯỚC KHI CHẠY", level=1)
    for txt in [
        "Ngôn ngữ kênh: tiếng Việt hay tiếng Anh (ảnh hưởng toàn bộ hook + title).",
        "Phần mềm dựng chốt: CapCut hay Premiere (chọn 1, không đổi giữa chừng).",
        "Tài khoản Claude cho editor (nếu chưa có).",
        "Ngân sách tài nguyên: nhạc/b-roll miễn phí hay mua bản quyền.",
        "Kênh Telegram đích để gắn CTA.",
        "Duyệt bộ comment tương tác trước khi đăng lần đầu.",
    ]:
        doc.add_paragraph(txt, style="List Number")

    path = OUT / "AZZAM_SOP_EDITOR.docx"
    doc.save(path)
    return path


# ── XLSX ────────────────────────────────────────────────────────────────────

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

    wb = Workbook()
    used = [False]

    def sheet(name, title, note, headers, rows, widths=None, numbers=None, wrap=None):
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
                                        wrap_text=(headers[j-1] in (wrap or set())))
                if numbers and headers[j-1] in numbers and isinstance(v, (int, float)):
                    c.number_format = "#,##0"
        for j, h in enumerate(headers, 1):
            L = get_column_letter(j)
            if widths and h in widths:
                ws.column_dimensions[L].width = widths[h]
            else:
                longest = len(str(h))
                for row in rows[:200]:
                    if j - 1 < len(row):
                        longest = max(longest, len(str(row[j-1])))
                ws.column_dimensions[L].width = min(max(longest + 2, 10), 70)
        if rows:
            ws.auto_filter.ref = f"A{hr}:{get_column_letter(len(headers))}{hr+len(rows)}"
        ws.freeze_panes = ws.cell(row=hr + 1, column=1)
        return ws

    # 01 HIỆU SUẤT
    rows = [[a, b, c, b - c, d] for a, b, c, d in TIME_ROWS]
    tt = sum(x[1] for x in TIME_ROWS)
    ts = sum(x[2] for x in TIME_ROWS)
    rows.append(["TỔNG (phút)", tt, ts, tt - ts, ""])
    rows.append(["TỔNG (giờ)", round(tt/60, 2), round(ts/60, 2),
                 f"giảm {(1-ts/tt)*100:.0f}%", ""])
    sheet("01_HIEU_SUAT", "TÍNH HIỆU SUẤT — TRƯỚC VÀ SAU SOP",
          f"1 người làm {KPI['shorts']} Short + {KPI['long']} Long "
          f"{KPI['long_min']} phút. Đơn vị: phút.",
          ["Công đoạn", "Truyền thống", "Có SOP", "Tiết kiệm", "Cách đạt được"],
          rows,
          widths={"Công đoạn": 28, "Truyền thống": 13, "Có SOP": 11,
                  "Tiết kiệm": 12, "Cách đạt được": 55},
          numbers={"Truyền thống", "Có SOP", "Tiết kiệm"},
          wrap={"Cách đạt được"})

    # 02 LỊCH NGÀY
    sheet("02_LICH_NGAY", "LỊCH MỘT NGÀY",
          "Kết thúc 14:30, còn 30 phút buffer. Không nhảy bước.",
          ["Bắt đầu", "Kết thúc", "Thời lượng", "Công đoạn", "Việc cụ thể", "Output"],
          [list(x) for x in DAY_PLAN],
          widths={"Bắt đầu": 10, "Kết thúc": 10, "Thời lượng": 11,
                  "Công đoạn": 24, "Việc cụ thể": 55, "Output": 32},
          wrap={"Việc cụ thể", "Output"})

    # 03 TÀI NGUYÊN
    sheet("03_TAI_NGUYEN", "PHÂN BỔ TÀI NGUYÊN",
          "Không cần đầu tư lớn — thứ tốn nhất là thời gian dựng template lần đầu.",
          ["Hạng mục", "Cần gì", "Chi tiết", "Mức độ", "Ghi chú"],
          [list(x) for x in RESOURCE_ROWS],
          widths={"Hạng mục": 18, "Cần gì": 30, "Chi tiết": 45,
                  "Mức độ": 12, "Ghi chú": 45},
          wrap={"Cần gì", "Chi tiết", "Ghi chú"})

    # 04 AI WORKFLOW
    sheet("04_AI_WORKFLOW", "TÍCH HỢP AI / CLAUDE",
          "AI làm phần chữ, người làm phần hình. Prompt pack ở thư mục prompts/.",
          ["Công đoạn", "AI làm gì", "File prompt", "Thời gian", "Người duyệt"],
          [list(x) for x in AI_ROWS],
          widths={"Công đoạn": 22, "AI làm gì": 50, "File prompt": 32,
                  "Thời gian": 11, "Người duyệt": 26},
          wrap={"AI làm gì", "Người duyệt"})

    # 05 BUILD TO SELL
    sheet("05_BUILD_TO_SELL", "TIÊU CHÍ BUILD-TO-SELL",
          "Kiểm tra: nếu editor nghỉ hôm nay, người mới đọc SOP có chạy được không?",
          ["Tiêu chí", "Nghĩa là", "Ngưỡng đo được", "Bằng chứng"],
          [list(x) for x in BTS_ROWS],
          widths={"Tiêu chí": 24, "Nghĩa là": 50, "Ngưỡng đo được": 42,
                  "Bằng chứng": 42},
          wrap={"Nghĩa là", "Ngưỡng đo được", "Bằng chứng"})

    # 06 QC
    sheet("06_CHECKLIST_QC", "CHECKLIST QC TRƯỚC KHI ĐĂNG",
          "Mục Guardrail là điều kiện CHẶN ĐĂNG.",
          ["Hạng mục", "Tiêu chí", "Mức độ"],
          [list(x) for x in QC_ROWS],
          widths={"Hạng mục": 22, "Tiêu chí": 62, "Mức độ": 26},
          wrap={"Tiêu chí"})

    # 07 RỦI RO
    sheet("07_RUI_RO", "RỦI RO VÀ CÁCH XỬ LÝ",
          "Rủi ro mức Cao phải có phương án trước khi chạy.",
          ["Rủi ro", "Hậu quả", "Cách xử lý", "Mức độ"],
          [list(x) for x in RISK_ROWS],
          widths={"Rủi ro": 32, "Hậu quả": 38, "Cách xử lý": 55, "Mức độ": 12},
          wrap={"Hậu quả", "Cách xử lý"})

    # 08 THEO DÕI HIỆU SUẤT
    sheet("08_THEO_DOI_GIO", "BẢNG THEO DÕI GIỜ THỰC TẾ (điền mỗi ngày)",
          "Điền giờ thực tế để biết khâu nào đang chậm hơn mục tiêu.",
          ["Ngày", "Chọn nguyên liệu", "Viết script", "Tìm tài nguyên",
           "Dựng 3 Short", "Dựng Long", "Phụ đề/text", "Audio/color",
           "Export/QC", "Tương tác", "TỔNG", "Ghi chú"],
          [[""] * 12 for _ in range(31)],
          widths={"Ngày": 12, "Chọn nguyên liệu": 14, "Viết script": 12,
                  "Tìm tài nguyên": 14, "Dựng 3 Short": 13, "Dựng Long": 11,
                  "Phụ đề/text": 12, "Audio/color": 12, "Export/QC": 11,
                  "Tương tác": 11, "TỔNG": 10, "Ghi chú": 30})

    path = OUT / "AZZAM_SOP_EDITOR.xlsx"
    wb.save(path)
    return path


def main() -> int:
    d = build_docx()
    x = build_xlsx()
    tt = sum(r[1] for r in TIME_ROWS)
    ts = sum(r[2] for r in TIME_ROWS)
    print(f"Time traditional: {tt} min ({tt/60:.2f} h)")
    print(f"Time with SOP   : {ts} min ({ts/60:.2f} h)")
    print(f"Reduction       : {(1-ts/tt)*100:.0f}%")
    print(f"Buffer/day      : {(8-ts/60)*60:.0f} min")
    for p in (d, x):
        print(f"Saved: {p.resolve()}  ({p.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

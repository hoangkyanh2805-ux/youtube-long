#!/usr/bin/env python3
"""SINH TRANG HƯỚNG DẪN (SOP GUIDE) CHO TỪNG BÁO CÁO — click là biết làm.

Vấn đề: báo cáo gửi Telegram dài, người nhận đọc xong vẫn không biết BẮT ĐẦU TỪ ĐÂU,
mở file nào, làm bước nào trước. Editor/team phải hỏi lại.

Giải pháp: mỗi báo cáo có 1 TRANG HƯỚNG DẪN riêng, chuẩn SOP:
    5W1H   — What / Why / Who / When / Where / How
    SOP    — các bước đánh số, có checkbox
    VIỆC NGAY — 1 khối "làm gì tiếp theo" không thể hiểu sai
    FILE   — bảng đường dẫn click được (mở trực tiếp, không cần tìm)
    HIỆU SUẤT — tiết kiệm gì, đo bằng gì
    BUILD-TO-SELL — phần nào bán được / tái sử dụng được

Báo cáo Telegram chỉ gửi TÓM TẮT + LINK tới trang này.

Xuất:
    outputs/dashboard/guides.html            — mục lục mọi hướng dẫn
    outputs/dashboard/guides/<id>.html       — 1 trang/báo cáo
    (build_static_deploy.py copy sang deploy/ để lên dashboard.azzamedu.com)

Usage:
    python scripts/build_sop_guides.py
    python scripts/build_sop_guides.py --list
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "outputs" / "dashboard"
GUIDES = DASH / "guides"
SITE = "https://dashboard.azzamedu.com"

# ─────────────────────────────────────────────────────────────────────────────
# REGISTRY — nguồn sự thật duy nhất. Thêm báo cáo mới = thêm 1 entry ở đây.
# Mỗi entry phải trả lời được: người nhận mở ra, 30 giây sau biết làm gì.
# ─────────────────────────────────────────────────────────────────────────────
GUIDES_REGISTRY: list[dict] = [
    {
        "id": "p06-audience",
        "code": "P06",
        "title": "Phân khúc khán giả giá trị nhất",
        "owner": "content_bridge",
        "what": "Chấm điểm 7 nhóm khán giả có thể nhắm, từ 2,567 comment thật của khán giả ngách trading. Chọn ra nhóm nên đánh TRƯỚC.",
        "why": "Kênh đang làm nội dung cho 'mọi người' → không ai thấy mình trong đó. Biết nhóm cụ thể thì hook, thumbnail, tiêu đề mới trúng. Comment rate hiện 0.0111% vì nội dung không chạm được ai.",
        "who": "Alan duyệt nhóm mục tiêu. content_bridge giữ. Editor đọc để biết giọng.",
        "when": "1 lần, rồi xem lại mỗi 30 ngày khi có dữ liệu comment mới.",
        "where": "Duyệt ở Telegram topic 13 (Mục tiêu). File ở dashboard mục Dây chuyền sản xuất.",
        "how": "Đọc bảng chấm điểm → xem cột 'Điểm/100' → đọc chân dung nhóm điểm cao nhất → chốt nhóm đánh trước.",
        "sop": [
            "Mở file AUDIENCE_SEGMENTS.md, xem bảng 'BẢNG CHẤM ĐIỂM' ở mục 1.",
            "Đọc cột Điểm/100 — nhóm cao nhất là nhóm nên đánh trước (hiện: SEG-B Trader đã cháy tài khoản, 100/100).",
            "Đọc mục 2 'CHỌN PHÂN KHÚC NÊN ĐÁNH TRƯỚC' — có chân dung, nỗi đau, hook mẫu.",
            "Đối chiếu cột 'Comment' và 'Sales-angle ev' — hai nguồn KHÔNG phủ nhau, đừng chỉ nhìn 1 cột.",
            "Chốt nhóm đánh trước, ghi vào Telegram topic 13.",
            "Chuyển sang hướng dẫn P10 (SEO) — vì tiêu đề phải khớp nhóm đã chốt.",
        ],
        "next_action": "Chốt 1 nhóm đánh trước và trả lời topic 13. Nếu không chốt, P10/P11 vẫn chạy nhưng có thể lệch giọng.",
        "files": [
            ("AUDIENCE_SEGMENTS.md — bảng chấm điểm + chân dung", "outputs/strategy/AUDIENCE_SEGMENTS.md"),
            ("AUDIENCE_SEGMENTS.csv — dữ liệu thô để lọc", "outputs/strategy/AUDIENCE_SEGMENTS.csv"),
            ("AZZAM_AUDIENCE_SEGMENTS.docx — bản Word in ra", "outputs/reports/AZZAM_AUDIENCE_SEGMENTS.docx"),
            ("AZZAM_AUDIENCE_SEGMENTS.xlsx — Excel 3 sheet", "outputs/reports/AZZAM_AUDIENCE_SEGMENTS.xlsx"),
        ],
        "data": [("AUDIENCE_SEGMENTS.csv", "data/AUDIENCE_SEGMENTS.csv")],
        "efficiency": [
            ("Trước", "Chọn nhóm khán giả bằng cảm giác, làm 5-10 video mới biết sai"),
            ("Sau", "Chấm điểm từ 2,567 comment thật — biết trước khi quay"),
            ("Đo bằng", "Comment rate (mục tiêu > 0.05%, hiện 0.0111%) và sub ròng (hiện -3)"),
        ],
        "sell": "Phân khúc SEG-G (broker/prop firm) có khả năng chi cao nhất → đây là nhóm để gắn affiliate broker. SEG-B (cháy tài khoản) là nhóm mua khoá risk management.",
        "guardrail": "Cột 'Tiền' là đánh giá ĐỊNH TÍNH — không có dữ liệu RPM thật. Phải cắm affiliate link rồi đo mới có số thật.",
    },
    {
        "id": "p10-seo",
        "code": "P10",
        "title": "Gói SEO: tiêu đề, mô tả, tag",
        "owner": "content_bridge",
        "what": "24 gói SEO, mỗi video 1 gói: 5 mẫu tiêu đề, mô tả 150-200 từ có timestamp, 20 tag, 3 hashtag, khung giờ đăng.",
        "why": "Kênh chỉ có 1.2% traffic từ search. Tiêu đề/mô tả/tag quyết định video có được tìm thấy không. Tag lấy từ từ khoá THẬT khán giả dùng (200 long-tail mine từ comment), không phải tag đoán.",
        "who": "Editor copy-paste khi upload. content_bridge sinh. Alan duyệt trước khi đăng.",
        "when": "Mỗi lần upload video. Gói đã có sẵn, không cần sinh lại.",
        "where": "Copy trực tiếp từ file, dán vào YouTube Studio.",
        "how": "Mở file → tìm đúng chủ đề → chọn 1 trong 5 tiêu đề → copy mô tả nguyên khối → copy dòng tag → dán vào YouTube.",
        "sop": [
            "Mở SEO_PACKAGES.md, tìm mục có số STT trùng với video đang upload.",
            "Xem bảng '5 mẫu tiêu đề' — chọn 1 mẫu. Kiểm tra cột 'Ký tự' phải ≤ 60.",
            "Copy khối trong dấu ``` ở 'Mô tả (copy nguyên khối)' — dán vào ô Description.",
            "Kiểm tra mô tả có 150-200 từ (file ghi rõ số từ). Không sửa thêm, từ khoá đã rải sẵn.",
            "Copy dòng tag (20 tag, phân cách bằng dấu phẩy) — dán vào ô Tags.",
            "Copy 3 hashtag — dán vào cuối mô tả.",
            "Chọn khung giờ đăng theo bảng 'Khung giờ đăng' — đăng ĐÚNG GIỜ cố định để thuật toán học quy luật.",
        ],
        "next_action": "Chọn 1 trong 5 tiêu đề cho video hôm nay và dán nguyên khối mô tả. Không tự viết lại.",
        "files": [
            ("SEO_PACKAGES.md — copy-paste được luôn", "outputs/strategy/SEO_PACKAGES.md"),
            ("SEO_PACKAGES.json — bản máy đọc", "outputs/strategy/SEO_PACKAGES.json"),
            ("AZZAM_SEO_PACKAGES.docx — Word 3 sheet", "outputs/reports/AZZAM_SEO_PACKAGES.docx"),
            ("AZZAM_SEO_PACKAGES.xlsx — Excel", "outputs/reports/AZZAM_SEO_PACKAGES.xlsx"),
        ],
        "data": [("SEO_PACKAGES.json", "data/SEO_PACKAGES.json")],
        "efficiency": [
            ("Trước", "Mỗi video 30-45 phút nghĩ tiêu đề + mô tả + tag"),
            ("Sau", "Copy-paste 3 phút, từ khoá từ dữ liệu thật"),
            ("Đo bằng", "CTR và % traffic từ YouTube Search (hiện 1.2%)"),
        ],
        "sell": "Tag mượn view đối thủ — video mình xuất hiện cạnh video họ trong Suggested. Đây là kênh traffic miễn phí để đưa người xem vào phễu affiliate.",
        "guardrail": "Không nhồi keyword/tag rác. Không dùng tiêu đề gây hiểu sai (ví dụ hứa lợi nhuận).",
    },
    {
        "id": "p11-thumbnail",
        "code": "P11",
        "title": "Concept thumbnail + Design Brief",
        "owner": "content_bridge → Designer/Editor",
        "what": "72 concept thumbnail (24 video × 3), 5 archetype, kèm prompt AI tạo hình và brief chi tiết cho designer.",
        "why": "Thumbnail quyết định CTR. Nếu CTR thấp, mọi nỗ lực về nội dung đều vô nghĩa vì không ai bấm vào. Brief rõ để designer không phải đoán và không phải sửa nhiều vòng.",
        "who": "Designer/Editor thực thi. platform_ux review khả năng đọc trên mobile. Alan chọn concept.",
        "when": "Cùng lúc với edit video, TRƯỚC khi upload.",
        "where": "DESIGN_BRIEF.md cho designer. THUMBNAIL_CONCEPTS.md để lấy prompt AI.",
        "how": "Mở brief → tìm STT video → đọc concept được chỉ định → dùng prompt AI hoặc tự thiết kế → làm 2 biến thể A/B → nghiệm thu.",
        "sop": [
            "Mở DESIGN_BRIEF.md, đọc mục 1 'QUY TẮC BẮT BUỘC' (10 quy tắc) — đây là điều kiện bắt buộc.",
            "Xem bảng màu ở mục 2. Nền #0D1117, nhấn vàng #FFD400. Đỏ và xanh mỗi thứ tối đa 1 điểm.",
            "Tìm STT video trong bảng mục 4 'DANH SÁCH VIỆC THEO VIDEO' → cột 'Concept' là archetype chính.",
            "Mở THUMBNAIL_CONCEPTS.md, tìm concept đó, copy 'Prompt AI' nếu muốn dùng AI tạo hình.",
            "Làm 2 biến thể A/B. Ghi rõ biến thể nào là chính.",
            "Nghiệm thu theo mục 5: thu nhỏ về 120px còn đọc được chữ? Chuyển grayscale vẫn đọc được?",
            "Đặt tên file: <stt>-<topic-slug>-<A|B>.png — ví dụ 01-stop-loss-dung-cach-A.png",
        ],
        "next_action": "Chọn concept cho video đầu tiên, làm 2 biến thể A/B, tự test ở 120px trước khi giao.",
        "files": [
            ("DESIGN_BRIEF.md — brief cho designer", "outputs/strategy/DESIGN_BRIEF.md"),
            ("THUMBNAIL_CONCEPTS.md — 72 concept + prompt AI", "outputs/strategy/THUMBNAIL_CONCEPTS.md"),
            ("THUMBNAIL_CONCEPTS.json — bản máy đọc", "outputs/strategy/THUMBNAIL_CONCEPTS.json"),
            ("AZZAM_THUMBNAIL_BRIEF.docx — Word", "outputs/reports/AZZAM_THUMBNAIL_BRIEF.docx"),
            ("AZZAM_THUMBNAIL_BRIEF.xlsx — Excel có prompt AI", "outputs/reports/AZZAM_THUMBNAIL_BRIEF.xlsx"),
        ],
        "data": [("THUMBNAIL_CONCEPTS.json", "data/THUMBNAIL_CONCEPTS.json")],
        "efficiency": [
            ("Trước", "Designer tự nghĩ concept, sửa 3-5 vòng vì không đúng ý"),
            ("Sau", "Brief có concept + bảng màu + tiêu chí nghiệm thu → 1-2 vòng"),
            ("Đo bằng", "CTR theo biến thể A/B; số vòng sửa"),
        ],
        "sell": "Thumbnail nhất quán giúp kênh nhận diện được → người xem quay lại → tệp khán giả trung thành là nền để bán VIP group.",
        "guardrail": "KHÔNG hình gây hiểu sai. KHÔNG giả mạo kết quả trading. KHÔNG hiện số dư tài khoản hoặc số lợi nhuận — kể cả của chính mình.",
    },
    {
        "id": "p05-repurpose",
        "code": "P05",
        "title": "Đa nền tảng: 1 video → 5 định dạng",
        "owner": "content_bridge → Editor",
        "what": "120 asset: 24 video × 5 định dạng (Short, bài chữ, carousel, bài quan điểm, checklist). Mỗi định dạng một GÓC khác nhau.",
        "why": "Đây là khâu nặng nhất trong dây chuyền. Một video long 8 phút chỉ dùng 1 lần là lãng phí. Cùng nội dung đó cắt thành 5 thứ khác nhau → phủ nhiều nền tảng, cùng thời gian quay.",
        "who": "Editor thực thi. content_bridge sinh gói. Alan duyệt trước khi đăng.",
        "when": "Ngay sau khi có video long. Short cắt TỪ video long, không quay riêng.",
        "where": "REPURPOSE_PACKAGES.md để làm. EDITOR_HANDOFF.md để biết nhận gì, giao gì.",
        "how": "Mở handoff → xem bảng giao việc → với mỗi video: dựng long → cắt 3 Short → viết 1 bài chữ → 1 carousel → 1 checklist.",
        "sop": [
            "Mở EDITOR_HANDOFF.md, đọc 'Quy trình nhận việc' (5 bước) và 'Bảng giao việc'.",
            "Mở REPURPOSE_PACKAGES.md, tìm STT video đang làm.",
            "Phần F1 Short: đọc 'Nhịp kịch bản' (5 đoạn có mốc giây), làm theo đúng mốc.",
            "Cắt Short từ CHÍNH video long — dùng đoạn cao trào, không quay lại.",
            "Phần F2 bài chữ: copy nội dung trong khối ```, đăng Facebook/LinkedIn.",
            "Phần F3 carousel: 9 slide, mỗi slide 1 ý, chữ tối đa 15 từ.",
            "Phần F5 checklist: in ra, dán cạnh màn hình — đây là lead magnet cho Telegram.",
            "Kiểm tra 'Nguyên tắc nguyên liệu' trong handoff trước khi giao.",
        ],
        "next_action": "Video đầu tiên: dựng long theo outline, cắt 3 Short, viết 1 bài chữ. Checklist in ra làm lead magnet.",
        "files": [
            ("EDITOR_HANDOFF.md — brief giao việc + nghiệm thu", "outputs/strategy/EDITOR_HANDOFF.md"),
            ("REPURPOSE_PACKAGES.md — 5 định dạng mỗi video", "outputs/strategy/REPURPOSE_PACKAGES.md"),
            ("REPURPOSE_PACKAGES.json — bản máy đọc", "outputs/strategy/REPURPOSE_PACKAGES.json"),
            ("AZZAM_REPURPOSE.docx — Word", "outputs/reports/AZZAM_REPURPOSE.docx"),
            ("AZZAM_REPURPOSE.xlsx — Excel 4 sheet", "outputs/reports/AZZAM_REPURPOSE.xlsx"),
        ],
        "data": [("REPURPOSE_PACKAGES.json", "data/REPURPOSE_PACKAGES.json")],
        "efficiency": [
            ("Trước", "1 video long dùng 1 lần. Short quay riêng, tốn thời gian gấp đôi"),
            ("Sau", "1 lần quay → 5 asset. Short cắt từ long"),
            ("Đo bằng", "Số asset hữu dụng/video; thời gian sản xuất (mục tiêu 2 ngày/video)"),
        ],
        "sell": "Checklist (F5) và carousel (F3) là lead magnet đưa người xem vào Telegram → phễu bán khoá học và VIP group. Bài quan điểm (F4) tạo tranh luận → tăng reach tự nhiên.",
        "guardrail": "Không lặp nguyên văn 5 lần — mỗi định dạng phải một góc. Không dùng asset không có quyền (clip đối thủ). Không hiện số dư/lợi nhuận.",
    },
    {
        "id": "checklist-30d",
        "code": "30D",
        "title": "Checklist sản xuất 30 ngày",
        "owner": "youtube_workflow + Alan",
        "what": "Lịch 30 ngày: 15 video long + 45 Short, nhịp 2 ngày/video, kèm việc hằng ngày và 4 mốc kiểm tra (ngày 7/14/21/30).",
        "why": "Không có lịch thì không có nhịp. Thuật toán cần kênh đăng đều mới học được quy luật. Đây là công cụ để biết hôm nay làm gì, không phải nghĩ lại từ đầu.",
        "who": "Alan giữ nhịp. Editor thực thi theo lịch. youtube_workflow theo dõi mốc.",
        "when": "Bắt đầu 2026-10-03, kết thúc 2026-11-01. Xem mỗi sáng.",
        "where": "PRODUCTION_30D.md để đọc có checkbox. Excel để in ra dán tường.",
        "how": "Mỗi sáng mở lịch → xem ngày hôm nay ở pha nào → làm đúng việc trong cột 'Việc' → tick. Đến ngày 7/14/21/30 thì trả lời câu hỏi kiểm tra.",
        "sop": [
            "Mở PRODUCTION_30D.md, tìm mục 'Ngày N — <ngày>' tương ứng hôm nay.",
            "Xem dòng 'Pha' — SẢN XUẤT (ngày lẻ) hay HOÀN THIỆN & ĐĂNG (ngày chẵn).",
            "Làm hết các việc trong khối 'Việc:' — tick từng cái.",
            "Làm 3 việc lặp mỗi ngày ở đầu file (8:00 comment, 8:30 số liệu, 21:00 đăng nội dung phụ).",
            "Đến ngày 7/14/21/30: trả lời câu hỏi ở mục 'Điểm kiểm tra' — ghi kết quả vào topic 13.",
            "Sau 30 ngày: đọc mục 'Sau 30 ngày — đánh giá lại' và quyết giữ nhịp hay tăng.",
        ],
        "next_action": "Mở lịch, xem ngày 1 (2026-10-03) — pha SẢN XUẤT, chủ đề 'Stop Loss đúng cách'. Đọc outline + evidence trước khi viết kịch bản.",
        "files": [
            ("PRODUCTION_30D.md — lịch có checkbox", "outputs/strategy/PRODUCTION_30D.md"),
            ("PRODUCTION_30D.csv — dữ liệu để lọc", "outputs/strategy/PRODUCTION_30D.csv"),
            ("AZZAM_PRODUCTION_30D.docx — Word in ra dán tường", "outputs/reports/AZZAM_PRODUCTION_30D.docx"),
            ("AZZAM_PRODUCTION_30D.xlsx — Excel 4 sheet", "outputs/reports/AZZAM_PRODUCTION_30D.xlsx"),
        ],
        "data": [("PRODUCTION_30D.csv", "data/PRODUCTION_30D.csv")],
        "efficiency": [
            ("Trước", "Mỗi ngày tự nghĩ hôm nay làm gì. Không đo được tiến độ"),
            ("Sau", "Mở lịch là biết việc. 4 mốc kiểm tra đo được"),
            ("Đo bằng", "Số video đúng hạn; comment rate; sub ròng; %xem"),
        ],
        "sell": "15 video long trong 30 ngày là nền để bật YPP và có đủ nội dung gắn affiliate. Nhịp đều cũng là điều kiện để bán hệ thống này cho kênh khác (build-to-sell).",
        "guardrail": "Không premiere/đặt lịch khi kênh còn nhỏ — đăng thẳng. Giữ giờ cố định để thuật toán học.",
    },
    {
        "id": "evergreen",
        "code": "EVERGREEN",
        "title": "Plan 24 video evergreen",
        "owner": "youtube_workflow",
        "what": "24 chủ đề video 5-8 phút lấy từ 500 long-tail phrase mine từ 7,937 comment thật. 18/24 chủ đề đối thủ CHƯA làm.",
        "why": "Video evergreen còn mang view nhiều tháng/năm sau khi đăng, khác Short (hết sau vài ngày) và livestream (chỉ có view lúc phát). Kênh mình: 15 video 1-10 phút trung bình 6 view. Đối thủ: 31 video, trung bình 395 view — khoảng cách 66 lần.",
        "who": "Alan duyệt chủ đề. Editor sản xuất. youtube_workflow cập nhật.",
        "when": "Duyệt 1 lần, sản xuất theo lịch 30 ngày.",
        "where": "EVERGREEN_PLAN.csv để lọc. Word/Excel để đọc chi tiết.",
        "how": "Đọc bảng plan → chọn chủ đề theo tuần → mỗi video có sẵn title, hook 3 giây, outline, keyword, bằng chứng.",
        "sop": [
            "Mở EVERGREEN_PLAN.md hoặc .csv.",
            "Xem cột 'doi_thu_da_lam' — giá trị 0 nghĩa là đối thủ CHƯA làm, đây là khoảng trống nên đánh.",
            "Đọc cột 'hook_3s' — đây là 3 giây đầu, phải nói ngay người xem được gì.",
            "Đọc cột 'outline' — bố cục video, cài cao trào ở mốc 30/60/80%.",
            "Đọc cột 'evidence_quote' + 'evidence_url' — comment thật chứng minh nhu cầu.",
            "Chuyển sang P05 để lấy 5 định dạng cho video đã chọn.",
        ],
        "next_action": "Chọn 12 chủ đề làm trước (hoặc duyệt hết 24) và trả lời topic 13.",
        "files": [
            ("EVERGREEN_PLAN.csv — 24 video, 18 cột", "outputs/strategy/EVERGREEN_PLAN.csv"),
            ("EVERGREEN_PLAN.md — đọc chi tiết", "outputs/strategy/EVERGREEN_PLAN.md"),
            ("AZZAM_EVERGREEN_PLAN.docx — Word", "outputs/reports/AZZAM_EVERGREEN_PLAN.docx"),
            ("AZZAM_EVERGREEN_PLAN.xlsx — Excel 6 sheet", "outputs/reports/AZZAM_EVERGREEN_PLAN.xlsx"),
        ],
        "data": [("EVERGREEN_PLAN.csv", "data/EVERGREEN_PLAN.csv")],
        "efficiency": [
            ("Trước", "Mò chủ đề, viết xong mới biết không ai tìm"),
            ("Sau", "Chủ đề từ từ khoá thật khán giả dùng + biết đối thủ đã làm chưa"),
            ("Đo bằng", "% traffic từ YouTube Search (hiện 1.2%) và view trung bình/video"),
        ],
        "sell": "Video evergreen là nơi bán offer tốt nhất vì người xem đã có ý định học. Đây cũng là tài sản kênh — có nội dung evergreen mới bán được kênh (build-to-sell).",
        "guardrail": "Chủ đề phải có bằng chứng comment thật. Không bịa nhu cầu.",
    },
    {
        "id": "analytics-blindspots",
        "code": "ANALYTICS",
        "title": "Analytics + 11 điểm mù",
        "owner": "youtube_data + hermes_dashboard",
        "what": "Số liệu thật 28 ngày từ YouTube Analytics API (OAuth, số liệu riêng) + 11 điểm mù phát hiện được.",
        "why": "Không đo thì không biết video rớt ở đâu. Đây là số liệu NỘI BỘ (không phải số công khai), cho biết watch time, retention, nguồn traffic, thiết bị, địa lý.",
        "who": "Alan đọc để quyết. youtube_data cập nhật tự động 8:00 mỗi ngày.",
        "when": "Tự động mỗi ngày. Đọc khi cần quyết định sửa gì.",
        "where": "Dashboard mục Dashboard — analytics dashboard.",
        "how": "Xem phễu Hiển thị → CTR → %xem để biết video rớt ở nấc nào, rồi sửa đúng nấc đó.",
        "sop": [
            "Mở youtube-analytics-real.html trên dashboard.",
            "Xem 11 điểm mù trước — đây là vấn đề đã phát hiện, không cần tự tìm.",
            "Đọc cảnh báo traffic bot ở đầu trang: 47.9% view là view mua, không phải khách thật.",
            "Với video cần sửa: xem phễu Hiển thị → CTR → %xem. Rớt ở CTR thì sửa thumbnail/tiêu đề. Rớt ở %xem thì sửa hook 3 giây đầu.",
            "Đối chiếu với baseline THẬT: khoảng 4,700 view/tháng (đã trừ bot).",
        ],
        "next_action": "Đọc cảnh báo bot trước. Mọi kết luận dựa trên số liệu hiện tại đều KHÔNG đáng tin cho tới khi lọc được nguồn bot.",
        "files": [
            ("blindspots.md — 11 điểm mù", "outputs/reports/blindspots.md"),
            ("blindspots.json — dữ liệu điểm mù", "outputs/reports/blindspots.json"),
            ("AZZAM_ANALYTICS_DIEM_MU.docx — Word", "outputs/reports/AZZAM_ANALYTICS_DIEM_MU.docx"),
            ("AZZAM_ANALYTICS_DIEM_MU.xlsx — Excel 10 sheet", "outputs/reports/AZZAM_ANALYTICS_DIEM_MU.xlsx"),
        ],
        "data": [("blindspots.json", "data/blindspots.json")],
        "efficiency": [
            ("Trước", "Đoán video rớt ở đâu, sửa mò"),
            ("Sau", "Phễu chỉ rõ rớt ở nấc nào → sửa đúng nấc"),
            ("Đo bằng", "CTR, %xem trung bình (hiện 29%), comment rate"),
        ],
        "sell": "Số liệu retention chứng minh nội dung có giá trị → dùng làm bằng chứng xã hội khi bán khoá học.",
        "guardrail": "🔴 47.9% view là view MUA. Không dùng số liệu này để khoe với nhà quảng cáo hoặc đối tác. Rủi ro YouTube phạt theo Fake Engagement Policy.",
    },
    {
        "id": "mrbeast-audit",
        "code": "AUDIT",
        "title": "Audit MrBeast + Plan 90 ngày + SOP + Build-to-sell",
        "owner": "hermes_dashboard + youtube_workflow",
        "what": "Chẩn đoán kênh theo khung MrBeast (4 phần), plan hành động 90 ngày, SOP triển khai, và lộ trình build-to-sell 12 tháng.",
        "why": "Cần một bản chẩn đoán tổng thể để biết kênh đang ở đâu và đi đâu. Điểm MrBeast hiện 3.1/10, mục tiêu 6/10.",
        "who": "Alan đọc và quyết. Đây là tài liệu chiến lược, không phải việc hằng ngày.",
        "when": "Đọc 1 lần để chốt hướng. Xem lại mỗi quý.",
        "where": "Telegram topic 239 (AUDIT - MrBeast).",
        "how": "Đọc chẩn đoán → xem bảng điểm → đọc plan 90 ngày → chọn việc cho 30 ngày đầu.",
        "sop": [
            "Đọc phần 1 'Chẩn đoán' — biết kênh đang yếu ở đâu.",
            "Xem bảng điểm MrBeast — điểm nào thấp nhất thì ưu tiên sửa trước.",
            "Đọc 'Plan action 90 ngày' — chia 3 tháng, mỗi tháng một mục tiêu.",
            "Đọc 'SOP triển khai' — 8 bước mỗi ngày.",
            "Đọc 'Build-to-sell' — lộ trình 12 tháng để hệ thống bán được.",
            "Chốt: làm theo checklist 30 ngày (xem hướng dẫn 30D).",
        ],
        "next_action": "Xem điểm nào thấp nhất trong bảng MrBeast và đối chiếu với 11 điểm mù — trùng nhau là ưu tiên số 1.",
        "files": [
            ("MRBEAST_AUDIT.md — chẩn đoán + bảng điểm", "outputs/reports/MRBEAST_AUDIT.md"),
            ("MRBEAST_PLAN_ACTION.md — plan 90 ngày", "outputs/strategy/MRBEAST_PLAN_ACTION.md"),
            ("MRBEAST_SOP.md — SOP 8 bước/ngày", "outputs/strategy/MRBEAST_SOP.md"),
            ("MRBEAST_BUILD_TO_SELL.md — lộ trình 12 tháng", "outputs/strategy/MRBEAST_BUILD_TO_SELL.md"),
            ("AZZAM_MRBEAST_AUDIT.docx — Word", "outputs/reports/AZZAM_MRBEAST_AUDIT.docx"),
            ("AZZAM_MRBEAST_AUDIT.xlsx — Excel 8 sheet", "outputs/reports/AZZAM_MRBEAST_AUDIT.xlsx"),
        ],
        "data": [],
        "efficiency": [
            ("Trước", "Không biết kênh yếu ở đâu, sửa mọi thứ cùng lúc"),
            ("Sau", "Bảng điểm chỉ rõ điểm yếu nhất → sửa theo thứ tự"),
            ("Đo bằng", "Điểm MrBeast 3.1 → mục tiêu 6/10"),
        ],
        "sell": "Phần 'Build-to-sell' là lộ trình 12 tháng để biến kênh thành tài sản bán được — không chỉ là kênh kiếm quảng cáo.",
        "guardrail": "Không cam kết lợi nhuận. Không trình bày chart mô phỏng như trade thật.",
    },
]


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def esc(s) -> str:
    return escape(str(s))


CSS = """
:root { --bg:#0f1216; --sf:#171c22; --sf2:#1e242c; --bd:#2c343d; --tx:#e6edf5;
  --mu:#94a3b8; --bl:#60a5fa; --gr:#4ade80; --am:#fbbf24; --rd:#f87171; --ac:#38bdf8; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--tx);
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; line-height:1.6; padding:24px; }
.wrap { max-width:980px; margin:0 auto; }
a { color:var(--ac); }
header { border-bottom:1px solid var(--bd); padding-bottom:14px; margin-bottom:22px; }
.crumb { font-size:12px; color:var(--mu); margin-bottom:8px; }
.crumb a { color:var(--mu); }
h1 { margin:0 0 6px; font-size:26px; letter-spacing:-.02em; }
h2 { font-size:13px; text-transform:uppercase; letter-spacing:.08em; color:var(--mu);
  margin:28px 0 10px; font-weight:600; }
.sub { color:var(--mu); font-size:13px; }
.badge { display:inline-block; background:var(--sf2); border:1px solid var(--bd);
  border-radius:6px; padding:2px 9px; font-size:11px; color:var(--ac);
  font-weight:700; letter-spacing:.05em; margin-right:8px; }
.action { background:#0d2818; border:1px solid #1e5c37; border-left:3px solid var(--gr);
  border-radius:8px; padding:15px 18px; margin:20px 0; }
.action .lbl { font-size:10.5px; text-transform:uppercase; letter-spacing:.08em;
  color:var(--gr); font-weight:700; margin-bottom:5px; }
.action .txt { font-size:14.5px; color:#d1fae5; }
.guard { background:#2a1a1a; border:1px solid #5c2626; border-left:3px solid var(--rd);
  border-radius:8px; padding:14px 18px; margin:18px 0; font-size:13px; color:#fca5a5; }
.guard .lbl { font-size:10.5px; text-transform:uppercase; letter-spacing:.08em;
  color:var(--rd); font-weight:700; margin-bottom:5px; }
table { width:100%; border-collapse:collapse; font-size:13.5px; background:var(--sf);
  border:1px solid var(--bd); border-radius:10px; overflow:hidden; }
th { text-align:left; font-size:10.5px; text-transform:uppercase; letter-spacing:.06em;
  color:var(--mu); padding:9px 13px; border-bottom:1px solid var(--bd); background:var(--sf2); }
td { padding:10px 13px; border-bottom:1px solid var(--bd); vertical-align:top; }
tr:last-child td { border-bottom:none; }
td.k { color:var(--am); font-weight:700; white-space:nowrap; width:130px; }
ol.sop { counter-reset:s; list-style:none; padding:0; margin:0; }
ol.sop li { counter-increment:s; position:relative; padding:11px 14px 11px 52px;
  background:var(--sf); border:1px solid var(--bd); border-radius:9px; margin-bottom:8px;
  font-size:13.5px; }
ol.sop li::before { content:counter(s); position:absolute; left:13px; top:11px;
  width:26px; height:26px; border-radius:50%; background:var(--ac); color:#04121c;
  font-weight:800; font-size:13px; display:flex; align-items:center; justify-content:center; }
.files { list-style:none; padding:0; margin:0; }
.files li { background:var(--sf); border:1px solid var(--bd); border-radius:9px;
  padding:11px 14px; margin-bottom:7px; font-size:13px; }
.files li a { font-weight:600; }
.files li .p { display:block; color:var(--mu); font-size:11px; margin-top:3px;
  font-family:ui-monospace,Consolas,monospace; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:10px; }
.card { background:var(--sf); border:1px solid var(--bd); border-radius:10px; padding:13px 15px; }
.card .t { font-size:10.5px; text-transform:uppercase; letter-spacing:.06em;
  color:var(--mu); margin-bottom:5px; }
.card .v { font-size:14px; }
.card .n { font-size:11.5px; color:var(--mu); margin-top:5px; }
footer { margin-top:34px; padding-top:14px; border-top:1px solid var(--bd);
  color:var(--mu); font-size:11.5px; }
.hub { display:inline-block; background:var(--sf2); border:1px solid var(--bd);
  border-radius:8px; padding:9px 16px; margin-top:8px; font-size:13px;
  text-decoration:none; color:var(--tx); }
.hub:hover { border-color:var(--ac); }
"""


def guide_html(g: dict, all_guides: list[dict]) -> str:
    """Sinh HTML cho 1 trang hướng dẫn."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # 5W1H
    wh = [
        ("WHAT — Việc gì", g["what"]),
        ("WHY — Vì sao cần", g["why"]),
        ("WHO — Ai làm", g["who"]),
        ("WHEN — Khi nào", g["when"]),
        ("WHERE — Ở đâu", g["where"]),
        ("HOW — Làm thế nào", g["how"]),
    ]
    wh_rows = "".join(
        f'<tr><td class="k">{esc(k)}</td><td>{esc(v)}</td></tr>' for k, v in wh)

    # SOP
    sop_items = "".join(f"<li>{esc(s)}</li>" for s in g["sop"])

    # Files — link TRỰC TIẾP tới đúng file, không trỏ về Drive folder root.
    #
    # BÀI HỌC (Alan báo lỗi thật): trước đây mọi link Word/Excel/md đều trỏ về
    # CÙNG 1 Drive folder → bấm cái nào cũng ra cùng thư mục 32 file, phải tự
    # tìm. Sai hoàn toàn với yêu cầu "bấm là ra đúng nguồn".
    #
    # Cách đúng: host file trong deploy/files/<path> và link tới chính nó.
    # build_static_deploy.py copy toàn bộ file trong registry này.
    files_items = ""
    for label, rel in g["files"]:
        exists = (ROOT / rel).exists()
        if not exists:
            files_items += (
                f'<li><span style="color:#f87171">{esc(label)}</span>'
                f'<span class="p">CHƯA SINH — chạy script tương ứng</span></li>')
            continue
        # đường dẫn trên web: giữ nguyên cấu trúc outputs/... dưới /files/
        web = f"{SITE}/files/{rel}"
        sz = (ROOT / rel).stat().st_size
        szs = f"{sz/1024:.0f} KB" if sz < 1_000_000 else f"{sz/1_000_000:.1f} MB"
        files_items += (
            f'<li><a href="{web}" target="_blank" rel="noopener">{esc(label)}</a>'
            f'<span class="p">{esc(rel)} · {szs} · mở/tải trực tiếp</span></li>')

    for label, rel in g.get("data", []):
        files_items += (
            f'<li><a href="{SITE}/{esc(rel)}" target="_blank" rel="noopener">{esc(label)}</a>'
            f'<span class="p">{SITE}/{esc(rel)} · mở trực tiếp trên web</span></li>')

    # Efficiency
    eff = "".join(
        f'<div class="card"><div class="t">{esc(k)}</div><div class="v">{esc(v)}</div></div>'
        for k, v in g["efficiency"])

    # Nav sang các guide khác
    others = "".join(
        f'<li><a href="guides/{esc(o["id"])}.html">'
        f'<span class="badge">{esc(o["code"])}</span>{esc(o["title"])}</a></li>'
        for o in all_guides if o["id"] != g["id"])

    return f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(g['code'])} — {esc(g['title'])}</title>
<style>{CSS}</style></head><body><div class="wrap">
<div class="crumb"><a href="../index.html">Report Hub</a> ›
<a href="../guides.html">Hướng dẫn</a> › {esc(g['code'])}</div>
<header>
  <h1><span class="badge">{esc(g['code'])}</span>{esc(g['title'])}</h1>
  <div class="sub">Owner: {esc(g['owner'])} · Cập nhật {now}</div>
</header>

<div class="action">
  <div class="lbl">▶ Việc cần làm ngay</div>
  <div class="txt">{esc(g['next_action'])}</div>
</div>

<h2>5W1H — Hiểu trong 30 giây</h2>
<table>{wh_rows}</table>

<h2>SOP — Làm theo thứ tự</h2>
<ol class="sop">{sop_items}</ol>

<h2>File &amp; đường dẫn — bấm là mở</h2>
<ul class="files">{files_items}</ul>

<h2>Hiệu suất — được gì</h2>
<div class="grid">{eff}</div>

<h2>Build-to-sell — phần nào ra tiền</h2>
<div class="card"><div class="v">{esc(g['sell'])}</div></div>

<div class="guard">
  <div class="lbl">⚠ Guardrail — không được vi phạm</div>
  {esc(g['guardrail'])}
</div>

<h2>Hướng dẫn khác</h2>
<ul class="files">{others}</ul>

<footer>
  Sinh tự động bởi <code>scripts/build_sop_guides.py</code> ·
  <a href="../index.html">Report Hub</a> ·
  <a href="{SITE}" target="_blank">{SITE}</a>
</footer>
</div></body></html>"""


def index_html(guides: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cards = ""
    for g in guides:
        cards += (
            f'<a class="gcard" href="guides/{esc(g["id"])}.html">'
            f'<div class="gcode">{esc(g["code"])}</div>'
            f'<div class="gtitle">{esc(g["title"])}</div>'
            f'<div class="gwhat">{esc(g["what"][:120])}…</div>'
            f'<div class="gnext">▶ {esc(g["next_action"][:90])}…</div></a>')

    return f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hướng dẫn — Azzam Master Trading</title>
<style>{CSS}
.gcards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:14px; }}
.gcard {{ display:block; background:var(--sf); border:1px solid var(--bd); border-radius:12px;
  padding:16px 18px; text-decoration:none; color:var(--tx); }}
.gcard:hover {{ border-color:var(--ac); }}
.gcode {{ font-size:11px; font-weight:800; letter-spacing:.08em; color:var(--ac); }}
.gtitle {{ font-size:16px; font-weight:700; margin:5px 0 7px; }}
.gwhat {{ font-size:12.5px; color:var(--mu); line-height:1.5; }}
.gnext {{ font-size:12px; color:var(--gr); margin-top:9px; }}
</style></head><body><div class="wrap">
<div class="crumb"><a href="index.html">Report Hub</a> › Hướng dẫn</div>
<header>
  <h1>Hướng dẫn sử dụng — click là biết làm</h1>
  <div class="sub">{len(guides)} hướng dẫn · mỗi cái có 5W1H + SOP + đường dẫn ·
    cập nhật {now}</div>
</header>
<p class="sub">Mỗi báo cáo có 1 trang riêng: hiểu trong 30 giây, làm theo thứ tự,
bấm link là mở file. Không cần hỏi lại.</p>
<div class="gcards">{cards}</div>
<footer>Sinh tự động bởi <code>scripts/build_sop_guides.py</code> ·
  <a href="index.html">Report Hub</a></footer>
</div></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="chỉ liệt kê")
    args = ap.parse_args()

    if args.list:
        for g in GUIDES_REGISTRY:
            print(f"  {g['code']:10} {g['title']}")
            print(f"             next: {g['next_action'][:80]}")
        return 0

    GUIDES.mkdir(parents=True, exist_ok=True)

    for g in GUIDES_REGISTRY:
        out = GUIDES / f"{g['id']}.html"
        out.write_text(guide_html(g, GUIDES_REGISTRY), encoding="utf-8")
        print(f"  ✓ {out.relative_to(ROOT)}  ({out.stat().st_size:,} B)")

    idx = DASH / "guides.html"
    idx.write_text(index_html(GUIDES_REGISTRY), encoding="utf-8")
    print(f"  ✓ {idx.relative_to(ROOT)}  ({idx.stat().st_size:,} B)")

    # Kiểm tra mỗi guide có đủ 4 phần bắt buộc
    print(f"\n=== Kiểm tra chất lượng ({len(GUIDES_REGISTRY)} guide) ===")
    bad = 0
    for g in GUIDES_REGISTRY:
        issues = []
        if not g.get("sop") or len(g["sop"]) < 3:
            issues.append(f"SOP chỉ {len(g.get('sop', []))} bước")
        if not g.get("files"):
            issues.append("không có file")
        if not g.get("next_action"):
            issues.append("thiếu việc-ngay")
        if not g.get("guardrail"):
            issues.append("thiếu guardrail")
        if not g.get("sell"):
            issues.append("thiếu build-to-sell")
        for k in ["what", "why", "who", "when", "where", "how"]:
            if not g.get(k):
                issues.append(f"thiếu {k}")
        if issues:
            bad += 1
            print(f"  ✗ {g['code']}: {', '.join(issues)}")
        else:
            print(f"  ✓ {g['code']:10} {len(g['sop'])} bước SOP · "
                  f"{len(g['files'])} file · 5W1H đủ")

    print(f"\n{len(GUIDES_REGISTRY) - bad}/{len(GUIDES_REGISTRY)} guide đạt chuẩn")
    print(f"\nMở: {SITE}/guides.html")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

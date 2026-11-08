# -*- coding: utf-8 -*-
"""
Generate official Vietnamese Capstone Project Plan Document (.docx)
Output: D:\scam-detector\TAILIEU_CAPSTONE_C1SE06_SFDS\2. PROJECT PLAN\C1SE.06_ProjectPlan_SFDS_v1.2_VI.docx
"""
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=130, right=130):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="000000", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def format_cell_text(cell, text, bold=False, italic=False, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.LEFT, color_rgb=(0,0,0)):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)
    return run

def add_body_p(doc, text="", space_after=6, space_before=0, line_spacing=1.3):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    if text:
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        r.font.color.rgb = RGBColor(0, 0, 0)
    return p

def create_project_plan_docx_vi():
    doc = docx.Document()
    
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(13)
    style_normal.font.color.rgb = RGBColor(0, 0, 0)
    
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        s.header.is_linked_to_previous = False
        
        p_hdr = s.header.paragraphs[0]
        p_hdr.text = "KẾ HOẠCH DỰ ÁN\t\tKhóa Luận Tốt Nghiệp 1 – Năm 2026"
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p_hdr.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            r.font.italic = True
            r.font.color.rgb = RGBColor(0, 0, 0)
            
        p_ftr = s.footer.paragraphs[0]
        p_ftr.text = "C1SE.06\t\tSFDS Project Plan v1.2 (Bản Tiếng Việt)"
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p_ftr.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(0, 0, 0)

    # =========================================================================
    # TRANG 1: ẢNH BÌA
    # =========================================================================
    logo_path = "extracted_media/image_1.png"
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(0)
        p_logo.paragraph_format.space_after = Pt(6)
        r = p_logo.add_run()
        r.add_picture(logo_path, width=Inches(3.0))

    p_dtu = doc.add_paragraph()
    p_dtu.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dtu.paragraph_format.space_after = Pt(2)
    r_dtu = p_dtu.add_run("VIỆN ĐÀO TẠO & NGHIÊN CỨU QUỐC TẾ\nĐỒ ÁN TỐT NGHIỆP 1 / CAPSTONE PROJECT 1\nCMU-SE 450 – C1SE.06")
    r_dtu.font.name = "Times New Roman"
    r_dtu.font.size = Pt(13)
    r_dtu.font.bold = True
    
    p_title_doc = doc.add_paragraph()
    p_title_doc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title_doc.paragraph_format.space_before = Pt(22)
    r_title_doc = p_title_doc.add_run("KẾ HOẠCH DỰ ÁN (PROJECT PLAN)\nPhiên bản 1.2\nNgày: 02 tháng 09 năm 2026")
    r_title_doc.font.name = "Times New Roman"
    r_title_doc.font.size = Pt(17)
    r_title_doc.font.bold = True
    
    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_before = Pt(18)
    p_proj.paragraph_format.space_after = Pt(22)
    r_proj = p_proj.add_run("SFDS\nHệ Thống Cảnh Báo và Phát Hiện Lừa Đảo Trực Tuyến Đa Phương Thức Có Giải Thích")
    r_proj.font.name = "Times New Roman"
    r_proj.font.size = Pt(16)
    r_proj.font.bold = True
    
    p_created = doc.add_paragraph()
    p_created.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cr = p_created.add_run("Thực hiện bởi Nhóm C1SE.06\n")
    r_cr.font.name = "Times New Roman"
    r_cr.font.size = Pt(13)
    r_cr.font.bold = True
    r_mem = p_created.add_run("Hào, Phạm Tấn\nNhung, Đào Thị Mỹ\nNam, Trần Hoàng Nhật\nTuấn, Nguyễn Phan Đức\n")
    r_mem.font.name = "Times New Roman"
    r_mem.font.size = Pt(13)
    
    p_app = doc.add_paragraph()
    p_app.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_app.paragraph_format.space_before = Pt(14)
    r_app = p_app.add_run("Giảng viên hướng dẫn\nKS. Hà Mạnh Toàn\n")
    r_app.font.name = "Times New Roman"
    r_app.font.size = Pt(13)
    r_app.font.bold = True
    
    p_rep = doc.add_paragraph()
    p_rep.paragraph_format.space_before = Pt(24)
    r_rep = p_rep.add_run("Đại diện Hội đồng Đánh giá Kế hoạch Dự án:\nHọ và tên: ______________________    Chữ ký: ________________    Ngày: ________\n\nGiảng viên Hướng dẫn Đồ án Capstone 1:\nHọ và tên: KS. Hà Mạnh Toàn         Chữ ký: ________________    Ngày: ________")
    r_rep.font.name = "Times New Roman"
    r_rep.font.size = Pt(12)

    doc.add_page_break()

    # =========================================================================
    # TRANG 2: THÔNG TIN DỰ ÁN & PHÊ DUYỆT
    # =========================================================================
    p_h = doc.add_paragraph()
    r = p_h.add_run("THÔNG TIN DỰ ÁN")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    tbl_info = doc.add_table(rows=7, cols=4)
    set_table_borders(tbl_info, color="000000", sz="4")
    tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    info_data = [
        ("Tên viết tắt", "SFDS", "", ""),
        ("Tên đầy đủ dự án", "Hệ Thống Cảnh Báo và Phát Hiện Lừa Đảo Trực Tuyến Đa Phương Thức Có Giải Thích", "", ""),
        ("Ngày bắt đầu", "23 tháng 08 năm 2026", "Ngày kết thúc", "22 tháng 12 năm 2026"),
        ("Đơn vị chủ quản", "Viện Đào tạo & Nghiên cứu Quốc tế, Đại học Duy Tân", "", ""),
        ("Người hướng dẫn", "KS. Hà Mạnh Toàn", "", ""),
        ("Trưởng nhóm / Liên hệ", "Phạm Tấn Hào\nEmail: phamtanhao1909@gmail.com\nĐT: 0961651933 | Mã SV: 29219020823", "", ""),
        ("Đơn vị đối tác", "Đại học Duy Tân", "", "")
    ]
    for row_idx, data in enumerate(info_data):
        cells = tbl_info.rows[row_idx].cells
        if data[2] == "":
            cells[1].merge(cells[2]).merge(cells[3])
            format_cell_text(cells[0], data[0], bold=True, size_pt=11)
            format_cell_text(cells[1], data[1], bold=(row_idx==0), size_pt=11)
            set_cell_background(cells[0], "F2F2F2")
            set_cell_background(cells[1], "FFFFFF")
        else:
            format_cell_text(cells[0], data[0], bold=True, size_pt=11)
            format_cell_text(cells[1], data[1], size_pt=11)
            format_cell_text(cells[2], data[2], bold=True, size_pt=11)
            format_cell_text(cells[3], data[3], size_pt=11)
            set_cell_background(cells[0], "F2F2F2")
            set_cell_background(cells[1], "FFFFFF")
            set_cell_background(cells[2], "F2F2F2")
            set_cell_background(cells[3], "FFFFFF")

    p_m = doc.add_paragraph()
    p_m.paragraph_format.space_before = Pt(14)
    r = p_m.add_run("Thông Tin Liên Hệ Các Thành Viên Nhóm:")
    r.font.name = "Times New Roman"
    r.font.bold = True
    r.font.size = Pt(12)
    
    tbl_mem = doc.add_table(rows=5, cols=4)
    set_table_borders(tbl_mem, color="000000", sz="4")
    tbl_mem.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    headers_mem = ["Mã sinh viên", "Họ và tên thành viên", "Địa chỉ Email", "Số điện thoại"]
    for i, h in enumerate(headers_mem):
        format_cell_text(tbl_mem.rows[0].cells[i], h, bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_mem.rows[0].cells[i], "E6E6E6")
        
    members_data = [
        ("29219020823", "Phạm Tấn Hào (Trưởng nhóm / Scrum Master)", "phamtanhao1909@gmail.com", "0961651933"),
        ("29209200048", "Đào Thị Mỹ Nhung (QA Lead / UI-UX Lead)", "mynhung150905@gmail.com", "0376415338"),
        ("29219423638", "Trần Hoàng Nhật Nam (Frontend Developer)", "trannamnhathoang@gmail.com", "0795798736"),
        ("29211151140", "Nguyễn Phan Đức Tuấn (AI Lead / Full-stack Dev)", "ductuan02072005@gmail.com", "0932442770")
    ]
    for r_idx, m in enumerate(members_data):
        row = tbl_mem.rows[r_idx + 1]
        for c_idx, val in enumerate(m):
            format_cell_text(row.cells[c_idx], val, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,3] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    p_ctrl_h = doc.add_paragraph()
    p_ctrl_h.paragraph_format.space_before = Pt(14)
    r = p_ctrl_h.add_run("QUẢN LÝ TÀI LIỆU (DOCUMENT CONTROL)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True

    tbl_ctrl = doc.add_table(rows=4, cols=2)
    set_table_borders(tbl_ctrl, color="000000", sz="4")
    tbl_ctrl.alignment = WD_TABLE_ALIGNMENT.CENTER
    ctrl_data = [
        ("Tên tài liệu", "Kế hoạch Quản lý Dự án (Project Management Plan)"),
        ("Tác giả chính", "Đào Thị Mỹ Nhung & Phạm Tấn Hào"),
        ("Ngày phát hành", "02 tháng 09 năm 2026 (Cập nhật tiếng Việt: 05/11/2026)"),
        ("Tên tệp lưu trữ", "C1SE.06_ProjectPlan_SFDS_v1.2_VI.docx")
    ]
    for i, d in enumerate(ctrl_data):
        format_cell_text(tbl_ctrl.rows[i].cells[0], d[0], bold=True, size_pt=11)
        format_cell_text(tbl_ctrl.rows[i].cells[1], d[1], size_pt=11)
        set_cell_background(tbl_ctrl.rows[i].cells[0], "F2F2F2")
        set_cell_background(tbl_ctrl.rows[i].cells[1], "FFFFFF")

    p_rev_h = doc.add_paragraph()
    p_rev_h.paragraph_format.space_before = Pt(14)
    r = p_rev_h.add_run("LỊCH SỬ CHỈNH SỬA TÀI LIỆU")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True
    
    tbl_rev = doc.add_table(rows=3, cols=5)
    set_table_borders(tbl_rev, color="000000", sz="4")
    tbl_rev.alignment = WD_TABLE_ALIGNMENT.CENTER
    rev_headers = ["Phiên bản", "Ngày", "Mô tả nội dung thay đổi", "Tác giả", "Phê duyệt"]
    for i, h in enumerate(rev_headers):
        format_cell_text(tbl_rev.rows[0].cells[i], h, bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_rev.rows[0].cells[i], "E6E6E6")
    
    rev_vals = [
        ("1.0", "02/09/2026", "Phát hành Kế hoạch Dự án hoàn chỉnh ban đầu", "Đào Thị Mỹ Nhung", "Phạm Tấn Hào"),
        ("1.2", "05/11/2026", "Bản dịch tiếng Việt chuẩn học thuật đồng bộ 6 Sprint WBS và Ma trận Rủi ro", "Đào Thị Mỹ Nhung", "KS. Hà Mạnh Toàn")
    ]
    for r_idx, r_item in enumerate(rev_vals):
        for i, val in enumerate(r_item):
            format_cell_text(tbl_rev.rows[r_idx + 1].cells[i], val, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER if i in [0,1,3,4] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(tbl_rev.rows[r_idx + 1].cells[i], "FFFFFF")

    doc.add_page_break()

    # =========================================================================
    # TRANG 3: MỤC LỤC
    # =========================================================================
    p_toc_h = doc.add_paragraph()
    r = p_toc_h.add_run("MỤC LỤC")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    p_toc_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    toc_items = [
        ("1. Giới thiệu", "3"),
        ("   1.1. Mục đích tài liệu", "3"),
        ("   1.2. Tổng quan dự án", "3"),
        ("   1.3. Sản phẩm bàn giao của dự án", "3"),
        ("2. Tổ chức nhóm dự án", "4"),
        ("   2.1. Thông tin nhóm Scrum", "4"),
        ("   2.2. Vai trò và trách nhiệm (RACI Matrix)", "4"),
        ("   2.3. Phương pháp giao tiếp & Quy tắc ứng xử", "5"),
        ("   2.4. Báo cáo và theo dõi tiến độ", "5"),
        ("3. Phương pháp luận phát triển Agile/Scrum", "6"),
        ("4. Kế hoạch tiến độ và Chi phí", "7"),
        ("   4.1. Lịch trình chi tiết (Phân rã 6 Sprint WBS)", "7"),
        ("   4.2. Chi phí giờ công nhân sự", "9"),
        ("   4.3. Dự toán tổng giá trị dự án", "9"),
        ("5. Quản trị rủi ro dự án & Biện pháp giảm thiểu", "10"),
        ("6. Kế hoạch bàn giao sản phẩm", "11")
    ]
    for item, page in toc_items:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.2
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        r_item = p.add_run(item)
        r_item.font.name = "Times New Roman"
        r_item.font.size = Pt(12)
        r_item.font.bold = not item.startswith("   ")
        dots_count = max(5, 75 - len(item) * 2)
        r_dot = p.add_run(" " + "." * dots_count + " ")
        r_dot.font.name = "Times New Roman"
        r_dot.font.size = Pt(11)
        r_dot.font.color.rgb = RGBColor(120, 120, 120)
        r_pg = p.add_run(page)
        r_pg.font.name = "Times New Roman"
        r_pg.font.size = Pt(12)
        r_pg.font.bold = True

    doc.add_page_break()

    # =========================================================================
    # MỤC 1: GIỚI THIỆU
    # =========================================================================
    h1 = doc.add_heading(level=1)
    r = h1.add_run("1. Giới thiệu")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("1.1. Mục đích tài liệu")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "Mục đích của tài liệu này là xác lập kế hoạch quản lý chi tiết cho dự án SFDS (Scam Fraud Detection System with Explanations). Tài liệu vạch rõ mục tiêu dự án, vai trò và trách nhiệm các thành viên, phương pháp phát triển Agile/Scrum, kế hoạch thực thi 6 Sprint, dự toán ngân sách chi phí, ma trận quản lý rủi ro và lộ trình các mốc bàn giao học thuật. Mục tiêu tối thượng là đảm bảo việc kỹ nghệ, kiểm thử và chuyển giao nền tảng phát hiện lừa đảo đa phương thức có giải thích thành công cho Đồ án Tốt nghiệp 1 (CMU-SE 450).")

    h2 = doc.add_heading(level=2)
    r = h2.add_run("1.2. Tổng quan dự án")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "(Tham chiếu Đề cương C1SE.06-Proposal_SFDS_v2.0.docx)\nTrong thời đại chuyển đổi số, các hình ảnh giả mạo mang tính lừa đảo—bao gồm biên lai chuyển tiền ngân hàng giả (fake bill), thông báo trúng thưởng giả mạo, tin nhắn lừa đảo và mã QR độc hại—đang ngày càng lan rộng với thủ đoạn tinh vi. Các công cụ quét an ninh mạng truyền thống thường chỉ đưa ra các nhãn phân loại thô, thiếu minh bạch ('An toàn' hoặc 'Độc hại') mà không cung cấp bằng chứng giải thích cụ thể cho nạn nhân.")
    add_body_p(doc, "SFDS là hệ thống hỗ trợ phát hiện và khuyến nghị an toàn dựa trên AI, được thiết kế để phân tích hình ảnh, trích xuất văn bản tiếng Việt qua Tesseract OCR, thực hiện pháp chứng hình ảnh (phân tích EXIF và Error Level Analysis - ELA), phân tích từ vựng URL với PhishVN và phân loại đe dọa với ResNet18. Hệ thống tính toán điểm rủi ro chuẩn hóa (0–100) và cung cấp lời giải thích bằng ngôn ngữ tự nhiên cùng các hành động ứng phó khẩn cấp.")

    h2 = doc.add_heading(level=2)
    r = h2.add_run("1.3. Sản phẩm bàn giao của dự án")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "• Sản phẩm phần mềm cốt lõi: Ứng dụng web hoàn chỉnh hỗ trợ chế độ quét nhanh cho công dân không cần đăng nhập, lưu lịch sử quét cục bộ trên trình duyệt, và cổng quản trị bảo mật cho chuyên gia an ninh.\n• Các tạo tác AI / Machine Learning: Checkpoint mô hình phân loại hình ảnh ResNet18, mô hình từ vựng URL PhishVN, và động cơ tính điểm rủi ro có giải thích CoT.\n• Tài liệu kỹ thuật đi kèm: Đặc tả Yêu cầu Phần mềm (SRS), Tài liệu Thiết kế Phần mềm (SDD/Architecture), Báo cáo Đánh giá Benchmark AI (Macro-F1, Recall, CER/WER), Hướng dẫn Sử dụng và Báo cáo Kỹ thuật Đồ án Tốt nghiệp.")

    # =========================================================================
    # MỤC 2: TỔ CHỨC NHÓM DỰ ÁN
    # =========================================================================
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("2. Tổ chức nhóm dự án")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True

    h2 = doc.add_heading(level=2)
    r = h2.add_run("2.1. Thông tin nhóm Scrum")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    p_t1 = doc.add_paragraph("Bảng 1. Cơ cấu nhân sự nhóm Scrum dự án SFDS")
    p_t1.runs[0].font.name = "Times New Roman"
    p_t1.runs[0].font.bold = True
    p_t1.runs[0].font.size = Pt(11.5)
    
    tbl_t1 = doc.add_table(rows=6, cols=4)
    set_table_borders(tbl_t1, color="000000", sz="4")
    tbl_t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    t1_headers = ["Họ và tên", "Số điện thoại", "Email", "Vị trí trong nhóm"]
    for i, h in enumerate(t1_headers):
        format_cell_text(tbl_t1.rows[0].cells[i], h, bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t1.rows[0].cells[i], "E6E6E6")
    t1_data = [
        ("KS. Hà Mạnh Toàn", "-", "lhttuy@gmail.com", "Giảng viên hướng dẫn (Mentor)"),
        ("Phạm Tấn Hào", "0961651933", "phamtanhao1909@gmail.com", "Trưởng nhóm / Scrum Master / Backend"),
        ("Đào Thị Mỹ Nhung", "0376415338", "mynhung150905@gmail.com", "QA Lead / UI-UX Lead / Quản lý tài liệu"),
        ("Trần Hoàng Nhật Nam", "0795798736", "trannamnhathoang@gmail.com", "Frontend Developer / Viết tài liệu kỹ thuật"),
        ("Nguyễn Phan Đức Tuấn", "0932442770", "ductuan02072005@gmail.com", "AI Lead / Full-stack Developer")
    ]
    for r_idx, d in enumerate(t1_data):
        row = tbl_t1.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [1] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("2.2. Vai trò và trách nhiệm (RACI Matrix)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    p_t2 = doc.add_paragraph("Bảng 2. Bảng phân công vai trò và trách nhiệm chính")
    p_t2.runs[0].font.name = "Times New Roman"
    p_t2.runs[0].font.bold = True
    p_t2.runs[0].font.size = Pt(11.5)
    
    tbl_t2 = doc.add_table(rows=7, cols=3)
    set_table_borders(tbl_t2, color="000000", sz="4")
    tbl_t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    t2_headers = ["Vai trò", "Trách nhiệm chính", "Thành viên đảm nhiệm"]
    for i, h in enumerate(t2_headers):
        format_cell_text(tbl_t2.rows[0].cells[i], h, bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t2.rows[0].cells[i], "E6E6E6")
    t2_data = [
        ("Product Owner", "Định nghĩa yêu cầu hệ thống, quản lý Product Backlog, đảm bảo giá trị sản phẩm và làm việc với các bên liên quan.", "Phạm Tấn Hào"),
        ("Scrum Master", "Điều phối các nghi thức Scrum, tháo gỡ khó khăn kỹ thuật cho nhóm, theo dõi tiến độ burn-down chart.", "Phạm Tấn Hào"),
        ("AI / Backend Dev", "Hiện thực hóa OCR trích xuất văn bản tiếng Việt, mô hình URL PhishVN, ResNet18 và các dịch vụ FastAPI.", "Nguyễn Phan Đức Tuấn & Phạm Tấn Hào"),
        ("Frontend Dev", "Xây dựng giao diện React 18 đáp ứng, quản lý trạng thái, và bộ máy lưu trữ lịch sử quét trên LocalStorage.", "Trần Hoàng Nhật Nam"),
        ("QA / Designer", "Thiết kế wireframe trên Figma, soạn thảo Test Cases, kiểm thử API, kiểm thử bảo mật và kiểm thử chấp nhận UAT.", "Đào Thị Mỹ Nhung"),
        ("Giảng viên hướng dẫn", "Định hướng giải pháp kỹ thuật, thẩm định thiết kế kiến trúc và đánh giá định kỳ các mốc tiến độ.", "KS. Hà Mạnh Toàn")
    ]
    for r_idx, d in enumerate(t2_data):
        row = tbl_t2.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=10)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("2.3. Phương pháp giao tiếp & Quy tắc ứng xử")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    p_t3 = doc.add_paragraph("Bảng 3. Kế hoạch và phương thức giao tiếp dự án")
    p_t3.runs[0].font.name = "Times New Roman"
    p_t3.runs[0].font.bold = True
    p_t3.runs[0].font.size = Pt(11.5)
    
    tbl_t3 = doc.add_table(rows=4, cols=4)
    set_table_borders(tbl_t3, color="000000", sz="4")
    tbl_t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    t3_headers = ["Đối tượng tham gia", "Chủ đề / Mục đích cuộc họp", "Tần suất", "Công cụ / Hình thức"]
    for i, h in enumerate(t3_headers):
        format_cell_text(tbl_t3.rows[0].cells[i], h, bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t3.rows[0].cells[i], "E6E6E6")
    t3_data = [
        ("Toàn bộ thành viên nhóm", "Họp Daily Scrum: Cập nhật tiến độ hàng ngày, khó khăn vướng mắc và kế hoạch trong 24h tiếp theo.", "2 ngày một lần (15 phút)", "Trực tuyến qua Google Meet / Discord"),
        ("Thành viên nhóm & GVHD", "Họp Sprint Review & Báo cáo tiến độ: Báo cáo kết quả Sprint, demo bản tăng trưởng phần mềm và tiếp thu góp ý.", "2 tuần một lần", "Trực tiếp tại văn phòng IS hoặc Google Meet"),
        ("Toàn bộ thành viên nhóm", "Họp Sprint Retrospective: Đánh giá những điểm làm tốt, điểm chưa tốt và hành động cải tiến cho Sprint tới.", "Cuối mỗi Sprint", "Trực tuyến kết hợp ghi chép trên Notion")
    ]
    for r_idx, d in enumerate(t3_data):
        row = tbl_t3.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=10)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("2.4. Báo cáo và theo dõi tiến độ")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "Tiến độ dự án được theo dõi chặt chẽ trên bảng quản trị dự án Jira/GitHub Projects. Mỗi nhiệm vụ được lượng giá theo điểm độ phức tạp (Story Points - SP) và gán mã công việc chuẩn hóa (SFDS-1 đến SFDS-42). Các nhánh mã nguồn được kiểm soát qua quy trình Git Flow: nhánh main chỉ nhận mã đã kiểm thử đạt, các tính năng mới được phát triển trên nhánh feature/* và tạo Pull Request có ít nhất 1 thành viên review trước khi merge.")

    # =========================================================================
    # MỤC 3: PHƯƠNG PHÁP LUẬN PHÁT TRIỂN AGILE/SCRUM
    # =========================================================================
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("3. Phương pháp luận phát triển Agile/Scrum")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    add_body_p(doc, "Dự án SFDS áp dụng khung làm việc Agile/Scrum gồm 6 Sprint kế tiếp nhau (mỗi Sprint kéo dài 2 tuần). Khung Scrum đặc biệt phù hợp với các dự án tích hợp AI đa phương thức vì cho phép nhóm liên tục thích ứng, đo lường độ chính xác và tinh chỉnh tham số mô hình qua từng chu kỳ.")
    add_body_p(doc, "• Kế hoạch Sprint (Sprint Planning): Đầu mỗi Sprint, nhóm chọn lọc các User Story ưu tiên từ Product Backlog, phân rã công việc kỹ thuật và cam kết mục tiêu Sprint.\n• Thực thi & Kiểm thử song song: Lập trình viên viết mã kết hợp viết unit test; chuyên viên QA chuẩn bị test case và thực hiện kiểm thử tự động ngay khi có bản build mới.\n• Định nghĩa Hoàn thành (Definition of Done - DoD): Một User Story chỉ được coi là hoàn thành khi đáp ứng toàn bộ Tiêu chí Chấp nhận (Acceptance Criteria), vượt qua 100% test case tự động, mã nguồn được review sạch và tài liệu liên quan được cập nhật đồng bộ.")

    doc.add_page_break()

    # =========================================================================
    # MỤC 4: KẾ HOẠCH TIẾN ĐỘ VÀ CHI PHÍ
    # =========================================================================
    h1 = doc.add_heading(level=1)
    r = h1.add_run("4. Kế hoạch tiến độ và Chi phí")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("4.1. Lịch trình chi tiết (Phân rã 6 Sprint WBS)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True

    p_t5 = doc.add_paragraph("Bảng 4. Lịch trình chi tiết các Sprint và phân rã công việc (Jira WBS SFDS-1 đến 42)")
    p_t5.runs[0].font.name = "Times New Roman"
    p_t5.runs[0].font.bold = True
    p_t5.runs[0].font.size = Pt(11.5)

    schedule_data = [
        ("0", "Giai đoạn Khởi tạo Dự án & Hoàn thiện Đề cương", "23/08/2026", "02/09/2026", "80", "-", "Tất cả thành viên", True),
        ("0.1", "Họp khởi động dự án & Phân công trách nhiệm", "23/08/2026", "25/08/2026", "20", "-", "Tất cả thành viên", False),
        ("0.2", "Khảo sát tài liệu nghiên cứu & Thu thập mẫu lừa đảo ban đầu", "26/08/2026", "30/08/2026", "30", "-", "Tuấn, Nguyễn Phan Đức", False),
        ("0.3", "Soạn thảo Đề cương & Kế hoạch Dự án v1.0", "31/08/2026", "02/09/2026", "30", "-", "Nhung & Hào", False),

        ("1", "Sprint 1: Phân tích Yêu cầu, Thiết kế Kiến trúc & UI Mockup", "03/09/2026", "18/09/2026", "200", "34", "Tất cả thành viên", True),
        ("1.1", "Họp lập kế hoạch Sprint 1 Planning", "03/09/2026", "03/09/2026", "12", "-", "Tất cả thành viên", False),
        ("1.2", "Đặc tả yêu cầu phần mềm SRS (SFDS-1)", "04/09/2026", "10/09/2026", "36", "8", "Nhung, Đào Thị Mỹ", False),
        ("1.3", "Thiết kế Wireframe & Prototype trên Figma (SFDS-2)", "05/09/2026", "12/09/2026", "32", "5", "Nhung, Đào Thị Mỹ", False),
        ("1.4", "Thiết kế Kiến trúc C&C, Module, Deployment (SFDS-3)", "06/09/2026", "14/09/2026", "38", "8", "Hào, Phạm Tấn", False),
        ("1.5", "Thiết kế CSDL Quan hệ & ERD (SFDS-4)", "08/09/2026", "15/09/2026", "34", "5", "Hào, Phạm Tấn", False),
        ("1.6", "Khởi tạo Repository Git & Cấu hình Docker cơ bản (SFDS-5)", "10/09/2026", "16/09/2026", "24", "5", "Tuấn & Nam", False),
        ("1.7", "Thẩm định tính khả thi của mô hình OCR và URL (SFDS-6, 7)", "12/09/2026", "17/09/2026", "16", "3", "Tuấn, Nguyễn Phan Đức", False),
        ("1.8", "Họp Đánh giá & Rút kinh nghiệm Sprint 1", "18/09/2026", "18/09/2026", "8", "-", "Tất cả thành viên", False),

        ("2", "Sprint 2: Xây dựng Pipeline AI Tiền xử lý, OCR & Mô hình URL", "19/09/2026", "02/10/2026", "200", "41", "Tất cả thành viên", True),
        ("2.1", "Họp lập kế hoạch Sprint 2 Planning", "19/09/2026", "19/09/2026", "12", "-", "Tất cả thành viên", False),
        ("2.2", "Xây dựng Pipeline OCR Tesseract tiếng Việt (SFDS-8)", "20/09/2026", "26/09/2026", "38", "8", "Tuấn, Nguyễn Phan Đức", False),
        ("2.3", "Huấn luyện & Tích hợp Bộ trích xuất URL PhishVN (SFDS-9)", "21/09/2026", "27/09/2026", "36", "8", "Tuấn, Nguyễn Phan Đức", False),
        ("2.4", "Xây dựng Khung giao diện Web Quét an toàn (SFDS-10)", "22/09/2026", "28/09/2026", "34", "8", "Nam, Trần Hoàng Nhật", False),
        ("2.5", "Hiện thực hóa Cổng API FastAPI tiếp nhận tệp (SFDS-11)", "23/09/2026", "29/09/2026", "32", "8", "Hào, Phạm Tấn", False),
        ("2.6", "Tích hợp Giải mã mã QR (SFDS-12)", "25/09/2026", "30/09/2026", "24", "5", "Nam, Trần Hoàng Nhật", False),
        ("2.7", "Thiết kế & Thực thi Unit Test cho Sprint 2 (SFDS-13, 14)", "28/09/2026", "01/10/2026", "16", "4", "Nhung, Đào Thị Mỹ", False),
        ("2.8", "Họp Đánh giá & Rút kinh nghiệm Sprint 2", "02/10/2026", "02/10/2026", "8", "-", "Tất cả thành viên", False),

        ("3", "Sprint 3: Suy luận Giải thích CoT, ResNet18 & Lịch sử Quét", "03/10/2026", "16/10/2026", "200", "38", "Tất cả thành viên", True),
        ("3.1", "Họp lập kế hoạch Sprint 3 Planning", "03/10/2026", "03/10/2026", "12", "-", "Tất cả thành viên", False),
        ("3.2", "Động cơ Suy luận CoT & Bầu chọn Đồng thuận (SFDS-15)", "04/10/2026", "10/10/2026", "40", "8", "Hào, Phạm Tấn", False),
        ("3.3", "Huấn luyện Checkpoint ResNet-18 phân loại ảnh (SFDS-16)", "05/10/2026", "11/10/2026", "38", "8", "Tuấn, Nguyễn Phan Đức", False),
        ("3.4", "Phân tích mức nén ảnh JPEG ELA & EXIF (SFDS-17)", "06/10/2026", "12/10/2026", "30", "5", "Tuấn, Nguyễn Phan Đức", False),
        ("3.5", "Giao diện Kết quả Thẩm định rủi ro & Đồng hồ đo (SFDS-18)", "07/10/2026", "13/10/2026", "36", "8", "Nam, Trần Hoàng Nhật", False),
        ("3.6", "Lưu trữ Lịch sử quét trên LocalStorage (SFDS-19)", "09/10/2026", "14/10/2026", "20", "5", "Nam, Trần Hoàng Nhật", False),
        ("3.7", "Kiểm thử tích hợp & Test Cases Sprint 3 (SFDS-20, 21)", "13/10/2026", "15/10/2026", "16", "4", "Nhung, Đào Thị Mỹ", False),
        ("3.8", "Họp Đánh giá & Rút kinh nghiệm Sprint 3", "16/10/2026", "16/10/2026", "8", "-", "Tất cả thành viên", False),

        ("4", "Sprint 4: Cổng Quản trị, Quản lý Quy tắc Động & Tăng cường Bảo mật", "17/10/2026", "31/10/2026", "200", "42", "Tất cả thành viên", True),
        ("4.1", "Họp lập kế hoạch Sprint 4 Planning", "17/10/2026", "17/10/2026", "12", "-", "Tất cả thành viên", False),
        ("4.2", "Giao diện Cổng Quản trị: Dữ liệu & Checkpoint AI (SFDS-22)", "18/10/2026", "24/10/2026", "36", "8", "Nam, Trần Hoàng Nhật", False),
        ("4.3", "Quản lý Động Từ khóa Lừa đảo & Trọng số Rủi ro (SFDS-23)", "19/10/2026", "26/10/2026", "34", "8", "Nam, Trần Hoàng Nhật", False),
        ("4.4", "Vẽ khung tọa độ vi phạm OCR trên Canvas (SFDS-24)", "20/10/2026", "27/10/2026", "36", "8", "Tuấn, Nguyễn Phan Đức", False),
        ("4.5", "Bảo mật tệp tải lên Magic Bytes & Khóa JWT (SFDS-25)", "21/10/2026", "27/10/2026", "30", "8", "Hào, Phạm Tấn", False),
        ("4.6", "Lưu trữ Nhật ký Kiểm toán & Xuất báo cáo CSV (SFDS-26)", "23/10/2026", "28/10/2026", "24", "8", "Hào, Phạm Tấn", False),
        ("4.7", "Kiểm thử An ninh & Trải nghiệm Thông báo Toast (SFDS-27, 28)", "28/10/2026", "30/10/2026", "20", "10", "Nhung, Đào Thị Mỹ", False),
        ("4.8", "Họp Đánh giá & Rút kinh nghiệm Sprint 4", "31/10/2026", "31/10/2026", "8", "-", "Tất cả thành viên", False),

        ("5", "Sprint 5: Đánh giá Benchmark Mô hình, Docker hóa & Tối ưu tải", "01/11/2026", "15/11/2026", "200", "37", "Tất cả thành viên", True),
        ("5.1", "Họp lập kế hoạch Sprint 5 Planning", "01/11/2026", "01/11/2026", "12", "-", "Tất cả thành viên", False),
        ("5.2", "Đo lường Benchmark AI: Macro-F1, Recall, Báo nhầm (SFDS-29)", "02/11/2026", "08/11/2026", "38", "8", "Tuấn, Nguyễn Phan Đức", False),
        ("5.3", "Đo lường Độ chính xác OCR (Tỷ lệ lỗi CER & WER) (SFDS-30)", "03/11/2026", "09/11/2026", "32", "8", "Tuấn, Nguyễn Phan Đức", False),
        ("5.4", "Hiệu chuẩn Ngưỡng rủi ro giảm thiểu Báo động nhầm (SFDS-31)", "05/11/2026", "11/11/2026", "34", "8", "Hào, Phạm Tấn", False),
        ("5.5", "Đóng gói Container: Dockerfile & Docker-Compose (SFDS-32)", "06/11/2026", "12/11/2026", "32", "8", "Hào, Phạm Tấn", False),
        ("5.6", "Cấu hình CI/CD tự động bằng GitHub Actions (SFDS-33)", "08/11/2026", "13/11/2026", "20", "5", "Nam, Trần Hoàng Nhật", False),
        ("5.7", "Kiểm thử Chịu tải & Khảo sát Độ hữu ích Lời giải thích (SFDS-34, 35)", "12/11/2026", "14/11/2026", "24", "13", "Nhung, Đào Thị Mỹ", False),
        ("5.8", "Họp Đánh giá & Rút kinh nghiệm Sprint 5", "15/11/2026", "15/11/2026", "8", "-", "Tất cả thành viên", False),

        ("6", "Sprint 6: Kiểm thử Chấp nhận UAT & Triển khai Máy chủ Staging", "16/11/2026", "01/12/2026", "200", "29", "Tất cả thành viên", True),
        ("6.1", "Họp lập kế hoạch Sprint 6 Planning", "16/11/2026", "16/11/2026", "12", "-", "Tất cả thành viên", False),
        ("6.2", "Thực thi Kiểm thử Chấp nhận Người dùng UAT (SFDS-36)", "17/11/2026", "24/11/2026", "40", "8", "Nhung, Đào Thị Mỹ", False),
        ("6.3", "Triển khai lên Máy chủ Thử nghiệm AWS EC2 (SFDS-37)", "18/11/2026", "25/11/2026", "38", "8", "Hào, Phạm Tấn", False),
        ("6.4", "Sửa lỗi toàn diện & Tinh chỉnh Hoàn thiện Giao diện (SFDS-38)", "20/11/2026", "28/11/2026", "42", "8", "Nam, Trần Hoàng Nhật", False),
        ("6.5", "Soạn thảo Sổ tay Người dùng & Cẩm nang Quản trị (SFDS-39)", "24/11/2026", "30/11/2026", "34", "8", "Nhung, Đào Thị Mỹ", False),
        ("6.6", "Demo Sản phẩm Hoàn chỉnh cho Giảng viên Hướng dẫn", "01/12/2026", "01/12/2026", "8", "-", "Tất cả thành viên", False),
        ("6.7", "Đóng băng Mã nguồn & Phát hành Thẻ Git Tag v1.0 (SFDS-42)", "01/12/2026", "01/12/2026", "26", "5", "Tuấn, Nguyễn Phan Đức", False),

        ("7", "Hoàn thiện Báo cáo Kỹ thuật Đồ án & Chuẩn bị Bảo vệ", "02/12/2026", "18/12/2026", "200", "-", "Tất cả thành viên", True),
        ("7.1", "Hoàn thiện Báo cáo Kỹ thuật Đồ án Tốt nghiệp 1 (SFDS-40)", "02/12/2026", "12/12/2026", "110", "-", "Tất cả thành viên", False),
        ("7.2", "Soạn thảo Slide Thuyết trình & Kịch bản Demo Trực tiếp (SFDS-41)", "13/12/2026", "18/12/2026", "90", "-", "Tất cả thành viên", False),
        ("8", "Họp Tổng kết Dự án & Buổi Bảo vệ Thử nghiệm (Mock Defense)", "18/12/2026", "20/12/2026", "10", "-", "Tất cả thành viên", True),
        ("9", "Buổi Bảo vệ Chính thức Trước Hội đồng & Chuyển giao", "22/12/2026", "22/12/2026", "15", "-", "Tất cả thành viên", True)
    ]

    tbl_t5 = doc.add_table(rows=len(schedule_data) + 1, cols=7)
    set_table_borders(tbl_t5, color="000000", sz="4")
    tbl_t5.alignment = WD_TABLE_ALIGNMENT.CENTER
    t5_headers = ["STT", "Tên Giai đoạn / Nhiệm vụ", "Bắt đầu", "Kết thúc", "Công số (h)", "SP", "Người thực hiện"]
    for i, h in enumerate(t5_headers):
        format_cell_text(tbl_t5.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t5.rows[0].cells[i], "E6E6E6")

    for r_idx, row_item in enumerate(schedule_data):
        no, name, start, end, effort, sp, assignee, is_hdr = row_item
        row = tbl_t5.rows[r_idx + 1]
        bg = "F0F0F0" if is_hdr else "FFFFFF"
        for c_idx, val in enumerate([no, name, start, end, effort, sp, assignee]):
            format_cell_text(row.cells[c_idx], val, bold=is_hdr, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,2,3,4,5] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], bg)

    # 4.2 CHI PHÍ GIỜ CÔNG
    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(16)
    r = h2.add_run("4.2. Chi phí giờ công nhân sự")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    p_t6 = doc.add_paragraph("Bảng 5. Đơn giá nhân công theo giờ của các thành viên")
    p_t6.runs[0].font.name = "Times New Roman"
    p_t6.runs[0].font.bold = True
    p_t6.runs[0].font.size = Pt(11.5)
    
    tbl_t6 = doc.add_table(rows=5, cols=3)
    set_table_borders(tbl_t6, color="000000", sz="4")
    tbl_t6.alignment = WD_TABLE_ALIGNMENT.CENTER
    t6_headers = ["Họ và tên thành viên", "Vai trò đảm nhiệm", "Đơn giá (USD/giờ)"]
    for i, h in enumerate(t6_headers):
        format_cell_text(tbl_t6.rows[0].cells[i], h, bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t6.rows[0].cells[i], "E6E6E6")
    t6_data = [
        ("Phạm Tấn Hào", "Trưởng nhóm / Scrum Master / Backend", "3.00"),
        ("Đào Thị Mỹ Nhung", "QA Lead / UI-UX Lead", "3.00"),
        ("Trần Hoàng Nhật Nam", "Frontend Developer", "3.00"),
        ("Nguyễn Phan Đức Tuấn", "AI Lead / Full-stack Developer", "3.00")
    ]
    for r_idx, d in enumerate(t6_data):
        row = tbl_t6.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx == 2 else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # 4.3 DỰ TOÁN TỔNG CHI PHÍ
    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("4.3. Dự toán tổng giá trị dự án")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    p_t7 = doc.add_paragraph("Bảng 6. Bảng dự toán tổng chi phí và giá trị đầu tư dự án")
    p_t7.runs[0].font.name = "Times New Roman"
    p_t7.runs[0].font.bold = True
    p_t7.runs[0].font.size = Pt(11.5)
    
    tbl_t7 = doc.add_table(rows=7, cols=5)
    set_table_borders(tbl_t7, color="000000", sz="4")
    tbl_t7.alignment = WD_TABLE_ALIGNMENT.CENTER
    t7_headers = ["STT", "Hạng mục chi phí", "Căn cứ tính toán", "Tổng chi phí (USD)", "Quy đổi (VNĐ)"]
    for i, h in enumerate(t7_headers):
        format_cell_text(tbl_t7.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t7.rows[0].cells[i], "E6E6E6")
    t7_data = [
        ("1", "Công số kỹ thuật / Nhân công", "4 thành viên x 4 giờ/ngày x 93 ngày = 1.488 giờ @ 3 USD/giờ", "4.464,00", "~111.600.000"),
        ("2", "Lưu trữ Đám mây (AWS EC2 & S3)", "Gói AWS EC2 t3.medium + bộ nhớ S3 (3 tháng)", "120,00", "~3.000.000"),
        ("3", "Phần cứng & Tính toán GPU", "Google Colab Pro+ / Điện năng trạm GPU cục bộ", "80,00", "~2.000.000"),
        ("4", "Bản quyền Phần mềm & Tên miền", "Figma Pro, đăng ký tên miền riêng, chứng chỉ SSL", "60,00", "~1.500.000"),
        ("5", "In ấn Tài liệu, Bìa cứng & Poster", "In ấn tài liệu đồ án, đóng bìa mạ vàng, in poster", "80,00", "~2.000.000"),
        ("", "TỔNG GIÁ TRỊ DỰ ÁN ƯỚC TÍNH", "Nhân công + Hạ tầng + Chi phí vận hành", "$4.804,00", "~120.100.000 VNĐ")
    ]
    for r_idx, d in enumerate(t7_data):
        row = tbl_t7.rows[r_idx + 1]
        is_tot = (r_idx == len(t7_data) - 1)
        bg = "F0F0F0" if is_tot else "FFFFFF"
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, bold=is_tot, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,3] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], bg)

    p_exp = doc.add_paragraph()
    p_exp.paragraph_format.space_before = Pt(8)
    r = p_exp.add_run("Giải trình cơ cấu chi phí:\n• Tổng chi phí nhân công kỹ thuật = 4 thành viên × 4 giờ/ngày × 93 ngày = 1.488 giờ × 3,00 USD/giờ = 4.464,00 USD.\n• Chi phí tiền mặt thực tế (Đám mây, GPU, Tên miền, In ấn) = 340,00 USD (~8.500.000 VNĐ), do các thành viên nhóm tự đóng góp chi trả đồng đều.\n• Tổng giá trị ước tính của toàn bộ dự án = 4.804,00 USD (~120.100.000 VNĐ).")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.italic = True

    doc.add_page_break()

    # =========================================================================
    # MỤC 5: QUẢN TRỊ RỦI RO DỰ ÁN
    # =========================================================================
    h1 = doc.add_heading(level=1)
    r = h1.add_run("5. Quản trị rủi ro dự án & Biện pháp giảm thiểu")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True

    p_t8 = doc.add_paragraph("Bảng 7. Thang đo đánh giá Xác suất và Mức độ nghiêm trọng của Rủi ro")
    p_t8.runs[0].font.name = "Times New Roman"
    p_t8.runs[0].font.bold = True
    p_t8.runs[0].font.size = Pt(11.5)
    
    tbl_t8 = doc.add_table(rows=5, cols=4)
    set_table_borders(tbl_t8, color="000000", sz="4")
    tbl_t8.alignment = WD_TABLE_ALIGNMENT.CENTER
    t8_headers = ["Mã", "Xác suất xảy ra (Likelihood)", "Mã", "Mức độ ảnh hưởng (Seriousness)"]
    for i, h in enumerate(t8_headers):
        format_cell_text(tbl_t8.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t8.rows[0].cells[i], "E6E6E6")
    t8_data = [
        ("L", "Thấp: Ít có khả năng xảy ra (< 20%)", "L", "Thấp: Ảnh hưởng nhỏ, tiến độ không bị chậm trễ"),
        ("M", "Trung bình: Có thể phát sinh (20% - 50%)", "M", "Trung bình: Cần làm lại, chậm tiến độ nhẹ (< 1 tuần)"),
        ("H", "Cao: Rất dễ xảy ra (> 50%)", "H", "Cao: Hỏng module trọng yếu, chậm tiến độ lớn (> 2 tuần)"),
        ("-", "Không áp dụng", "E", "Cực kỳ nghiêm trọng: Dự án thất bại, không thể tốt nghiệp")
    ]
    for r_idx, d in enumerate(t8_data):
        row = tbl_t8.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,2] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    p_t9 = doc.add_paragraph()
    p_t9.paragraph_format.space_before = Pt(14)
    r = p_t9.add_run("Bảng 8. Ma trận rủi ro chi tiết và kế hoạch ứng phó giảm thiểu")
    r.font.name = "Times New Roman"
    r.font.bold = True
    r.font.size = Pt(11.5)

    tbl_t9 = doc.add_table(rows=7, cols=5)
    set_table_borders(tbl_t9, color="000000", sz="4")
    tbl_t9.alignment = WD_TABLE_ALIGNMENT.CENTER
    t9_headers = ["Phạm vi rủi ro", "Mô tả rủi ro & Hậu quả tiềm ẩn", "Mức ảnh hưởng", "Xác suất", "Chiến lược ứng phó & Giải pháp giảm thiểu"]
    for i, h in enumerate(t9_headers):
        format_cell_text(tbl_t9.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t9.rows[0].cells[i], "E6E6E6")
        
    t9_data = [
        ("Khan hiếm Dữ liệu Tiếng Việt", "Khó khăn trong việc thu thập mẫu hóa đơn ngân hàng giả và ảnh chụp lừa đảo chất lượng cao do tính chất bảo mật thông tin cá nhân.", "H", "H", "Khai thác tập dữ liệu mở (PhishVN v3.1.0); ẩn danh hóa dữ liệu; sinh các mẫu biên lai lừa đảo tổng hợp với nhiều font chữ bằng script generator."),
        ("Sai số Nhận diện OCR", "Ảnh chụp bị mờ, chụp nghiêng hoặc tương phản kém khiến Tesseract đọc sai ký tự, bỏ sót số tài khoản hoặc liên kết URL.", "H", "M", "Tiền xử lý ảnh bằng OpenCV (khử góc nghiêng deskew, ngưỡng tương thích, lọc nhiễu bilateral); kết hợp Tesseract với thuật toán so khớp mờ từ vựng."),
        ("Báo động nhầm Hóa đơn Thật", "Quy tắc chấm điểm từ khóa quá khắt khe gắn cờ nhầm các hóa đơn điện nước hay giao dịch ngân hàng thật, làm giảm lòng tin của người dùng.", "M", "H", "Thực hiện hiệu chuẩn ngưỡng rủi ro trong Sprint 5; phân chia 3 cấp độ cảnh báo rõ ràng (An toàn 0-25, Nghi ngờ 26-59, Nguy hiểm 60-100); minh bạch chuỗi giải thích CoT."),
        ("Lỗ hổng Tải tệp lên Máy chủ", "Kẻ xấu cố tình tải lên các tập tin thực thi độc hại giả dạng phần mở rộng hình ảnh nhằm tấn công máy chủ backend.", "H", "M", "Kiểm tra mã byte định danh thực tế (python-magic) thay vì tin tưởng đuôi tệp; giới hạn dung lượng tối đa 15MB; cách ly thư mục lưu trữ tạm thời."),
        ("Áp lực Môn học & Thi cử", "Lịch thi giữa kỳ và khối lượng môn học nặng trong tháng 11 có nguy cơ làm sụt giảm vận tốc Sprint và trễ hạn hoàn thành.", "M", "H", "Duy trì nghiêm túc họp ngắn định kỳ 2 ngày/lần; rà soát backlog ưu tiên tính năng bắt buộc trước tính năng phụ; tăng cường làm thêm vào các ngày cuối tuần."),
        ("Chi phí Hạ tầng Đám mây", "Chi phí duy trì máy chủ đám mây GPU liên tục vượt quá khả năng tài chính sinh viên.", "L", "M", "Phát triển và huấn luyện cục bộ trên máy trạm; triển khai các mô hình suy luận nhẹ (ResNet18, HistGradientBoosting); tận dụng gói miễn phí AWS EC2 chỉ bật khi cần demo.")
    ]
    for r_idx, d in enumerate(t9_data):
        row = tbl_t9.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [2,3] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # =========================================================================
    # MỤC 6: KẾ HOẠCH BÀN GIAO SẢN PHẨM
    # =========================================================================
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("6. Kế hoạch bàn giao sản phẩm")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True

    p_t10 = doc.add_paragraph("Bảng 9. Danh mục sản phẩm bàn giao và thời hạn hoàn thành")
    p_t10.runs[0].font.name = "Times New Roman"
    p_t10.runs[0].font.bold = True
    p_t10.runs[0].font.size = Pt(11.5)

    tbl_t10 = doc.add_table(rows=11, cols=4)
    set_table_borders(tbl_t10, color="000000", sz="4")
    tbl_t10.alignment = WD_TABLE_ALIGNMENT.CENTER
    t10_headers = ["STT", "Tên Tài liệu / Sản phẩm Bàn giao", "Hạn hoàn thành", "Tên tệp / Tạo tác tương ứng"]
    for i, h in enumerate(t10_headers):
        format_cell_text(tbl_t10.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t10.rows[0].cells[i], "E6E6E6")
        
    t10_data = [
        ("1", "Tài liệu Đề cương Dự án (Proposal)", "23/08/2026", "C1SE.06-Proposal_SFDS_v2.0.docx"),
        ("2", "Tài liệu Kế hoạch Dự án (Project Plan)", "02/09/2026", "C1SE.06_ProjectPlan_SFDS_v1.2.docx"),
        ("3", "Đặc tả Yêu cầu Phần mềm (SRS)", "20/09/2026", "C1SE.06_SRS_SFDS_v1.0.docx"),
        ("4", "Thiết kế Kiến trúc & Thiết kế CSDL (Architecture & DB)", "15/10/2026", "C1SE.06_ArchitectureDesign & DatabaseDesign.docx"),
        ("5", "Bản tăng trưởng Phần mềm Khả dụng (Working Prototype)", "16/10/2026", "Bản demo trực tiếp trên Localhost:5173"),
        ("6", "Báo cáo Đánh giá Benchmark AI (F1, Recall, CER)", "15/11/2026", "C1SE.06_AI_Benchmark_Report.docx"),
        ("7", "Mã nguồn Hệ thống & Cấu hình Docker Hoàn chỉnh", "01/12/2026", "GitHub Repository Tag v1.0-release"),
        ("8", "Sổ tay Người dùng & Cẩm nang Quản trị viên", "08/12/2026", "C1SE.06_UserManual_SFDS_v1.0.docx"),
        ("9", "Báo cáo Kỹ thuật Đồ án Tốt nghiệp 1 Hoàn chỉnh", "18/12/2026", "C1SE.06_TechnicalReport_SFDS_Final.docx"),
        ("10", "Slide Thuyết trình & Video Demo Bảo vệ Đồ án", "20/12/2026", "C1SE.06_FinalPresentation.pptx + Video Demo")
    ]
    for r_idx, d in enumerate(t10_data):
        row = tbl_t10.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,2] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # Lưu tập tin kết quả
    output_path = r"D:\scam-detector\TAILIEU_CAPSTONE_C1SE06_SFDS\2. PROJECT PLAN\C1SE.06_ProjectPlan_SFDS_v1.2_VI.docx"
    doc.save(output_path)
    print("Successfully generated:", output_path)

if __name__ == "__main__":
    create_project_plan_docx_vi()

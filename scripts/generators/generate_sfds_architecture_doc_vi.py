# -*- coding: utf-8 -*-
"""
Generate official Vietnamese Capstone Architecture Design Document (.docx)
Output: D:\scam-detector\TAILIEU_CAPSTONE_C1SE06_SFDS\4. ARCHITECTURE DESIGN\C1SE.06_ArchitectureDesign_SFDS_v1.0_VI.docx
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

def create_architecture_doc_vi():
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
        p_hdr.text = "THIẾT KẾ KIẾN TRÚC HỆ THỐNG\t\tKhóa Luận Tốt Nghiệp 1 – Năm 2026"
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p_hdr.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            r.font.italic = True
            r.font.color.rgb = RGBColor(0, 0, 0)
            
        p_ftr = s.footer.paragraphs[0]
        p_ftr.text = "C1SE.06\t\tSFDS Architecture Design v1.0 (Bản Tiếng Việt)"
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
    r_title_doc = p_title_doc.add_run("TÀI LIỆU THIẾT KẾ KIẾN TRÚC HỆ THỐNG\nPhiên bản 1.0\nNgày: Tháng 10 năm 2026")
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
    r_rep = p_rep.add_run("Đại diện Hội đồng Đánh giá Thiết kế Kiến trúc:\nHọ và tên: ______________________    Chữ ký: ________________    Ngày: ________\n\nGiảng viên Hướng dẫn Đồ án Capstone 1:\nHọ và tên: KS. Hà Mạnh Toàn         Chữ ký: ________________    Ngày: ________")
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
        ("Tên đầy đủ dự án", "SFDS – Hệ Thống Cảnh Báo và Phát Hiện Lừa Đảo Trực Tuyến Đa Phương Thức Có Giải Thích", "", ""),
        ("Ngày bắt đầu", "23 tháng 08 năm 2026", "Ngày kết thúc", "22 tháng 12 năm 2026"),
        ("Đơn vị chủ quản", "Viện Đào tạo & Nghiên cứu Quốc tế, Đại học Duy Tân", "", ""),
        ("Người hướng dẫn", "KS. Hà Mạnh Toàn", "", ""),
        ("Nhóm thực hiện", "C1SE.06 – Khóa Luận Tốt Nghiệp 1 (CMU-SE 450)", "", ""),
        ("Cơ quan tài trợ", "Viện Đào tạo Quốc tế (IS) – Đại học Duy Tân", "", "")
    ]
    for r_idx, row in enumerate(info_data):
        cells = tbl_info.rows[r_idx].cells
        format_cell_text(cells[0], row[0], bold=True, size_pt=11)
        set_cell_background(cells[0], "F2F2F2")
        if row[2] == "":
            cells[1].merge(cells[2]).merge(cells[3])
            format_cell_text(cells[1], row[1], size_pt=11)
            set_cell_background(cells[1], "FFFFFF")
        else:
            format_cell_text(cells[1], row[1], size_pt=11)
            format_cell_text(cells[2], row[2], bold=True, size_pt=11)
            format_cell_text(cells[3], row[3], size_pt=11)
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

    p_app_h = doc.add_paragraph()
    p_app_h.paragraph_format.space_before = Pt(18)
    r = p_app_h.add_run("PHÊ DUYỆT TÀI LIỆU")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    p_app_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p_req = doc.add_paragraph("Tài liệu thiết kế kiến trúc này yêu cầu các bên liên quan ký xác nhận và phê duyệt:")
    p_req.runs[0].font.name = "Times New Roman"
    p_req.runs[0].font.size = Pt(12)
    p_req.runs[0].font.italic = True
    
    tbl_app = doc.add_table(rows=6, cols=3)
    set_table_borders(tbl_app, color="000000", sz="4")
    tbl_app.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    app_headers = ["Họ tên thành viên & Vai trò", "Chữ ký xác nhận", "Ngày ký"]
    for i, h in enumerate(app_headers):
        format_cell_text(tbl_app.rows[0].cells[i], h, bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_app.rows[0].cells[i], "E6E6E6")
        
    approvals_rows = [
        ("KS. Hà Mạnh Toàn – Giảng viên hướng dẫn", "", ""),
        ("Phạm Tấn Hào (Mã SV: 29219020823) – Trưởng nhóm / Scrum Master", "", ""),
        ("Đào Thị Mỹ Nhung (Mã SV: 29209200048) – QA Lead / UI-UX Lead", "", ""),
        ("Trần Hoàng Nhật Nam (Mã SV: 29219423638) – Frontend Developer", "", ""),
        ("Nguyễn Phan Đức Tuấn (Mã SV: 29211151140) – AI Lead / Full-stack Dev", "", "")
    ]
    for r_idx, app in enumerate(approvals_rows):
        row = tbl_app.rows[r_idx + 1]
        format_cell_text(row.cells[0], app[0], size_pt=11)
        format_cell_text(row.cells[1], app[1], size_pt=11)
        format_cell_text(row.cells[2], app[2], size_pt=11)
        for cell in row.cells:
            set_cell_background(cell, "FFFFFF")

    p_rev_h = doc.add_paragraph()
    p_rev_h.paragraph_format.space_before = Pt(16)
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
        ("1.0", "15/10/2026", "Phát hành tài liệu Thiết kế Kiến trúc Hệ thống chính thức", "Phạm Tấn Hào", "KS. Hà Mạnh Toàn"),
        ("1.1", "05/11/2026", "Bản dịch tiếng Việt chuẩn học thuật đồng bộ 6 góc nhìn kiến trúc C&C, Module, Allocation", "Phạm Tấn Hào", "KS. Hà Mạnh Toàn")
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
        ("1. Giới thiệu", "4"),
        ("   1.1. Mục đích tài liệu", "4"),
        ("   1.2. Tài liệu tham chiếu", "4"),
        ("2. Tổng quan dự án", "4"),
        ("   2.1. Tổng quan dự án", "4"),
        ("   2.2. Động lực kinh doanh & Nghiệp vụ", "5"),
        ("      2.2.1. Bối cảnh dự án & Động lực thực hiện", "5"),
        ("      2.2.2. Giải pháp đề xuất", "5"),
        ("      2.2.3. Mục tiêu dự án", "6"),
        ("      2.2.4. Các tính năng cốt lõi", "6"),
        ("3. Trình điều khiển kiến trúc (Architecture Drivers)", "7"),
        ("   3.1. Yêu cầu cấp cao", "7"),
        ("   3.2. Đặc tả chi tiết các trình điều khiển kiến trúc", "8"),
        ("      3.2.1. Thực thể tham gia Use Case", "8"),
        ("      3.2.2. Ca sử dụng vận hành (UC-01 đến UC-08)", "10"),
        ("   3.3. Thuộc tính chất lượng (Kịch bản QA01 đến QA05)", "15"),
        ("4. Các ràng buộc hệ thống", "17"),
        ("   4.1. Ràng buộc kinh doanh", "17"),
        ("   4.2. Ràng buộc kỹ thuật & Công nghệ", "18"),
        ("5. Sơ đồ & Các góc nhìn kiến trúc hệ thống", "19"),
        ("   5.1. Góc nhìn Thành phần & Kết nối (C&C View)", "19"),
        ("      5.1.1. Góc nhìn C&C phía Client", "19"),
        ("      5.1.2. Góc nhìn C&C phía Server & Pipeline phân tích AI", "22"),
        ("   5.2. Góc nhìn Module", "25"),
        ("      5.2.1. Phân rã Module phía Client", "25"),
        ("      5.2.2. Phân rã Module phía Server", "27"),
        ("   5.3. Góc nhìn Phân bổ & Triển khai (Allocation View)", "29"),
        ("6. Tài liệu tham khảo", "32")
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
    
    add_body_p(doc, "Tài liệu này xác lập Thiết kế Kiến trúc Hệ thống chính thức cho nền tảng SFDS (Scam Fraud Detection System with Explanations). Tài liệu cung cấp bản thiết kế có cấu trúc và chuẩn mực ghi lại cấu trúc hệ thống cấp cao, các trình điều khiển kiến trúc (architectural drivers), cây tiện ích thuộc tính chất lượng (quality attribute utility tree), các ca sử dụng vận hành và đa góc nhìn kiến trúc tuân thủ chuẩn Kiến trúc Phần mềm SEI/CMU (Bass, Clements, & Kazman).")
    add_body_p(doc, "Đối tượng độc giả mục tiêu của tài liệu bao gồm hội đồng đánh giá học thuật, giảng viên hướng dẫn, kiến trúc sư phần mềm và các kỹ sư phát triển full-stack. Tài liệu đóng vai trò định hướng triển khai, bảo đảm pipeline AI đa phương thức, cổng API bất đồng bộ và giao diện bảo vệ quyền riêng tư người dùng phối hợp nhịp nhàng và nhất quán.")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(12)
    r = h2.add_run("1.2. Tài liệu tham chiếu")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    p_t1 = doc.add_paragraph("Bảng 1. Danh mục tài liệu tham chiếu nội bộ")
    p_t1.runs[0].font.name = "Times New Roman"
    p_t1.runs[0].font.bold = True
    p_t1.runs[0].font.size = Pt(11.5)

    tbl_t1 = doc.add_table(rows=4, cols=3)
    set_table_borders(tbl_t1, color="000000", sz="4")
    tbl_t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    t1_headers = ["STT", "Mã tài liệu", "Tên tài liệu & Phạm vi mô tả"]
    for i, h in enumerate(t1_headers):
        format_cell_text(tbl_t1.rows[0].cells[i], h, bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t1.rows[0].cells[i], "E6E6E6")

    docs_ref = [
        ("1", "C1SE.06-Proposal_SFDS_v2.1.docx", "Đề cương Dự án: Đặt vấn đề, Phạm vi nghiên cứu, Mục tiêu & Khảo sát công nghệ"),
        ("2", "C1SE.06_ProjectPlan_SFDS_v1.0.docx", "Kế hoạch Quản lý Dự án: Lộ trình 6 Sprint, Jira WBS (SFDS-1..42), Ngân sách & Rủi ro"),
        ("3", "C1SE.06_SRS_SFDS_v1.0.docx", "Đặc tả Yêu cầu Phần mềm: Yêu cầu chức năng và Phi chức năng chi tiết")
    ]
    for r_idx, d in enumerate(docs_ref):
        row = tbl_t1.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,1] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # =========================================================================
    # MỤC 2: TỔNG QUAN DỰ ÁN
    # =========================================================================
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("2. Tổng quan dự án")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("2.1. Tổng quan dự án")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "SFDS là nền tảng an toàn thông tin thông minh có khả năng giải thích, được phát triển chuyên biệt nhằm phát hiện và phân tích các thủ đoạn lừa đảo thị giác và văn bản trong không gian mạng Việt Nam. Với triết lý ưu tiên quyền riêng tư (privacy-first), SFDS cho phép người dân quét thẩm định nội dung khả nghi ngay lập tức mà không cần tạo tài khoản, đồng thời cung cấp cổng quản trị cấp chuyên gia để điều phối và quản trị tri thức đe dọa an ninh mạng.")

    p_t2 = doc.add_paragraph("Bảng 2. Phân công trách nhiệm kiến trúc trong nhóm phát triển")
    p_t2.runs[0].font.name = "Times New Roman"
    p_t2.runs[0].font.bold = True
    p_t2.runs[0].font.size = Pt(11.5)

    tbl_t2 = doc.add_table(rows=5, cols=3)
    set_table_borders(tbl_t2, color="000000", sz="4")
    tbl_t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    t2_headers = ["Họ và tên thành viên", "Vai trò dự án", "Trách nhiệm kiến trúc & Quản lý phân hệ"]
    for i, h in enumerate(t2_headers):
        format_cell_text(tbl_t2.rows[0].cells[i], h, bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t2.rows[0].cells[i], "E6E6E6")

    team_roles = [
        ("Phạm Tấn Hào", "Trưởng nhóm / Scrum Master", "Chịu trách nhiệm Backend Core (FastAPI, JWT Auth, Docker, Thuật toán tổng hợp đồng thuận Consensus Fusion)."),
        ("Đào Thị Mỹ Nhung", "QA Lead / UI-UX Lead", "Đảm bảo chất lượng (QA), Thiết kế Wireframe UI/UX, Thiết kế Test Case, Kiểm thử chấp nhận UAT, Soạn thảo tài liệu."),
        ("Trần Hoàng Nhật Nam", "Frontend Developer", "Chịu trách nhiệm Frontend (React 18, Vite, Canvas Bounding Box, Bộ máy lưu trữ LocalStorage)."),
        ("Nguyễn Phan Đức Tuấn", "AI Lead / Full-stack Developer", "Chịu trách nhiệm Pipeline AI (Tesseract OCR, Mô hình URL PhishVN, ResNet-18, Phân tích ELA).")
    ]
    for r_idx, d in enumerate(team_roles):
        row = tbl_t2.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("2.2. Động lực kinh doanh & Nghiệp vụ")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True

    add_body_p(doc, "2.2.1. Bối cảnh dự án & Động lực thực hiện:\nLừa đảo tài chính số thông qua các tạo tác hình ảnh giả mạo đang bùng nổ theo cấp số nhân tại Việt Nam. Các đối tượng lừa đảo thường xuyên chế tác hóa đơn chuyển khoản ngân hàng giả (fake payment bill), làm giả giấy triệu tập của công an/viện kiểm sát, và phát tán mã QR chứa liên kết độc hại. Người dân đại chúng thiếu các công cụ giám định số, trong khi các phần mềm diệt virus hoặc tường lửa truyền thống chỉ kiểm tra tên miền cơ bản mà không thể phân tích nội dung hình ảnh hay ngữ cảnh tiếng Việt bản địa.")
    add_body_p(doc, "2.2.2. Giải pháp đề xuất:\nSFDS cung cấp giải pháp quét thị giác đa phương thức toàn diện. Khi tiếp nhận ảnh chụp, tệp PDF hoặc đoạn văn bản, hệ thống thực hiện OCR trích xuất văn bản tiếng Việt, giải mã mã QR, phân tích 21 đặc trưng cấu trúc URL (PhishVN), thực hiện phân tích mức nén ảnh JPEG ELA (Error Level Analysis), và so khớp bố cục thị giác (ResNet-18). Động cơ suy luận chuỗi giải thích Chain-of-Thought (CoT) tổng hợp đa tín hiệu thành điểm số rủi ro chuẩn hóa (0–100) kèm bằng chứng thị giác trực quan.")
    add_body_p(doc, "2.2.3. Mục tiêu dự án:\n• Cung cấp khả năng đánh giá điểm rủi ro lừa đảo tự động, tức thời (độ trễ < 3.0 giây) với độ chính xác cao.\n• Phân rã nguyên nhân nguy cơ thành bằng chứng trực quan, dễ hiểu cho người phổ thông (Ngữ nghĩa văn bản, Nguy cơ URL, Dấu vết chỉnh sửa ảnh).\n• Bảo đảm tuyệt đối quyền riêng tư thông qua chế độ quét khách vãng lai không thu thập định danh (zero-PII) và lưu trữ cục bộ trên trình duyệt.\n• Cung cấp pipeline AI dạng module linh hoạt, cho phép thay thế (hot-swap) các trọng số học sâu mà không làm gián đoạn dịch vụ web.")
    add_body_p(doc, "2.2.4. Các tính năng cốt lõi:\n• Tiếp nhận đa phương thức: Hỗ trợ tệp ảnh (JPG/PNG/WEBP), quét trực tiếp từ camera, dán văn bản (tối đa 20.000 ký tự), tài liệu PDF (tối đa 10 trang) và kiểm tra liên kết web (URL).\n• Bảng điều khiển Trí tuệ Nhân tạo Có Thể Giải Thích (XAI): Đồng hồ rủi ro chuẩn hóa (An toàn 0-25, Đáng ngờ 26-59, Nguy hiểm 60-100), đóng khung vùng nghi vấn (bounding box) và phân rã điểm thành phần.\n• Trợ lý An toàn Tương tác: Module hướng dẫn khắc phục thông minh hỗ trợ người dùng các bước cần làm ngay (khóa thẻ, báo ngân hàng, gửi đơn tố giác).\n• Cổng Quản trị Chuyên sâu: Bảng điều khiển phân quyền RBAC phục vụ quản trị tập dữ liệu, giám sát mô hình AI, đo lường benchmark và theo dõi nhật ký kiểm toán hệ thống.")

    doc.add_page_break()

    # =========================================================================
    # MỤC 3: TRÌNH ĐIỀU KHIỂN KIẾN TRÚC
    # =========================================================================
    h1 = doc.add_heading(level=1)
    r = h1.add_run("3. Trình điều khiển kiến trúc (Architecture Drivers)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("3.1. Yêu cầu cấp cao")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "Thiết kế kiến trúc hệ thống được dẫn dắt bởi các bên liên quan và các năng lực vận hành then chốt:")
    add_body_p(doc, "• Người dùng đại chúng (Khách vãng lai):\n  - Quét an toàn đa nguồn (Ảnh chụp, Văn bản, URL, PDF, QR)\n  - Tính điểm rủi ro thời gian thực và đóng khung vùng vi phạm trực quan\n  - Tương tác giải đáp cùng Trợ lý An toàn mạng\n  - Quản lý lịch sử quét trên thiết bị cá nhân (tối đa 50 bản ghi)")
    add_body_p(doc, "• Quản trị viên hệ thống:\n  - Xác thực an toàn bằng JWT và quản lý phiên làm việc\n  - Quản trị tập dữ liệu huấn luyện AI và xuất dữ liệu\n  - Giám sát các checkpoint mô hình AI và đánh giá chất lượng benchmark\n  - Theo dõi nhật ký bảo mật và vệt kiểm toán hệ thống (Audit Trail)")
    add_body_p(doc, "• Các trình điều khiển phân hệ ngoại vi:\n  - Động cơ OCR Tesseract tiếng Việt (vie)\n  - Bộ phân loại từ vựng URL PhishVN (21 đặc trưng)\n  - Bộ phân loại bố cục thị giác ResNet-18\n  - Bộ công cụ pháp chứng thị giác OpenCV (phân tích ELA & siêu dữ liệu EXIF)")

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists("arch_diagrams/fig1_system_context.png"):
        p.add_run().add_picture("arch_diagrams/fig1_system_context.png", width=Inches(6.0))
        
    p_fig1 = doc.add_paragraph("Hình 1. Sơ đồ Bối cảnh Hệ thống (System Context Diagram)")
    p_fig1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fig1.runs[0].font.name = "Times New Roman"
    p_fig1.runs[0].font.italic = True
    p_fig1.runs[0].font.size = Pt(11)

    # 3.2 THỰC THỂ THAM GIA USE CASE
    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("3.2. Đặc tả chi tiết các trình điều khiển kiến trúc")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    h3 = doc.add_heading(level=3)
    r = h3.add_run("3.2.1. Thực thể tham gia Use Case")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True

    entity_tables = [
        ("Bảng 3. Thực thể E01: Luồng Dữ liệu Đa phương thức Đầu vào", [
            ("Mã định danh", "E01"),
            ("Tên thực thể", "Cảm biến / Luồng tiếp nhận Đa phương tiện"),
            ("Mô tả nghiệp vụ", "Các tạo tác kỹ thuật số do người dùng tải lên (Tệp ảnh, tài liệu PDF, ảnh chụp mã QR, chuỗi văn bản thô)."),
            ("Giả định cung cấp", "Truyền tệp nhị phân thô hoặc chuỗi ký tự chuẩn UTF-8 đến cổng tiếp nhận API Gateway."),
            ("Giả định yêu cầu", "Tệp tin phải tuân thủ định dạng hỗ trợ (JPG, PNG, WEBP, PDF) và dung lượng tối đa 15MB."),
            ("Ca sử dụng liên quan", "Tiếp nhận và gửi dữ liệu lên Backend API phục vụ phân tích.")
        ]),
        ("Bảng 4. Thực thể E02: Lớp Xử lý Phân tích & AI", [
            ("Mã định danh", "E02"),
            ("Tên thực thể", "Động cơ Suy luận AI & Pháp chứng Thị giác"),
            ("Mô tả nghiệp vụ", "Phân hệ bao gồm Tesseract OCR, bộ phân loại PhishVN, ResNet-18 và công nhân phân tích ELA OpenCV."),
            ("Giả định cung cấp", "Xử lý dữ liệu đa phương tiện thô thành siêu dữ liệu phân tích có cấu trúc (văn bản, tọa độ, xác suất)."),
            ("Giả định yêu cầu", "Các tệp checkpoint mô hình huấn luyện sẵn (ResNet-18 pt, PhishVN joblib, Tesseract vie) phải được nạp sẵn."),
            ("Ca sử dụng liên quan", "Trích xuất văn bản, dự đoán nguy cơ lừa đảo, phát hiện can thiệp ảnh và cung cấp tín hiệu cho động cơ CoT.")
        ]),
        ("Bảng 5. Thực thể E03: Người dùng Đại chúng (Khách vãng lai)", [
            ("Mã định danh", "E03"),
            ("Tên thực thể", "Người dùng Cuối / Công dân"),
            ("Mô tả nghiệp vụ", "Đối tượng thụ hưởng chính sử dụng ứng dụng web để thẩm định các nội dung kỹ thuật số đáng ngờ."),
            ("Giả định cung cấp", "Gửi hình ảnh hoặc tin nhắn nghi vấn để kiểm tra mức độ an toàn."),
            ("Giả định yêu cầu", "Nhận báo cáo giải thích rủi ro nhanh chóng, dễ hiểu và không gặp rào cản đăng nhập/đăng ký."),
            ("Ca sử dụng liên quan", "Tải tệp đa phương thức, Xem điểm rủi ro, Quan sát vùng nghi vấn, Tương tác với Trợ lý An toàn.")
        ]),
        ("Bảng 6. Thực thể E04: Quản trị viên Hệ thống", [
            ("Mã định danh", "E04"),
            ("Tên thực thể", "Quản trị viên Hệ thống / Chuyên viên An ninh"),
            ("Mô tả nghiệp vụ", "Tác nhân đặc quyền quản lý các mô hình AI, tập dữ liệu huấn luyện và cấu hình vận hành hệ thống."),
            ("Giả định cung cấp", "Sở hữu thông tin đăng nhập quản trị hợp lệ được xác thực bằng mật khẩu băm và mã JWT Token."),
            ("Giả định yêu cầu", "Hệ thống backend cung cấp các điểm cuối REST API bảo mật cho hoạt động quản trị và kiểm toán."),
            ("Ca sử dụng liên quan", "Đăng nhập/Đăng xuất, Quản lý tập dữ liệu, Xem xét đánh giá mô hình, Kiểm tra nhật ký kiểm toán.")
        ]),
        ("Bảng 7. Thực thể E05: Máy chủ Ứng dụng Backend", [
            ("Mã định danh", "E05"),
            ("Tên thực thể", "Máy chủ Ứng dụng Lõi FastAPI"),
            ("Mô tả nghiệp vụ", "Động cơ điều phối trung tâm quản lý các yêu cầu, thực thi pipeline AI và lưu trữ dữ liệu an toàn."),
            ("Giả định cung cấp", "Cung cấp các điểm cuối RESTful API bất đồng bộ an toàn và thực thi suy luận CoT giải thích rủi ro."),
            ("Giả định yêu cầu", "Cơ sở dữ liệu bền vững (MySQL/SQLite) và thư mục lưu trữ tạm thời scratch hoạt động bình thường."),
            ("Ca sử dụng liên quan", "Thực thi tiếp nhận dữ liệu, Chạy tổng hợp đồng thuận Consensus Fusion, Xây dựng chuỗi giải thích CoT.")
        ])
    ]

    for title, rows_data in entity_tables:
        p_t = doc.add_paragraph(title)
        p_t.runs[0].font.name = "Times New Roman"
        p_t.runs[0].font.bold = True
        p_t.runs[0].font.size = Pt(11)
        p_t.paragraph_format.space_before = Pt(8)

        tbl = doc.add_table(rows=len(rows_data), cols=2)
        set_table_borders(tbl, color="000000", sz="4")
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        for r_idx, d in enumerate(rows_data):
            format_cell_text(tbl.rows[r_idx].cells[0], d[0], bold=True, size_pt=10)
            format_cell_text(tbl.rows[r_idx].cells[1], d[1], size_pt=10)
            set_cell_background(tbl.rows[r_idx].cells[0], "F2F2F2")
            set_cell_background(tbl.rows[r_idx].cells[1], "FFFFFF")

    doc.add_page_break()

    # 3.2.2 CA SỬ DỤNG VẬN HÀNH
    h3 = doc.add_heading(level=3)
    r = h3.add_run("3.2.2. Ca sử dụng vận hành (Operational Use Cases)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True

    op_use_cases = [
        ("Bảng 8. Ca sử dụng UC-01: Tiếp nhận & Tiền xử lý Đa phương tiện", [
            ("Mã ca sử dụng", "UC-01"),
            ("Tiêu đề", "Tiếp nhận & Tiền xử lý Đa phương tiện"),
            ("Mô tả", "Hệ thống tiếp nhận các tệp đa phương tiện của người dùng (ảnh, PDF, văn bản), xác thực mã magic bytes và chuẩn bị bộ nhớ đệm."),
            ("Thực thể tham gia", "Tác nhân: Người dùng cuối; Hệ thống: FastAPI Gateway, MagicByteValidator, Thư mục đệm tạm thời."),
            ("Điều kiện tiên quyết", "1. Người dùng đã mở trang Quét an toàn. 2. Kích thước tệp dưới 15MB."),
            ("Luồng sự kiện chính", "1. Người dùng tải ảnh/PDF hoặc dán nội dung văn bản.\n2. Cổng tiếp nhận kiểm tra MIME magic bytes của tệp.\n3. Tệp hợp lệ được đưa vào bộ nhớ đệm scratch riêng biệt.\n4. Bộ định tuyến điều phối nhiệm vụ tới pipeline OCR và Pháp chứng."),
            ("Điều kiện sau", "Dữ liệu đã được làm sạch sẵn sàng cho các phân hệ suy luận AI tiếp theo."),
            ("Luồng ngoại lệ", "1. Định dạng không hỗ trợ hoặc tệp giả mạo: Trả về lỗi 400 Bad Request.\n2. Dung lượng vượt 15MB: Trả về lỗi 413 Payload Too Large.")
        ]),
        ("Bảng 9. Ca sử dụng UC-02: Nhận diện OCR Tiếng Việt & Giải mã QR Code", [
            ("Mã ca sử dụng", "UC-02"),
            ("Tiêu đề", "Nhận diện OCR Tiếng Việt & Giải mã QR Code"),
            ("Mô tả", "Trích xuất văn bản tiếng Việt có dấu kèm tọa độ hiển thị, đồng thời giải mã nội dung thanh toán hoặc URL từ mã QR."),
            ("Thực thể tham gia", "Hệ thống: Động cơ Tesseract OCR (vie), Thư viện Pillow, Bộ giải mã Pyzbar QR."),
            ("Điều kiện tiên quyết", "Bộ đệm hình ảnh tiền xử lý đã sẵn sàng trong bộ nhớ RAM."),
            ("Luồng sự kiện chính", "1. Pillow chuẩn hóa kênh màu và độ tương phản.\n2. Pyzbar quét tìm ma trận mã vạch 2D / mã QR.\n3. Tesseract thực thi trích xuất văn bản với gói ngôn ngữ vie+eng.\n4. Hệ thống trích xuất tọa độ đóng khung từng từ và chuỗi văn bản hoàn chỉnh."),
            ("Điều kiện sau", "Chuỗi văn bản và các liên kết giải mã từ QR được chuyển đến Động cơ Rủi ro và PhishVN."),
            ("Luồng ngoại lệ", "1. Văn bản mờ không đọc được: Trả về chuỗi rỗng và gắn cờ cảnh báo độ tương phản thấp.")
        ]),
        ("Bảng 10. Ca sử dụng UC-03: Phân tích Rủi ro Từ vựng URL PhishVN", [
            ("Mã ca sử dụng", "UC-03"),
            ("Tiêu đề", "Phân tích Rủi ro Từ vựng URL PhishVN"),
            ("Mô tả", "Trích xuất các liên kết web từ văn bản OCR hoặc mã QR và tính toán xác suất lừa đảo dựa trên 21 đặc trưng cấu trúc URL."),
            ("Thực thể tham gia", "Hệ thống: Bộ trích xuất URL, Bộ trích xuất đặc trưng PhishVN, Mô hình HistGradientBoosting."),
            ("Điều kiện tiên quyết", "Văn bản trích xuất hoặc mã QR chứa một hoặc nhiều chuỗi URL."),
            ("Luồng sự kiện chính", "1. Biểu thức Regex bóc tách các chuỗi URL từ kết quả OCR.\n2. Trích xuất 21 đặc trưng từ vựng (độ dài, tên miền phụ, entropy, ký tự đặc biệt).\n3. Mô hình HistGradientBoosting dự đoán xác suất giả mạo phishing.\n4. Chuẩn hóa điểm đe dọa URL (0–100) và đánh dấu các từ tố khả nghi."),
            ("Điều kiện sau", "Điểm rủi ro URL và danh mục phân tích đặc trưng được gắn kèm vào ngữ cảnh phân tích."),
            ("Luồng ngoại lệ", "1. Không phát hiện URL nào: Đặt điểm rủi ro URL = 0 và ghi nhận mô hình không áp dụng.")
        ]),
        ("Bảng 11. Ca sử dụng UC-04: Giám định Pháp chứng Thị giác ELA & Dấu vết Cắt ghép", [
            ("Mã ca sử dụng", "UC-04"),
            ("Tiêu đề", "Giám định Pháp chứng Thị giác ELA & Dấu vết Cắt ghép"),
            ("Mô tả", "Áp dụng kỹ thuật phân tích mức nén ảnh Error Level Analysis (ELA) để phát hiện dấu vết sửa đổi JPEG và kiểm tra siêu dữ liệu máy ảnh."),
            ("Thực thể tham gia", "Hệ thống: Bộ phân tích OpenCV ELA, Bộ đọc Pillow EXIF, Mô hình ResNet-18."),
            ("Điều kiện tiên quyết", "Tệp đầu vào là hình ảnh định dạng JPEG/PNG."),
            ("Luồng sự kiện chính", "1. Tạo ảnh tham chiếu lưu lại ở mức chất lượng JPEG 90%.\n2. Tính ma trận sai phân điểm ảnh để làm nổi bật vùng nén không đồng nhất.\n3. Đọc các thẻ siêu dữ liệu EXIF nhằm xác minh dấu vết phần mềm chỉnh sửa đồ họa.\n4. ResNet-18 suy luận xác suất bố cục gian lận với kỹ thuật hiệu chỉnh nhiệt độ (T=1.8)."),
            ("Điều kiện sau", "Điểm pháp chứng thị giác và các cờ bất thường được bổ sung vào ngữ cảnh kết quả."),
            ("Luồng ngoại lệ", "1. Ảnh không chứa thẻ EXIF: Ghi nhận cờ thiếu EXIF mà không trừ điểm oan cho ảnh.")
        ]),
        ("Bảng 12. Ca sử dụng UC-05: Tổng hợp Đồng thuận Đa phương thức (Consensus Fusion)", [
            ("Mã ca sử dụng", "UC-05"),
            ("Tiêu đề", "Tổng hợp Đồng thuận Đa phương thức"),
            ("Mô tả", "Tổng hợp các tín hiệu đa nguồn (từ khóa văn bản, PhishVN, pháp chứng thị giác, ResNet-18) thông qua cơ chế bầu chọn mềm có trọng số."),
            ("Thực thể tham gia", "Hệ thống: Động cơ Suy luận CoT Đa phương thức, Động cơ Rủi ro theo Quy tắc."),
            ("Điều kiện tiên quyết", "Tất cả các module phân tích độc lập đã trả về điểm tín hiệu tương ứng."),
            ("Luồng sự kiện chính", "1. Bộ lọc cổng chuyên biệt (Domain Gating) kiểm tra mẫu ảnh đời thường hoặc đoạn mã nguồn.\n2. Xác định các tín hiệu nguy cơ chính (Văn bản, URL, CoT) và tín hiệu thứ cấp (ELA, ResNet).\n3. Tính điểm đồng thuận có trọng số (0–100) tránh các mức điểm cực đoan thiếu chuẩn hóa.\n4. Ánh xạ điểm số sang 3 mức độ an toàn: An toàn (0-25), Nghi ngờ (26-59), Nguy hiểm (60-100)."),
            ("Điều kiện sau", "Điểm rủi ro và nhãn phân loại chuẩn hóa cuối cùng được tạo để chuyển về client."),
            ("Luồng ngoại lệ", "1. Domain Gating xác nhận đây là ảnh sinh hoạt đời thường lành tính: Ép điểm an toàn (<=15).")
        ]),
        ("Bảng 13. Ca sử dụng UC-06: Hướng dẫn Khắc phục & Trợ lý An toàn Tương tác", [
            ("Mã ca sử dụng", "UC-06"),
            ("Tiêu đề", "Hướng dẫn Khắc phục & Trợ lý An toàn Tương tác"),
            ("Mô tả", "Sinh các khuyến nghị an ninh mạng theo ngữ cảnh và cung cấp trợ lý đàm thoại tương tác hỗ trợ nạn nhân."),
            ("Thực thể tham gia", "Tác nhân: Người dùng cuối; Hệ thống: SafetyAssistant, ExplanationBuilder."),
            ("Điều kiện tiên quyết", "Kết quả quét và các chỉ số nguy cơ đã được tính toán xong."),
            ("Luồng sự kiện chính", "1. ExplanationBuilder tổng hợp các tín hiệu nguy cơ thành văn bản tiếng Việt dễ hiểu.\n2. Xây dựng 3 biện pháp ứng phó khẩn cấp cần thực hiện ngay.\n3. Người dùng chọn câu hỏi nhanh hoặc nhập câu hỏi hỗ trợ riêng.\n4. SafetyAssistant phản hồi câu hỏi dựa trên ngữ cảnh phiên quét hiện tại."),
            ("Điều kiện sau", "Người dùng nhận được chỉ dẫn hành động cụ thể để ngăn chặn thiệt hại tài chính hoặc lộ lọt danh tính."),
            ("Luồng ngoại lệ", "1. Người dùng hỏi chủ đề ngoài phạm vi: Trợ lý điều hướng lại về các bước ứng phó lừa đảo.")
        ]),
        ("Bảng 14. Ca sử dụng UC-07: Quản lý Lịch sử Quét Bảo vệ Quyền Riêng tư", [
            ("Mã ca sử dụng", "UC-07"),
            ("Tiêu đề", "Quản lý Lịch sử Quét Bảo vệ Quyền Riêng tư"),
            ("Mô tả", "Lưu trữ nhật ký các phiên kiểm tra trực tiếp trên trình duyệt web của người dùng mà không cần tài khoản."),
            ("Thực thể tham gia", "Tác nhân: Người dùng cuối; Hệ thống: React Client, Bộ nhớ HTML5 localStorage."),
            ("Điều kiện tiên quyết", "Kết quả quét được trả về thành công từ máy chủ backend."),
            ("Luồng sự kiện chính", "1. React client chuyển đổi tóm tắt kết quả thành định dạng JSON.\n2. Lưu trữ bản ghi vào localStorage của trình duyệt theo khóa dữ liệu định sẵn.\n3. Duy trì giới hạn FIFO tối đa 50 bản ghi kiểm tra gần nhất.\n4. Người dùng mở tab Lịch sử để xem lại hoặc chủ động xóa sạch dữ liệu."),
            ("Điều kiện sau", "Lịch sử quét được bảo toàn trên thiết bị; máy chủ không lưu trữ bất kỳ thông tin cá nhân nào của khách."),
            ("Luồng ngoại lệ", "1. Vượt quá hạn mức bộ nhớ localStorage: Tự động dọn dẹp các bản ghi cũ nhất.")
        ]),
        ("Bảng 15. Ca sử dụng UC-08: Quản trị Mô hình & Tập Dữ liệu Cấp Quản trị viên", [
            ("Mã ca sử dụng", "UC-08"),
            ("Tiêu đề", "Quản trị Mô hình & Tập Dữ liệu Cấp Quản trị viên"),
            ("Mô tả", "Cho phép quản trị viên đã đăng nhập quản lý tập dữ liệu AI, theo dõi đánh giá benchmark và kiểm toán hệ thống."),
            ("Thực thể tham gia", "Tác nhân: Quản trị viên; Hệ thống: Các điểm cuối FastAPI Admin, SQLAlchemy, MySQL."),
            ("Điều kiện tiên quyết", "Quản trị viên đã xác thực đăng nhập thành công qua /login (nhận mã JWT Bearer Token)."),
            ("Luồng sự kiện chính", "1. Quản trị viên gửi thông tin định danh lên điểm cuối /login.\n2. Máy chủ kiểm tra mật khẩu băm và cấp mã JWT ký số an toàn.\n3. Quản trị viên truy cập các phân hệ dữ liệu huấn luyện, đánh giá mô hình và nhật ký hệ thống.\n4. Cập nhật động trọng số từ khóa lừa đảo và xuất báo cáo kiểm toán."),
            ("Điều kiện sau", "Cấu hình hệ thống và vệt kiểm toán được cập nhật bền vững vào cơ sở dữ liệu."),
            ("Luồng ngoại lệ", "1. Mã Token hết hạn hoặc không hợp lệ: Trả về lỗi 401 Unauthorized và chuyển hướng về trang đăng nhập.")
        ])
    ]

    for title, rows_data in op_use_cases:
        p_t = doc.add_paragraph(title)
        p_t.runs[0].font.name = "Times New Roman"
        p_t.runs[0].font.bold = True
        p_t.runs[0].font.size = Pt(11)
        p_t.paragraph_format.space_before = Pt(8)

        tbl = doc.add_table(rows=len(rows_data), cols=2)
        set_table_borders(tbl, color="000000", sz="4")
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        for r_idx, d in enumerate(rows_data):
            format_cell_text(tbl.rows[r_idx].cells[0], d[0], bold=True, size_pt=10)
            format_cell_text(tbl.rows[r_idx].cells[1], d[1], size_pt=10)
            set_cell_background(tbl.rows[r_idx].cells[0], "F2F2F2")
            set_cell_background(tbl.rows[r_idx].cells[1], "FFFFFF")

    doc.add_page_break()

    # =========================================================================
    # 3.3 THUỘC TÍNH CHẤT LƯỢNG
    # =========================================================================
    h2 = doc.add_heading(level=2)
    r = h2.add_run("3.3. Thuộc tính chất lượng (Kịch bản QA01 đến QA05)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "Các thuộc tính chất lượng được đặc tả theo khung kịch bản cụ thể chuẩn SEI gồm 6 thành phần: Nguồn kích thích (Source), Kích thích (Stimulus), Môi trường (Environment), Tác tạo kích thích (Artifact), Phản ứng hệ thống (Response), và Thước đo phản ứng (Response Measure).")

    qa_scenarios = [
        ("Bảng 16. Thuộc tính chất lượng QA01: Hiệu năng / Độ trễ xử lý", [
            ("Mã kịch bản", "QA01"),
            ("Thuộc tính chất lượng", "Hiệu năng (Độ trễ & Thông lượng)"),
            ("Kích thích (Stimulus)", "Người dùng tải lên một tạo tác đa phương thức (ảnh 3MB gồm chữ tiếng Việt, mã QR và liên kết URL)."),
            ("Nguồn kích thích", "Trình duyệt web của người dùng cuối."),
            ("Môi trường", "Hệ thống đang chịu tải đồng thời bình thường (10-20 yêu cầu đồng thời)."),
            ("Tác tạo kích thích", "Bộ định tuyến FastAPI Router, Tesseract OCR, PhishVN, ResNet-18."),
            ("Phản ứng hệ thống", "Máy chủ bóc tách ảnh, giải mã QR, thực thi suy luận mô hình, tạo chuỗi giải thích và trả về JSON."),
            ("Thước đo phản ứng", "Toàn bộ chu kỳ phản hồi từ đầu đến cuối hoàn tất trong thời gian dưới 3.0 giây (P95 latency < 2.5s).")
        ]),
        ("Bảng 17. Thuộc tính chất lượng QA02: Bảo mật & Riêng tư / Không lưu định danh (Zero-PII)", [
            ("Mã kịch bản", "QA02"),
            ("Thuộc tính chất lượng", "Bảo mật & Quyền riêng tư Dữ liệu"),
            ("Kích thích (Stimulus)", "Người dùng tải lên ảnh chụp chứa số tài khoản ngân hàng bảo mật hoặc biên lai giao dịch cá nhân."),
            ("Nguồn kích thích", "Người dùng đại chúng (khách vãng lai)."),
            ("Môi trường", "Chế độ quét khách thông thường."),
            ("Tác tạo kích thích", "Thư mục tải lên cách ly Sandbox, CSDL MySQL, LocalStorage."),
            ("Phản ứng hệ thống", "Hệ thống xử lý ảnh trên bộ nhớ tạm, loại bỏ các trường định danh cá nhân và không lưu PII của khách lên máy chủ."),
            ("Thước đo phản ứng", "100% tệp ảnh quét của khách bị xóa khỏi thư mục tạm sau khi phân tích xong; 0 byte dữ liệu PII lưu trong MySQL.")
        ]),
        ("Bảng 18. Thuộc tính chất lượng QA03: Tính Module & Khả năng Nâng cấp Nóng", [
            ("Mã kịch bản", "QA03"),
            ("Thuộc tính chất lượng", "Tính Module & Khả năng Mở rộng"),
            ("Kích thích (Stimulus)", "Đội ngũ kỹ sư nâng cấp bộ phân loại hình ảnh từ ResNet-18 lên mô hình thị giác ngôn ngữ lớn (Qwen2.5-VL)."),
            ("Nguồn kích thích", "Đội ngũ phát triển AI."),
            ("Môi trường", "Giai đoạn phát triển thử nghiệm và bảo trì."),
            ("Tác tạo kích thích", "vlm_image_analyzer.py, reasoning_engine.py."),
            ("Phản ứng hệ thống", "Kỹ sư cập nhật đường dẫn checkpoint mô hình hoặc bật biến môi trường USE_VLM_ANALYZER=true mà không phải sửa REST API."),
            ("Thước đo phản ứng", "Thời gian tích hợp mô hình mới <= 4 giờ lập trình viên; không gây bất kỳ thay đổi nào làm gãy hợp đồng giao tiếp API với client.")
        ]),
        ("Bảng 19. Thuộc tính chất lượng QA04: Khả năng Bảo trì & Sửa đổi Quy tắc", [
            ("Mã kịch bản", "QA04"),
            ("Thuộc tính chất lượng", "Khả năng Bảo trì & Sức khỏe Mã nguồn"),
            ("Kích thích (Stimulus)", "Phát hiện một từ khóa bị báo động nhầm hoặc trọng số rủi ro chưa chuẩn trong động cơ rủi ro."),
            ("Nguồn kích thích", "Đội ngũ kiểm thử QA / Đóng góp ý kiến từ người dùng."),
            ("Môi trường", "Môi trường vận hành thực tế (Production)."),
            ("Tác tạo kích thích", "risk_engine.py / Bảng từ khóa động trên cổng quản trị."),
            ("Phản ứng hệ thống", "Quản trị viên cập nhật trọng số từ khóa trực tiếp trên cổng Admin hoặc lập trình viên chỉnh sửa từ điển trong mã nguồn."),
            ("Thước đo phản ứng", "Thời gian triển khai cập nhật dưới 2 giờ; bộ kiểm thử tự động pytest hoàn tất toàn bộ trong vòng dưới 15 giây.")
        ]),
        ("Bảng 20. Thuộc tính chất lượng QA05: Độ sẵn sàng & Khả năng Chịu lỗi", [
            ("Mã kịch bản", "QA05"),
            ("Thuộc tính chất lượng", "Độ sẵn sàng & Tính kiên cường của Hệ thống"),
            ("Kích thích (Stimulus)", "Sự cố phân hệ phụ thuộc bên ngoài (dịch vụ MySQL tạm thời khởi động lại hoặc tệp bị hỏng làm lỗi OCR)."),
            ("Nguồn kích thích", "Lỗi nội bộ hệ thống hoặc tải dữ liệu sai lệch cấu trúc."),
            ("Môi trường", "Thời gian chạy hệ thống thực tế."),
            ("Tác tạo kích thích", "Bộ kết nối CSDL Connection Pool, Bộ xử lý ngoại lệ API Error Handlers."),
            ("Phản ứng hệ thống", "FastAPI bắt gọn ngoại lệ, tự động kích hoạt cơ chế dự phòng an toàn và trả về thông báo lỗi thân thiện cho người dùng."),
            ("Thước đo phản ứng", "Thời gian sẵn sàng của hệ thống đạt >= 99.0%; không bao giờ sập máy chủ trả mã lỗi 500; người dùng nhận được thông báo hướng dẫn rõ ràng.")
        ])
    ]

    for title, rows_data in qa_scenarios:
        p_t = doc.add_paragraph(title)
        p_t.runs[0].font.name = "Times New Roman"
        p_t.runs[0].font.bold = True
        p_t.runs[0].font.size = Pt(11)
        p_t.paragraph_format.space_before = Pt(8)

        tbl = doc.add_table(rows=len(rows_data), cols=2)
        set_table_borders(tbl, color="000000", sz="4")
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        for r_idx, d in enumerate(rows_data):
            format_cell_text(tbl.rows[r_idx].cells[0], d[0], bold=True, size_pt=10)
            format_cell_text(tbl.rows[r_idx].cells[1], d[1], size_pt=10)
            set_cell_background(tbl.rows[r_idx].cells[0], "F2F2F2")
            set_cell_background(tbl.rows[r_idx].cells[1], "FFFFFF")

    doc.add_page_break()

    # =========================================================================
    # MỤC 4: RÀNG BUỘC HỆ THỐNG
    # =========================================================================
    h1 = doc.add_heading(level=1)
    r = h1.add_run("4. Các ràng buộc hệ thống")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("4.1. Ràng buộc kinh doanh")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    p_t21 = doc.add_paragraph("Bảng 21. Ma trận ràng buộc kinh doanh và tiêu chí chấp nhận")
    p_t21.runs[0].font.name = "Times New Roman"
    p_t21.runs[0].font.bold = True
    p_t21.runs[0].font.size = Pt(11.5)

    tbl_t21 = doc.add_table(rows=5, cols=3)
    set_table_borders(tbl_t21, color="000000", sz="4")
    tbl_t21.alignment = WD_TABLE_ALIGNMENT.CENTER
    t21_headers = ["Lĩnh vực ràng buộc", "Nội dung ràng buộc chi tiết", "Tiêu chí và Định hướng chấp nhận"]
    for i, h in enumerate(t21_headers):
        format_cell_text(tbl_t21.rows[0].cells[i], h, bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t21.rows[0].cells[i], "E6E6E6")

    biz_constraints = [
        ("Ngân sách kinh tế", "Kinh phí nghiên cứu đồ án sinh viên giới hạn dưới $350 USD cho toàn bộ chi phí lưu trữ và tính toán.", "Tận dụng máy trạm cục bộ để huấn luyện mô hình; triển khai trên gói miễn phí AWS EC2 và thư viện mã nguồn mở."),
        ("Môi trường / Dữ liệu đầu vào", "Độ chính xác của OCR và mô hình AI phụ thuộc nhiều vào độ phân giải ảnh và ánh sáng chụp.", "Tích hợp các giải thuật tiền xử lý OpenCV (khử nghiêng, ngưỡng tương thích) để xử lý ảnh chất lượng kém."),
        ("Đạo đức & Quyền riêng tư", "Xử lý các hình ảnh nhạy cảm như biên lai chuyển khoản ngân hàng và nhật ký trò chuyện riêng tư.", "Ẩn danh hóa toàn bộ dữ liệu kiểm thử; cam kết không lưu giữ ảnh quét của khách trên máy chủ."),
        ("Xã hội & Mức độ tiếp nhận", "Người dân không chuyên công nghệ cần hiểu rõ mức độ nguy hiểm một cách nhanh chóng, trực quan.", "Thiết kế cảnh báo màu sắc đèn giao thông (Xanh/Vàng/Đỏ) kèm lời giải thích bằng tiếng Việt phổ thông.")
    ]
    for r_idx, d in enumerate(biz_constraints):
        row = tbl_t21.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("4.2. Ràng buộc kỹ thuật & Công nghệ")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "• Ngôn ngữ lập trình: Python 3.12 (Phía Backend & Pipelines AI), JavaScript ECMAScript 2022 (Phía Frontend).\n• Khung phần mềm Web: FastAPI 0.110+ (Chạy trên Uvicorn ASGI Server), React 18 với công cụ đóng gói Vite.\n• Trí tuệ nhân tạo & Học máy: PyTorch 2.4, Scikit-Learn 1.5, Tesseract OCR 5.3 (mô hình ngôn ngữ vie+eng), OpenCV-Python 4.10, Pillow 10.4.\n• Lưu trữ dữ liệu & CSDL: SQLAlchemy 2.0 ORM, SQLite 3 (phát triển & kiểm thử cục bộ), MySQL 8.0 (môi trường sản xuất).\n• An ninh & Xác thực: python-jose (Mã xác thực JWT Bearer Token), passlib (Băm mật khẩu PBKDF2-HMAC-SHA256), python-magic.\n• Hạ tầng triển khai: Docker, Docker Compose, Git / GitHub Actions CI/CD.")

    doc.add_page_break()

    # =========================================================================
    # MỤC 5: SƠ ĐỒ & CÁC GÓC NHÌN KIẾN TRÚC
    # =========================================================================
    h1 = doc.add_heading(level=1)
    r = h1.add_run("5. Sơ đồ & Các góc nhìn kiến trúc hệ thống")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("5.1. Góc nhìn Thành phần & Kết nối (C&C View)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True

    h3 = doc.add_heading(level=3)
    r = h3.add_run("5.1.1. Góc nhìn C&C phía Client")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    img_cc_client = "arch_diagrams/fig2_cc_client.png"
    if not os.path.exists(img_cc_client):
        img_cc_client = "TAILIEU_CAPSTONE_C1SE06_SFDS/4. ARCHITECTURE DESIGN/diagrams/fig2_cc_client.png"
    if os.path.exists(img_cc_client):
        p.add_run().add_picture(img_cc_client, width=Inches(5.5))
        
    p_fig2 = doc.add_paragraph("Hình 2. Góc nhìn Thành phần & Kết nối (C&C) phía Client")
    p_fig2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fig2.runs[0].font.name = "Times New Roman"
    p_fig2.runs[0].font.italic = True
    p_fig2.runs[0].font.size = Pt(11)

    add_body_p(doc, "Mô tả kiến trúc Client:\nKiến trúc phía Client được phát triển dưới dạng ứng dụng đơn trang (SPA) bằng React 18. Người dùng tương tác qua các Khung chứa trang (ScanPage, AdminPage, HistoryPage), các khung chứa này tập hợp các Thành phần giao diện tái sử dụng (UploadDropzone, CanvasHighlight, SafetyAssistantWidget). Các dịch vụ quản lý trạng thái (useAppController, localStorageManager) đóng gói việc gọi API thông qua Axios và đồng bộ lịch sử quét vào bộ nhớ trình duyệt. Dữ liệu JSON phản hồi từ backend FastAPI được hiển thị động thành đồng hồ đo rủi ro, khung tọa độ vi phạm và thẻ giải thích chi tiết.")
    add_body_p(doc, "Vai trò và trách nhiệm các thành phần Client:\n• Người dùng cuối: Tải tệp lên, quan sát điểm số rủi ro, kiểm tra vùng nghi vấn và đặt câu hỏi cho trợ lý an toàn.\n• Khung chứa trang (Page Containers): Điều phối phân cấp hiển thị, gắn kết các thành phần giao diện và ủy thác các cuộc gọi API bất đồng bộ.\n• Thành phần UI (Components): Các khối hiển thị trực quan tái sử dụng (vùng kéo thả tải ảnh, lớp vẽ canvas tọa độ, thanh đo điểm rủi ro).\n• Dịch vụ & Hooks: Đóng gói các lời gọi REST API, quản lý mã xác thực JWT trong HTTP Header và quản lý bộ nhớ localStorage.\n• Máy chủ Backend: Nhận các yêu cầu dữ liệu multipart và phản hồi các gói tin JSON thẩm định rủi ro có cấu trúc.")

    h3 = doc.add_heading(level=3)
    p = h3.paragraph_format
    p.space_before = Pt(14)
    r = h3.add_run("5.1.2. Góc nhìn C&C phía Server & Pipeline phân tích AI")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    img_cc_server = "arch_diagrams/fig3_cc_server.png"
    if not os.path.exists(img_cc_server):
        img_cc_server = "TAILIEU_CAPSTONE_C1SE06_SFDS/4. ARCHITECTURE DESIGN/diagrams/fig3_cc_server.png"
    if os.path.exists(img_cc_server):
        p.add_run().add_picture(img_cc_server, width=Inches(6.0))
        
    p_fig3 = doc.add_paragraph("Hình 3. Góc nhìn Thành phần & Kết nối (C&C) phía Server & Pipeline AI")
    p_fig3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fig3.runs[0].font.name = "Times New Roman"
    p_fig3.runs[0].font.italic = True
    p_fig3.runs[0].font.size = Pt(11)

    add_body_p(doc, "Mô tả kiến trúc Server:\nPhía Server tận dụng khung làm việc bất đồng bộ ASGI của FastAPI để đạt thông lượng cao và độ trễ thấp. Mọi yêu cầu được kiểm tra qua các middleware bảo mật (kiểm tra mã tệp magic byte, CORS, xác thực JWT). Động cơ Suy luận CoT Đa phương thức điều phối việc phân tích qua 4 phân hệ chuyên biệt: Tesseract OCR (trích xuất văn bản tiếng Việt), PhishVN (21 đặc trưng URL), ResNet-18 (phân loại bố cục ảnh kèm chuẩn hóa nhiệt độ T=1.8), và OpenCV (phân tích mức nén ảnh ELA). Module Consensus Fusion tổng hợp các tín hiệu thành điểm số rủi ro chuẩn hóa, trong khi ExplanationBuilder và SafetyAssistant sinh nội dung giải thích và hướng dẫn khắc phục.")
    add_body_p(doc, "Vai trò và trách nhiệm các thành phần Server:\n• Bộ định tuyến API Router: Kiểm tra tính hợp lệ dữ liệu HTTP, áp dụng giới hạn tần suất gửi yêu cầu (rate limiting), kiểm tra định dạng tệp và chuyển tiếp yêu cầu.\n• Động cơ Suy luận CoT Đa phương thức: Kiểm tra cổng chuyên biệt (Domain Gating) và tổng hợp bằng chứng đa nguồn thành chuỗi giải thích có cấu trúc.\n• Các pipeline suy luận AI: Các tiến trình chạy chuyên trách thực thi thư viện Tesseract C-bindings, Scikit-learn HistGB và mạng nơ-ron PyTorch.\n• Dịch vụ ứng dụng (Services): Lớp nghiệp vụ xử lý khuyến nghị an toàn, ghi vệt kiểm toán và truy vấn dữ liệu.\n• Tầng Cơ sở dữ liệu: Lớp ORM SQLAlchemy tương tác với SQLite (môi trường thử nghiệm cục bộ) và MySQL 8.0 (sản xuất).")

    doc.add_page_break()

    # =========================================================================
    # 5.2 GÓC NHÌN MODULE
    # =========================================================================
    h2 = doc.add_heading(level=2)
    r = h2.add_run("5.2. Góc nhìn Module")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True

    h3 = doc.add_heading(level=3)
    r = h3.add_run("5.2.1. Phân rã Module phía Client")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    img_mod_client = "arch_diagrams/fig4_module_client.png"
    if not os.path.exists(img_mod_client):
        img_mod_client = "TAILIEU_CAPSTONE_C1SE06_SFDS/4. ARCHITECTURE DESIGN/diagrams/fig4_module_client.png"
    if os.path.exists(img_mod_client):
        p.add_run().add_picture(img_mod_client, width=Inches(5.8))
        
    p_fig4 = doc.add_paragraph("Hình 4. Sơ đồ Phân rã Module phía Client")
    p_fig4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fig4.runs[0].font.name = "Times New Roman"
    p_fig4.runs[0].font.italic = True
    p_fig4.runs[0].font.size = Pt(11)

    add_body_p(doc, "Cấu trúc phân tầng Module phía Client:\nKiến trúc module Client tuân thủ nguyên tắc phân tách trách nhiệm chặt chẽ qua 3 tầng rõ rệt:\n1. Tầng Trang giao diện (Page View Modules): Các bộ điều khiển góc nhìn chính (ScanPage, HistoryPage, AdminPage, AuthPage, OverviewPage) tương ứng với các định tuyến của ứng dụng.\n2. Tầng Thành phần tái sử dụng (Reusable Component Modules): Các đơn vị hiển thị phi trạng thái (UploadDropzone, CanvasBoundingBox, ScoreMeterBar, SafetyAssistantWidget, TechnicalBreakdown) chuyên trách kết xuất đồ họa và tương tác cục bộ.\n3. Tầng Trạng thái & Dịch vụ (State & Service Modules): Các custom hook React (useAppController) và các module tiện ích (localStorageManager, apiClient) đóng gói các thao tác giao tiếp mạng, bẫy lỗi và lưu trữ cục bộ.")

    h3 = doc.add_heading(level=3)
    p = h3.paragraph_format
    p.space_before = Pt(14)
    r = h3.add_run("5.2.2. Phân rã Module phía Server")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    img_mod_server = "arch_diagrams/fig5_module_server.png"
    if not os.path.exists(img_mod_server):
        img_mod_server = "TAILIEU_CAPSTONE_C1SE06_SFDS/4. ARCHITECTURE DESIGN/diagrams/fig5_module_server.png"
    if os.path.exists(img_mod_server):
        p.add_run().add_picture(img_mod_server, width=Inches(6.0))
        
    p_fig5 = doc.add_paragraph("Hình 5. Sơ đồ Phân rã Module phía Server")
    p_fig5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fig5.runs[0].font.name = "Times New Roman"
    p_fig5.runs[0].font.italic = True
    p_fig5.runs[0].font.size = Pt(11)

    add_body_p(doc, "Cấu trúc phân tầng Module phía Server:\nKiến trúc module máy chủ chia thành 4 lớp nghiệp vụ mạch lạc:\n1. Tầng Giao diện API (Interface Layer): Bao gồm tệp main.py và các bộ định tuyến router xử lý yêu cầu HTTP và chuyển tiếp tới các dịch vụ lõi.\n2. Tầng Phân tích & Suy luận AI (Core Inference Layer): Bao gồm reasoning_engine.py (tổng hợp CoT), ocr_engine.py (Tesseract), phishvn_url_model.py (đặc trưng URL PhishVN) và vision_engine.py (ResNet-18 và OpenCV ELA).\n3. Tầng Dịch vụ Ứng dụng (Application Service Layer): Điều phối quy trình phân tích, xây dựng chuỗi giải thích thân thiện và hỗ trợ người dùng tương tác.\n4. Tầng Dữ liệu & Lưu trữ (Data Access Layer): Lớp cơ sở dữ liệu database.py và các mô hình models.py sử dụng SQLAlchemy ORM để truy xuất bền vững.")

    doc.add_page_break()

    # =========================================================================
    # 5.3 GÓC NHÌN PHÂN BỔ & TRIỂN KHAI
    # =========================================================================
    h2 = doc.add_heading(level=2)
    r = h2.add_run("5.3. Góc nhìn Phân bổ & Triển khai (Allocation View)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    img_alloc = "arch_diagrams/fig6_allocation_view.png"
    if not os.path.exists(img_alloc):
        img_alloc = "TAILIEU_CAPSTONE_C1SE06_SFDS/4. ARCHITECTURE DESIGN/diagrams/fig6_allocation_view.png"
    if os.path.exists(img_alloc):
        p.add_run().add_picture(img_alloc, width=Inches(5.8))
        
    p_fig6 = doc.add_paragraph("Hình 6. Góc nhìn Phân bổ & Triển khai Hệ thống (Allocation View)")
    p_fig6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fig6.runs[0].font.name = "Times New Roman"
    p_fig6.runs[0].font.italic = True
    p_fig6.runs[0].font.size = Pt(11)

    add_body_p(doc, "Mô tả phân bổ triển khai:\nGóc nhìn phân bổ thể hiện cách các đơn vị phần mềm thực thi được ánh xạ lên các nút vật lý và môi trường container hóa:\n• Tầng Client (Máy trạm người dùng): Ứng dụng React SPA thực thi trực tiếp trên môi trường trình duyệt web hiện đại (Chrome, Firefox, Safari, Edge). Toàn bộ việc kết xuất giao diện, tính toán tọa độ canvas bounding box và lưu trữ lịch sử được thực hiện cục bộ trên thiết bị của người dùng, giải phóng tải cho máy chủ.\n• Nút Máy chủ Ứng dụng (Docker Container / Linux VM): Dịch vụ backend chạy trong container Docker độc lập trên nền tảng Python 3.12. Máy chủ Uvicorn ASGI lắng nghe tại cổng 8000. Máy chủ quản lý thư mục lưu trữ tạm thời scratch (uploads/) và nạp các checkpoint mô hình học sâu (models/phishing_resnet18.pt, models/phishvn_url_histgb.joblib) cùng mô hình ngôn ngữ Tesseract (tessdata/vie.traineddata).\n• Nút Cơ sở Dữ liệu: Trong môi trường phát triển, SQLite lưu trữ tệp cục bộ (scam_detector.db). Trong môi trường vận hành thực tế, MySQL 8.0 chạy trong container riêng biệt qua cổng TCP 3306 và được quản lý bằng cơ chế Connection Pooling của SQLAlchemy.")
    add_body_p(doc, "Vai trò và trách nhiệm các nút vật lý & tiến trình:\n• Môi trường Trình duyệt Web: Kết xuất các góc nhìn giao diện, quản lý lớp phủ vẽ canvas và cung cấp bộ nhớ lưu trữ localStorage an toàn trên máy khách.\n• Container FastAPI ASGI: Điều phối các điểm cuối REST API, quản lý các luồng công nhân nền cho các mô hình AI và xác thực mã an ninh.\n• Hệ thống Tệp lưu trữ tạm (Scratch): Thư mục đệm xử lý ảnh và tệp PDF với cơ chế tự động dọn dẹp giải phóng bộ nhớ sau khi phân tích xong.\n• Container Cơ sở Dữ liệu: Lưu trữ thông tin tài khoản quản trị viên, danh mục lừa đảo, tập dữ liệu huấn luyện và nhật ký kiểm toán hệ thống.")

    doc.add_page_break()

    # =========================================================================
    # MỤC 6: TÀI LIỆU THAM KHẢO
    # =========================================================================
    h1 = doc.add_heading(level=1)
    r = h1.add_run("6. Tài liệu tham khảo")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    p_t22 = doc.add_paragraph("Bảng 22. Danh mục tài liệu tham khảo học thuật & tiêu chuẩn kiến trúc")
    p_t22.runs[0].font.name = "Times New Roman"
    p_t22.runs[0].font.bold = True
    p_t22.runs[0].font.size = Pt(11.5)

    tbl_t22 = doc.add_table(rows=8, cols=3)
    set_table_borders(tbl_t22, color="000000", sz="4")
    tbl_t22.alignment = WD_TABLE_ALIGNMENT.CENTER
    t22_headers = ["STT", "Tiêu chuẩn / Tài liệu tham khảo", "Trích dẫn đầy đủ & Nguồn tài liệu"]
    for i, h in enumerate(t22_headers):
        format_cell_text(tbl_t22.rows[0].cells[i], h, bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t22.rows[0].cells[i], "E6E6E6")

    arch_refs = [
        ("1", "Software Architecture in Practice", "Bass, L., Clements, P., & Kazman, R. (2021). Software Architecture in Practice (4th ed.). Addison-Wesley Professional."),
        ("2", "Documenting Software Architectures", "Clements, P. et al. (2010). Documenting Software Architectures: Views and Beyond (2nd ed.). SEI Series in Software Engineering."),
        ("3", "FastAPI Framework", "Tiangolo, S. (2024). FastAPI: High-performance Python Web Framework. https://fastapi.tiangolo.com/"),
        ("4", "React 18 & Vite", "Meta Platforms & Evan You. (2024). React Library & Vite Frontend Tooling. https://react.dev/"),
        ("5", "PhishVN Dataset", "Nguyen, H. et al. (2024). PhishVN: A Time-Stamped Vietnamese URL Phishing Dataset. Mendeley Data."),
        ("6", "Deep Residual Learning", "He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep Residual Learning for Image Recognition. IEEE CVPR."),
        ("7", "ISO/IEC/IEEE 42010:2011", "Systems and software engineering - Architecture description standards. IEEE Computer Society.")
    ]
    for r_idx, d in enumerate(arch_refs):
        row = tbl_t22.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,1] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # Lưu tập tin kết quả
    output_path = r"D:\scam-detector\TAILIEU_CAPSTONE_C1SE06_SFDS\4. ARCHITECTURE DESIGN\C1SE.06_ArchitectureDesign_SFDS_v1.0_VI.docx"
    doc.save(output_path)
    print("Successfully generated:", output_path)

if __name__ == "__main__":
    create_architecture_doc_vi()

# -*- coding: utf-8 -*-
"""
Generate official Vietnamese Capstone Database Design Document (.docx)
Output: D:\scam-detector\TAILIEU_CAPSTONE_C1SE06_SFDS\5. DATABASE DESIGN\C1SE.06_DatabaseDesign_SFDS_v1.1_VI.docx
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_table_borders(table, color="000000", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_p(doc, text="", space_before=0, space_after=4, line_spacing=1.25, align=WD_ALIGN_PARAGRAPH.LEFT, bold=False, italic=False, font_size=13, color=RGBColor(0,0,0)):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    p.alignment = align
    if text:
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.name = "Times New Roman"
        run.font.size = Pt(font_size)
        run.font.color.rgb = color
    return p

def add_run(p, text, bold=False, italic=False, font_size=13, color=RGBColor(0,0,0)):
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.name = "Times New Roman"
    run.font.size = Pt(font_size)
    run.font.color.rgb = color
    return run

def create_styled_table(doc, headers, data, col_widths=None, alignment=WD_TABLE_ALIGNMENT.CENTER):
    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = alignment
    set_table_borders(table, color="000000", sz="4")

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = ""
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        add_run(p, h, bold=True, font_size=11, color=RGBColor(0,0,0))
        set_cell_bg(hdr_cells[i], "E6E6E6")
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
        hdr_cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    # Data Rows
    for r_idx, row_data in enumerate(data):
        row_cells = table.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = ""
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15

            if c_idx in [0] or str(val) in ["PK", "FK", "Index", "Required", "Optional", "Bắt buộc", "Tùy chọn", "Khóa chính"]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT

            is_bold = (c_idx == 1 and len(row_data) >= 5) or (c_idx == 0 and len(row_data) < 4)
            add_run(p, str(val), bold=is_bold, font_size=10.5, color=RGBColor(0,0,0))
            set_cell_bg(row_cells[c_idx], "FFFFFF")
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=100, right=100)
            row_cells[c_idx].vertical_alignment = WD_ALIGN_VERTICAL.TOP

    if col_widths:
        for row in table.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = Inches(width)

    add_p(doc, "", space_before=0, space_after=4)
    return table

def generate_document():
    doc = docx.Document()

    # Configure Margins: 1 inch
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)

    # =========================================================================
    # TRANG 1: ẢNH BÌA
    # =========================================================================
    logo_path = "extracted_media/image_1.png"
    if os.path.exists(logo_path):
        p_logo = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
        p_logo.add_run().add_picture(logo_path, width=Inches(3.2))

    add_p(doc, "VIỆN ĐÀO TẠO & NGHIÊN CỨU QUỐC TẾ", bold=True, font_size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    add_p(doc, "ĐỒ ÁN TỐT NGHIỆP 1 / CAPSTONE PROJECT 1", bold=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p(doc, "CMU-SE 450 – C1SE.06", bold=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    add_p(doc, "TÀI LIỆU THIẾT KẾ CƠ SỞ DỮ LIỆU", bold=True, font_size=20, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    add_p(doc, "Phiên bản 1.1", bold=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p(doc, "Ngày: 04 tháng 11 năm 2026", italic=True, font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    add_p(doc, "SFDS", bold=True, font_size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p(doc, "Hệ Thống Cảnh Báo và Phát Hiện Lừa Đảo Trực Tuyến Đa Phương Thức Có Giải Thích", italic=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)

    add_p(doc, "Thực hiện bởi", bold=True, font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    add_p(doc, "Hào, Phạm Tấn\nNhung, Đào Thị Mỹ\nNam, Trần Hoàng Nhật\nTuấn, Nguyễn Phan Đức", font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14, line_spacing=1.2)

    add_p(doc, "Giảng viên hướng dẫn", bold=True, font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    add_p(doc, "KS. Hà Mạnh Toàn", font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)

    add_p(doc, "Đại diện Hội đồng Đánh giá Thiết kế CSDL:", bold=True, font_size=11, space_before=10, space_after=6)
    p_rep = add_p(doc, space_after=16)
    add_run(p_rep, "Họ và tên: ________________________        Chữ ký: ________________________        Ngày: ____________", font_size=11)

    add_p(doc, "Giảng viên Hướng dẫn Đồ án Capstone 1:", bold=True, font_size=11, space_before=6, space_after=6)
    p_men = add_p(doc, space_after=16)
    add_run(p_men, "Họ và tên: KS. Hà Mạnh Toàn               Chữ ký: ________________________        Ngày: ____________", font_size=11)

    doc.add_page_break()

    # =========================================================================
    # TRANG 2: THÔNG TIN DỰ ÁN & PHÊ DUYỆT
    # =========================================================================
    add_p(doc, "THÔNG TIN DỰ ÁN", bold=True, font_size=13, space_before=4, space_after=6)

    proj_table = doc.add_table(rows=12, cols=4)
    proj_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(proj_table, color="000000", sz="4")
    
    col_w = [1.8, 2.2, 1.2, 1.3]
    for row in proj_table.rows:
        for idx, w in enumerate(col_w):
            row.cells[idx].width = Inches(w)

    def fill_row(table, r_idx, label, val, is_colspan=True):
        cells = table.rows[r_idx].cells
        cells[0].text = ""
        p0 = cells[0].paragraphs[0]
        p0.paragraph_format.space_before = Pt(2)
        p0.paragraph_format.space_after = Pt(2)
        add_run(p0, label, bold=True, font_size=10.5)
        set_cell_bg(cells[0], "E6E6E6")
        set_cell_margins(cells[0], top=80, bottom=80, left=100, right=100)
        
        if is_colspan:
            cells[1].merge(cells[2]).merge(cells[3])
            cells[1].text = ""
            p1 = cells[1].paragraphs[0]
            p1.paragraph_format.space_before = Pt(2)
            p1.paragraph_format.space_after = Pt(2)
            add_run(p1, val, font_size=10.5)
            set_cell_bg(cells[1], "FFFFFF")
            set_cell_margins(cells[1], top=80, bottom=80, left=100, right=100)
        else:
            cells[1].text = ""
            p1 = cells[1].paragraphs[0]
            p1.paragraph_format.space_before = Pt(2)
            p1.paragraph_format.space_after = Pt(2)
            add_run(p1, val[0], font_size=10.5)
            set_cell_bg(cells[1], "FFFFFF")
            set_cell_margins(cells[1], top=80, bottom=80, left=100, right=100)

            cells[2].text = ""
            p2 = cells[2].paragraphs[0]
            p2.paragraph_format.space_before = Pt(2)
            p2.paragraph_format.space_after = Pt(2)
            add_run(p2, val[1], bold=True, font_size=10.5)
            set_cell_bg(cells[2], "E6E6E6")
            set_cell_margins(cells[2], top=80, bottom=80, left=100, right=100)

            cells[3].text = ""
            p3 = cells[3].paragraphs[0]
            p3.paragraph_format.space_before = Pt(2)
            p3.paragraph_format.space_after = Pt(2)
            add_run(p3, val[2], font_size=10.5)
            set_cell_bg(cells[3], "FFFFFF")
            set_cell_margins(cells[3], top=80, bottom=80, left=100, right=100)

    fill_row(proj_table, 0, "Tên viết tắt dự án", "SFDS")
    fill_row(proj_table, 1, "Tên đầy đủ dự án", "Hệ Thống Cảnh Báo và Phát Hiện Lừa Đảo Trực Tuyến Đa Phương Thức Có Giải Thích")
    fill_row(proj_table, 2, "Thời gian thực hiện", ("23/08/2026", "Ngày kết thúc", "22/12/2026"), is_colspan=False)
    fill_row(proj_table, 3, "Đơn vị chủ quản", "Viện Đào tạo & Nghiên cứu Quốc tế, Đại học Duy Tân")
    fill_row(proj_table, 4, "Giảng viên hướng dẫn", "KS. Hà Mạnh Toàn")
    fill_row(proj_table, 5, "Nhóm sinh viên", "C1SE.06 - Ngành Kỹ thuật Phần mềm CMU")
    fill_row(proj_table, 6, "Liên hệ người hướng dẫn", ("lhttuy@gmail.com", "Điện thoại", "0905 123 456"), is_colspan=False)
    fill_row(proj_table, 7, "Cơ quan tài trợ", "Viện Đào tạo Quốc tế (IS) - Đại học Duy Tân")
    fill_row(proj_table, 8, "Tên tài liệu", "THIẾT KẾ CƠ SỞ DỮ LIỆU (DATABASE DESIGN DOCUMENT)")

    m_hdr_cells = proj_table.rows[9].cells
    m_labels = ["STT / Mã SV", "Họ và tên thành viên", "Email cá nhân", "Số điện thoại"]
    for idx, ml in enumerate(m_labels):
        m_hdr_cells[idx].text = ""
        p = m_hdr_cells[idx].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(p, ml, bold=True, font_size=10)
        set_cell_bg(m_hdr_cells[idx], "E6E6E6")

    members_data = [
        ("29219020823", "Phạm Tấn Hào (Trưởng nhóm / Scrum Master)", "phamtanhao1909@gmail.com", "0961651933"),
        ("29209200048", "Đào Thị Mỹ Nhung (QA Lead / UI-UX Lead)", "mynhung150905@gmail.com", "0376415338"),
        ("29219423638", "Trần Hoàng Nhật Nam (Frontend Dev / Viết tài liệu)", "trannamnhathoang@gmail.com", "0795798736"),
        ("29211151140", "Nguyễn Phan Đức Tuấn (AI Lead / Full-stack Dev)", "ductuan02072005@gmail.com", "0932442770")
    ]

    for idx, (m_no, m_name, m_email, m_tel) in enumerate(members_data[:2]):
        cur_cells = proj_table.rows[10 + idx].cells
        for c_idx, val in enumerate([m_no, m_name, m_email, m_tel]):
            cur_cells[c_idx].text = ""
            p = cur_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 3] else WD_ALIGN_PARAGRAPH.LEFT
            add_run(p, val, font_size=10)
            set_cell_bg(cur_cells[c_idx], "FFFFFF")

    for m_no, m_name, m_email, m_tel in members_data[2:]:
        new_row = proj_table.add_row()
        for idx, w in enumerate(col_w):
            new_row.cells[idx].width = Inches(w)
        for c_idx, val in enumerate([m_no, m_name, m_email, m_tel]):
            new_row.cells[c_idx].text = ""
            p = new_row.cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 3] else WD_ALIGN_PARAGRAPH.LEFT
            add_run(p, val, font_size=10)
            set_cell_bg(new_row.cells[c_idx], "FFFFFF")

    add_p(doc, "", space_before=0, space_after=6)

    add_p(doc, "PHÊ DUYỆT TÀI LIỆU", bold=True, font_size=12, space_before=6, space_after=4)
    add_p(doc, "Tài liệu này yêu cầu các bên liên quan ký xác nhận và phê duyệt:", italic=True, font_size=10.5, space_after=4)
    approvals_data = [
        ["Phạm Tấn Hào\nMã SV: 29219020823\nTrưởng nhóm / Scrum Master", "Chữ ký: _______________", "Ngày: 04/11/2026"],
        ["Đào Thị Mỹ Nhung\nMã SV: 29209200048\nQA Lead / UI-UX Lead", "Chữ ký: _______________", "Ngày: 04/11/2026"],
        ["Trần Hoàng Nhật Nam\nMã SV: 29219423638\nFrontend Developer", "Chữ ký: _______________", "Ngày: 04/11/2026"],
        ["Nguyễn Phan Đức Tuấn\nMã SV: 29211151140\nAI Lead", "Chữ ký: _______________", "Ngày: 04/11/2026"],
        ["KS. Hà Mạnh Toàn\nGiảng viên hướng dẫn\nĐại học Duy Tân", "Chữ ký: _______________", "Ngày: 04/11/2026"]
    ]
    create_styled_table(doc, ["Bên liên quan / Vai trò", "Chữ ký xác nhận", "Ngày ký"], approvals_data, col_widths=[3.2, 2.0, 1.3])

    add_p(doc, "LỊCH SỬ CHỈNH SỬA TÀI LIỆU", bold=True, font_size=12, space_before=6, space_after=4)
    rev_data = [
        ["1.0", "04/11/2026", "Tài liệu Thiết kế Cơ sở Dữ liệu chính thức cho Đồ án SFDS", "Phạm Tấn Hào", "KS. Hà Mạnh Toàn"],
        ["1.1", "05/11/2026", "Bản dịch tiếng Việt chuẩn học thuật đồng bộ mô hình ERD dạng Danh sách", "Phạm Tấn Hào", "KS. Hà Mạnh Toàn"]
    ]
    create_styled_table(doc, ["Phiên bản", "Ngày", "Mô tả nội dung thay đổi", "Tác giả", "Phê duyệt"], rev_data, col_widths=[0.8, 1.2, 2.7, 1.0, 1.0])

    doc.add_page_break()

    # =========================================================================
    # TRANG 3: MỤC LỤC
    # =========================================================================
    add_p(doc, "MỤC LỤC", bold=True, font_size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)
    toc_items = [
        ("1. Giới thiệu", "4"),
        ("   1.1 Mục đích tài liệu", "4"),
        ("   1.2 Phạm vi lưu trữ dữ liệu", "4"),
        ("   1.3 Tổng quan Hệ quản trị CSDL Quan hệ (MySQL & SQLite)", "4"),
        ("2. Sơ đồ cơ sở dữ liệu", "6"),
        ("   2.1 Tổng quan danh mục bảng", "6"),
        ("   2.2 Sơ đồ thực thể liên kết (ERD)", "7"),
        ("3. Thiết kế chi tiết các bảng CSDL cho Sprint", "9"),
        ("   3.1 Bảng users", "9"),
        ("   3.2 Bảng auth_identities", "10"),
        ("   3.3 Bảng scam_categories", "11"),
        ("   3.4 Bảng scan_history", "12"),
        ("   3.5 Bảng incidents", "14"),
        ("   3.6 Bảng scam_keywords", "15"),
        ("   3.7 Bảng training_dataset", "16"),
        ("   3.8 Bảng ai_models", "17"),
        ("   3.9 Bảng model_evaluations", "18"),
        ("   3.10 Bảng system_activity_logs", "19"),
        ("4. Yêu cầu phần cứng và phần mềm", "20"),
        ("   4.1 Thuộc tính công nghệ hệ thống", "20"),
        ("   4.2 Ước lượng dung lượng lưu trữ CSDL", "21"),
        ("   4.3 Chính sách bảo mật dữ liệu, sao lưu và phục hồi", "22")
    ]
    for title, page in toc_items:
        p_toc = add_p(doc, space_after=3, line_spacing=1.15)
        add_run(p_toc, title, bold=("." not in title[:3]), font_size=12)
        dots_count = max(5, 75 - len(title))
        add_run(p_toc, " " + "." * dots_count + " ", font_size=11, color=RGBColor(120, 120, 120))
        add_run(p_toc, page, bold=True, font_size=12)

    doc.add_page_break()

    # =========================================================================
    # MỤC 1: GIỚI THIỆU
    # =========================================================================
    add_p(doc, "1. Giới thiệu", bold=True, font_size=16, space_before=12, space_after=8)
    add_p(doc, (
        "Thiết kế Cơ sở Dữ liệu (Database Design) ánh xạ mô hình dữ liệu logic sang hệ quản trị cơ sở dữ liệu mục tiêu "
        "dưới sự xem xét chặt chẽ về các yêu cầu hiệu năng, tính toàn vẹn và độ sẵn sàng cao của hệ thống. "
        "Tài liệu chuyển đổi các cấu trúc dữ liệu khái niệm thành các cấu trúc vật lý cụ thể (bảng, cột, chỉ mục, khóa ngoại, "
        "và các ràng buộc toàn vẹn dữ liệu) trên hệ quản trị CSDL được lựa chọn."
    ), space_after=6)

    add_p(doc, "1.1 Mục đích tài liệu", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "Mục đích của tài liệu Thiết kế CSDL là đảm bảo mọi giao dịch truy vấn, ghi dữ liệu pháp chứng và lập chỉ mục "
        "đạt hoặc vượt các chỉ số hiệu năng yêu cầu. Tài liệu tính toán dung lượng dữ liệu, tần suất truy xuất đồng thời "
        "để xây dựng lược đồ cơ sở dữ liệu và môi trường vận hành tối ưu nhất."
    ), space_after=6)

    add_p(doc, "1.2 Phạm vi lưu trữ dữ liệu", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "Tài liệu Thiết kế Cơ sở Dữ liệu hướng đến các mục tiêu trọng tâm sau:\n"
        "• Mô tả thiết kế chuẩn hóa của cơ sở dữ liệu quan hệ, nơi lưu trữ có cấu trúc các thông tin nghiệp vụ phòng chống lừa đảo, "
        "danh mục rủi ro, lịch sử quét an toàn, tập dữ liệu huấn luyện AI và nhật ký kiểm toán hệ thống.\n"
        "• Đóng vai trò là tài liệu kỹ thuật nền tảng cho việc khởi tạo CSDL (schema migration), lập trình các lớp truy xuất dữ liệu "
        "(ORM / Repository pattern) và bảo đảm tính toàn vẹn dữ liệu giữa các dịch vụ của SFDS."
    ), space_after=6)

    add_p(doc, "1.3 Tổng quan Hệ quản trị CSDL Quan hệ (MySQL & SQLite)", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "MySQL là hệ quản trị cơ sở dữ liệu quan hệ (RDBMS) mã nguồn mở hàng đầu, lưu trữ dữ liệu trong các bảng có cấu trúc "
        "gồm các hàng và cột chặt chẽ. Hệ thống sử dụng ngôn ngữ truy vấn có cấu trúc (SQL) để thao tác và truy vấn dữ liệu. "
        "Khác với các CSDL NoSQL hướng tài liệu, MySQL đảm bảo tuân thủ nghiêm ngặt chuẩn giao dịch ACID (Atomicity, Consistency, "
        "Isolation, Durability), rất phù hợp với nghiệp vụ pháp chứng số, theo dõi kiểm toán và phân loại gian lận – nơi tính toàn vẹn "
        "tham chiếu và yêu cầu không thất thoát dữ liệu là bắt buộc.\n\n"
        "Trong nền tảng SFDS, dữ liệu được chuẩn hóa qua 10 bảng quan hệ. MySQL 8.0 được triển khai cho môi trường sản xuất tải cao, "
        "trong khi SQLite 3.42 phục vụ kiểm thử đơn vị và môi trường phát triển cục bộ qua SQLAlchemy ORM. Tính năng hỗ trợ kiểu dữ liệu JSON "
        "bản địa của MySQL 8.0 cho phép lưu trữ song song các trường quan hệ có cấu trúc cố định (mã người dùng, mốc thời gian, điểm rủi ro) "
        "cùng các gói dữ liệu JSON bán cấu trúc linh hoạt (tọa độ vùng ảnh khả nghi, dấu hiệu vi phạm ngữ cảnh, chuỗi suy luận CoT từng bước) "
        "mà vẫn giữ trọn các cam kết toàn vẹn quan hệ."
    ), space_after=6)

    doc.add_page_break()

    # =========================================================================
    # MỤC 2: SƠ ĐỒ CƠ SỞ DỮ LIỆU
    # =========================================================================
    add_p(doc, "2. Sơ đồ cơ sở dữ liệu", bold=True, font_size=16, space_before=12, space_after=8)
    add_p(doc, "2.1 Tổng quan danh mục bảng", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Bảng 1. Danh mục và mục đích các bảng trong CSDL SFDS", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)

    table_overview_data = [
        ["users", "Lưu trữ tài khoản quản trị viên và chuyên viên an ninh mạng, thông tin định danh và phân quyền ('user', 'admin')."],
        ["auth_identities", "Liên kết tài khoản người dùng nội bộ với các nhà cung cấp xác thực OAuth bên ngoài (Google, Zalo) phục vụ SSO."],
        ["scam_categories", "Danh mục chuẩn hóa phân loại các hình thức lừa đảo mạng (giả mạo ngân hàng, app tài chính, mạo danh công quyền)."],
        ["scan_history", "Lưu trữ giao dịch các phiên quét pháp chứng: loại đầu vào (URL, văn bản, ảnh chụp), điểm rủi ro và chuỗi giải thích AI."],
        ["incidents", "Quản lý các vụ việc lừa đảo được báo cáo, quy trình xử lý ('moi', 'dang_xu_ly', 'da_xu_ly') và chuyên viên tiếp nhận."],
        ["scam_keywords", "Từ điển các cụm từ lừa đảo tiếng Việt, mẫu regex nhận diện và trọng số điểm rủi ro đóng góp."],
        ["training_dataset", "Kho mẫu dữ liệu hình ảnh và văn bản đã ẩn danh hóa (PII) và được chuyên gia kiểm duyệt phục vụ tái huấn luyện AI."],
        ["ai_models", "Sổ đăng ký mô hình AI theo dõi các phiên bản giải thuật đã triển khai (PhoBERT, ResNet-18, CoT) và cờ kích hoạt thực tế."],
        ["model_evaluations", "Kết quả đo lường benchmark định kỳ của mô hình AI (Macro F1, Recall, Tỷ lệ báo nhầm, Điểm hữu ích của lời giải thích)."],
        ["system_activity_logs", "Nhật ký kiểm toán an ninh ghi vết mọi thao tác quản trị, thay đổi trọng số quy tắc và sự kiện hệ thống quan trọng."]
    ]
    create_styled_table(doc, ["Tên bảng / Tập thực thể", "Mô tả mục đích nghiệp vụ"], table_overview_data, col_widths=[2.0, 4.5])

    add_p(doc, "2.2 Sơ đồ thực thể liên kết (ERD)", bold=True, font_size=14, space_before=12, space_after=4)
    add_p(doc, (
        "Hình 1 minh họa Sơ đồ Thực thể Liên kết (Entity-Relationship Diagram - ERD) của cơ sở dữ liệu SFDS, thể hiện đầy đủ 10 bảng, "
        "khóa chính (PK), khóa ngoại (FK), các trường dữ liệu và bản số quan hệ (cardinality 1:1, 1:N)."
    ), space_after=6)

    erd_image_path = "TAILIEU_CAPSTONE_C1SE06_SFDS/5. DATABASE DESIGN/SFDS_Database_ERD.png"
    if not os.path.exists(erd_image_path):
        erd_image_path = "arch_diagrams/fig_sfds_erd.png"
    if os.path.exists(erd_image_path):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=4)
        p_img.add_run().add_picture(erd_image_path, width=Inches(6.4))
        add_p(doc, "Hình 1. Sơ đồ Thực thể Liên kết Cơ sở Dữ liệu SFDS (ERD)", bold=True, italic=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

    doc.add_page_break()

    # =========================================================================
    # MỤC 3: THIẾT KẾ CHI TIẾT CÁC BẢNG CSDL CHO SPRINT (TỪ ĐIỂN DỮ LIỆU)
    # =========================================================================
    add_p(doc, "3. Thiết kế chi tiết các bảng CSDL cho Sprint", bold=True, font_size=16, space_before=12, space_after=8)
    col_w_dict = [0.5, 1.4, 1.3, 1.6, 1.7]
    dict_headers = ["STT", "Tên trường", "Kiểu dữ liệu", "Ràng buộc", "Mô tả nghiệp vụ"]

    # 3.1 users
    add_p(doc, "3.1 Bảng users", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Bảng 2. Bảng users", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    users_dict = [
        ["1", "id", "INT", "Khóa chính, Tự tăng", "Định danh duy nhất của tài khoản người dùng."],
        ["2", "email", "VARCHAR(255)", "Bắt buộc, Duy nhất", "Địa chỉ email đăng nhập của tài khoản."],
        ["3", "password_hash", "VARCHAR(255)", "Bắt buộc", "Chuỗi mật khẩu băm bảo mật bằng thuật toán Bcrypt."],
        ["4", "full_name", "VARCHAR(255)", "Tùy chọn", "Họ và tên đầy đủ của người dùng."],
        ["5", "role", "ENUM('user','admin')", "Mặc định: 'user'", "Vai trò người dùng quản lý quyền truy cập chức năng."],
        ["6", "is_active", "BOOLEAN", "Mặc định: true", "Cờ trạng thái cho biết tài khoản có đang hoạt động hay không."],
        ["7", "created_at", "TIMESTAMP", "Mặc định: CURRENT_TIMESTAMP", "Thời điểm tài khoản được khởi tạo."],
        ["8", "updated_at", "TIMESTAMP", "Mặc định: CURRENT_TIMESTAMP", "Thời điểm cập nhật thông tin tài khoản gần nhất."]
    ]
    create_styled_table(doc, dict_headers, users_dict, col_widths=col_w_dict)

    # 3.2 auth_identities
    add_p(doc, "3.2 Bảng auth_identities", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Bảng 3. Bảng auth_identities", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    auth_dict = [
        ["1", "id", "INT", "Khóa chính, Tự tăng", "Định danh duy nhất cho bản ghi liên kết xác thực ngoài."],
        ["2", "user_id", "INT", "Bắt buộc, Khóa ngoại", "Tham chiếu users(id) ON DELETE CASCADE."],
        ["3", "provider", "VARCHAR(50)", "Bắt buộc", "Tên nhà cung cấp OAuth (ví dụ: 'google', 'zalo')."],
        ["4", "provider_subject", "VARCHAR(255)", "Bắt buộc", "Mã định danh duy nhất do nhà cung cấp OAuth cấp."],
        ["5", "created_at", "TIMESTAMP", "Mặc định: CURRENT_TIMESTAMP", "Thời điểm liên kết tài khoản OAuth."]
    ]
    create_styled_table(doc, dict_headers, auth_dict, col_widths=col_w_dict)

    # 3.3 scam_categories
    add_p(doc, "3.3 Bảng scam_categories", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Bảng 4. Bảng scam_categories", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    cat_dict = [
        ["1", "id", "INT", "Khóa chính, Tự tăng", "Định danh duy nhất của danh mục lừa đảo."],
        ["2", "code", "VARCHAR(50)", "Bắt buộc, Duy nhất", "Mã rút gọn danh mục (ví dụ: 'phishing', 'fake_invoice')."],
        ["3", "display_name", "VARCHAR(150)", "Bắt buộc", "Tên hiển thị tiếng Việt của loại hình lừa đảo."],
        ["4", "description", "TEXT", "Tùy chọn", "Mô tả chi tiết đặc điểm và thủ đoạn lừa đảo."]
    ]
    create_styled_table(doc, dict_headers, cat_dict, col_widths=col_w_dict)

    # 3.4 scan_history
    add_p(doc, "3.4 Bảng scan_history", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Bảng 5. Bảng scan_history", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    scan_dict = [
        ["1", "id", "INT", "Khóa chính, Tự tăng", "Định danh duy nhất cho giao dịch quét an toàn."],
        ["2", "user_id", "INT", "Bắt buộc, Khóa ngoại", "Tham chiếu users(id) ON DELETE CASCADE."],
        ["3", "image_url", "VARCHAR(1024)", "Tùy chọn", "Đường dẫn lưu trữ ảnh chụp màn hình khả nghi."],
        ["4", "original_filename", "VARCHAR(512)", "Tùy chọn", "Tên tệp gốc được người dùng tải lên."],
        ["5", "extracted_text", "LONGTEXT", "Tùy chọn", "Toàn bộ nội dung văn bản tiếng Việt trích xuất từ Tesseract OCR."],
        ["6", "scam_category_id", "INT", "Tùy chọn, Khóa ngoại", "Tham chiếu scam_categories(id) ON DELETE SET NULL."],
        ["7", "risk_score", "INT", "Bắt buộc, Dải: 0-100", "Điểm rủi ro tổng hợp chuẩn hóa từ mô hình AI."],
        ["8", "risk_level", "ENUM('an_toan','nghi_ngo','nguy_hiem')", "Bắt buộc", "Cấp độ phân loại rủi ro chính thức."],
        ["9", "explanation", "TEXT", "Tùy chọn", "Nội dung giải thích lý do đánh giá rủi ro dạng văn phong tự nhiên."],
        ["10", "highlighted_regions", "LONGTEXT / JSON", "Tùy chọn", "Tọa độ vùng nghi vấn và các từ khóa vi phạm trong bằng chứng."],
        ["11", "suggested_action", "TEXT", "Tùy chọn", "Các khuyến nghị hành động khẩn cấp cho người dùng."],
        ["12", "created_at", "TIMESTAMP", "Mặc định: CURRENT_TIMESTAMP", "Thời điểm thực hiện phiên quét an toàn."]
    ]
    create_styled_table(doc, dict_headers, scan_dict, col_widths=col_w_dict)

    # 3.5 incidents
    add_p(doc, "3.5 Bảng incidents", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Bảng 6. Bảng incidents", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    incidents_dict = [
        ["1", "id", "INT", "Khóa chính, Tự tăng", "Định danh duy nhất cho hồ sơ sự cố lừa đảo."],
        ["2", "sme_user_id", "INT", "Bắt buộc, Khóa ngoại", "Tham chiếu users(id) ON DELETE CASCADE."],
        ["3", "scan_history_id", "INT", "Bắt buộc, Khóa ngoại", "Tham chiếu scan_history(id) ON DELETE CASCADE."],
        ["4", "status", "ENUM('moi','dang_xu_ly','da_xu_ly','bo_qua')", "Mặc định: 'moi'", "Trạng thái của vụ việc trong quy trình xử lý."],
        ["5", "assigned_to", "VARCHAR(255)", "Tùy chọn", "Họ tên chuyên viên pháp chứng được phân công thụ lý."],
        ["6", "notes", "TEXT", "Tùy chọn", "Ghi chú quá trình điều tra và kết luận xử lý."],
        ["7", "created_at", "TIMESTAMP", "Mặc định: CURRENT_TIMESTAMP", "Thời điểm tạo hồ sơ sự cố."],
        ["8", "updated_at", "TIMESTAMP", "Mặc định: CURRENT_TIMESTAMP", "Thời điểm cập nhật trạng thái sự cố gần nhất."]
    ]
    create_styled_table(doc, dict_headers, incidents_dict, col_widths=col_w_dict)

    # 3.6 scam_keywords
    add_p(doc, "3.6 Bảng scam_keywords", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Bảng 7. Bảng scam_keywords", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    kw_dict = [
        ["1", "id", "INT", "Khóa chính, Tự tăng", "Định danh duy nhất của quy tắc từ khóa."],
        ["2", "keyword", "VARCHAR(255)", "Bắt buộc", "Từ khóa lừa đảo tiếng Việt hoặc biểu thức chính quy (Regex)."],
        ["3", "category", "VARCHAR(100)", "Bắt buộc", "Loại hình lừa đảo gắn liền với từ khóa."],
        ["4", "weight", "INT", "Mặc định: 10", "Trọng số đóng góp vào điểm rủi ro (5 đến 25 điểm)."],
        ["5", "created_at", "TIMESTAMP", "Mặc định: CURRENT_TIMESTAMP", "Thời điểm đăng ký từ khóa vào hệ thống."]
    ]
    create_styled_table(doc, dict_headers, kw_dict, col_widths=col_w_dict)

    # 3.7 training_dataset
    add_p(doc, "3.7 Bảng training_dataset", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Bảng 8. Bảng training_dataset", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    train_dict = [
        ["1", "id", "INT", "Khóa chính, Tự tăng", "Định danh duy nhất của mẫu dữ liệu huấn luyện."],
        ["2", "image_url", "VARCHAR(1024)", "Bắt buộc", "Đường dẫn lưu trữ tệp hình ảnh/văn bản huấn luyện."],
        ["3", "scam_category_id", "INT", "Tùy chọn, Khóa ngoại", "Tham chiếu scam_categories(id) ON DELETE SET NULL."],
        ["4", "is_anonymized", "BOOLEAN", "Mặc định: false", "Xác nhận mẫu dữ liệu đã được làm mờ thông tin cá nhân (PII)."],
        ["5", "is_verified", "BOOLEAN", "Mặc định: false", "Xác nhận nhãn dữ liệu chuẩn đã được chuyên gia kiểm duyệt."],
        ["6", "uploaded_by", "INT", "Bắt buộc, Khóa ngoại", "Tham chiếu users(id) ON DELETE CASCADE."],
        ["7", "created_at", "TIMESTAMP", "Mặc định: CURRENT_TIMESTAMP", "Thời điểm tải mẫu dữ liệu lên hệ thống."]
    ]
    create_styled_table(doc, dict_headers, train_dict, col_widths=col_w_dict)

    # 3.8 ai_models
    add_p(doc, "3.8 Bảng ai_models", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Bảng 9. Bảng ai_models", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    ai_dict = [
        ["1", "id", "INT", "Khóa chính, Tự tăng", "Định danh duy nhất của mô hình AI."],
        ["2", "version_name", "VARCHAR(100)", "Bắt buộc, Duy nhất", "Tên phiên bản mô hình (ví dụ: 'PhishVN-v1.2', 'ResNet18-v2.0')."],
        ["3", "description", "TEXT", "Tùy chọn", "Mô tả kiến trúc mô hình, siêu tham số và tập dữ liệu huấn luyện."],
        ["4", "is_active", "BOOLEAN", "Mặc định: false", "Cờ cho biết mô hình có đang trực tiếp phục vụ người dùng hay không."],
        ["5", "created_at", "TIMESTAMP", "Mặc định: CURRENT_TIMESTAMP", "Thời điểm đăng ký checkpoint mô hình vào hệ thống."]
    ]
    create_styled_table(doc, dict_headers, ai_dict, col_widths=col_w_dict)

    # 3.9 model_evaluations
    add_p(doc, "3.9 Bảng model_evaluations", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Bảng 10. Bảng model_evaluations", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    eval_dict = [
        ["1", "id", "INT", "Khóa chính, Tự tăng", "Định danh duy nhất cho kết quả đánh giá benchmark."],
        ["2", "ai_model_id", "INT", "Bắt buộc, Khóa ngoại", "Tham chiếu ai_models(id) ON DELETE CASCADE."],
        ["3", "macro_f1", "DECIMAL(5,4)", "Tùy chọn", "Điểm số Macro F1 trên tập kiểm thử xác thực."],
        ["4", "recall", "DECIMAL(5,4)", "Tùy chọn", "Tỷ lệ phát hiện đúng các mẫu lừa đảo thực tế."],
        ["5", "false_alarm_rate", "DECIMAL(5,4)", "Tùy chọn", "Tỷ lệ cảnh báo nhầm đối với các mẫu giao dịch an toàn."],
        ["6", "explanation_usefulness", "DECIMAL(5,4)", "Tùy chọn", "Điểm số chuyên gia đánh giá mức độ rõ ràng của chuỗi giải thích CoT."],
        ["7", "evaluated_at", "TIMESTAMP", "Mặc định: CURRENT_TIMESTAMP", "Thời điểm thực hiện bài kiểm tra benchmark."]
    ]
    create_styled_table(doc, dict_headers, eval_dict, col_widths=col_w_dict)

    # 3.10 system_activity_logs
    add_p(doc, "3.10 Bảng system_activity_logs", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Bảng 11. Bảng system_activity_logs", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    log_dict = [
        ["1", "id", "INT", "Khóa chính, Tự tăng", "Định danh duy nhất của dòng nhật ký hoạt động."],
        ["2", "admin_id", "INT", "Tùy chọn, Khóa ngoại", "Tham chiếu users(id) ON DELETE SET NULL."],
        ["3", "action_type", "VARCHAR(100)", "Bắt buộc", "Loại hành động (ví dụ: 'CAP_NHAT_QUY_TAC', 'XU_LY_SU_CO')."],
        ["4", "description", "TEXT", "Tùy chọn", "Mô tả chi tiết thay đổi cấu hình hoặc sự kiện quản trị."],
        ["5", "created_at", "TIMESTAMP", "Mặc định: CURRENT_TIMESTAMP", "Thời điểm xảy ra thao tác quản trị."]
    ]
    create_styled_table(doc, dict_headers, log_dict, col_widths=col_w_dict)

    doc.add_page_break()

    # =========================================================================
    # MỤC 4: YÊU CẦU PHẦN CỨNG VÀ PHẦN MỀM
    # =========================================================================
    add_p(doc, "4. Yêu cầu phần cứng và phần mềm", bold=True, font_size=16, space_before=12, space_after=8)
    add_p(doc, (
        "Mục này cung cấp tổng quan về các yêu cầu phần cứng và phần mềm phục vụ vận hành cơ sở dữ liệu. "
        "Dưới đây là các thuộc tính công nghệ cấu thành nền tảng SFDS:"
    ), space_after=6)

    add_p(doc, "Bảng 12. Thuộc tính công nghệ nền tảng SFDS", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    tech_data = [
        ["Hệ quản trị CSDL", "MySQL 8.0 Community Server (Môi trường sản xuất, InnoDB Engine, mã hóa utf8mb4)\nSQLite 3.42 (Môi trường phát triển & kiểm thử cục bộ)\nSQLAlchemy 2.0 ORM + Alembic migration tool"],
        ["Công nghệ phần mềm", "Frontend: React 18, Vite 5, Tailwind CSS, Recharts\nBackend: Python 3.12, FastAPI, Uvicorn ASGI Server\nLõi AI: PyTorch, Scikit-Learn, OpenCV"],
        ["Yêu cầu phần cứng", "Máy chủ Backend/Cloud: 8 Cores CPU, 16 GB RAM, 256 GB NVMe SSD\nMáy trạm người dùng: Trình duyệt web hiện đại, tối thiểu 4 GB RAM"],
        ["Thư viện bổ trợ", "Framework: FastAPI, React 18, Tailwind CSS\nMô hình AI: PhishVN (HistGB), ResNet-18, Tesseract OCR 5.3 (vie+eng)"]
    ]
    create_styled_table(doc, ["Thuộc tính kỹ thuật", "Mô tả chi tiết"], tech_data, col_widths=[2.0, 4.5])

    # Luu tap tin ket qua
    output_path = r"D:\scam-detector\TAILIEU_CAPSTONE_C1SE06_SFDS\5. DATABASE DESIGN\C1SE.06_DatabaseDesign_SFDS_v1.1_VI.docx"
    doc.save(output_path)
    print("Successfully generated:", output_path)

if __name__ == "__main__":
    generate_document()

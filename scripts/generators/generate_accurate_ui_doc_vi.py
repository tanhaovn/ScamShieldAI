# -*- coding: utf-8 -*-
"""
Generate official Vietnamese Capstone User Interface Design Document (.docx)
Output: D:\scam-detector\TAILIEU_CAPSTONE_C1SE06_SFDS\6. USER INTERFACE DESIGN\C1SE.06_UIDesign_SFDS_v1.0_VI.docx
"""

import os
import shutil
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

            if c_idx in [0] or val in ["Nút bấm", "Biểu tượng", "Ô nhập liệu", "Chọn ngày", "Hộp thả xuống", "Button", "Icon", "Input Field", "Date Input", "Dropdown"]:
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

    # Configure Margins: 1 inch everywhere
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)

    # =========================================================================
    # TRANG 1: ẢNH BÌA CHUẨN ĐỒ ÁN CAPSTONE DUY TÂN
    # =========================================================================
    logo_path = "extracted_media/image_1.png"
    if os.path.exists(logo_path):
        p_logo = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
        p_logo.add_run().add_picture(logo_path, width=Inches(3.2))

    add_p(doc, "VIỆN ĐÀO TẠO & NGHIÊN CỨU QUỐC TẾ", bold=True, font_size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    add_p(doc, "ĐỒ ÁN TỐT NGHIỆP 1 / CAPSTONE PROJECT 1", bold=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p(doc, "CMU-SE 450 – C1SE.06", bold=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    add_p(doc, "TÀI LIỆU THIẾT KẾ GIAO DIỆN NGƯỜI DÙNG", bold=True, font_size=20, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    add_p(doc, "Phiên bản 1.0", bold=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p(doc, "Ngày: 05 tháng 11 năm 2026", italic=True, font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    add_p(doc, "SFDS", bold=True, font_size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p(doc, "Hệ Thống Cảnh Báo và Phát Hiện Lừa Đảo Trực Tuyến Đa Phương Thức Có Giải Thích", italic=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)

    add_p(doc, "Thực hiện bởi", bold=True, font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    add_p(doc, "Hào, Phạm Tấn\nNhung, Đào Thị Mỹ\nNam, Trần Hoàng Nhật\nTuấn, Nguyễn Phan Đức", font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14, line_spacing=1.2)

    add_p(doc, "Giảng viên hướng dẫn", bold=True, font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    add_p(doc, "KS. Hà Mạnh Toàn", font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)

    add_p(doc, "Đại diện Hội đồng Đánh giá Thiết kế Giao diện:", bold=True, font_size=11, space_before=10, space_after=6)
    p_rep = add_p(doc, space_after=16)
    add_run(p_rep, "Họ và tên: ________________________        Chữ ký: ________________________        Ngày: ____________", font_size=11)

    add_p(doc, "Giảng viên Hướng dẫn Đồ án Capstone 1:", bold=True, font_size=11, space_before=6, space_after=6)
    p_men = add_p(doc, space_after=16)
    add_run(p_men, "Họ và tên: KS. Hà Mạnh Toàn               Chữ ký: ________________________        Ngày: ____________", font_size=11)

    doc.add_page_break()

    # =========================================================================
    # TRANG 2: THÔNG TIN DỰ ÁN, PHÊ DUYỆT & LỊCH SỬ CHỈNH SỬA
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
    fill_row(proj_table, 8, "Tên tài liệu", "THIẾT KẾ GIAO DIỆN NGƯỜI DÙNG (USER INTERFACE DESIGN)")
    
    # Header cho danh sách thành viên nhóm
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
        ["KS. Hà Mạnh Toàn\nGiảng viên hướng dẫn\nĐại học Duy Tân", "Chữ ký: _______________", "Ngày: 05/11/2026"],
        ["Đào Thị Mỹ Nhung\nMã SV: 29209200048\nQA Lead / UI-UX Lead", "Chữ ký: _______________", "Ngày: 05/11/2026"],
        ["Phạm Tấn Hào\nMã SV: 29219020823\nTrưởng nhóm / Scrum Master", "Chữ ký: _______________", "Ngày: 05/11/2026"],
        ["Trần Hoàng Nhật Nam\nMã SV: 29219423638\nFrontend Developer", "Chữ ký: _______________", "Ngày: 05/11/2026"],
        ["Nguyễn Phan Đức Tuấn\nMã SV: 29211151140\nAI Lead", "Chữ ký: _______________", "Ngày: 05/11/2026"]
    ]
    create_styled_table(doc, ["Bên liên quan / Vai trò", "Chữ ký xác nhận", "Ngày ký"], approvals_data, col_widths=[3.2, 2.0, 1.3])

    add_p(doc, "LỊCH SỬ CHỈNH SỬA TÀI LIỆU", bold=True, font_size=12, space_before=6, space_after=4)
    rev_data = [
        ["1.0", "05/11/2026", "Phiên bản khởi tạo - Đặc tả đầy đủ thiết kế giao diện UI/UX", "Đào Thị Mỹ Nhung", "KS. Hà Mạnh Toàn"],
        ["1.1", "05/11/2026", "Đồng bộ chuẩn mã nguồn dự án thực tế (Loại bỏ luồng đăng ký công khai)", "Đào Thị Mỹ Nhung", "KS. Hà Mạnh Toàn"]
    ]
    create_styled_table(doc, ["Phiên bản", "Ngày", "Mô tả nội dung thay đổi", "Tác giả", "Phê duyệt"], rev_data, col_widths=[0.8, 1.2, 2.7, 1.0, 1.0])

    doc.add_page_break()

    # =========================================================================
    # TRANG 3: MỤC LỤC
    # =========================================================================
    add_p(doc, "MỤC LỤC", bold=True, font_size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)
    toc_items = [
        ("1. Giới thiệu", "4"),
        ("   1.1. Mục đích tài liệu", "4"),
        ("   1.2. Phạm vi thiết kế", "4"),
        ("2. Thiết kế chi tiết các màn hình giao diện", "5"),
        ("   2.1 Màn hình Tổng quan (Cổng thông tin & Cảnh báo lừa đảo)", "5"),
        ("   2.2 Màn hình Quét an toàn đa phương thức", "7"),
        ("   2.3 Màn hình Kết quả phân tích rủi ro & Chuỗi giải thích CoT", "9"),
        ("   2.4 Màn hình Lịch sử quét & Pháp chứng số", "12"),
        ("   2.5 Màn hình Hồ sơ người dùng & Không gian cá nhân", "14"),
        ("   2.6 Cổng bảo mật Quản trị viên (Admin Security Gate)", "16"),
        ("   2.7 Bảng điều khiển Quản trị & Quản trị mô hình AI", "18"),
        ("3. Hệ thống thiết kế & Quy chuẩn giao diện", "21"),
        ("   3.1 Phân cấp kiểu chữ & Bảng màu chủ đạo", "21"),
        ("   3.2 Khả năng tiếp cận & Thiết kế đáp ứng đa thiết bị", "22")
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
    
    add_p(doc, "1.1. Mục đích tài liệu", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "Tài liệu này đặc tả chi tiết thiết kế giao diện người dùng (UI) và trải nghiệm người dùng (UX) cho hệ thống "
        "\"SFDS – Hệ Thống Cảnh Báo và Phát Hiện Lừa Đảo Trực Tuyến Đa Phương Thức Có Giải Thích\". Tài liệu mô tả cách hệ thống hỗ trợ người dân Việt Nam, "
        "các doanh nghiệp vừa và nhỏ (SMEs), cùng đội ngũ chuyên gia phân tích an ninh mạng trong việc nhận diện và phòng ngừa các chiến dịch lừa đảo mạng tinh vi "
        "thông qua công nghệ AI giám định đa phương thức (hình ảnh, chụp màn hình, liên kết URL, tin nhắn SMS/Zalo/Telegram và tài liệu số).\n\n"
        "Tài liệu giúp đội ngũ lập trình Frontend, kiểm thử QA, và chuyên gia bảo mật nắm rõ cấu trúc phân cấp thành phần, bố cục thị giác, các trạng thái tương tác, "
        "quy tắc kiểm tra dữ liệu đầu vào (validation), cũng như các tiêu chuẩn tiếp cận nhằm xây dựng một ứng dụng an toàn không gian mạng nhất quán, hiện đại và lấy con người làm trung tâm."
    ), space_after=6)

    add_p(doc, "1.2. Phạm vi thiết kế", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "Trải nghiệm người dùng trong SFDS được định hướng tối ưu hóa tối đa, loại bỏ mọi rào cản cho người dân đại chúng trong khi kiểm soát nghiêm ngặt đối với quản trị viên:\n"
        "• Tiếp cận không rào cản (Không yêu cầu Đăng ký): Người dân khi gặp tình huống nghi vấn có thể ngay lập tức truy cập hệ thống, quét nội dung đa phương thức "
        "(URL, ảnh chụp giao dịch giả mạo, tin nhắn trúng thưởng, tài liệu PDF) và nhận kết quả giải thích rủi ro từ AI mà không cần phải đăng ký hay đăng nhập tài khoản. "
        "Thiết kế này giúp người dùng hành động nhanh trong thời khắc cấp bách khi đối mặt với thủ đoạn lừa đảo.\n"
        "• Lưu trữ nhật ký phía máy khách (Client-side Persistence): Lịch sử các lần quét và dữ liệu pháp chứng được lưu trữ an toàn ngay trên trình duyệt của người dùng "
        "thông qua localStorage (giới hạn tối đa 50 bản ghi gần nhất), vừa bảo vệ quyền riêng tư cá nhân vừa tối ưu tải cho máy chủ trung tâm.\n"
        "• Cổng bảo mật Quản trị viên (Admin Security Gate): Khu vực quản trị được bảo vệ nghiêm ngặt bằng cơ chế xác thực JWT, chỉ cấp quyền cho quản trị viên và chuyên viên phân tích "
        "để quản lý tập dữ liệu huấn luyện, chu kỳ sống của các mô hình AI, đánh giá chất lượng mô hình và theo dõi nhật ký kiểm toán hệ thống."
    ), space_after=6)

    # =========================================================================
    # MỤC 2: THIẾT KẾ CHI TIẾT CÁC MÀN HÌNH GIAO DIỆN
    # =========================================================================
    add_p(doc, "2. Thiết kế chi tiết các màn hình giao diện", bold=True, font_size=16, space_before=14, space_after=8)
    
    headers_ui = ["STT", "Tên thành phần", "Loại", "Mô tả chức năng", "Hành động / Kiểm tra hợp lệ"]
    col_w_ui = [0.5, 1.4, 0.9, 2.3, 1.4]

    # -------------------------------------------------------------
    # 2.1 Màn hình Tổng quan
    # -------------------------------------------------------------
    add_p(doc, "2.1 Màn hình Tổng quan (Cổng thông tin & Cảnh báo lừa đảo)", bold=True, font_size=14, space_before=10, space_after=4)
    add_p(doc, (
        "Màn hình Tổng quan đóng vai trò là cổng chào thông tin chính thống của SFDS. Màn hình cung cấp bức tranh toàn cảnh về tình hình an ninh mạng "
        "tại Việt Nam, hiển thị các chỉ số đo lường trực tiếp (tổng số lượt quét, tỷ lệ rủi ro cao được ngăn chặn, số chiến dịch đang hoành hành) "
        "và các thẻ cảnh báo trực quan về những thủ đoạn giả mạo thương hiệu ngân hàng, app đầu tư tài chính bất hợp pháp, hay mạo danh cơ quan công quyền."
    ), space_after=6)

    img_path = "ui_diagrams/fig1_ui_overview.png"
    if os.path.exists(img_path):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
        p_img.add_run().add_picture(img_path, width=Inches(6.2))
        add_p(doc, "Hình 2.1: Giao diện Màn hình Tổng quan & Cổng thông tin Cảnh báo lừa đảo", italic=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    t1_data = [
        ["1", "Thanh điều hướng chính", "Khung chứa", "Chứa logo SFDS, các liên kết Tổng quan, Quét an toàn, Lịch sử, Cá nhân và nút Quản trị.", "Chuyển trang mượt mà không tải lại (SPA Router)."],
        ["2", "Thẻ Cảnh báo khẩn cấp", "Thẻ cảnh báo", "Thông báo nổi bật về chiến dịch lừa đảo mạo danh ngân hàng hoặc cơ quan nhà nước mới xuất hiện.", "Nhấn vào mở chi tiết thủ đoạn và biện pháp phòng tránh."],
        ["3", "Chỉ số thống kê trực tiếp", "Thống kê KPI", "Hiển thị 3 chỉ số chính: Tổng lượt quét, Cảnh báo nguy cơ cao, và Chiến dịch lừa đảo đã ghi nhận.", "Cập nhật số liệu động thời gian thực từ API backend."],
        ["4", "Thẻ thủ đoạn lừa đảo", "Thẻ nội dung", "Danh sách thẻ tương tác phân loại các hình thức: Giả mạo mBanking, Sàn đầu tư tài chính, Mạo danh công an/viện kiểm sát.", "Hiển thị mức độ cảnh báo (Nguy cấp, Cao, Trung bình)."],
        ["5", "Nút Quét ngay lập tức", "Nút bấm", "Nút kêu gọi hành động (CTA) nổi bật trên banner chính.", "Điều hướng ngay tới màn hình Quét an toàn đa phương thức."]
    ]
    create_styled_table(doc, headers_ui, t1_data, col_widths=col_w_ui)

    # -------------------------------------------------------------
    # 2.2 Màn hình Quét đa phương thức
    # -------------------------------------------------------------
    add_p(doc, "2.2 Màn hình Quét an toàn đa phương thức", bold=True, font_size=14, space_before=14, space_after=4)
    add_p(doc, (
        "Màn hình Quét đa phương thức là trung tâm xử lý cốt lõi của SFDS dành cho mọi công dân. Người dùng có thể quét bất kỳ nội dung khả nghi nào "
        "thông qua 4 chế độ linh hoạt: tải ảnh chụp màn hình/kéo thả, chụp trực tiếp bằng camera, kiểm tra liên kết trang web (URL), dán nội dung tin nhắn văn bản, "
        "hoặc tải tập tin tài liệu PDF. Quá trình xử lý diễn ra ngay lập tức với thanh tiến trình trực quan theo thời gian thực."
    ), space_after=6)

    img_path = "ui_diagrams/fig2_ui_scan_input.png"
    if os.path.exists(img_path):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
        p_img.add_run().add_picture(img_path, width=Inches(6.2))
        add_p(doc, "Hình 2.2: Giao diện Khung quét an toàn đa phương thức", italic=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    t2_data = [
        ["1", "Bộ chọn chế độ quét", "Tab chuyển đổi", "Chuyển đổi giữa 4 chế độ: Tải ảnh/Chụp ảnh, Kiểm tra URL, Phân tích văn bản tin nhắn, và Quét tài liệu PDF.", "Chuyển đổi giao diện nhập liệu tương ứng ngay lập tức."],
        ["2", "Khu vực kéo thả tập tin", "Vùng tải lên", "Cho phép kéo thả hoặc duyệt ảnh chụp màn hình (PNG, JPG, WebP) dung lượng tối đa 15MB.", "Kiểm tra định dạng và kích thước tập tin trước khi tải lên."],
        ["3", "Ô nhập liên kết URL", "Ô nhập liệu", "Trường nhập địa chỉ web với tiền tố https:// bắt buộc.", "Kiểm tra tính hợp lệ của định dạng URL; tự động chuẩn hóa chuỗi."],
        ["4", "Ô nhập văn bản tin nhắn", "Khung văn bản", "Vùng dán nội dung tin nhắn lừa đảo từ SMS, Zalo, Messenger, Telegram (tối đa 5000 ký tự).", "Bộ đếm số ký tự trực tiếp; kiểm tra không được để trống."],
        ["5", "Nút Kích hoạt quét AI", "Nút bấm", "Nút gửi dữ liệu lên pipeline AI đa phương thức để tiến hành OCR, NLP và đối soát cơ sở dữ liệu tri thức.", "Vô hiệu hóa nút và hiển thị thanh tiến trình xử lý khi đang quét."]
    ]
    create_styled_table(doc, headers_ui, t2_data, col_widths=col_w_ui)

    # -------------------------------------------------------------
    # 2.3 Màn hình Kết quả phân tích rủi ro & Chuỗi giải thích CoT
    # -------------------------------------------------------------
    add_p(doc, "2.3 Màn hình Kết quả phân tích rủi ro & Chuỗi giải thích CoT", bold=True, font_size=14, space_before=14, space_after=4)
    add_p(doc, (
        "Màn hình Kết quả là điểm khác biệt công nghệ cốt lõi của SFDS so với các công cụ quét mã độc thông thường. Thay vì chỉ đưa ra một nhãn nhị phân vô cảm, "
        "hệ thống trình bày một đồng hồ đo điểm rủi ro trực quan (0–100%), phân rã điểm số chi tiết theo từng khía cạnh kỹ thuật, và chuỗi suy luận từng bước "
        "(Chain-of-Thought - CoT) giải thích cặn kẽ tại sao nội dung này là lừa đảo (phân tích giả mạo thương hiệu, ngôn từ thôi thúc tâm lý, dấu hiệu kỹ thuật ngầm). "
        "Ngoài ra, màn hình cung cấp danh sách hành động khẩn cấp cần thực hiện và cửa sổ đóng góp ý kiến (User Feedback modal) để người dùng phản hồi về độ chính xác."
    ), space_after=6)

    img_path = "ui_diagrams/fig3_ui_scan_result.png"
    if os.path.exists(img_path):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
        p_img.add_run().add_picture(img_path, width=Inches(6.2))
        add_p(doc, "Hình 2.3: Giao diện Kết quả phân tích rủi ro & Chuỗi giải thích CoT", italic=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    t3_data = [
        ["1", "Đồng hồ đo mức rủi ro", "Đồng hồ đo", "Hiển thị điểm số rủi ro tổng hợp từ 0 đến 100 kèm mã màu trực quan: Xanh lá (An toàn), Vàng (Nghi ngờ), Đỏ (Nguy hiểm cao).", "Tự động kích hoạt hiệu ứng cảnh báo khi điểm số >= 75%."],
        ["2", "Thanh phân rã điểm số con", "Thanh tiến trình", "Phân rã trọng số rủi ro: Giả mạo thị giác/Logo (35%), Phân tích ngôn từ thao túng (40%), Rủi ro kỹ thuật ngầm (25%).", "Tính toán động từ kết quả đầu ra của pipeline AI."],
        ["3", "Chuỗi suy luận giải thích CoT", "Khung giải thích", "Trình bày 4 bước lập luận logic: 1. Nhận diện thương hiệu; 2. Phát hiện bất thường ngữ cảnh; 3. Dấu hiệu thao túng tâm lý; 4. Kết luận phân loại rủi ro.", "Văn phong tiếng Việt rõ ràng, dễ hiểu cho người dùng phổ thông."],
        ["4", "Khuyến nghị hành động khẩn", "Danh sách hướng dẫn", "Cung cấp danh mục các bước cần làm ngay: Không click đường dẫn, khóa tạm thời tài khoản ngân hàng, báo cáo Cục An toàn thông tin.", "Kèm nút một chạm để sao chép nội dung cảnh báo nhanh."],
        ["5", "Nút Đóng góp ý kiến (Feedback)", "Nút bấm", "Mở cửa sổ tiếp nhận phản hồi của người dùng về kết quả thẩm định (Chính xác, Báo động nhầm, Cần cải thiện).", "Gửi phản hồi về hệ thống để đội ngũ AI xem xét huấn luyện lại."]
    ]
    create_styled_table(doc, headers_ui, t3_data, col_widths=col_w_ui)

    # -------------------------------------------------------------
    # 2.4 Màn hình Lịch sử quét & Pháp chứng số
    # -------------------------------------------------------------
    add_p(doc, "2.4 Màn hình Lịch sử quét & Pháp chứng số", bold=True, font_size=14, space_before=14, space_after=4)
    add_p(doc, (
        "Màn hình Lịch sử cho phép người dùng xem lại toàn bộ các phiên thẩm định đã thực hiện trên trình duyệt hiện tại. Dữ liệu được lưu trữ trực tiếp "
        "trong bộ nhớ localStorage (tối đa 50 bản ghi gần nhất). Người dùng có thể tìm kiếm nhanh theo từ khóa, lọc theo mức độ rủi ro (Tất cả, Nghi ngờ, Nguy cơ cao), "
        "mở lại kết quả giải thích chi tiết, hoặc xuất báo cáo pháp chứng dạng tệp CSV để gửi cho cơ quan công an khi cần tố giác tội phạm."
    ), space_after=6)

    img_path = "ui_diagrams/fig4_ui_history.png"
    if os.path.exists(img_path):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
        p_img.add_run().add_picture(img_path, width=Inches(6.2))
        add_p(doc, "Hình 2.4: Giao diện Lịch sử quét an toàn & Pháp chứng số", italic=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    t4_data = [
        ["1", "Ô tìm kiếm nhật ký", "Ô nhập liệu", "Lọc các bản ghi lịch sử theo từ khóa tên tập tin, địa chỉ URL hoặc nội dung trích xuất.", "Cập nhật danh sách kết quả ngay khi người dùng gõ phím."],
        ["2", "Bộ lọc mức độ rủi ro", "Nút lọc dạng Tab", "Lọc nhanh các bản ghi theo phân loại: Tất cả, An toàn, Đáng ngờ, Nguy cơ cao.", "Cập nhật hiển thị số lượng tương ứng trên từng thẻ trạng thái."],
        ["3", "Bảng danh sách lịch sử", "Bảng dữ liệu", "Bảng hiển thị các cột: Thời gian quét, Đối tượng quét, Điểm số rủi ro, Phân loại thủ đoạn, và Cột hành động.", "Hỗ trợ phân trang khi số lượng bản ghi vượt quá 10 dòng."],
        ["4", "Nút Xem lại chi tiết", "Nút biểu tượng", "Nạp lại đầy đủ kết quả phân tích AI và chuỗi suy luận CoT của bản ghi đã lưu.", "Mở lại màn hình Kết quả thẩm định với đầy đủ dữ liệu gốc."],
        ["5", "Nút Xuất dữ liệu CSV", "Nút bấm", "Xuất toàn bộ bảng lịch sử quét ra tập tin CSV có cấu trúc chuẩn.", "Tự động tải tệp SFDS_Scan_History.csv về máy tính người dùng."]
    ]
    create_styled_table(doc, headers_ui, t4_data, col_widths=col_w_ui)

    # -------------------------------------------------------------
    # 2.5 Màn hình Hồ sơ người dùng & Không gian cá nhân
    # -------------------------------------------------------------
    add_p(doc, "2.5 Màn hình Hồ sơ người dùng & Không gian cá nhân", bold=True, font_size=14, space_before=14, space_after=4)
    add_p(doc, (
        "Màn hình Hồ sơ cá nhân đóng vai trò là không gian riêng tư của người dùng trên thiết bị. Màn hình cung cấp khả năng cá nhân hóa tên hiển thị, "
        "thống kê tổng số phiên quét an toàn đã thực hiện, tỷ lệ phát hiện các mối đe dọa, và tùy chọn quyền riêng tư cho phép xóa sạch hoàn toàn "
        "bộ nhớ lịch sử trên trình duyệt chỉ với một nút bấm."
    ), space_after=6)

    img_path = "ui_diagrams/fig5_ui_profile.png"
    if os.path.exists(img_path):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
        p_img.add_run().add_picture(img_path, width=Inches(6.2))
        add_p(doc, "Hình 2.5: Giao diện Màn hình Hồ sơ người dùng & Không gian cá nhân", italic=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    t5_data = [
        ["1", "Ảnh đại diện & Tên hiển thị", "Khối thông tin", "Hiển thị ảnh đại diện người dùng cùng tên định danh trên thiết bị (mặc định: Anonymous Defender).", "Cho phép chỉnh sửa và lưu vào bộ nhớ cục bộ."],
        ["2", "Thẻ thống kê bảo vệ", "Thống kê KPI", "Tổng kết: Tổng số lượt quét an toàn, Số vụ lừa đảo đã phát hiện, và Điểm cảnh giác số cá nhân.", "Tính toán tự động từ tập dữ liệu lịch sử cục bộ."],
        ["3", "Cấu hình phân tích cá nhân", "Công tắc bật/tắt", "Bật/tắt tùy chọn: Tự động cảnh báo khi dán liên kết web, Lưu trữ lịch sử quét cục bộ.", "Lưu trực tiếp trạng thái cấu hình vào bộ nhớ trình duyệt."],
        ["4", "Nút Xóa sạch dữ liệu cục bộ", "Nút bấm nguy hiểm", "Xóa toàn bộ lịch sử quét, cấu hình cá nhân và giải phóng hoàn toàn bộ nhớ localStorage.", "Bắt buộc người dùng xác nhận qua hộp thoại cảnh báo trước khi thực hiện."],
        ["5", "Nút Xuất dữ liệu cá nhân", "Nút bấm", "Sao lưu toàn bộ thông tin cá nhân và nhật ký quét thành tệp sao lưu JSON.", "Tạo và tải về tập tin sao lưu cá nhân có mã hóa."]
    ]
    create_styled_table(doc, headers_ui, t5_data, col_widths=col_w_ui)

    # -------------------------------------------------------------
    # 2.6 Cổng bảo mật Quản trị viên
    # -------------------------------------------------------------
    add_p(doc, "2.6 Cổng bảo mật Quản trị viên (Admin Security Gate)", bold=True, font_size=14, space_before=14, space_after=4)
    add_p(doc, (
        "Cổng bảo mật Quản trị viên là điểm chốt chặn xác thực bắt buộc trước khi truy cập vào các công cụ nhạy cảm của hệ thống. "
        "Hệ thống không cung cấp chức năng đăng ký công khai cho người dùng thông thường nhằm ngăn ngừa rủi ro bị khai thác. "
        "Chỉ có các quản trị viên hệ thống và chuyên gia an ninh mạng đã được tạo tài khoản trước trong cơ sở dữ liệu mới có thể đăng nhập bằng thông tin định danh hợp lệ."
    ), space_after=6)

    img_path = "ui_diagrams/fig6_ui_admin_login.png"
    if os.path.exists(img_path):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
        p_img.add_run().add_picture(img_path, width=Inches(6.2))
        add_p(doc, "Hình 2.6: Giao diện Cổng bảo mật xác thực Quản trị viên", italic=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    t6_data = [
        ["1", "Biểu tượng khóa bảo mật", "Biểu tượng", "Biểu tượng chiếc khiên số cùng thông báo cổng an ninh quản trị dành riêng cho nhân sự được phân quyền.", "Hiển thị tĩnh, định danh trực quan cổng bảo mật."],
        ["2", "Ô nhập Email Quản trị", "Ô nhập liệu", "Trường nhập địa chỉ email của Quản trị viên hoặc Chuyên viên phân tích an ninh.", "Kiểm tra đúng định dạng email RFC 5322; không được để trống."],
        ["3", "Ô nhập Mật khẩu", "Ô mật khẩu", "Trường nhập mật khẩu có nút ẩn/hiển thị ký tự bảo mật.", "Mã hóa một chiều tại phía client trước khi gửi qua HTTPS; tối thiểu 8 ký tự."],
        ["4", "Nút Đăng nhập Quản trị", "Nút bấm", "Gửi yêu cầu xác thực đăng nhập đến điểm cuối bảo mật /api/auth/login.", "Hiển thị hiệu ứng chờ (loading spinner); cấp mã JWT Token an toàn khi thành công."],
        ["5", "Thông báo chính sách bảo mật", "Nhãn thông báo", "Cảnh báo truy cập trái phép bị nghiêm cấm theo quy định an toàn thông tin.", "Hiển thị cố định dưới khung đăng nhập."]
    ]
    create_styled_table(doc, headers_ui, t6_data, col_widths=col_w_ui)

    # -------------------------------------------------------------
    # 2.7 Bảng điều khiển Quản trị & Quản trị mô hình AI
    # -------------------------------------------------------------
    add_p(doc, "2.7 Bảng điều khiển Quản trị & Quản trị mô hình AI", bold=True, font_size=14, space_before=14, space_after=4)
    add_p(doc, (
        "Bảng điều khiển Quản trị là không gian làm việc chuyên sâu dành cho Quản trị viên hệ thống và Đội ngũ kỹ sư AI. "
        "Giao diện chia thành 4 khu vực quản trị trọng yếu: Quản lý tập dữ liệu huấn luyện (Training Dataset), Quản trị chu kỳ sống mô hình AI (Model Registry), "
        "Đánh giá hiệu năng và độ chính xác mô hình (Evaluation Benchmarks), và Giám sát nhật ký hoạt động hệ thống (System Activity Logs)."
    ), space_after=6)

    img_path = "ui_diagrams/fig7_ui_admin_console.png"
    if os.path.exists(img_path):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
        p_img.add_run().add_picture(img_path, width=Inches(6.2))
        add_p(doc, "Hình 2.7: Giao diện Bảng điều khiển Quản trị & Quản trị mô hình AI", italic=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    t7_data = [
        ["1", "Thanh điều hướng Quản trị", "Menu phụ", "Chuyển đổi giữa 4 phân hệ: Dữ liệu huấn luyện, Quản trị mô hình AI, Đánh giá Benchmark, và Nhật ký hệ thống.", "Tải dữ liệu động qua API tương ứng mà không tải lại trang."],
        ["2", "Thống kê tổng quan quản trị", "Thẻ chỉ số", "Thống kê: Tổng mẫu dữ liệu đã gán nhãn, Mô hình AI đang chạy thực tế, Điểm Macro F1 trung bình, Số nhật ký hoạt động.", "Đồng bộ hóa dữ liệu trực tiếp với cơ sở dữ liệu."],
        ["3", "Bảng Quản lý Mô hình AI", "Bảng dữ liệu", "Danh sách các phiên bản mô hình AI (PhoBERT, CLIP, Gemini, OCR-Ensemble) cùng trạng thái hoạt động (Kích hoạt / Dự phòng).", "Cho phép chuyển đổi mô hình chính (Active) chỉ với 1 click."],
        ["4", "Biểu đồ đánh giá Benchmark", "Biểu đồ đo lường", "Trực quan hóa các chỉ số kỹ thuật của mô hình: Macro F1, Recall, Độ hữu ích của lời giải thích (Explanation Usefulness), Tỷ lệ báo động nhầm (False Alarm Rate).", "Vẽ biểu đồ động theo các lần kiểm thử benchmark."],
        ["5", "Bảng kiểm toán hoạt động (Audit Log)", "Bảng kiểm toán", "Theo dõi chi tiết các thao tác nhạy cảm: Tải tập dữ liệu lên, Chuyển đổi mô hình, Thay đổi trọng số, Lỗi hệ thống.", "Hỗ trợ tìm kiếm, lọc theo ngày và xuất biên bản kiểm toán."]
    ]
    create_styled_table(doc, headers_ui, t7_data, col_widths=col_w_ui)

    # =========================================================================
    # MỤC 3: HỆ THỐNG THIẾT KẾ & QUY CHUẨN GIAO DIỆN
    # =========================================================================
    add_p(doc, "3. Hệ thống thiết kế & Quy chuẩn giao diện", bold=True, font_size=16, space_before=16, space_after=8)
    
    add_p(doc, "3.1 Phân cấp kiểu chữ & Bảng màu chủ đạo", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "Giao diện của SFDS tuân thủ nghiêm ngặt chuẩn mực hiện đại dành cho ứng dụng an ninh mạng chuyên nghiệp. Bảng màu được thiết kế để tạo sự tin cậy, "
        "tập trung và rõ ràng về các cấp độ cảnh báo rủi ro:"
    ), space_after=6)

    color_headers = ["Mã định danh", "Mã Hex", "Mẫu màu", "Mục đích sử dụng trong hệ thống"]
    color_data = [
        ["Màu chủ đạo (Primary)", "#0F172A", "Xanh đen Slate 900", "Nền thanh điều hướng, tiêu đề chính, các khối chứa cấu trúc giao diện."],
        ["Màu nhấn mạnh (Accent)", "#2563EB", "Xanh dương Royal Blue", "Nút bấm hành động chính (CTA), liên kết kích hoạt, trạng thái đang chọn."],
        ["Cảnh báo nguy cấp (Critical)", "#DC2626", "Đỏ Crimson Red", "Mức rủi ro lừa đảo cao (>= 75%), cảnh báo nguy hiểm khẩn, nút xóa dữ liệu."],
        ["Cảnh báo đáng ngờ (Warning)", "#D97706", "Vàng hổ phách Amber", "Mức rủi ro trung bình/nghi ngờ (40% - 74%), thẻ cảnh báo cần lưu ý."],
        ["Trạng thái an toàn (Success)", "#16A34A", "Xanh lục Emerald Green", "Nội dung an toàn (< 40%), thông báo thành công, chỉ số hoạt động bình thường."],
        ["Màu nền chính (Background)", "#F8FAFC", "Xám sáng Slate 50", "Màu nền toàn bộ ứng dụng, tạo sự dễ chịu cho mắt người dùng."],
        ["Màu đường viền (Border)", "#E2E8F0", "Xám nhạt Slate 200", "Đường viền các thẻ nội dung, phân chia hàng bảng dữ liệu, ô nhập liệu."]
    ]
    create_styled_table(doc, color_headers, color_data, col_widths=[1.5, 1.0, 1.5, 2.5])

    add_p(doc, "3.2 Khả năng tiếp cận & Thiết kế đáp ứng đa thiết bị", bold=True, font_size=14, space_before=12, space_after=4)
    add_p(doc, (
        "SFDS được tối ưu hóa giao diện dựa trên hai nguyên tắc căn bản nhằm phục vụ đại đa số người dân Việt Nam:\n"
        "• Khả năng tiếp cận cao (Accessibility - WCAG 2.1 AA): Đảm bảo tỷ lệ tương phản màu sắc văn bản tối thiểu 4.5:1 đối với chữ thông thường và 3:1 đối với chữ lớn. "
        "Tất cả các thành phần tương tác (nút bấm, ô nhập liệu) đều hỗ trợ thao tác hoàn toàn bằng bàn phím (Tab, Enter, Space) và có nhãn aria-label hỗ trợ phần mềm đọc màn hình "
        "dành cho người khiếm thị.\n"
        "• Thiết kế đáp ứng linh hoạt (Responsive Adaptation): Giao diện tự động tối ưu hiển thị mượt mà trên mọi kích thước màn hình từ điện thoại thông minh (375px+), "
        "máy tính bảng (768px+) cho đến máy tính để bàn độ phân giải cao (1920px+). Trên thiết bị di động, thanh điều hướng tự động chuyển thành thanh điều hướng dưới đáy (Bottom Navigation) "
        "giúp người dùng dễ dàng thao tác quét an toàn bằng một tay khi đang di chuyển."
    ), space_after=8)

    # Luu tap tin ket qua
    output_path = r"D:\scam-detector\TAILIEU_CAPSTONE_C1SE06_SFDS\6. USER INTERFACE DESIGN\C1SE.06_UIDesign_SFDS_v1.0_VI.docx"
    doc.save(output_path)
    print("Successfully generated:", output_path)

if __name__ == "__main__":
    generate_document()

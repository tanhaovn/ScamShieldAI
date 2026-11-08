# -*- coding: utf-8 -*-
"""
Generate accurate Capstone User Interface Design Document (.docx)
Reflecting the real SFDS features (No registration required, instant public scan,
admin gate, dataset management, AI models registry, history, and profile).
Output: D:\scam-detector\TAILIEU_CAPSTONE_C1SE06_SFDS\6. USER INTERFACE DESIGN\C1SE.06_UIDesign_SFDS_v1.0.docx
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

            if c_idx in [0] or val in ["Button", "Icon", "Input Field", "Date Input", "Dropdown"]:
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

    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)

    # =========================================================================
    # PAGE 1: EXACT STORELENS COVER PAGE
    # =========================================================================
    logo_path = "extracted_media/image_1.png"
    if os.path.exists(logo_path):
        p_logo = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
        p_logo.add_run().add_picture(logo_path, width=Inches(3.2))

    add_p(doc, "International School", bold=True, font_size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    add_p(doc, "Capstone Project 1", bold=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p(doc, "CMU-SE 450 – C1SE.06", bold=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    add_p(doc, "User Interface Design", bold=True, font_size=22, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    add_p(doc, "Version 1.0", bold=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p(doc, "Date: Nov 5th, 2026", italic=True, font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    add_p(doc, "SFDS", bold=True, font_size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p(doc, "Scam Fraud Detection System with Explanations", italic=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)

    add_p(doc, "Created by", bold=True, font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    add_p(doc, "Hao, Pham Tan\nNhung, Dao Thi My\nNam, Tran Hoang Nhat\nTuan, Nguyen Phan Duc", font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14, line_spacing=1.2)

    add_p(doc, "Approved by", bold=True, font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    add_p(doc, "Eng. Toan, Ha Manh", font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)

    add_p(doc, "User Interface Design Review Panel Representative:", bold=True, font_size=11, space_before=10, space_after=6)
    p_rep = add_p(doc, space_after=16)
    add_run(p_rep, "Name: ________________________        Signature: ________________________        Date: ____________", font_size=11)

    add_p(doc, "Capstone Project 1 - Mentor:", bold=True, font_size=11, space_before=6, space_after=6)
    p_men = add_p(doc, space_after=16)
    add_run(p_men, "Name: ________________________        Signature: ________________________        Date: ____________", font_size=11)

    doc.add_page_break()

    # =========================================================================
    # PAGE 2: PROJECT INFORMATION, APPROVALS, METADATA & REVISION HISTORY
    # =========================================================================
    add_p(doc, "PROJECT INFORMATION", bold=True, font_size=13, space_before=4, space_after=6)

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

    fill_row(proj_table, 0, "Project acronym", "SFDS")
    fill_row(proj_table, 1, "Project Title", "“SFDS” – Scam Fraud Detection System with Explanations")
    fill_row(proj_table, 2, "Start Date", ("02 Sep 2026", "End Date", "15 Dec 2026"), is_colspan=False)
    fill_row(proj_table, 3, "Lead Institution", "International School, Duy Tan University")
    fill_row(proj_table, 4, "Project Mentor", "Eng. Ha Manh Toan (Email: lhttuy@gmail.com)")
    fill_row(proj_table, 5, "Product Owner / Leader", "Hao, Pham Tan   Email: phamtanhao1909@gmail.com   Tel: 0961 651 933   ID: 29219020823")
    fill_row(proj_table, 6, "Scrum master / UI Lead", "Nhung, Dao Thi My   Email: mynhung150905@gmail.com   Tel: 0376 415 338   ID: 29209200048")
    fill_row(proj_table, 7, "Partner Organization", "Duy Tan University")

    row8_cells = proj_table.rows[8].cells
    row8_cells[0].merge(row8_cells[1]).merge(row8_cells[2]).merge(row8_cells[3])
    row8_cells[0].text = ""
    p8 = row8_cells[0].paragraphs[0]
    p8.alignment = WD_ALIGN_PARAGRAPH.LEFT
    add_run(p8, "Team members:", bold=True, font_size=10.5)
    set_cell_bg(row8_cells[0], "E6E6E6")

    members_data = [
        ("1", "Hao, Pham Tan", "phamtanhao1909@gmail.com", "0961651933"),
        ("2", "Nhung, Dao Thi My", "mynhung150905@gmail.com", "0376415338"),
        ("3", "Nam, Tran Hoang Nhat", "trannamnhathoang@gmail.com", "0795798736"),
        ("4", "Tuan, Nguyen Phan Duc", "ductuan02072005@gmail.com", "0932442770")
    ]
    row9_cells = proj_table.rows[9].cells
    for i, t in enumerate(["No.", "Name", "Email", "Tel"]):
        row9_cells[i].text = ""
        p = row9_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(p, t, bold=True, font_size=10)
        set_cell_bg(row9_cells[i], "E6E6E6")

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

    add_p(doc, "DOCUMENT APPROVALS", bold=True, font_size=12, space_before=6, space_after=4)
    add_p(doc, "The following signatures are required for approval of this document.", italic=True, font_size=10.5, space_after=4)
    approvals_data = [
        ["Eng. Ha Manh Toan\nProject Mentor\nDuy Tan University", "Signature: _______________", "Date: 05/11/2026"],
        ["Nhung, Dao Thi My\nStudent ID: 29209200048\nQA Lead / UI-UX Lead", "Signature: _______________", "Date: 05/11/2026"],
        ["Hao, Pham Tan\nStudent ID: 29219020823\nProject Leader / Scrum Master", "Signature: _______________", "Date: 05/11/2026"],
        ["Nam, Tran Hoang Nhat\nStudent ID: 29219423638\nFrontend Developer", "Signature: _______________", "Date: 05/11/2026"],
        ["Tuan, Nguyen Phan Duc\nStudent ID: 29211151140\nAI Lead", "Signature: _______________", "Date: 05/11/2026"]
    ]
    create_styled_table(doc, ["Stakeholder", "Signature", "Date"], approvals_data, col_widths=[3.2, 2.0, 1.3])

    add_p(doc, "REVISION HISTORY", bold=True, font_size=12, space_before=6, space_after=4)
    rev_data = [
        ["1.0", "05/11/2026", "Initial Release - Full UI/UX Design Specification", "Nhung, Dao Thi My", "Eng. Ha Manh Toan"],
        ["2.0", "05/11/2026", "Official Capstone User Interface Design Document (Synchronized with Codebase)", "Nhung, Dao Thi My", "Eng. Ha Manh Toan"]
    ]
    create_styled_table(doc, ["Version", "Date", "Comments", "Author", "Approval"], rev_data, col_widths=[0.8, 1.2, 2.7, 1.0, 1.0])

    doc.add_page_break()

    # =========================================================================
    # PAGE 3: TABLE OF CONTENTS
    # =========================================================================
    add_p(doc, "TABLE OF CONTENTS", bold=True, font_size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)
    toc_items = [
        ("1. Introduction", "4"),
        ("   1.1. Purpose", "4"),
        ("   1.2. Scope", "4"),
        ("2. Interface Design", "5"),
        ("   2.1 Overview (Portal Landing & Threat Intelligence)", "5"),
        ("   2.2 Multimodal Scan Interface", "7"),
        ("   2.3 Explainable Risk Verdict & CoT Reasoning", "9"),
        ("   2.4 Scan History & Forensic Audit", "12"),
        ("   2.5 User Profile & Personal Space", "14"),
        ("   2.6 Admin Security Gate (Admin Authentication)", "16"),
        ("   2.7 Admin Control Center & Model Governance", "18"),
        ("3. Design System & Guidelines", "21"),
        ("   3.1 Typography & Color Hierarchy", "21"),
        ("   3.2 Accessibility & Responsive Adaptation", "22")
    ]
    for title, page in toc_items:
        p_toc = add_p(doc, space_after=3, line_spacing=1.15)
        add_run(p_toc, title, bold=("." not in title[:3]), font_size=12)
        dots_count = max(5, 75 - len(title))
        add_run(p_toc, " " + "." * dots_count + " ", font_size=11, color=RGBColor(120, 120, 120))
        add_run(p_toc, page, bold=True, font_size=12)

    doc.add_page_break()

    # =========================================================================
    # SECTION 1: INTRODUCTION
    # =========================================================================
    add_p(doc, "1. Introduction", bold=True, font_size=16, space_before=12, space_after=8)
    
    add_p(doc, "1.1. Purpose", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "This specification covers the following aspects:\n"
        "The documentation provides a detailed description of the user interface (UI) and user experience (UX) design for the "
        "“SFDS – Scam Fraud Detection System with Explanations” platform. It explains how the system supports Vietnamese citizens, "
        "enterprise security teams (SMEs), and administrative cyber analysts in identifying and mitigating sophisticated online scam campaigns "
        "through multimodal AI-driven video, image, text, and URL forensics.\n\n"
        "With this documentation, the frontend engineering, QA, and security development teams can clearly understand the component hierarchy, "
        "visual layouts, interaction states, input validation rules, and accessibility standards required to build a consistent, responsive, "
        "and human-centric cyber safety application."
    ), space_after=6)

    add_p(doc, "1.2. Scope", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "The SFDS user experience is purposely designed to be frictionless for public citizens while strictly controlled for system administrators:\n"
        "• Frictionless Public Access (No Registration Required): Regular citizens can immediately access the portal, perform scans across multiple "
        "modalities (URL, screenshots, messages, document scans), and view explainable AI verdicts without being required to create or register an account. "
        "This design eliminates onboarding friction, encouraging immediate threat verification during urgent suspicious interactions.\n"
        "• Client-Side Persistence: Historical scan logs and forensic audit trails for public users are persisted directly on the client device "
        "via browser localStorage (capped at 50 records), preserving privacy and eliminating unneeded database overhead.\n"
        "• Privileged Admin Security Gate: A dedicated Admin Gate enforces secure JWT authentication for authorized personnel, granting access "
        "to training dataset curation, AI model lifecycle management, performance evaluations, and system audit logs."
    ), space_after=6)

    doc.add_page_break()

    # =========================================================================
    # SECTION 2: INTERFACE DESIGN
    # =========================================================================
    add_p(doc, "2. Interface Design", bold=True, font_size=16, space_before=12, space_after=8)

    # -------------------------------------------------------------
    # 2.1 Overview (Portal Landing)
    # -------------------------------------------------------------
    add_p(doc, "2.1 Overview (Portal Landing & Threat Intelligence)", bold=True, font_size=14, space_before=8, space_after=4)
    
    img_over = "ui_diagrams/fig1_ui_overview.png"
    if os.path.exists(img_over):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=4)
        p_img.add_run().add_picture(img_over, width=Inches(6.2))
        add_p(doc, "Figure 1. UI Overview / Portal Landing Page", bold=True, italic=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    add_p(doc, "Table 1. Description UI Overview", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    over_fields = [
        ["1", "navBrandLogo", "Logo + Text", "Position: Top left; Text: 'SFDS - SCAM FRAUD DETECTOR'", "Brand logo navigating to homepage"],
        ["2", "topNavbarLinks", "Navigation", "Links: 'Tổng quan', 'Kiểm tra lừa đảo', 'Lịch sử', 'Cá nhân', 'Quản trị'", "Primary navigation bar across application modules"],
        ["3", "userStatusPill", "Status Badge", "Position: Top right; Text: 'Khách trải nghiệm' / 'Admin'", "Display current session state and privileges"],
        ["4", "heroBannerTitle", "Heading", "Font: Bold 14pt; Text: 'LÁ CHẮN AI BẢO VỆ NGƯỜI DÂN...'", "Headline communicating platform cyber safety mission"],
        ["5", "quickScanCTA", "Button", "Solid Blue; Pill shape; Text: 'BẮT ĐẦU QUÉT NGAY'", "One-click shortcut directing citizens into scan interface"],
        ["6", "threatCard_Police", "Card", "Red tag; Title: 'Mạo danh Công an'; Explanatory summary", "Warn citizens regarding fake arrest warrants & coercive threats"],
        ["7", "threatCard_Bank", "Card", "Orange tag; Title: 'Giả mạo Ngân hàng'; Explanatory summary", "Warn citizens against deceptive phishing URLs and OTP theft"],
        ["8", "threatCard_Bill", "Card", "Sky-blue tag; Title: 'Biên lai Fake'; Explanatory summary", "Educate users on fake bank transfer receipt tampering"],
        ["9", "threatCard_Job", "Card", "Purple tag; Title: 'Bẫy Đầu tư / Việc làm'; Explanatory summary", "Expose recruitment commission and ponzi scheme traps"],
        ["10", "statTotalScans", "KPI Metric", "Value: '12,450+'; Subtext: 'Lượt quét toàn hệ thống'", "Demonstrate public adoption and platform operational scale"],
        ["11", "statAccuracy", "KPI Metric", "Value: '98.4%'; Green color; Subtext: 'Độ chính xác'", "Build citizen confidence in AI multimodal consensus accuracy"],
        ["12", "statLatency", "KPI Metric", "Value: '< 2.1 giây'; Blue color; Subtext: 'Tốc độ xử lý'", "Demonstrate instant, sub-second inspection performance"]
    ]
    create_styled_table(doc, ["No.", "Field name", "Type", "Require", "Target"], over_fields, col_widths=[0.4, 1.4, 1.2, 1.8, 1.7])

    doc.add_page_break()

    # -------------------------------------------------------------
    # 2.2 Multimodal Scan Interface
    # -------------------------------------------------------------
    add_p(doc, "2.2 Multimodal Scan Interface", bold=True, font_size=14, space_before=8, space_after=4)

    img_scan = "ui_diagrams/fig2_ui_scan_input.png"
    if os.path.exists(img_scan):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=4)
        p_img.add_run().add_picture(img_scan, width=Inches(6.2))
        add_p(doc, "Figure 2. UI Multimodal Scan Viewport", bold=True, italic=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    add_p(doc, "Table 2. Description UI Multimodal Scan Interface", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    scan_fields = [
        ["1", "tabImage", "Tab Button", "Active blue; Icon: Camera; Label: 'Ảnh chụp màn hình'", "Select screenshot inspection mode (ResNet-18 + ELA forensics)"],
        ["2", "tabURL", "Tab Button", "Inactive state; Icon: Link; Label: 'Đường link (URL)'", "Select URL lexical inspection mode (PhishVN feature extractor)"],
        ["3", "tabMessage", "Tab Button", "Inactive state; Icon: Chat; Label: 'Đoạn chat / Tin nhắn'", "Select conversational text inspection mode (NLP Risk Lexicon)"],
        ["4", "tabPDF", "Tab Button", "Inactive state; Icon: File; Label: 'File tài liệu PDF'", "Select legal document scanning mode (Tesseract OCR Engine)"],
        ["5", "viewportContainer", "HUD Viewport", "Dark tech aesthetic (#0F172A); Laser grid border", "Visual canvas previewing evidence and bounding box annotations"],
        ["6", "hudStatusBadge", "Status Pill", "Glowing green indicator; Text: 'AI VISION ACTIVE'", "Inform citizen that AI visual pipeline is online and ready"],
        ["7", "dragDropZone", "Drop Target", "Dashed cyan outline; Interactive drag-and-drop listener", "Allow drag-and-drop or file picker upload (PNG, JPG up to 10MB)"],
        ["8", "browseFileButton", "Button", "Solid Blue; Text: 'Chọn file từ thiết bị'", "Trigger native OS file selection dialogue for uploading proof"],
        ["9", "urlInputAux", "Input Field", "Placeholder: 'http://vietcombank-xacminh.com'; Clear icon", "Allow entering matching URL accompanying the screenshot proof"],
        ["10", "messageInputAux", "Text Area", "Multi-line text; Max 2000 chars; Scrollbar auto", "Allow pasting message transcript received alongside the screenshot"],
        ["11", "executeScanButton", "Button", "Solid Red (#DC2626); Pulsing glow; Text: 'PHÂN TÍCH RỦI RO NGAY'", "Submit multimodal payload to FastAPI orchestrator for analysis"]
    ]
    create_styled_table(doc, ["No.", "Field name", "Type", "Require", "Target"], scan_fields, col_widths=[0.4, 1.4, 1.2, 1.8, 1.7])

    doc.add_page_break()

    # -------------------------------------------------------------
    # 2.3 Explainable Risk Verdict & CoT Reasoning
    # -------------------------------------------------------------
    add_p(doc, "2.3 Explainable Risk Verdict & CoT Reasoning", bold=True, font_size=14, space_before=8, space_after=4)

    img_res = "ui_diagrams/fig3_ui_scan_result.png"
    if os.path.exists(img_res):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=4)
        p_img.add_run().add_picture(img_res, width=Inches(6.2))
        add_p(doc, "Figure 3. UI Risk Analysis & Verdict Explanation", bold=True, italic=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    add_p(doc, "Table 3. Description UI Risk Analysis & Verdict", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    result_fields = [
        ["1", "riskGaugeCard", "Card Container", "Left panel; High-contrast border; White background", "Group comprehensive risk score and sub-modal metrics"],
        ["2", "gaugeVisualCircle", "Radial Gauge", "Circular gauge 0-100; Value: '88%'; Red stroke (#DC2626)", "Visually signal urgent threat severity to citizens instantaneously"],
        ["3", "verdictBadge", "Label Badge", "Caps bold; Background: Light Red; Text: 'NGUY HIỂM CAO'", "Categorical rating (An toàn <40%, Nghi ngờ 40-69%, Nguy hiểm >=70%)"],
        ["4", "scorePhishVN", "Metric Item", "Text: 'Tên miền: 92% (Giả mạo)'; Red indicator", "Display URL lexical fraud contribution from PhishVN model"],
        ["5", "scoreResNet", "Metric Item", "Text: 'Hình ảnh: 85% (Logo mạo danh)'; Orange indicator", "Display visual brand classification score from ResNet-18 CNN"],
        ["6", "scoreNLP", "Metric Item", "Text: 'Nội dung: 88% (Hối thúc, mã OTP)'; Red indicator", "Display linguistic threat score from Vietnamese scam lexicon"],
        ["7", "scoreELA", "Metric Item", "Text: 'Pháp y ảnh: Phát hiện can thiệp số'; Yellow indicator", "Display Error Level Analysis compression artifact flag"],
        ["8", "feedbackModalButton", "Button", "Outline button; Flag icon; Text: 'Báo cáo sai lệch / Phản hồi'", "Trigger community feedback modal to appeal false positive/negative"],
        ["9", "cotExplanationList", "List Group", "Numbered steps (1 to 4); Red highlighted headings", "Synthesize plain-language Chain-of-Thought (CoT) reasoning reasons"],
        ["10", "cotStep1_Domain", "List Item", "Text: 'Tên miền bất thường: vietcombank-xacminh.com...'", "Explain domain age and spoofing technique used"],
        ["11", "cotStep2_Visual", "List Item", "Text: 'Mạo danh thương hiệu: Logo ngân hàng Vietcombank...'", "Explain unauthorized brand logo usage and counterfeit UI layout"],
        ["12", "cotStep3_Urgency", "List Item", "Text: 'Ngữ cảnh thúc ép: Yêu cầu mã OTP khẩn cấp...'", "Explain psychological manipulation and urgency tactics detected"],
        ["13", "cotStep4_Forensics", "List Item", "Text: 'Dấu vết chỉnh sửa (ELA): Số tiền bị làm mờ...'", "Explain digital image tampering identified on the evidence"],
        ["14", "actionGuidanceBox", "Callout Box", "Light blue background (#EFF6FF); Blue border; Lightbulb icon", "Provide specific, actionable security instructions to prevent losses"]
    ]
    create_styled_table(doc, ["No.", "Field name", "Type", "Require", "Target"], result_fields, col_widths=[0.4, 1.4, 1.2, 1.8, 1.7])

    doc.add_page_break()

    # -------------------------------------------------------------
    # 2.4 Scan History & Forensic Audit
    # -------------------------------------------------------------
    add_p(doc, "2.4 Scan History & Forensic Audit", bold=True, font_size=14, space_before=8, space_after=4)

    img_hist = "ui_diagrams/fig4_ui_history.png"
    if os.path.exists(img_hist):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=4)
        p_img.add_run().add_picture(img_hist, width=Inches(6.2))
        add_p(doc, "Figure 4. UI Scan History & Local Audit Trail", bold=True, italic=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    add_p(doc, "Table 4. Description UI Scan History", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    hist_fields = [
        ["1", "searchFilterBar", "Input Field", "Placeholder: 'Tìm kiếm từ khóa, URL hoặc mã quét...'", "Filter inspection history by input domain or message snippet"],
        ["2", "riskFilterPills", "Filter Group", "Interactive chips: [Tất cả] [Nguy hiểm] [Nghi ngờ] [An toàn]", "Filter history table by categorical risk classification"],
        ["3", "exportCSVButton", "Button", "Solid Blue; Download icon; Text: 'Xuất CSV'", "Export client-side scan audit logs into CSV spreadsheet"],
        ["4", "tableHeader_Time", "Table Header", "Text: 'Thời gian'; Center alignment", "Display scan execution timestamp (DD/MM HH:mm)"],
        ["5", "tableHeader_Type", "Table Header", "Text: 'Loại dữ liệu'; Badges: URL, Hình ảnh, Tin nhắn, PDF", "Display input modality used during inspection"],
        ["6", "tableHeader_Content", "Table Header", "Text: 'Nội dung kiểm tra'; Truncated text preview", "Display submitted target URL or file name"],
        ["7", "tableHeader_Score", "Table Header", "Text: 'Điểm rủi ro'; Format: XX/100; Colored text", "Display numerical multimodal risk score"],
        ["8", "tableHeader_Level", "Table Header", "Text: 'Mức độ'; Badges: An toàn (Xanh), Nguy hiểm (Đỏ)", "Display human-readable categorical severity"],
        ["9", "actionReplayDetail", "Action Button", "Text: 'Xem chi tiết'; Hyperlink style", "Re-open full CoT reasoning modal without re-running backend scan"],
        ["10", "storageIndicator", "Footer Text", "Text: 'Bộ nhớ cục bộ lưu trữ tối đa 50 lượt gần nhất'", "Inform user that data is persisted securely in browser localStorage"]
    ]
    create_styled_table(doc, ["No.", "Field name", "Type", "Require", "Target"], hist_fields, col_widths=[0.4, 1.4, 1.2, 1.8, 1.7])

    doc.add_page_break()

    # -------------------------------------------------------------
    # 2.5 User Profile & Personal Space
    # -------------------------------------------------------------
    add_p(doc, "2.5 User Profile & Personal Space", bold=True, font_size=14, space_before=8, space_after=4)

    img_prof = "ui_diagrams/fig5_ui_profile.png"
    if os.path.exists(img_prof):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=4)
        p_img.add_run().add_picture(img_prof, width=Inches(6.2))
        add_p(doc, "Figure 5. UI User Profile & Personal Device Space", bold=True, italic=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    add_p(doc, "Table 5. Description UI User Profile", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    prof_fields = [
        ["1", "profileAvatar", "Avatar Circle", "Initials badge; Text: 'KH' / 'AD'; Cyan border", "Visual avatar generated from display name or role"],
        ["2", "profileDisplayName", "Text Heading", "Text: 'Khách Trải Nghiệm' (hoặc tên Admin); Editable", "Display current session identity"],
        ["3", "profileRoleBadge", "Role Pill", "Text: 'VAI TRÒ: CITIZEN / USER' (hoặc 'ADMIN')", "Display role-based permissions and privilege tier"],
        ["4", "deviceStorageCounter", "Text Metric", "Text: 'Bộ nhớ thiết bị: 40 lượt quét'", "Display total local scan records stored in device localStorage"],
        ["5", "aiVersionIndicator", "Text Metric", "Text: 'Phiên bản AI: PhishVN-v1.2'", "Display current active model checkpoint deployed on system"],
        ["6", "statsDangerousCount", "Data Row", "Text: 'Số vụ phát hiện Nguy hiểm: 14 vụ (35%)'; Red color", "Quantify threats prevented on current user device"],
        ["7", "statsSafeCount", "Data Row", "Text: 'Số lượt An toàn: 22 lượt (55%)'; Green color", "Quantify benign scans confirmed on current user device"],
        ["8", "clearHistoryButton", "Button", "Light Red background (#FEE2E2); Text: 'Xóa lịch sử cục bộ'", "Wipe browser localStorage scan logs for privacy protection"],
        ["9", "syncDataButton", "Button", "Light Gray background (#F1F5F9); Text: 'Đồng bộ dữ liệu'", "Trigger synchronization with cloud persistence layer (if authenticated)"]
    ]
    create_styled_table(doc, ["No.", "Field name", "Type", "Require", "Target"], prof_fields, col_widths=[0.4, 1.4, 1.2, 1.8, 1.7])

    doc.add_page_break()

    # -------------------------------------------------------------
    # 2.6 Admin Security Gate
    # -------------------------------------------------------------
    add_p(doc, "2.6 Admin Security Gate (Admin Authentication)", bold=True, font_size=14, space_before=8, space_after=4)

    img_login = "ui_diagrams/fig6_ui_admin_login.png"
    if os.path.exists(img_login):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=4)
        p_img.add_run().add_picture(img_login, width=Inches(6.0))
        add_p(doc, "Figure 6. UI Admin Security Gate", bold=True, italic=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    add_p(doc, "Table 6. Description UI Admin Security Gate", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    login_fields = [
        ["1", "showcaseBrand", "Logo + Text", "Brand shield logo; Text: 'SFDS ADMIN GATE'", "Display system brand identity and privileged gateway status"],
        ["2", "showcaseTitle", "Text Heading", "Font-weight: Bold; Text: 'Khu vực quản trị hệ thống'", "Welcome administrative personnel to secure zone"],
        ["3", "showcaseDesc", "Text Description", "Text: 'Quyền truy cập dành riêng cho quản trị viên...'", "Explain role-based access restrictions and responsibilities"],
        ["4", "coreVisual", "HUD Graphic", "Glowing radar core; Nodes: DB, LOG, AI; Label: 'ADMIN GATE'", "Reinforce cryptographic and AI security trust visually"],
        ["5", "loginTitle", "Text Heading", "Font-weight: Bold; Text: 'Đăng Nhập Quản Trị'", "Form title on the right login card"],
        ["6", "emailInput", "Input Field", "Placeholder: 'admin@scamdetector.local'; Email format check", "Allow administrator to enter username/email address"],
        ["7", "passwordInput", "Input Field", "Type: Password; Includes visibility toggle; Required", "Allow administrator to enter secure account password"],
        ["8", "submitButton", "Button", "Full-width; Solid Blue (#2563EB); Text: 'ĐĂNG NHẬP HỆ THỐNG'", "Submit credentials to FastAPI /auth/login for JWT issuance"],
        ["9", "publicBackLink", "Text Link", "Text: 'Quay lại trang quét công cộng (Không cần đăng nhập)'", "Navigate non-admin citizens back to instant public scan portal"]
    ]
    create_styled_table(doc, ["No.", "Field name", "Type", "Require", "Target"], login_fields, col_widths=[0.4, 1.4, 1.2, 1.8, 1.7])

    doc.add_page_break()

    # -------------------------------------------------------------
    # 2.7 Admin Control Center & Model Governance
    # -------------------------------------------------------------
    add_p(doc, "2.7 Admin Control Center & Model Governance", bold=True, font_size=14, space_before=8, space_after=4)

    img_adm = "ui_diagrams/fig7_ui_admin_console.png"
    if os.path.exists(img_adm):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=4)
        p_img.add_run().add_picture(img_adm, width=Inches(6.2))
        add_p(doc, "Figure 7. UI Admin Control Center (Dataset & Model Management)", bold=True, italic=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    add_p(doc, "Table 7. Description UI Admin Control Center", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    adm_fields = [
        ["1", "adminProfileBanner", "Top Bar", "Right aligned; Text: 'admin@scamdetector.local (ADMIN)'", "Display authenticated administrator session identity"],
        ["2", "adminTab_Dataset", "Tab Button", "Active blue; Text: 'Dataset Huấn Luyện'", "Manage image and text samples used for AI model retraining"],
        ["3", "adminTab_Models", "Tab Button", "Inactive state; Text: 'Mô Hình AI'", "Inspect and toggle active model versions in registry"],
        ["4", "adminTab_Evaluations", "Tab Button", "Inactive state; Text: 'Đánh Giá Model'", "Monitor benchmark metrics (Macro F1, Recall, False Alarm Rate)"],
        ["5", "adminTab_Logs", "Tab Button", "Inactive state; Text: 'Nhật Ký Hệ Thống'", "Audit administrative actions and security configuration changes"],
        ["6", "datasetInput_URL", "Input Field", "Placeholder: 'uploads/samples/fake_bill_01.jpg'", "Input path or storage URL of newly curated training evidence"],
        ["7", "datasetCategorySelect", "Dropdown", "Options: 'Phishing', 'Fake Bill', 'Mạo danh công an', etc.", "Assign standardized fraud category label to training sample"],
        ["8", "checkboxAnonymized", "Checkbox", "Label: '[✓] Anonymized (Đã làm mờ thông tin PII)'", "Enforce privacy compliance before adding sample to dataset pool"],
        ["9", "checkboxVerified", "Checkbox", "Label: '[✓] Verified (Đã xác minh nhãn Ground-truth)'", "Enforce expert human verification of sample labels"],
        ["10", "saveDatasetButton", "Button", "Solid Green (#059669); Text: 'LƯU VÀO KHO DỮ LIỆU HUẤN LUYỆN'", "Persist new dataset record into database via FastAPI endpoint"],
        ["11", "datasetListItems", "List Table", "Displays Code, Category, Status badge (Verified/Pending), Uploader", "Review curated training datasets and verification lifecycle"]
    ]
    create_styled_table(doc, ["No.", "Field name", "Type", "Require", "Target"], adm_fields, col_widths=[0.4, 1.4, 1.2, 1.8, 1.7])

    doc.add_page_break()

    # =========================================================================
    # SECTION 3: DESIGN SYSTEM & GUIDELINES
    # =========================================================================
    add_p(doc, "3. Design System & Guidelines", bold=True, font_size=16, space_before=12, space_after=8)

    add_p(doc, "3.1 Typography & Color Hierarchy", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "The SFDS user interface follows a modern, cyber-security design language combining dark tech aesthetic viewports "
        "with clean, accessible white content cards. The visual hierarchy utilizes Tailwind CSS default scale:\n"
        "• Primary Fonts: Inter / Roboto for clean digital readability across Latin and Vietnamese diacritics.\n"
        "• Academic Document Font: Times New Roman, 13 pt body text, line spacing 1.25.\n"
        "• Severity Color Hierarchy:\n"
        "   - Safe (An toàn): Emerald Green (`#059669` / `#22C55E`), used for verified government/banking domains and low risk scores (0-39%).\n"
        "   - Suspicious (Nghi ngờ): Amber / Orange (`#EA580C` / `#EAB308`), used for unverified links or moderate ambiguity (40-69%).\n"
        "   - Dangerous (Nguy hiểm): Crimson Red (`#DC2626` / `#EF4444`), used for confirmed brand impersonation and high risk scores (70-100%).\n"
        "   - Primary Action / HUD: Cyber Blue (`#2563EB` / `#38BDF8`), used for scanning lasers, active buttons, and primary focal points."
    ), space_after=6)

    add_p(doc, "3.2 Accessibility & Responsive Adaptation", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "To ensure citizens across diverse demographics (including elderly users and non-technical mobile users) can easily utilize the system:\n"
        "• Frictionless Citizen Onboarding: Public users never need to remember passwords or configure credentials to check suspicious content.\n"
        "• High Contrast Ratio: All text elements achieve a minimum WCAG 2.1 AA contrast ratio of 4.5:1 against their background.\n"
        "• Redundant Indicators: Risk levels never rely solely on color; they are always accompanied by textual badges (AN TOÀN, NGHI NGỜ, NGUY HIỂM) "
        "and clear percentage scores.\n"
        "• Responsive Breakpoints: The interface adapts fluidly across Mobile (375px+), Tablet (768px+), and Desktop (1280px+). On mobile devices, "
        "the multimodal scan viewport collapses into a single-column thumb-friendly layout with camera snapshot capabilities."
    ), space_after=8)

    # Save to workspace destination
    output_path = r"D:\scam-detector\TAILIEU_CAPSTONE_C1SE06_SFDS\6. USER INTERFACE DESIGN\C1SE.06_UIDesign_SFDS_v1.0.docx"
    doc.save(output_path)
    print(f"Successfully generated: {output_path}")

    # Also save a backup copy in workspace root
    backup_path = "C1SE.06_UIDesign_SFDS_v1.0.docx"
    try:
        doc.save(backup_path)
    except PermissionError:
        pass

if __name__ == "__main__":
    generate_document()

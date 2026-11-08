# -*- coding: utf-8 -*-
"""
Generate official C1SE.06-Proposal_SFDS_v2.1.docx
CMU-SE 450 Capstone Project 1 Proposal
Consistent 100% with the real SFDS scam-detector codebase.
Format: Times New Roman, 13pt body, Monochrome/Grayscale academic standard.
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

def create_proposal_docx():
    doc = docx.Document()
    
    # Configure default style to Times New Roman, 13 pt
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(13)
    style_normal.font.color.rgb = RGBColor(0, 0, 0)
    
    # Page setup (Standard 1-inch margins)
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        s.header.is_linked_to_previous = False
        
        # Header setup
        p_hdr = s.header.paragraphs[0]
        p_hdr.text = "PROPOSAL\t\tInternational School Capstone 1 – 2026"
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p_hdr.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            r.font.italic = True
            r.font.color.rgb = RGBColor(0, 0, 0)
            
        # Footer setup
        p_ftr = s.footer.paragraphs[0]
        p_ftr.text = "C1SE.06\t\tSFDS Proposal v2.1"
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p_ftr.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(0, 0, 0)

    # -------------------------------------------------------------
    # COVER PAGE
    # -------------------------------------------------------------
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists("extracted_media/image_1.png"):
        p_logo.add_run().add_picture("extracted_media/image_1.png", width=Inches(3.0))
        
    p_school = doc.add_paragraph()
    p_school.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_school.paragraph_format.space_before = Pt(8)
    r_school = p_school.add_run("International School\nCapstone Project 1\nCMU-SE 450 – C1SE.06")
    r_school.font.name = "Times New Roman"
    r_school.font.size = Pt(14)
    r_school.font.bold = True
    
    p_title_doc = doc.add_paragraph()
    p_title_doc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title_doc.paragraph_format.space_before = Pt(24)
    r_title_doc = p_title_doc.add_run("Proposal\nVersion 2.1\nDate: August 23, 2026")
    r_title_doc.font.name = "Times New Roman"
    r_title_doc.font.size = Pt(17)
    r_title_doc.font.bold = True
    
    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_before = Pt(20)
    p_proj.paragraph_format.space_after = Pt(24)
    r_proj = p_proj.add_run("SFDS\nFraudulent Image Detection and Warning System with Explanations")
    r_proj.font.name = "Times New Roman"
    r_proj.font.size = Pt(16)
    r_proj.font.bold = True
    
    p_created = doc.add_paragraph()
    p_created.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cr = p_created.add_run("Submitted by\n")
    r_cr.font.name = "Times New Roman"
    r_cr.font.size = Pt(13)
    r_cr.font.bold = True
    r_mem = p_created.add_run("Hao, Pham Tan\nNhung, Dao Thi My\nNam, Tran Hoang Nhat\nTuan, Nguyen Phan Duc\n")
    r_mem.font.name = "Times New Roman"
    r_mem.font.size = Pt(13)
    
    p_app = doc.add_paragraph()
    p_app.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_app.paragraph_format.space_before = Pt(16)
    r_app = p_app.add_run("Approved by\nEng. Toan, Ha Manh\n")
    r_app.font.name = "Times New Roman"
    r_app.font.size = Pt(13)
    r_app.font.bold = True
    
    p_rep = doc.add_paragraph()
    p_rep.paragraph_format.space_before = Pt(26)
    r_rep = p_rep.add_run("Proposal Review Panel Representative:\nName: ______________________    Signature: ________________    Date: ________\n\nCapstone Project 1 - Mentor:\nName: Eng. Toan, Ha Manh        Signature: ________________    Date: ________")
    r_rep.font.name = "Times New Roman"
    r_rep.font.size = Pt(12)

    doc.add_page_break()

    # -------------------------------------------------------------
    # PROJECT INFORMATION TABLE
    # -------------------------------------------------------------
    p_h = doc.add_paragraph()
    r = p_h.add_run("PROJECT INFORMATION")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    tbl_info = doc.add_table(rows=7, cols=4)
    set_table_borders(tbl_info, color="000000", sz="4")
    tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    info_data = [
        ("Project acronym", "SFDS", "", ""),
        ("Project Title", "Fraudulent image detection and warning system with explanations", "", ""),
        ("Start Date", "August 23, 2026", "End Date", "December 22, 2026"),
        ("Lead Institution", "International School, Duy Tan University", "", ""),
        ("Project Mentor", "Eng. Toan, Ha Manh", "", ""),
        ("Scrum Master / Project Leader & Contact", "Hao, Pham Tan\nEmail: phamtanhao1909@gmail.com\nTel: 0961651933 | Student ID: 29219020823", "", ""),
        ("Partner Organization", "Duy Tan University", "", "")
    ]
    
    for row_idx, data in enumerate(info_data):
        cells = tbl_info.rows[row_idx].cells
        if data[2] == "":
            cells[0].merge(cells[0])
            cells[1].merge(cells[3])
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
            
    # Team members sub-table
    p_m = doc.add_paragraph()
    p_m.paragraph_format.space_before = Pt(14)
    r = p_m.add_run("Team Members Contact Details:")
    r.font.name = "Times New Roman"
    r.font.bold = True
    r.font.size = Pt(12)
    
    tbl_mem = doc.add_table(rows=5, cols=4)
    set_table_borders(tbl_mem, color="000000", sz="4")
    tbl_mem.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    headers_mem = ["Student ID", "Full Name", "Email Address", "Phone Number"]
    for i, h in enumerate(headers_mem):
        format_cell_text(tbl_mem.rows[0].cells[i], h, bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_mem.rows[0].cells[i], "E6E6E6")
        
    members_data = [
        ("29219020823", "Hao, Pham Tan", "phamtanhao1909@gmail.com", "0961651933"),
        ("29209200048", "Nhung, Dao Thi My", "mynhung150905@gmail.com", "0376415338"),
        ("29219423638", "Nam, Tran Hoang Nhat", "trannamnhathoang@gmail.com", "0795798736"),
        ("29211151140", "Tuan, Nguyen Phan Duc", "ductuan02072005@gmail.com", "0932442770")
    ]
    for r_idx, m in enumerate(members_data):
        row = tbl_mem.rows[r_idx + 1]
        for c_idx, val in enumerate(m):
            format_cell_text(row.cells[c_idx], val, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,3] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # DOCUMENT NAME & REVISION
    p_ctrl_h = doc.add_paragraph()
    p_ctrl_h.paragraph_format.space_before = Pt(18)
    r = p_ctrl_h.add_run("DOCUMENT NAME: PROPOSAL")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True
    
    tbl_ctrl = doc.add_table(rows=4, cols=2)
    set_table_borders(tbl_ctrl, color="000000", sz="4")
    tbl_ctrl.alignment = WD_TABLE_ALIGNMENT.CENTER
    ctrl_data = [
        ("Document Title", "Proposal Document"),
        ("Reporting Period", "December 2026"),
        ("Author(s) & Project", "Hao, Pham Tan & Nhung, Dao Thi My"),
        ("Date & File Name", "August 23, 2026 | C1SE.06-Proposal_SFDS_v2.1.docx")
    ]
    for i, d in enumerate(ctrl_data):
        format_cell_text(tbl_ctrl.rows[i].cells[0], d[0], bold=True, size_pt=11)
        format_cell_text(tbl_ctrl.rows[i].cells[1], d[1], size_pt=11)
        set_cell_background(tbl_ctrl.rows[i].cells[0], "F2F2F2")
        set_cell_background(tbl_ctrl.rows[i].cells[1], "FFFFFF")

    p_rev_h = doc.add_paragraph()
    p_rev_h.paragraph_format.space_before = Pt(14)
    r = p_rev_h.add_run("REVISION HISTORY")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True
    
    tbl_rev = doc.add_table(rows=3, cols=5)
    set_table_borders(tbl_rev, color="000000", sz="4")
    tbl_rev.alignment = WD_TABLE_ALIGNMENT.CENTER
    rev_headers = ["Version", "Date", "Comments", "Author", "Approval"]
    for i, h in enumerate(rev_headers):
        format_cell_text(tbl_rev.rows[0].cells[i], h, bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_rev.rows[0].cells[i], "E6E6E6")
    
    rev_rows = [
        ("1.0", "August 22, 2026", "Initial Release", "Hao, Pham Tan", "Eng. Toan, Ha Manh"),
        ("2.1", "August 23, 2026", "Synchronize with Multimodal Architecture, FastAPI, PhishVN and Complete Scope", "Nhung, Dao Thi My", "Eng. Toan, Ha Manh")
    ]
    for r_idx, rvals in enumerate(rev_rows):
        row = tbl_rev.rows[r_idx + 1]
        for c_idx, val in enumerate(rvals):
            format_cell_text(row.cells[c_idx], val, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,1,3,4] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # DOCUMENT APPROVALS
    p_app_h = doc.add_paragraph()
    p_app_h.paragraph_format.space_before = Pt(18)
    r = p_app_h.add_run("DOCUMENT APPROVALS")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    p_app_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p_req = doc.add_paragraph("The following signatures are required for approval of this document:")
    p_req.runs[0].font.name = "Times New Roman"
    p_req.runs[0].font.size = Pt(12)
    p_req.runs[0].font.italic = True
    
    tbl_app = doc.add_table(rows=6, cols=3)
    set_table_borders(tbl_app, color="000000", sz="4")
    tbl_app.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    app_headers = ["Member Name & Role", "Signature", "Date"]
    for i, h in enumerate(app_headers):
        format_cell_text(tbl_app.rows[0].cells[i], h, bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_app.rows[0].cells[i], "E6E6E6")
        
    approvals_rows = [
        ("Eng. Toan, Ha Manh - Project Mentor", "", ""),
        ("Hao, Pham Tan (Student ID: 29219020823) - Scrum Master / Project Leader", "", ""),
        ("Nhung, Dao Thi My (Student ID: 29209200048) - QA / UI-UX Designer", "", ""),
        ("Nam, Tran Hoang Nhat (Student ID: 29219423638) - Frontend Developer", "", ""),
        ("Tuan, Nguyen Phan Duc (Student ID: 29211151140) - Full-stack Developer / AI Lead", "", "")
    ]
    for r_idx, app in enumerate(approvals_rows):
        row = tbl_app.rows[r_idx + 1]
        format_cell_text(row.cells[0], app[0], size_pt=11)
        format_cell_text(row.cells[1], app[1], size_pt=11)
        format_cell_text(row.cells[2], app[2], size_pt=11)
        for cell in row.cells:
            set_cell_background(cell, "FFFFFF")

    doc.add_page_break()

    # -------------------------------------------------------------
    # LIST OF CONTENTS
    # -------------------------------------------------------------
    p_toc_h = doc.add_paragraph()
    r = p_toc_h.add_run("LIST OF CONTENTS")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    p_toc_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    toc_items = [
        ("1. Project Title", "4"),
        ("2. Team Members", "4"),
        ("3. Supervisor", "4"),
        ("4. Problem Statement", "5"),
        ("5. Survey / Existing Solutions", "5"),
        ("6. Objectives and Scope", "7"),
        ("   6.1. Objectives", "7"),
        ("   6.2. Scope (In-Scope and Out-of-Scope)", "7"),
        ("7. Key Features & Requirements", "8"),
        ("   7.1. Functional Requirements", "8"),
        ("   7.2. Non-Functional Requirements", "9"),
        ("8. Constraints and Assumptions", "9"),
        ("   8.1. Constraints", "9"),
        ("   8.2. Assumptions", "10"),
        ("9. Target Users / Stakeholders", "10"),
        ("10. Technology Stack", "11"),
        ("11. Methodology & Development Plan", "12"),
        ("   11.1. Methodology", "12"),
        ("   11.2. Development Plan (6 Sprints Overview)", "13"),
        ("   11.3. Responsibilities", "14"),
        ("12. System Architecture Overview", "14"),
        ("   12.1. Layered Architecture", "14"),
        ("   12.2. System Context Diagram", "15"),
        ("13. Potential Risks and Mitigation Strategies", "16"),
        ("14. Expected Outcomes / Deliverables", "17"),
        ("15. References", "18")
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
        r_dot = p.add_run(" " + "." * (75 - len(item) * 2) + " ")
        r_dot.font.name = "Times New Roman"
        r_dot.font.size = Pt(11)
        r_dot.font.color.rgb = RGBColor(120, 120, 120)
        r_pg = p.add_run(page)
        r_pg.font.name = "Times New Roman"
        r_pg.font.size = Pt(12)
        r_pg.font.bold = True

    doc.add_page_break()

    # -------------------------------------------------------------
    # 1. PROJECT TITLE
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    r = h1.add_run("1. Project Title")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    add_body_p(doc, "Fraudulent Image Detection and Warning System with Explanations (SFDS)")

    # -------------------------------------------------------------
    # 2. TEAM MEMBERS
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(14)
    r = h1.add_run("2. Team Members")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    p_t1 = doc.add_paragraph("Table 1: Team Members")
    p_t1.runs[0].font.name = "Times New Roman"
    p_t1.runs[0].font.bold = True
    p_t1.runs[0].font.size = Pt(11.5)
    
    tbl_t1 = doc.add_table(rows=5, cols=4)
    set_table_borders(tbl_t1, color="000000", sz="4")
    tbl_t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    t1_headers = ["Full Name", "Student ID", "Email", "Assigned Role"]
    for i, h in enumerate(t1_headers):
        format_cell_text(tbl_t1.rows[0].cells[i], h, bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t1.rows[0].cells[i], "E6E6E6")
    t1_data = [
        ("Hao, Pham Tan", "29219020823", "phamtanhao1909@gmail.com", "Project Leader, Full-stack Developer"),
        ("Nhung, Dao Thi My", "29209200048", "mynhung150905@gmail.com", "UI/UX Designer, QA/Tester, Documentation"),
        ("Nam, Tran Hoang Nhat", "29219423638", "trannamnhathoang@gmail.com", "Frontend Developer, Technical Writer"),
        ("Tuan, Nguyen Phan Duc", "29211151140", "ductuan02072005@gmail.com", "AI Engineer, Full-stack Developer")
    ]
    for r_idx, d in enumerate(t1_data):
        row = tbl_t1.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [1] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # -------------------------------------------------------------
    # 3. SUPERVISOR
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(14)
    r = h1.add_run("3. Supervisor")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    p_t2 = doc.add_paragraph("Table 2: Supervisor Information")
    p_t2.runs[0].font.name = "Times New Roman"
    p_t2.runs[0].font.bold = True
    p_t2.runs[0].font.size = Pt(11.5)
    
    tbl_t2 = doc.add_table(rows=4, cols=2)
    set_table_borders(tbl_t2, color="000000", sz="4")
    tbl_t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    t2_data = [
        ("Full Name", "Eng. Toan, Ha Manh"),
        ("Faculty / Department", "International School - CMU, Duy Tan University"),
        ("Email Address", "lhttuy@gmail.com"),
        ("Position / Title", "Capstone Project 1 Academic Mentor")
    ]
    for r_idx, d in enumerate(t2_data):
        format_cell_text(tbl_t2.rows[r_idx].cells[0], d[0], bold=True, size_pt=10.5)
        format_cell_text(tbl_t2.rows[r_idx].cells[1], d[1], size_pt=10.5)
        set_cell_background(tbl_t2.rows[r_idx].cells[0], "F2F2F2")
        set_cell_background(tbl_t2.rows[r_idx].cells[1], "FFFFFF")

    # -------------------------------------------------------------
    # 4. PROBLEM STATEMENT
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("4. Problem Statement")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    add_body_p(doc, "In the current era of rapid digital transformation, online fraud and cyber deception in Vietnam have escalated into sophisticated, dangerous operations. Fraudsters systematically fabricate visual artifacts—such as fraudulent bank balance transfer receipts, bogus court summons or police arrest warrants, fake utility notices, deceptive employment recruitment banners, and counterfeit QR payment codes. These visual materials exploit psychological urgency and fear to manipulate victims into transferring money or disclosing confidential security credentials.")
    add_body_p(doc, "A critical limitation of existing security solutions is their 'black-box' nature: most scanners provide only a simplistic binary verdict ('Safe' or 'Scam') without providing clear explanations. Consequently, non-technical users cannot understand why an image is flagged as fraudulent or what immediate countermeasures they should undertake. Furthermore, conventional tools struggle with Vietnamese diacritics, localized scam linguistics, and multimodal fusion between visual manipulation and textual deceit.")
    add_body_p(doc, "To overcome these challenges, the team proposes developing the 'Scam Fraud Detection System with Explanations' (SFDS). SFDS integrates Vietnamese Tesseract OCR, visual image forensics (ELA/EXIF), PhishVN lexical URL analysis, and deep convolutional neural networks (ResNet-18) governed by a Multimodal Chain-of-Thought (CoT) reasoning engine. The system provides calibrated risk scores (0–100), transparent evidence decomposition, and contextual safety recommendations, empowering citizens and organizations to protect themselves against visual digital fraud.")

    # -------------------------------------------------------------
    # 5. SURVEY / EXISTING SOLUTIONS
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("5. Survey / Existing Solutions")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    add_body_p(doc, "A thorough survey of commercial platforms and academic research reveals four major categories of related solutions:")
    add_body_p(doc, "1. Google Lens / Microsoft Lens: Highly optimized for optical character recognition (OCR) and visual entity search across diverse languages. However, these tools are generic information retrieval engines; they lack fraud reasoning, banking invoice verification, and threat scoring.")
    add_body_p(doc, "2. Google Safe Browsing & ScamAdviser: Industry standards for web domain reputation and blacklist verification. While effective for live URLs, they cannot ingest image screenshots, analyze Vietnamese message semantics, or extract embedded QR codes.")
    add_body_p(doc, "3. VirusTotal: An aggregation scanner running multi-engine security checks for binaries and URLs. It provides comprehensive technical reports for security specialists but remains incomprehensible to regular consumers and lacks image-based multimodal inspection.")
    add_body_p(doc, "4. AI or Not: Specializes in detecting whether a digital image is AI-generated (Deepfake/GAN). While valuable for forensic media authentication, it is not tailored to cyber-fraud heuristics, fake invoices, or localized Vietnamese phishing campaigns.")

    p_t3 = doc.add_paragraph("Table 3: Comparison between Existing Solutions and Proposed SFDS System")
    p_t3.runs[0].font.name = "Times New Roman"
    p_t3.runs[0].font.bold = True
    p_t3.runs[0].font.size = Pt(11.5)

    tbl_t3 = doc.add_table(rows=7, cols=6)
    set_table_borders(tbl_t3, color="000000", sz="4")
    tbl_t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    t3_headers = ["Key Capability / Feature", "Google Lens", "SafeBrowsing", "VirusTotal", "AI or Not", "Proposed SFDS"]
    for i, h in enumerate(t3_headers):
        format_cell_text(tbl_t3.rows[0].cells[i], h, bold=True, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t3.rows[0].cells[i], "E6E6E6")

    comparison_data = [
        ("Vietnamese OCR Text Extraction", "+", "-", "-", "-", "+"),
        ("Multi-source Input (Image, QR, Text, PDF)", "△", "-", "-", "-", "+"),
        ("Malicious URL Lexical Analysis (PhishVN)", "-", "+", "+", "-", "+"),
        ("Image Manipulation Forensics (EXIF/ELA)", "-", "-", "-", "+", "+"),
        ("Calibrated Risk Score & Level (0-100)", "-", "+", "△", "-", "+"),
        ("Explainable Reasoning & Actionable Advice", "-", "-", "-", "-", "+")
    ]
    for r_idx, d in enumerate(comparison_data):
        row = tbl_t3.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    p_note = doc.add_paragraph("Note: +: Fully Supported; △: Partially Supported; −: Not Supported.")
    p_note.runs[0].font.name = "Times New Roman"
    p_note.runs[0].font.italic = True
    p_note.runs[0].font.size = Pt(10)

    # -------------------------------------------------------------
    # 6. OBJECTIVES AND SCOPE
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("6. Objectives and Scope")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("6.1. Objectives")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "The overarching objective of the SFDS project is to build an accessible, explainable, and scientifically validated detection platform for Vietnamese fraudulent visual media. The specific academic and engineering objectives comprise:")
    add_body_p(doc, "• Multi-modal Threat Classification: Accurately classify fraudulent images across 4 primary taxonomies: fake banking transaction bills, government authority impersonation notices, SMS/chat phishing screenshots, and fraudulent QR code payments.\n• Explainable AI (XAI) Synthesis: Provide transparent, decomposed explanations breaking down risk origins (text semantic keywords, lexical URL risks, visual tampering indicators, and model layout probabilities).\n• Objective Evaluation Metrics: Evaluate detection efficacy on independent test datasets using Character Error Rate (CER) & Word Error Rate (WER) for Vietnamese OCR, and Macro-F1, Recall, False Alarm Rate, and Explanation Usefulness (EU) score for scam classification.")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(12)
    r = h2.add_run("6.2. Scope")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "In-Scope:\n• Multi-source Scanning: Ingest images (JPG, PNG, WEBP, BMP), QR codes embedded in images, raw pasted text/SMS messages (up to 20,000 characters), and multi-page PDF documents (up to 10 pages / 15MB).\n• Image Forensics & Processing: Extract text via Tesseract OCR with Vietnamese language models; compute Error Level Analysis (ELA) and inspect EXIF metadata.\n• Machine Learning Models: HistGradientBoosting model trained on PhishVN v3.1.0 (21 lexical features) and fine-tuned ResNet-18 convolutional neural network.\n• Soft Consensus Risk Engine: Compute calibrated risk score (0–100) mapped into 3 safety tiers: Safe (0–25), Suspicious (26–59), and Dangerous (60–100).\n• Guest Inspection & Admin Portal: Allow instant guest inspection with local browser history (up to 50 scans via localStorage); authenticated administrative portal for training datasets, model checkpoints, evaluations, and audit logs.\n• Interactive Safety Assistant: Context-aware conversational guidance answering post-scan remediation inquiries.")
    add_body_p(doc, "Out-of-Scope:\n• Real-time video stream, deepfake video generation, and live telecommunication audio/voice call analysis.\n• Direct automated reporting to banking gateways or law enforcement criminal filing.\n• Native mobile client applications (the scope of Capstone Project 1 is strictly responsive Web Application).")

    # -------------------------------------------------------------
    # 7. KEY FEATURES & REQUIREMENTS
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("7. Key Features & Requirements")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("7.1. Functional Requirements")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    p_t4 = doc.add_paragraph("Table 4: Functional Requirements (FR)")
    p_t4.runs[0].font.name = "Times New Roman"
    p_t4.runs[0].font.bold = True
    p_t4.runs[0].font.size = Pt(11.5)

    tbl_t4 = doc.add_table(rows=9, cols=3)
    set_table_borders(tbl_t4, color="000000", sz="4")
    tbl_t4.alignment = WD_TABLE_ALIGNMENT.CENTER
    t4_headers = ["Req ID", "Requirement Title", "Detailed Functional Description"]
    for i, h in enumerate(t4_headers):
        format_cell_text(tbl_t4.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t4.rows[0].cells[i], "E6E6E6")

    fr_data = [
        ("FR01", "Multi-source Ingestion", "System allows users to upload images (JPG/PNG/WEBP/BMP), paste raw text, input URLs, and upload PDF documents for analysis."),
        ("FR02", "OCR & QR Processing", "Extracts Vietnamese text using Tesseract OCR (vie.traineddata) and decodes payment/URL QR codes embedded within images."),
        ("FR03", "PhishVN URL Analysis", "Parses extracted URLs, extracts 21 lexical features, and evaluates phishing probabilities via HistGradientBoosting."),
        ("FR04", "Visual Image Forensics", "Executes Error Level Analysis (ELA) and extracts EXIF camera metadata to detect composite digital manipulation."),
        ("FR05", "Risk Score & Decomposed XAI", "Computes calibrated risk score (0-100) and displays decomposed signal breakdown (Text, URL, Visual, Model)."),
        ("FR06", "Interactive Safety Assistant", "Provides contextual safety guidelines and interactive Q&A answering remediation queries based on scan findings."),
        ("FR07", "Privacy-first Guest History", "Stores up to 50 recent inspection reports locally on user's browser (localStorage) without mandatory user account creation."),
        ("FR08", "Admin Governance Portal", "Enables authenticated administrators (JWT) to manage training datasets, AI model checkpoints, evaluation metrics, and audit logs.")
    ]
    for r_idx, d in enumerate(fr_data):
        row = tbl_t4.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("7.2. Non-Functional Requirements")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    p_t5 = doc.add_paragraph("Table 5: Non-Functional Requirements (NFR)")
    p_t5.runs[0].font.name = "Times New Roman"
    p_t5.runs[0].font.bold = True
    p_t5.runs[0].font.size = Pt(11.5)

    tbl_t5 = doc.add_table(rows=6, cols=3)
    set_table_borders(tbl_t5, color="000000", sz="4")
    tbl_t5.alignment = WD_TABLE_ALIGNMENT.CENTER
    t5_headers = ["NFR ID", "Quality Attribute", "Measurable Specification Target"]
    for i, h in enumerate(t5_headers):
        format_cell_text(tbl_t5.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t5.rows[0].cells[i], "E6E6E6")

    nfr_data = [
        ("NFR01", "Performance & Latency", "End-to-end image processing (OCR, URL analysis, model inference) must respond within 3.0 seconds under normal payload."),
        ("NFR02", "Security & Upload Safety", "Strict validation of file magic bytes (python-magic), blocking malicious scripts, enforcing 15MB file size ceiling, and JWT auth for admin."),
        ("NFR03", "Data Privacy & Anonymity", "Guest uploads are analyzed in temporary isolated storage; sensitive customer banking logs are not stored without consent."),
        ("NFR04", "Scalability & Modular AI", "System supports hot-swapping or fine-tuning of machine learning checkpoints (PhoBERT, ResNet) without altering REST API schema."),
        ("NFR05", "Usability & Accessibility", "Clean responsive interface compliant with WCAG 2.1 accessibility; color-coded risk alerts (Green, Yellow, Red) with clear Vietnamese copy.")
    ]
    for r_idx, d in enumerate(nfr_data):
        row = tbl_t5.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # -------------------------------------------------------------
    # 8. CONSTRAINTS AND ASSUMPTIONS
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("8. Constraints and Assumptions")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("8.1. Constraints")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    p_t6 = doc.add_paragraph("Table 6: Project Constraints")
    p_t6.runs[0].font.name = "Times New Roman"
    p_t6.runs[0].font.bold = True
    p_t6.runs[0].font.size = Pt(11.5)

    tbl_t6 = doc.add_table(rows=6, cols=3)
    set_table_borders(tbl_t6, color="000000", sz="4")
    tbl_t6.alignment = WD_TABLE_ALIGNMENT.CENTER
    t6_headers = ["Category", "Constraint Description", "Guidelines for Acceptance"]
    for i, h in enumerate(t6_headers):
        format_cell_text(tbl_t6.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t6.rows[0].cells[i], "E6E6E6")

    constraints_data = [
        ("Time & Schedule", "Project must be completed within 16 calendar weeks (93 working days) across 6 Scrum Sprints.", "Weekly sprint tracking on Jira; burn-down velocity reviews with mentor."),
        ("Tool / Technology", "Standardized on Python (FastAPI), React, PyTorch, Scikit-Learn, and Docker.", "Tools must run cross-platform and support containerized staging deploy."),
        ("Hardware & GPU", "Inference must execute efficiently on commodity CPU/RAM or cloud instances (AWS EC2 t3.medium).", "Inference models must maintain memory footprint below 2.0 GB."),
        ("Dataset Privacy", "All Vietnamese scam samples must be anonymized before inclusion in benchmark sets.", "Scrub PII (Personally Identifiable Information) including names and real phone numbers."),
        ("Economic Budget", "Student budget cap of under $350 USD for external hosting, domain, and compute.", "Prioritize open-source libraries, local workstation training, and AWS Free Tier.")
    ]
    for r_idx, d in enumerate(constraints_data):
        row = tbl_t6.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("8.2. Assumptions")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "• Users possess stable internet connectivity to upload media and view analysis dashboards.\n• Uploaded images retain sufficient resolution (at least 300x300 pixels) to permit OCR font segmentation.\n• Benchmark datasets (PhishVN v3.1.0) and synthetically generated Vietnamese invoices provide statistically representative samples for evaluation.\n• Administrators hold valid credentials to operate model deployments and inspect system audit trails.")

    # -------------------------------------------------------------
    # 9. TARGET USERS / STAKEHOLDERS
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("9. Target Users / Stakeholders")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    p_t7 = doc.add_paragraph("Table 7: Stakeholders and Direct Benefits")
    p_t7.runs[0].font.name = "Times New Roman"
    p_t7.runs[0].font.bold = True
    p_t7.runs[0].font.size = Pt(11.5)

    tbl_t7 = doc.add_table(rows=3, cols=2)
    set_table_borders(tbl_t7, color="000000", sz="4")
    tbl_t7.alignment = WD_TABLE_ALIGNMENT.CENTER
    t7_headers = ["Stakeholder Group", "Direct Project Benefits"]
    for i, h in enumerate(t7_headers):
        format_cell_text(tbl_t7.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t7.rows[0].cells[i], "E6E6E6")

    stakeholder_data = [
        ("End Users / General Public", "• Easily inspect suspicious images, bills, SMS messages, and QR codes without account barriers.\n• Receive intuitive, transparent risk scores and localized explanations.\n• View highlighted evidence on canvas and obtain actionable immediate countermeasures.\n• Maintain local browser inspection history without privacy leakage."),
        ("System Administrators & Analysts", "• Govern AI model checkpoints, evaluate dataset performance, and review system audit logs.\n• Manage dynamic keyword scoring dictionaries without redeploying application code.\n• Monitor system health, API latency, and threat distribution statistics.")
    ]
    for r_idx, d in enumerate(stakeholder_data):
        row = tbl_t7.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # -------------------------------------------------------------
    # 10. TECHNOLOGY STACK
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("10. Technology Stack")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    p_t8 = doc.add_paragraph("Table 8: Synchronized Technology Stack")
    p_t8.runs[0].font.name = "Times New Roman"
    p_t8.runs[0].font.bold = True
    p_t8.runs[0].font.size = Pt(11.5)

    tbl_t8 = doc.add_table(rows=10, cols=3)
    set_table_borders(tbl_t8, color="000000", sz="4")
    tbl_t8.alignment = WD_TABLE_ALIGNMENT.CENTER
    t8_headers = ["System Component", "Selected Technology", "Architectural Role & Purpose"]
    for i, h in enumerate(t8_headers):
        format_cell_text(tbl_t8.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t8.rows[0].cells[i], "E6E6E6")

    tech_data = [
        ("Frontend UI", "React (Vite), JavaScript, CSS3", "High-performance Single Page Application (SPA), responsive inspection dashboard, and canvas highlighting."),
        ("Backend Web API", "Python 3.12, FastAPI, Uvicorn", "Asynchronous high-throughput REST API gateway, OpenAPI auto-docs (/docs), and request validation."),
        ("Database Engine", "SQLite (Local/Dev) & MySQL 8.0", "Hybrid persistence: zero-config SQLite for local demo/testing; MySQL schema for production and admin records."),
        ("ORM Framework", "SQLAlchemy 2.0", "Object-relational mapping, database connection pooling, and schema migration."),
        ("AI / OCR Engine", "Tesseract OCR (tessdata/vie)", "Optical character recognition optimized for accented Vietnamese text and banking receipt layouts."),
        ("AI / URL Scanner", "PhishVN (HistGradientBoosting)", "Extracts 21 lexical features from URLs to infer phishing probabilities using pre-trained models."),
        ("AI / Visual Classifier", "PyTorch, ResNet-18 fine-tuned", "Convolutional neural network for layout and counterfeit image classification."),
        ("Visual Forensics", "OpenCV, Pillow (ELA & EXIF)", "Error Level Analysis (ELA) for image resaving traces, JPEG compression artifacts, and metadata checks."),
        ("DevOps & Testing", "Docker, Docker Compose, Pytest", "Isolated containerization for microservices, automated regression test suites, and GitHub Actions CI/CD.")
    ]
    for r_idx, d in enumerate(tech_data):
        row = tbl_t8.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # -------------------------------------------------------------
    # 11. METHODOLOGY & DEVELOPMENT PLAN
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("11. Methodology & Development Plan")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("11.1. Methodology")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists("extracted_media/image_0.png"):
        p.add_run().add_picture("extracted_media/image_0.png", width=Inches(5.5))
        
    p_fig1 = doc.add_paragraph("Figure 1: Scrum Agile Framework")
    p_fig1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fig1.runs[0].font.name = "Times New Roman"
    p_fig1.runs[0].font.italic = True
    p_fig1.runs[0].font.size = Pt(11)

    add_body_p(doc, "The project utilizes the Agile Scrum Framework, structuring the development lifecycle into short, iterative 14-day Sprints. This methodology is particularly advantageous for AI-assisted engineering where data distributions, OCR edge cases, and machine learning thresholds require continual empirical calibration.")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("11.2. Development Plan")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    p_t9 = doc.add_paragraph("Table 9: Schedule Overview (6 Sprints Breakdown)")
    p_t9.runs[0].font.name = "Times New Roman"
    p_t9.runs[0].font.bold = True
    p_t9.runs[0].font.size = Pt(11.5)

    tbl_t9 = doc.add_table(rows=11, cols=6)
    set_table_borders(tbl_t9, color="000000", sz="4")
    tbl_t9.alignment = WD_TABLE_ALIGNMENT.CENTER
    t9_headers = ["No.", "Sprint / Milestone Name", "Duration", "Start Date", "Finish Date", "Effort (Hrs)"]
    for i, h in enumerate(t9_headers):
        format_cell_text(tbl_t9.rows[0].cells[i], h, bold=True, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t9.rows[0].cells[i], "E6E6E6")

    schedule_overview = [
        ("1", "Sprint 1: Architecture, DB Schema & Baseline Setup", "14 days", "02/09/2026", "16/09/2026", "200"),
        ("2", "Sprint 2: OCR Engine, PhishVN & Risk Base Engine", "14 days", "17/09/2026", "01/10/2026", "200"),
        ("3", "Sprint 3: Visual Forensics, Explanations & Multi-input", "14 days", "02/10/2026", "16/10/2026", "200"),
        ("4", "Sprint 4: Admin Portal, Dynamic Rules & Security", "14 days", "17/10/2026", "31/10/2026", "200"),
        ("5", "Sprint 5: Model Evaluation, Dockerizing & Optimization", "14 days", "01/11/2026", "15/11/2026", "200"),
        ("6", "Sprint 6: User Acceptance Testing (UAT) & Staging Deploy", "15 days", "16/11/2026", "01/12/2026", "200"),
        ("7", "Final Adjustments & Technical Report Documentation", "16 days", "02/12/2026", "18/12/2026", "200"),
        ("8", "Project Retrospective & Mock Defense Meeting", "2 days", "18/12/2026", "20/12/2026", "10"),
        ("9", "Official Capstone Project 1 Final Defense", "1 day", "22/12/2026", "22/12/2026", "15"),
        ("", "TOTAL CUMULATIVE ENGINEERING EFFORT", "93 days", "02/09/2026", "22/12/2026", "1,425 hrs")
    ]
    for r_idx, d in enumerate(schedule_overview):
        row = tbl_t9.rows[r_idx + 1]
        is_tot = (r_idx == len(schedule_overview) - 1)
        bg = "F0F0F0" if is_tot else "FFFFFF"
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, bold=is_tot, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,2,3,4,5] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], bg)

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("11.3. Responsibilities")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    p_t10 = doc.add_paragraph("Table 10: Team Member Role Allocation")
    p_t10.runs[0].font.name = "Times New Roman"
    p_t10.runs[0].font.bold = True
    p_t10.runs[0].font.size = Pt(11.5)

    tbl_t10 = doc.add_table(rows=5, cols=2)
    set_table_borders(tbl_t10, color="000000", sz="4")
    tbl_t10.alignment = WD_TABLE_ALIGNMENT.CENTER
    t10_headers = ["Member Name", "Core Responsibilities"]
    for i, h in enumerate(t10_headers):
        format_cell_text(tbl_t10.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t10.rows[0].cells[i], "E6E6E6")

    resp_data = [
        ("Hao, Pham Tan", "Project Leader, Scrum Master, Backend Developer (FastAPI, MySQL, Docker, System Integration)."),
        ("Nhung, Dao Thi My", "QA Lead, UI/UX Designer, Test Case Engineering, UAT Coordination, Technical Documentation."),
        ("Nam, Tran Hoang Nhat", "Frontend Developer (React, Vite, CSS3, Canvas Bounding Box, LocalStorage History)."),
        ("Tuan, Nguyen Phan Duc", "AI Lead, Full-stack Developer (Tesseract OCR, PhishVN, ResNet-18, Model Benchmark Evaluation).")
    ]
    for r_idx, d in enumerate(resp_data):
        row = tbl_t10.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # -------------------------------------------------------------
    # 12. SYSTEM ARCHITECTURE OVERVIEW
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("12. System Architecture Overview")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("12.1. Layered Architecture")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "The SFDS system implements a decoupled 4-tier microservice architecture ensuring high maintainability and security:")
    add_body_p(doc, "1. Presentation Layer (React Client): Provides an intuitive single-page application supporting drag-and-drop file ingestion, real-time bounding box highlighting, and localized inspection history management.\n2. API Gateway & Application Layer (FastAPI): Manages RESTful routing, payload validation (magic byte checks), rate limiting, and role-based access control (RBAC via JWT).\n3. Analytical & Machine Learning Layer: Houses the specialized detection sub-engines: Tesseract OCR, PhishVN URL classifier, ResNet-18 visual network, OpenCV ELA forensics, and the Multimodal CoT Reasoning Engine.\n4. Persistence & Cache Layer: Manages structured transactional data in MySQL, session caching in Redis, and client-side history in browser localStorage.")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("12.2. System Context Diagram")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists("extracted_media/image_12.png"):
        p.add_run().add_picture("extracted_media/image_12.png", width=Inches(5.5))
        
    p_fig2 = doc.add_paragraph("Figure 2: System Context Diagram (SFDS Interactions)")
    p_fig2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fig2.runs[0].font.name = "Times New Roman"
    p_fig2.runs[0].font.italic = True
    p_fig2.runs[0].font.size = Pt(11)

    # -------------------------------------------------------------
    # 13. POTENTIAL RISKS AND MITIGATION STRATEGIES
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("13. Potential Risks and Mitigation Strategies")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    p_t11 = doc.add_paragraph("Table 11: Risks and Mitigations Matrix")
    p_t11.runs[0].font.name = "Times New Roman"
    p_t11.runs[0].font.bold = True
    p_t11.runs[0].font.size = Pt(11.5)

    tbl_t11 = doc.add_table(rows=7, cols=7)
    set_table_borders(tbl_t11, color="000000", sz="4")
    tbl_t11.alignment = WD_TABLE_ALIGNMENT.CENTER
    t11_headers = ["No.", "Risk Title", "Risk Description", "P", "I", "E", "Mitigation Strategy"]
    for i, h in enumerate(t11_headers):
        format_cell_text(tbl_t11.rows[0].cells[i], h, bold=True, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t11.rows[0].cells[i], "E6E6E6")

    risks_data = [
        ("1", "Security Vulnerabilities", "Risks of arbitrary file upload, API parameter manipulation, or unauthorized administrative access.", "3", "5", "15", "Inspect magic bytes (python-magic), disallow script extensions, enforce role-based JWT auth, and isolate uploads."),
        ("2", "Project Schedule Slippage", "Development delays caused by complex AI model calibration or mid-semester academic workload.", "4", "4", "16", "Divide work strictly into 14-day sprints, monitor daily Jira velocity, and prioritize core functionality over optional extras."),
        ("3", "Server Performance Under Peak", "Concurrent image OCR and deep learning inference causing memory spikes or high API response latency.", "3", "4", "12", "Implement background task queues (Celery/Redis), rate limiting, and deploy lightweight quantized inference checkpoints."),
        ("4", "Data Privacy & Sensitive PII", "Uploaded receipts containing real victim names, bank accounts, or sensitive identity cards.", "3", "5", "15", "Store guest scans on client localStorage; scrub personal numbers from benchmark datasets; implement automated scratch cleanup."),
        ("5", "AI False Positives / Negatives", "Model misclassifies legitimate banking receipts or misses novel deceptive layouts.", "4", "5", "20", "Use Soft Consensus Fusion instead of raw max, calibrate decision thresholds on 200+ clean bills, and provide transparent explanations."),
        ("6", "Cloud Hosting Cost Overrun", "Continuous AWS EC2 and GPU usage exceeding the allocated student project budget.", "3", "3", "9", "Perform training on local workstations/Colab; deploy lightweight models (ResNet-18); run EC2 only during staging demo intervals.")
    ]
    for r_idx, d in enumerate(risks_data):
        row = tbl_t11.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=9, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,3,4,5] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # -------------------------------------------------------------
    # 14. EXPECTED OUTCOMES / DELIVERABLES
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("14. Expected Outcomes / Deliverables")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    add_body_p(doc, "• Complete Software Application: A fully functional, responsive web application supporting multi-source scanning (Image, Text, URL, QR, PDF) with explainable risk breakdown and interactive safety guidance.\n• Source Code Repository: Clean, well-documented source code for the React frontend, FastAPI backend, and AI/ML pipelines with Git version control.\n• Technical Engineering Documentation: Comprehensive Software Requirements Specification (SRS), Software Design Document (SDD), and API documentation via Swagger/OpenAPI.\n• Vietnamese Scam Benchmark Dataset: Curated, anonymized dataset of labeled Vietnamese scam images, fake invoices, and phishing URLs.\n• Scientific AI Benchmark Report: Documented evaluation results measuring Character Error Rate (CER), Word Error Rate (WER), Macro-F1, Recall, False Alarm Rate, and Explanation Usefulness.\n• User & Admin Manuals: Step-by-step illustrated operational guides for general users and system administrators.")

    # -------------------------------------------------------------
    # 15. REFERENCES
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("15. References")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    p_t12 = doc.add_paragraph("Table 12: Academic & Technical References")
    p_t12.runs[0].font.name = "Times New Roman"
    p_t12.runs[0].font.bold = True
    p_t12.runs[0].font.size = Pt(11.5)

    tbl_t12 = doc.add_table(rows=8, cols=3)
    set_table_borders(tbl_t12, color="000000", sz="4")
    tbl_t12.alignment = WD_TABLE_ALIGNMENT.CENTER
    t12_headers = ["No.", "Reference Topic", "Source Citation & Online Documentation"]
    for i, h in enumerate(t12_headers):
        format_cell_text(tbl_t12.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t12.rows[0].cells[i], "E6E6E6")

    ref_data = [
        ("1", "Scrum Agile Framework", "Schwaber, K. & Sutherland, J. (2020). The Scrum Guide. https://www.scrum.org/"),
        ("2", "Vietnamese Phishing Dataset", "Nguyen, H. et al. (2024). PhishVN: A Time-Stamped Vietnamese URL Phishing Dataset. Mendeley Data."),
        ("3", "FastAPI Framework", "Tiangolo, S. (2024). FastAPI: High performance, easy to learn, fast to code. https://fastapi.tiangolo.com/"),
        ("4", "React Framework", "Meta Platforms, Inc. (2024). React: The library for web and native user interfaces. https://react.dev/"),
        ("5", "Tesseract OCR", "Smith, R. (2007). An Overview of the Tesseract OCR Engine. IEEE ICDAR. https://tesseract-ocr.github.io/"),
        ("6", "Deep Residual Learning", "He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep Residual Learning for Image Recognition. IEEE CVPR."),
        ("7", "Software Engineering Standards", "ISO/IEC/IEEE 12207:2017 Systems and software engineering - Software life cycle processes.")
    ]
    for r_idx, d in enumerate(ref_data):
        row = tbl_t12.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # Save to files
    out_files = ["C1SE.06-Proposal_SFDS_v2.1.docx", "C1SE.06-Proposal_SFDS_v2.0.docx"]
    for fname in out_files:
        try:
            doc.save(fname)
            print(f"Successfully generated: {fname}")
        except Exception as e:
            print(f"Could not save {fname}: {e}")

if __name__ == "__main__":
    create_proposal_docx()

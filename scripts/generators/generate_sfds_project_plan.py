# -*- coding: utf-8 -*-
"""
Script to generate official C1SE.06_ProjectPlan_SFDS_v1.2.docx
Standard academic format:
- Font: Times New Roman, Size 13 pt for body
- Tables: Black borders (000000), White/Light-Grey cells, NO blue or colored fills.
- All headings and text: Pure Black (0, 0, 0)
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

def create_project_plan_docx():
    doc = docx.Document()
    
    # Configure default style to Times New Roman, 13 pt
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(13)
    style_normal.font.color.rgb = RGBColor(0, 0, 0)
    
    # Page setup
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        s.header.is_linked_to_previous = False
        
        # Header setup
        p_hdr = s.header.paragraphs[0]
        p_hdr.text = "PROJECT PLAN\t\tInternational School Capstone 1 – 2026"
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p_hdr.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            r.font.italic = True
            r.font.color.rgb = RGBColor(0, 0, 0)
            
        # Footer setup
        p_ftr = s.footer.paragraphs[0]
        p_ftr.text = "C1SE.06\t\tSFDS Project Plan v1.0"
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
    r_school.font.color.rgb = RGBColor(0, 0, 0)
    
    p_title_doc = doc.add_paragraph()
    p_title_doc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title_doc.paragraph_format.space_before = Pt(24)
    r_title_doc = p_title_doc.add_run("Project Plan\nVersion 1.0\nDate: September 02, 2026")
    r_title_doc.font.name = "Times New Roman"
    r_title_doc.font.size = Pt(17)
    r_title_doc.font.bold = True
    r_title_doc.font.color.rgb = RGBColor(0, 0, 0)
    
    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_before = Pt(20)
    p_proj.paragraph_format.space_after = Pt(24)
    r_proj = p_proj.add_run("SFDS\nFraudulent Image Detection and Warning System with Explanations")
    r_proj.font.name = "Times New Roman"
    r_proj.font.size = Pt(16)
    r_proj.font.bold = True
    r_proj.font.color.rgb = RGBColor(0, 0, 0)
    
    p_created = doc.add_paragraph()
    p_created.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cr = p_created.add_run("Created by C1SE.06\n")
    r_cr.font.name = "Times New Roman"
    r_cr.font.size = Pt(13)
    r_cr.font.bold = True
    r_cr.font.color.rgb = RGBColor(0, 0, 0)
    r_mem = p_created.add_run("Hao, Pham Tan\nNhung, Dao Thi My\nNam, Tran Hoang Nhat\nTuan, Nguyen Phan Duc\n")
    r_mem.font.name = "Times New Roman"
    r_mem.font.size = Pt(13)
    r_mem.font.color.rgb = RGBColor(0, 0, 0)
    
    p_app = doc.add_paragraph()
    p_app.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_app.paragraph_format.space_before = Pt(16)
    r_app = p_app.add_run("Approved by\nEng. Toan, Ha Manh\n")
    r_app.font.name = "Times New Roman"
    r_app.font.size = Pt(13)
    r_app.font.bold = True
    r_app.font.color.rgb = RGBColor(0, 0, 0)
    
    p_rep = doc.add_paragraph()
    p_rep.paragraph_format.space_before = Pt(26)
    r_rep = p_rep.add_run("Project Plan Review Panel Representative:\nName: ______________________    Signature: ________________    Date: ________\n\nCapstone Project 1 - Mentor:\nName: Eng. Toan, Ha Manh        Signature: ________________    Date: ________")
    r_rep.font.name = "Times New Roman"
    r_rep.font.size = Pt(12)
    r_rep.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_page_break()

    # -------------------------------------------------------------
    # PROJECT INFORMATION TABLE
    # -------------------------------------------------------------
    p_h = doc.add_paragraph()
    r = p_h.add_run("PROJECT INFORMATION")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
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
            format_cell_text(cells[0], data[0], bold=True, size_pt=11, color_rgb=(0,0,0))
            format_cell_text(cells[1], data[1], bold=(row_idx==0), size_pt=11, color_rgb=(0,0,0))
            set_cell_background(cells[0], "F2F2F2")
            set_cell_background(cells[1], "FFFFFF")
        else:
            format_cell_text(cells[0], data[0], bold=True, size_pt=11, color_rgb=(0,0,0))
            format_cell_text(cells[1], data[1], size_pt=11, color_rgb=(0,0,0))
            format_cell_text(cells[2], data[2], bold=True, size_pt=11, color_rgb=(0,0,0))
            format_cell_text(cells[3], data[3], size_pt=11, color_rgb=(0,0,0))
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
    r.font.color.rgb = RGBColor(0, 0, 0)
    
    tbl_mem = doc.add_table(rows=5, cols=4)
    set_table_borders(tbl_mem, color="000000", sz="4")
    tbl_mem.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    headers_mem = ["Student ID", "Full Name", "Email Address", "Phone Number"]
    for i, h in enumerate(headers_mem):
        format_cell_text(tbl_mem.rows[0].cells[i], h, bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER, color_rgb=(0,0,0))
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
            format_cell_text(row.cells[c_idx], val, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,3] else WD_ALIGN_PARAGRAPH.LEFT, color_rgb=(0,0,0))
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # DOCUMENT APPROVALS
    p_app_h = doc.add_paragraph()
    p_app_h.paragraph_format.space_before = Pt(18)
    r = p_app_h.add_run("DOCUMENT APPROVALS")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    p_app_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p_req = doc.add_paragraph("The following signatures are required for approval of this document:")
    p_req.runs[0].font.name = "Times New Roman"
    p_req.runs[0].font.size = Pt(12)
    p_req.runs[0].font.italic = True
    p_req.runs[0].font.color.rgb = RGBColor(0, 0, 0)
    
    tbl_app = doc.add_table(rows=6, cols=3)
    set_table_borders(tbl_app, color="000000", sz="4")
    tbl_app.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    app_headers = ["Member Name & Role", "Signature", "Date"]
    for i, h in enumerate(app_headers):
        format_cell_text(tbl_app.rows[0].cells[i], h, bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER, color_rgb=(0,0,0))
        set_cell_background(tbl_app.rows[0].cells[i], "E6E6E6")
        
    approvals_rows = [
        ("Eng. Toan, Ha Manh - Project Mentor", "", ""),
        ("Hao, Pham Tan (Student ID: 29219020823) - Scrum Master / Project Leader", "", ""),
        ("Nhung, Dao Thi My (Student ID: 29209200048) - QA / Documentation Lead", "", ""),
        ("Nam, Tran Hoang Nhat (Student ID: 29219423638) - Frontend Developer", "", ""),
        ("Tuan, Nguyen Phan Duc (Student ID: 29211151140) - Full-stack Developer / AI Lead", "", "")
    ]
    for r_idx, app in enumerate(approvals_rows):
        row = tbl_app.rows[r_idx + 1]
        format_cell_text(row.cells[0], app[0], size_pt=11, color_rgb=(0,0,0))
        format_cell_text(row.cells[1], app[1], size_pt=11, color_rgb=(0,0,0))
        format_cell_text(row.cells[2], app[2], size_pt=11, color_rgb=(0,0,0))
        for cell in row.cells:
            set_cell_background(cell, "FFFFFF")

    # PROJECT PLAN DOCUMENT CONTROL & REVISION
    p_ctrl_h = doc.add_paragraph()
    p_ctrl_h.paragraph_format.space_before = Pt(18)
    r = p_ctrl_h.add_run("PROJECT PLAN DOCUMENT SPECIFICATION")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    
    tbl_ctrl = doc.add_table(rows=3, cols=2)
    set_table_borders(tbl_ctrl, color="000000", sz="4")
    tbl_ctrl.alignment = WD_TABLE_ALIGNMENT.CENTER
    ctrl_data = [
        ("Document Title", "Project Plan Document"),
        ("Author(s) & Role", "Nhung, Dao Thi My (QA Lead) & Hao, Pham Tan (Scrum Master)"),
        ("Date & File Name", "September 02, 2026 | C1SE.06_ProjectPlan_SFDS_v1.0.docx")
    ]
    for i, d in enumerate(ctrl_data):
        format_cell_text(tbl_ctrl.rows[i].cells[0], d[0], bold=True, size_pt=11, color_rgb=(0,0,0))
        format_cell_text(tbl_ctrl.rows[i].cells[1], d[1], size_pt=11, color_rgb=(0,0,0))
        set_cell_background(tbl_ctrl.rows[i].cells[0], "F2F2F2")
        set_cell_background(tbl_ctrl.rows[i].cells[1], "FFFFFF")

    p_rev_h = doc.add_paragraph()
    p_rev_h.paragraph_format.space_before = Pt(14)
    r = p_rev_h.add_run("REVISION HISTORY")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    
    tbl_rev = doc.add_table(rows=2, cols=5)
    set_table_borders(tbl_rev, color="000000", sz="4")
    tbl_rev.alignment = WD_TABLE_ALIGNMENT.CENTER
    rev_headers = ["Version", "Date", "Comments", "Author", "Approval"]
    for i, h in enumerate(rev_headers):
        format_cell_text(tbl_rev.rows[0].cells[i], h, bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER, color_rgb=(0,0,0))
        set_cell_background(tbl_rev.rows[0].cells[i], "E6E6E6")
    
    rev_row = tbl_rev.rows[1]
    rev_vals = ["1.0", "Sep 02, 2026", "Initial Complete Project Plan Document", "Dao Thi My Nhung", "Pham Tan Hao"]
    for i, val in enumerate(rev_vals):
        format_cell_text(rev_row.cells[i], val, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER if i in [0,1,3,4] else WD_ALIGN_PARAGRAPH.LEFT, color_rgb=(0,0,0))
        set_cell_background(rev_row.cells[i], "FFFFFF")

    doc.add_page_break()

    # -------------------------------------------------------------
    # TABLE OF CONTENTS
    # -------------------------------------------------------------
    p_toc_h = doc.add_paragraph()
    r = p_toc_h.add_run("TABLE OF CONTENTS")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    p_toc_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    toc_items = [
        ("1. Introduction", "3"),
        ("   1.1. Purpose", "3"),
        ("   1.2. Project Overview", "3"),
        ("   1.3. Project Deliverable", "3"),
        ("2. Team Organisation", "4"),
        ("   2.1. Scrum Team Information", "4"),
        ("   2.2. Role and Responsibility", "4"),
        ("   2.3. Communication Methodology", "5"),
        ("   2.4. Communication and Report", "5"),
        ("3. Development Methodology", "6"),
        ("4. Schedule and Cost", "7"),
        ("   4.1. Detailed Schedule (6 Sprints Breakdown)", "7"),
        ("   4.2. Cost Person/Hours", "9"),
        ("   4.3. Total Cost Estimate", "9"),
        ("5. Project Risks & Mitigations", "10"),
        ("6. Deliverables", "11")
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
        r_item.font.color.rgb = RGBColor(0, 0, 0)
        r_dot = p.add_run(" " + "." * (75 - len(item) * 2) + " ")
        r_dot.font.name = "Times New Roman"
        r_dot.font.size = Pt(11)
        r_dot.font.color.rgb = RGBColor(120, 120, 120)
        r_pg = p.add_run(page)
        r_pg.font.name = "Times New Roman"
        r_pg.font.size = Pt(12)
        r_pg.font.bold = True
        r_pg.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_page_break()

    # -------------------------------------------------------------
    # 1. INTRODUCTION (Font 13 pt, Black)
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    r = h1.add_run("1. Introduction")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("1.1. Purpose")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    
    add_body_p(doc, "The purpose of this document is to establish a detailed project plan for the SFDS (Scam Fraud Detection System) project. It outlines the project objectives, team roles and responsibilities, agile development methodology, sprint schedule, cost estimations, risk management matrix, and academic deliverables. The ultimate goal is to ensure the successful engineering, testing, and deployment of an explainable fraudulent image detection platform for Capstone Project 1 (CMU-SE 450).")

    h2 = doc.add_heading(level=2)
    r = h2.add_run("1.2. Project Overview")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    
    add_body_p(doc, "(Reference to C1SE.06-Proposal_SFDS_v2.0.docx)\nIn the digital age, deceptive images—including fraudulent banking receipts, fake lottery/promotional announcements, phishing messages, and malicious QR codes—are becoming increasingly widespread and sophisticated. Traditional cybersecurity scanners frequently provide blunt, opaque classifications ('Safe' or 'Scam') without providing interpretable evidence to the victim.")
    add_body_p(doc, "SFDS is an AI-assisted detection and advisory system engineered to analyze images, extract Vietnamese text via Tesseract OCR, perform image forensics (EXIF and Error Level Analysis - ELA), parse lexical URL risks with PhishVN, and classify threats with ResNet18. The system computes a normalized risk score (0–100) and provides context-rich textual explanations and actionable security recommendations.")

    h2 = doc.add_heading(level=2)
    r = h2.add_run("1.3. Project Deliverable")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    
    add_body_p(doc, "• Primary deliverable: A fully functional web-based detection and warning application with guest inspection mode, local inspection history, and an authenticated administrative dashboard.\n• AI / ML artifacts: Trained ResNet18 image classifier checkpoint, PhishVN lexical analysis model, and an explainable risk scoring engine.\n• Supporting documentation: Software Requirements Specification (SRS), Software Design Document (SDD), AI benchmark report (CER/WER, Macro-F1, Recall), User Manual, and Final Capstone Technical Report.")

    # -------------------------------------------------------------
    # 2. TEAM ORGANISATION
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("2. Team Organisation")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)

    h2 = doc.add_heading(level=2)
    r = h2.add_run("2.1. Scrum Team Information")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    
    p_t1 = doc.add_paragraph("Table 1. Scrum Team Organization")
    p_t1.runs[0].font.name = "Times New Roman"
    p_t1.runs[0].font.bold = True
    p_t1.runs[0].font.size = Pt(11.5)
    p_t1.runs[0].font.color.rgb = RGBColor(0, 0, 0)
    
    tbl_t1 = doc.add_table(rows=6, cols=4)
    set_table_borders(tbl_t1, color="000000", sz="4")
    tbl_t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    t1_headers = ["Full Name", "Phone", "Email", "Team Position"]
    for i, h in enumerate(t1_headers):
        format_cell_text(tbl_t1.rows[0].cells[i], h, bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, color_rgb=(0,0,0))
        set_cell_background(tbl_t1.rows[0].cells[i], "E6E6E6")
    t1_data = [
        ("Eng. Toan, Ha Manh", "-", "lhttuy@gmail.com", "Project Mentor"),
        ("Pham Tan Hao", "0961651933", "phamtanhao1909@gmail.com", "Project Leader / Scrum Master"),
        ("Dao Thi My Nhung", "0376415338", "mynhung150905@gmail.com", "QA Lead / UI-UX Designer"),
        ("Tran Hoang Nhat Nam", "0795798736", "trannamnhathoang@gmail.com", "Frontend Developer / Technical Writer"),
        ("Nguyen Phan Duc Tuan", "0932442770", "ductuan02072005@gmail.com", "AI Engineer / Full-stack Developer")
    ]
    for r_idx, d in enumerate(t1_data):
        row = tbl_t1.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [1] else WD_ALIGN_PARAGRAPH.LEFT, color_rgb=(0,0,0))
            set_cell_background(row.cells[c_idx], "FFFFFF")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("2.2. Role and Responsibility")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    
    p_t2 = doc.add_paragraph("Table 2. Roles and Responsibilities")
    p_t2.runs[0].font.name = "Times New Roman"
    p_t2.runs[0].font.bold = True
    p_t2.runs[0].font.size = Pt(11.5)
    p_t2.runs[0].font.color.rgb = RGBColor(0, 0, 0)
    
    tbl_t2 = doc.add_table(rows=7, cols=3)
    set_table_borders(tbl_t2, color="000000", sz="4")
    tbl_t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    t2_headers = ["Role", "Responsibility", "Assigned Member"]
    for i, h in enumerate(t2_headers):
        format_cell_text(tbl_t2.rows[0].cells[i], h, bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, color_rgb=(0,0,0))
        set_cell_background(tbl_t2.rows[0].cells[i], "E6E6E6")
    t2_data = [
        ("Product Owner", "Defines requirements, maintains Product Backlog, ensures value delivery and stakeholder management.", "Pham Tan Hao"),
        ("Scrum Master", "Facilitates Scrum ceremonies, removes development impediments, tracks burn-down progress.", "Pham Tan Hao"),
        ("AI / Backend Dev", "Implements OCR text extraction, PhishVN URL model, ResNet18 classifier, and FastAPI services.", "Nguyen Phan Duc Tuan & Pham Tan Hao"),
        ("Frontend Dev", "Develops responsive Next.js/React interface, state management, and client localStorage inspection history.", "Tran Hoang Nhat Nam"),
        ("QA / Designer", "Designs Figma wireframes, drafts Test Cases, executes API, security, and User Acceptance Testing (UAT).", "Dao Thi My Nhung"),
        ("Mentor", "Provides technical guidance, validates architectural solutions, and conducts periodic assessments.", "Eng. Toan, Ha Manh")
    ]
    for r_idx, d in enumerate(t2_data):
        row = tbl_t2.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=10, color_rgb=(0,0,0))
            set_cell_background(row.cells[c_idx], "FFFFFF")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("2.3. Communication Methodology")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    
    p_t3 = doc.add_paragraph("Table 3. Communication Methodology")
    p_t3.runs[0].font.name = "Times New Roman"
    p_t3.runs[0].font.bold = True
    p_t3.runs[0].font.size = Pt(11.5)
    p_t3.runs[0].font.color.rgb = RGBColor(0, 0, 0)
    
    tbl_t3 = doc.add_table(rows=3, cols=4)
    set_table_borders(tbl_t3, color="000000", sz="4")
    tbl_t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    t3_headers = ["Audience / Attendees", "Topic / Deliverable", "Frequency", "Method / Tools"]
    for i, h in enumerate(t3_headers):
        format_cell_text(tbl_t3.rows[0].cells[i], h, bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, color_rgb=(0,0,0))
        set_cell_background(tbl_t3.rows[0].cells[i], "E6E6E6")
    t3_data = [
        ("Mentor and Team Members", "Milestone progress review, architecture approval, and thesis advisory", "Weekly", "Face-to-Face Meeting, Google Meet, Email"),
        ("All Team Members", "Sprint progress tracking, task assignment, bug fixing, and daily blockers", "Daily / Bi-daily", "Jira, GitHub, Discord, Zalo")
    ]
    for r_idx, d in enumerate(t3_data):
        row = tbl_t3.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx == 2 else WD_ALIGN_PARAGRAPH.LEFT, color_rgb=(0,0,0))
            set_cell_background(row.cells[c_idx], "FFFFFF")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("2.4. Communication and Report")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    
    p_t4 = doc.add_paragraph("Table 4. Communication and Reporting Protocols")
    p_t4.runs[0].font.name = "Times New Roman"
    p_t4.runs[0].font.bold = True
    p_t4.runs[0].font.size = Pt(11.5)
    p_t4.runs[0].font.color.rgb = RGBColor(0, 0, 0)
    
    tbl_t4 = doc.add_table(rows=5, cols=5)
    set_table_borders(tbl_t4, color="000000", sz="4")
    tbl_t4.alignment = WD_TABLE_ALIGNMENT.CENTER
    t4_headers = ["Type of Communication", "Methods / Tools", "Frequency", "Information Exchanged", "Attendees"]
    for i, h in enumerate(t4_headers):
        format_cell_text(tbl_t4.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER, color_rgb=(0,0,0))
        set_cell_background(tbl_t4.rows[0].cells[i], "E6E6E6")
    t4_data = [
        ("Daily Standup", "Discord / Google Meet", "Every 2 days (15 mins)", "Tasks completed in last 48h, current sprint goals, technical impediments and solutions.", "Project Team"),
        ("Sprint Planning", "Face-to-face / Labs", "Every 14 days", "Backlog grooming, user story sizing, task commitment, and architectural alignment.", "Project Team"),
        ("Retrospective Meeting", "Face-to-face", "Every 14 days", "Evaluation of completed sprint, identification of strengths/weaknesses, process refinements.", "Team & Mentor"),
        ("Progress Demo & Jira Tracking", "Jira & GitHub PRs", "Continuous / Daily", "Pull request reviews, bug tracking, CI/CD pipeline results, and automated test reports.", "Project Team")
    ]
    for r_idx, d in enumerate(t4_data):
        row = tbl_t4.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [1,2] else WD_ALIGN_PARAGRAPH.LEFT, color_rgb=(0,0,0))
            set_cell_background(row.cells[c_idx], "FFFFFF")

    doc.add_page_break()

    # -------------------------------------------------------------
    # 3. DEVELOPMENT METHODOLOGY (Font 13 pt, Black)
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    r = h1.add_run("3. Development Methodology")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists("extracted_media/image_0.png"):
        p.add_run().add_picture("extracted_media/image_0.png", width=Inches(5.6))
        
    p_fig = doc.add_paragraph("Figure 1. Scrum Process")
    p_fig.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fig.runs[0].font.name = "Times New Roman"
    p_fig.runs[0].font.italic = True
    p_fig.runs[0].font.size = Pt(11)
    p_fig.runs[0].font.color.rgb = RGBColor(0, 0, 0)
    
    add_body_p(doc, "Scrum is an iterative and incremental agile software development framework for managing software projects and product development. Scrum focuses on project management institutions where it is difficult to plan long-term deterministic specifications up front.")
    add_body_p(doc, "In the SFDS project, Scrum establishes empirical process control via continuous feedback loops: requirements analysis, sprint planning, feature prototyping, model calibration, and sprint retrospectives.")
    add_body_p(doc, "Benefits of the Scrum Methodology for SFDS:\n• Project responds easily to requirement changes in scam patterns and AI algorithms.\n• False alarms and accuracy bottlenecks are identified and corrected early.\n• Delivers a shippable increment of the system at the end of every sprint.\n• Maintains high productivity, transparent accountability, and a predictable schedule for graduation delivery.")

    # -------------------------------------------------------------
    # 4. SCHEDULE AND COST
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("4. Schedule and Cost")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)

    h2 = doc.add_heading(level=2)
    r = h2.add_run("4.1. Detailed Schedule")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    
    p_t5 = doc.add_paragraph("Table 5. Detailed Schedule (Mapped with Jira Issues SFDS-1 to SFDS-42)")
    p_t5.runs[0].font.name = "Times New Roman"
    p_t5.runs[0].font.bold = True
    p_t5.runs[0].font.size = Pt(11.5)
    p_t5.runs[0].font.color.rgb = RGBColor(0, 0, 0)

    schedule_data = [
        ("1", "Sprint 1: Architecture, DB Schema & Baseline Setup", "02/09/2026", "16/09/2026", "200", "42", "All Members", True),
        ("1.1", "Sprint 1 Planning & Requirements Breakdown", "02/09/2026", "02/09/2026", "16", "-", "All Members", False),
        ("1.2", "Setup Backend FastAPI Structure & Config (SFDS-1)", "03/09/2026", "08/09/2026", "36", "8", "Hao, Pham Tan", False),
        ("1.3", "Design & Implement MySQL DB Schema (SFDS-2)", "03/09/2026", "08/09/2026", "32", "8", "Hao, Pham Tan", False),
        ("1.4", "Figma Wireframe & Prototype UI/UX (SFDS-3)", "03/09/2026", "10/09/2026", "36", "8", "Nhung, Dao Thi My", False),
        ("1.5", "Survey & Dataset Collection (PhishVN, Fake Bills) (SFDS-4)", "05/09/2026", "12/09/2026", "32", "8", "Tuan, Nguyen Phan Duc", False),
        ("1.6", "Initialize Frontend Next.js/React Workspace (SFDS-5)", "06/09/2026", "13/09/2026", "24", "8", "Nam, Tran Hoang Nhat", False),
        ("1.7", "Git Repository, Branching Flow & Docs (SFDS-6, 7)", "14/09/2026", "15/09/2026", "16", "10", "Nam, Nhung", False),
        ("1.8", "Sprint 1 Review & Retrospective Meeting", "16/09/2026", "16/09/2026", "8", "-", "All Members", False),
        
        ("2", "Sprint 2: OCR Engine, PhishVN & Risk Base Engine", "17/09/2026", "01/10/2026", "200", "42", "All Members", True),
        ("2.1", "Sprint 2 Planning", "17/09/2026", "17/09/2026", "12", "-", "All Members", False),
        ("2.2", "Vietnamese OCR Integration (Tesseract vie) (SFDS-8)", "18/09/2026", "25/09/2026", "40", "8", "Tuan, Nguyen Phan Duc", False),
        ("2.3", "Integrate PhishVN Model for Suspicious URL Parsing (SFDS-9)", "18/09/2026", "26/09/2026", "36", "8", "Tuan, Nguyen Phan Duc", False),
        ("2.4", "Build Rule-based Risk Engine (Keyword matching) (SFDS-10)", "20/09/2026", "27/09/2026", "36", "8", "Hao, Pham Tan", False),
        ("2.5", "Upload UI Component & Risk Score Display (SFDS-11)", "22/09/2026", "28/09/2026", "36", "8", "Nam, Tran Hoang Nhat", False),
        ("2.6", "Admin Authentication Module (JWT + PBKDF2) (SFDS-12)", "23/09/2026", "29/09/2026", "20", "8", "Hao, Pham Tan", False),
        ("2.7", "Unit Testing for API /check-image & Swagger UI (SFDS-13, 14)", "29/09/2026", "30/09/2026", "12", "10", "Nhung, Nam", False),
        ("2.8", "Sprint 2 Review & Retrospective Meeting", "01/10/2026", "01/10/2026", "8", "-", "All Members", False),

        ("3", "Sprint 3: Visual Forensics, Explanations & Multi-input", "02/10/2026", "16/10/2026", "200", "45", "All Members", True),
        ("3.1", "Sprint 3 Planning", "02/10/2026", "02/10/2026", "12", "-", "All Members", False),
        ("3.2", "Visual Forensics: EXIF Metadata & ELA Analysis (SFDS-15)", "03/10/2026", "10/10/2026", "38", "8", "Tuan, Nguyen Phan Duc", False),
        ("3.3", "ResNet18 Image Classification Fine-Tuning (SFDS-16)", "04/10/2026", "12/10/2026", "40", "8", "Tuan, Nguyen Phan Duc", False),
        ("3.4", "Explanation Builder & Contextual Advisory Engine (SFDS-17)", "05/10/2026", "12/10/2026", "34", "8", "Hao, Pham Tan", False),
        ("3.5", "QR Code Decoding & Multi-page PDF Extraction (SFDS-18)", "06/10/2026", "13/10/2026", "30", "8", "Hao, Pham Tan", False),
        ("3.6", "Guest LocalStorage History & Result Breakdown UI (SFDS-19, 20)", "08/10/2026", "14/10/2026", "26", "13", "Nam, Tran Hoang Nhat", False),
        ("3.7", "Integration Testing: End-to-End Multi-source Scan (SFDS-21)", "14/10/2026", "15/10/2026", "12", "5", "Nhung, Dao Thi My", False),
        ("3.8", "Sprint 3 Review & Retrospective Meeting", "16/10/2026", "16/10/2026", "8", "-", "All Members", False),

        ("4", "Sprint 4: Admin Portal, Dynamic Rules & Security", "17/10/2026", "31/10/2026", "200", "42", "All Members", True),
        ("4.1", "Sprint 4 Planning", "17/10/2026", "17/10/2026", "12", "-", "All Members", False),
        ("4.2", "Admin Portal UI: Dataset & Model Checkpoints (SFDS-22)", "18/10/2026", "24/10/2026", "36", "8", "Nam, Tran Hoang Nhat", False),
        ("4.3", "Dynamic Scam Keyword & Risk Weight Management (SFDS-23)", "19/10/2026", "26/10/2026", "34", "8", "Nam, Tran Hoang Nhat", False),
        ("4.4", "OCR Bounding Box Localization on Canvas (SFDS-24)", "20/10/2026", "27/10/2026", "36", "8", "Tuan, Nguyen Phan Duc", False),
        ("4.5", "Security Hardening: File Magic Bytes & JWT Fixes (SFDS-25)", "21/10/2026", "27/10/2026", "30", "8", "Hao, Pham Tan", False),
        ("4.6", "Audit Log Storage & Report Export (CSV/Excel) (SFDS-26)", "23/10/2026", "28/10/2026", "24", "8", "Hao, Pham Tan", False),
        ("4.7", "Security Testing & Toast Notification UX (SFDS-27, 28)", "28/10/2026", "30/10/2026", "20", "10", "Nhung, Dao Thi My", False),
        ("4.8", "Sprint 4 Review & Retrospective Meeting", "31/10/2026", "31/10/2026", "8", "-", "All Members", False),

        ("5", "Sprint 5: Model Evaluation, Dockerizing & Optimization", "01/11/2026", "15/11/2026", "200", "37", "All Members", True),
        ("5.1", "Sprint 5 Planning", "01/11/2026", "01/11/2026", "12", "-", "All Members", False),
        ("5.2", "Scientific AI Evaluation: Macro-F1 & Recall (SFDS-29)", "02/11/2026", "08/11/2026", "38", "8", "Tuan, Nguyen Phan Duc", False),
        ("5.3", "OCR Accuracy Benchmark (CER & WER Testing) (SFDS-30)", "03/11/2026", "09/11/2026", "32", "8", "Tuan, Nguyen Phan Duc", False),
        ("5.4", "Threshold Calibration to Mitigate False Alarms (SFDS-31)", "05/11/2026", "11/11/2026", "34", "8", "Hao, Pham Tan", False),
        ("5.5", "Containerization: Dockerfile & Docker-Compose (SFDS-32)", "06/11/2026", "12/11/2026", "32", "8", "Hao, Pham Tan", False),
        ("5.6", "Setup Automated CI/CD with GitHub Actions (SFDS-33)", "08/11/2026", "13/11/2026", "20", "5", "Nam, Tran Hoang Nhat", False),
        ("5.7", "Stress Testing & Explanation Usefulness Survey (SFDS-34, 35)", "12/11/2026", "14/11/2026", "24", "13", "Nhung, Dao Thi My", False),
        ("5.8", "Sprint 5 Review & Retrospective Meeting", "15/11/2026", "15/11/2026", "8", "-", "All Members", False),

        ("6", "Sprint 6: User Acceptance Testing (UAT) & Staging Deploy", "16/11/2026", "01/12/2026", "200", "29", "All Members", True),
        ("6.1", "Sprint 6 Planning", "16/11/2026", "16/11/2026", "12", "-", "All Members", False),
        ("6.2", "User Acceptance Testing (UAT) Execution (SFDS-36)", "17/11/2026", "24/11/2026", "40", "8", "Nhung, Dao Thi My", False),
        ("6.3", "Cloud Deployment on AWS EC2 Staging Server (SFDS-37)", "18/11/2026", "25/11/2026", "38", "8", "Hao, Pham Tan", False),
        ("6.4", "Comprehensive Bug Fixing & UI Polish (SFDS-38)", "20/11/2026", "28/11/2026", "42", "8", "Nam, Tran Hoang Nhat", False),
        ("6.5", "User Manual & Administrator Guide Drafting (SFDS-39)", "24/11/2026", "30/11/2026", "34", "8", "Nhung, Dao Thi My", False),
        ("6.6", "Final Sprint Review & Demonstration to Mentor", "01/12/2026", "01/12/2026", "8", "-", "All Members", False),
        ("6.7", "Code Freeze & Git Tag Release v1.0 (SFDS-42)", "01/12/2026", "01/12/2026", "26", "5", "Tuan, Nguyen Phan Duc", False),

        ("7", "Final Adjustments, Capstone 1 Report & Presentation Prep", "02/12/2026", "18/12/2026", "200", "-", "All Members", True),
        ("7.1", "Complete Capstone 1 Technical Report Document (SFDS-40)", "02/12/2026", "12/12/2026", "110", "-", "All Members", False),
        ("7.2", "Prepare Presentation Slide Deck & Live Demo Script (SFDS-41)", "13/12/2026", "18/12/2026", "90", "-", "All Members", False),
        ("8", "Capstone Project Retrospective & Mock Defense", "18/12/2026", "20/12/2026", "10", "-", "All Members", True),
        ("9", "Official Final Defense & Release", "22/12/2026", "22/12/2026", "15", "-", "All Members", True)
    ]

    tbl_t5 = doc.add_table(rows=len(schedule_data) + 1, cols=7)
    set_table_borders(tbl_t5, color="000000", sz="4")
    tbl_t5.alignment = WD_TABLE_ALIGNMENT.CENTER
    t5_headers = ["No.", "Task / Sprint Name", "Start Date", "End Date", "Effort (Hrs)", "SP", "Assignee"]
    for i, h in enumerate(t5_headers):
        format_cell_text(tbl_t5.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER, color_rgb=(0,0,0))
        set_cell_background(tbl_t5.rows[0].cells[i], "E6E6E6")

    for r_idx, row_item in enumerate(schedule_data):
        no, name, start, end, effort, sp, assignee, is_hdr = row_item
        row = tbl_t5.rows[r_idx + 1]
        bg = "F0F0F0" if is_hdr else "FFFFFF"
        for c_idx, val in enumerate([no, name, start, end, effort, sp, assignee]):
            format_cell_text(row.cells[c_idx], val, bold=is_hdr, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,2,3,4,5] else WD_ALIGN_PARAGRAPH.LEFT, color_rgb=(0,0,0))
            set_cell_background(row.cells[c_idx], bg)

    # 4.2 COST PERSON/HOURS
    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(16)
    r = h2.add_run("4.2. Cost Person/Hours")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    
    p_t6 = doc.add_paragraph("Table 6. Cost of Person/Hours")
    p_t6.runs[0].font.name = "Times New Roman"
    p_t6.runs[0].font.bold = True
    p_t6.runs[0].font.size = Pt(11.5)
    p_t6.runs[0].font.color.rgb = RGBColor(0, 0, 0)
    
    tbl_t6 = doc.add_table(rows=5, cols=3)
    set_table_borders(tbl_t6, color="000000", sz="4")
    tbl_t6.alignment = WD_TABLE_ALIGNMENT.CENTER
    t6_headers = ["Member Name", "Assigned Role", "Rate (USD/hr)"]
    for i, h in enumerate(t6_headers):
        format_cell_text(tbl_t6.rows[0].cells[i], h, bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, color_rgb=(0,0,0))
        set_cell_background(tbl_t6.rows[0].cells[i], "E6E6E6")
    t6_data = [
        ("Pham Tan Hao", "Project Leader / Scrum Master", "3.00"),
        ("Dao Thi My Nhung", "QA Lead / UI-UX Designer", "3.00"),
        ("Tran Hoang Nhat Nam", "Frontend Developer", "3.00"),
        ("Nguyen Phan Duc Tuan", "AI Lead / Full-stack Developer", "3.00")
    ]
    for r_idx, d in enumerate(t6_data):
        row = tbl_t6.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx == 2 else WD_ALIGN_PARAGRAPH.LEFT, color_rgb=(0,0,0))
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # 4.3 TOTAL COST ESTIMATE
    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("4.3. Total Cost Estimate")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    
    p_t7 = doc.add_paragraph("Table 7. Total Cost Estimation")
    p_t7.runs[0].font.name = "Times New Roman"
    p_t7.runs[0].font.bold = True
    p_t7.runs[0].font.size = Pt(11.5)
    p_t7.runs[0].font.color.rgb = RGBColor(0, 0, 0)
    
    tbl_t7 = doc.add_table(rows=7, cols=5)
    set_table_borders(tbl_t7, color="000000", sz="4")
    tbl_t7.alignment = WD_TABLE_ALIGNMENT.CENTER
    t7_headers = ["No.", "Expenditure Criteria", "Calculation Basis", "Total (USD)", "Equivalent (VND)"]
    for i, h in enumerate(t7_headers):
        format_cell_text(tbl_t7.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER, color_rgb=(0,0,0))
        set_cell_background(tbl_t7.rows[0].cells[i], "E6E6E6")
    t7_data = [
        ("1", "Working Hours / Engineering Labor", "4 members x 4 hrs/day x 93 days = 1,488 hrs @ $3/hr", "4,464.00", "~111,600,000"),
        ("2", "Cloud Hosting (AWS EC2 & S3)", "AWS EC2 t3.medium + S3 storage (3 months)", "120.00", "~3,000,000"),
        ("3", "Hardware & GPU Compute", "Google Colab Pro+ / Local GPU electric costs", "80.00", "~2,000,000"),
        ("4", "Software & Tools Licenses", "Figma Pro, Domain registration, SSL certificate", "60.00", "~1,500,000"),
        ("5", "Documentation, Thesis Printing & Defense", "Thesis printing, hard cover binding, poster prints", "80.00", "~2,000,000"),
        ("", "TOTAL ESTIMATED PROJECT VALUE", "Labor + Infrastructure + Operating Costs", "$4,804.00", "~120,100,000 VND")
    ]
    for r_idx, d in enumerate(t7_data):
        row = tbl_t7.rows[r_idx + 1]
        is_tot = (r_idx == len(t7_data) - 1)
        bg = "F0F0F0" if is_tot else "FFFFFF"
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, bold=is_tot, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,3] else WD_ALIGN_PARAGRAPH.LEFT, color_rgb=(0,0,0))
            set_cell_background(row.cells[c_idx], bg)

    p_exp = doc.add_paragraph()
    p_exp.paragraph_format.space_before = Pt(8)
    r = p_exp.add_run("Explanation of Cost Formulation:\n• Total Engineering Labor = 4 members × 4 hours/day × 93 days = 1,488 hours × $3.00/hour = $4,464.00 USD.\n• Direct Out-of-Pocket Expenses (Cloud, GPU, Domain, Printing) = $340.00 USD (~8,500,000 VND), self-funded equally among team members.\n• Total Projected Value = $4,804.00 USD (~120,100,000 VND).")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.italic = True
    r.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_page_break()

    # -------------------------------------------------------------
    # 5. PROJECT RISKS & MITIGATIONS
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    r = h1.add_run("5. Project Risks & Mitigations")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)

    p_t8 = doc.add_paragraph("Table 8. Rating Criteria for Likelihood and Seriousness")
    p_t8.runs[0].font.name = "Times New Roman"
    p_t8.runs[0].font.bold = True
    p_t8.runs[0].font.size = Pt(11.5)
    p_t8.runs[0].font.color.rgb = RGBColor(0, 0, 0)
    
    tbl_t8 = doc.add_table(rows=5, cols=4)
    set_table_borders(tbl_t8, color="000000", sz="4")
    tbl_t8.alignment = WD_TABLE_ALIGNMENT.CENTER
    t8_headers = ["Code", "Likelihood (Probability)", "Code", "Seriousness (Impact)"]
    for i, h in enumerate(t8_headers):
        format_cell_text(tbl_t8.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER, color_rgb=(0,0,0))
        set_cell_background(tbl_t8.rows[0].cells[i], "E6E6E6")
    t8_data = [
        ("L", "Low: Unlikely to occur (< 20%)", "L", "Low: Minor inconvenience, negligible schedule impact"),
        ("M", "Medium: May occur during project (20% - 50%)", "M", "Medium: Requires rework, minor delay (< 1 week)"),
        ("H", "High: Very likely to occur (> 50%)", "H", "High: Critical module failure, significant delay (> 2 weeks)"),
        ("-", "Not Applicable", "E", "Extreme: Fatal project failure, unable to graduate")
    ]
    for r_idx, d in enumerate(t8_data):
        row = tbl_t8.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,2] else WD_ALIGN_PARAGRAPH.LEFT, color_rgb=(0,0,0))
            set_cell_background(row.cells[c_idx], "FFFFFF")

    p_t9 = doc.add_paragraph()
    p_t9.paragraph_format.space_before = Pt(14)
    r = p_t9.add_run("Table 9. Detailed Project Risk and Mitigation Matrix")
    r.font.name = "Times New Roman"
    r.font.bold = True
    r.font.size = Pt(11.5)
    r.font.color.rgb = RGBColor(0, 0, 0)

    tbl_t9 = doc.add_table(rows=7, cols=5)
    set_table_borders(tbl_t9, color="000000", sz="4")
    tbl_t9.alignment = WD_TABLE_ALIGNMENT.CENTER
    t9_headers = ["Risk Domain", "Risk Definition & Potential Consequence", "Level", "Likelihood", "Mitigation Strategy"]
    for i, h in enumerate(t9_headers):
        format_cell_text(tbl_t9.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER, color_rgb=(0,0,0))
        set_cell_background(tbl_t9.rows[0].cells[i], "E6E6E6")
        
    t9_data = [
        ("Vietnamese Dataset Scarcity", "Difficulty gathering authentic, high-quality labeled Vietnamese fake bank invoices and phishing screenshots due to sensitive personal data.", "H", "H", "Collect open benchmark datasets (PhishVN v3.1.0); anonymize data; generate synthetic fraudulent receipts with varied fonts using script generators."),
        ("OCR Recognition Inaccuracy", "Blurry, skewed, or low-contrast screenshots cause Tesseract OCR to misread text or omit bank account numbers and URLs.", "H", "M", "Pre-process images with OpenCV (deskewing, adaptive thresholding, bilateral noise filter); combine Tesseract with lexical fuzzy matching."),
        ("False Positives on Real Receipts", "Aggressive keyword scoring flags genuine utility bills or legitimate bank transfers, undermining user confidence.", "M", "H", "Conduct threshold calibration in Sprint 5; separate warnings into 3 levels (Safe 0-25, Suspicious 26-59, Dangerous 60-100); provide transparent explanations."),
        ("File Upload Security Exploits", "Malicious users attempt to upload executable scripts disguised as image extensions to breach server security.", "H", "M", "Validate actual magic bytes (python-magic) rather than filename extension; enforce 15MB file ceiling; isolate upload scratch directory."),
        ("Coursework & Exam Time Conflict", "Heavy semester workload and exams in November threaten sprint velocity and sprint deadlines.", "M", "H", "Maintain strict bi-daily standups; groom backlog to prioritize must-have features over nice-to-haves; allocate weekend sprint crunch time."),
        ("Cloud Infrastructure Costs", "Running AI models and continuous cloud instances exceeds student budget constraints.", "L", "M", "Perform initial development on local workstations; deploy lightweight inference models (ResNet18, HistGradientBoosting); utilize free-tier AWS and spin up EC2 solely for demo periods.")
    ]
    for r_idx, d in enumerate(t9_data):
        row = tbl_t9.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [2,3] else WD_ALIGN_PARAGRAPH.LEFT, color_rgb=(0,0,0))
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # -------------------------------------------------------------
    # 6. DELIVERABLES
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("6. Deliverables")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)

    p_t10 = doc.add_paragraph("Table 10. Deliverables Schedule")
    p_t10.runs[0].font.name = "Times New Roman"
    p_t10.runs[0].font.bold = True
    p_t10.runs[0].font.size = Pt(11.5)
    p_t10.runs[0].font.color.rgb = RGBColor(0, 0, 0)

    tbl_t10 = doc.add_table(rows=11, cols=4)
    set_table_borders(tbl_t10, color="000000", sz="4")
    tbl_t10.alignment = WD_TABLE_ALIGNMENT.CENTER
    t10_headers = ["No.", "Document / Deliverable Name", "Deadline", "File Name / Artifact"]
    for i, h in enumerate(t10_headers):
        format_cell_text(tbl_t10.rows[0].cells[i], h, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER, color_rgb=(0,0,0))
        set_cell_background(tbl_t10.rows[0].cells[i], "E6E6E6")
        
    t10_data = [
        ("1", "Proposal Document", "August 23, 2026", "C1SE.06-Proposal_SFDS_v2.0.docx"),
        ("2", "Project Plan Document", "September 02, 2026", "C1SE.06_ProjectPlan_SFDS_v1.0.docx"),
        ("3", "Software Requirements Specification (SRS)", "September 20, 2026", "C1SE.06_SRS_SFDS_v1.0.docx"),
        ("4", "Software Design Document (SDD)", "October 15, 2026", "C1SE.06_SDD_SFDS_v1.0.docx"),
        ("5", "Working Software Prototype Increment", "October 16, 2026", "Live Demo Increment on Localhost:5173"),
        ("6", "AI Benchmark & Evaluation Report", "November 15, 2026", "C1SE.06_AI_Benchmark_Report.docx"),
        ("7", "System Source Code & Docker Setup", "December 01, 2026", "GitHub Repo Tag v1.0-release"),
        ("8", "User Manual & Administrator Guide", "December 08, 2026", "C1SE.06_UserManual_SFDS_v1.0.docx"),
        ("9", "Capstone Project 1 Final Technical Report", "December 18, 2026", "C1SE.06_TechnicalReport_SFDS_Final.docx"),
        ("10", "Presentation Slides & Demo Video", "December 20, 2026", "C1SE.06_FinalPresentation.pptx + Video Demo")
    ]
    for r_idx, d in enumerate(t10_data):
        row = tbl_t10.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,2] else WD_ALIGN_PARAGRAPH.LEFT, color_rgb=(0,0,0))
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # Save documents
    for name in ["C1SE.06_ProjectPlan_SFDS_v1.2.docx", "C1SE.06_ProjectPlan_SFDS_v1.1.docx", "C1SE.06_ProjectPlan_SFDS_v1.0.docx"]:
        try:
            doc.save(name)
            print(f"Successfully saved: {name}")
        except Exception as e:
            print(f"Could not save {name} (probably locked): {e}")

if __name__ == "__main__":
    create_project_plan_docx()

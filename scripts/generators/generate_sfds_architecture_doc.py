# -*- coding: utf-8 -*-
"""
Script to generate official C1SE.06_ArchitectureDesign_SFDS_v1.0.docx
Follows DTU / CMU Capstone Software Architecture Design template.
Font: Times New Roman, Body: 13pt, Grayscale/Monochrome style.
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

def create_architecture_doc():
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
        p_hdr.text = "ARCHITECTURE DESIGN\t\tInternational School Capstone 1 – 2026"
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p_hdr.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            r.font.italic = True
            r.font.color.rgb = RGBColor(0, 0, 0)
            
        # Footer setup
        p_ftr = s.footer.paragraphs[0]
        p_ftr.text = "C1SE.06\t\tSFDS Architecture Design v1.0"
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
    p_title_doc.paragraph_format.space_before = Pt(22)
    r_title_doc = p_title_doc.add_run("Architecture Design\nVersion 1.0\nDate: September 2026")
    r_title_doc.font.name = "Times New Roman"
    r_title_doc.font.size = Pt(17)
    r_title_doc.font.bold = True
    
    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_before = Pt(18)
    p_proj.paragraph_format.space_after = Pt(22)
    r_proj = p_proj.add_run("SFDS\nFraudulent Image Detection and Warning System with Explanations")
    r_proj.font.name = "Times New Roman"
    r_proj.font.size = Pt(16)
    r_proj.font.bold = True
    
    p_created = doc.add_paragraph()
    p_created.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cr = p_created.add_run("Submitted by C1SE.06\n")
    r_cr.font.name = "Times New Roman"
    r_cr.font.size = Pt(13)
    r_cr.font.bold = True
    r_mem = p_created.add_run("Hao, Pham Tan\nNhung, Dao Thi My\nNam, Tran Hoang Nhat\nTuan, Nguyen Phan Duc\n")
    r_mem.font.name = "Times New Roman"
    r_mem.font.size = Pt(13)
    
    p_app = doc.add_paragraph()
    p_app.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_app.paragraph_format.space_before = Pt(14)
    r_app = p_app.add_run("Approved by\nEng. Toan, Ha Manh\n")
    r_app.font.name = "Times New Roman"
    r_app.font.size = Pt(13)
    r_app.font.bold = True
    
    p_rep = doc.add_paragraph()
    p_rep.paragraph_format.space_before = Pt(24)
    r_rep = p_rep.add_run("Architecture Design Review Panel Representative:\nName: ______________________    Signature: ________________    Date: ________\n\nCapstone Project 1 - Mentor:\nName: Eng. Toan, Ha Manh        Signature: ________________    Date: ________")
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
        ("Project Title", "SFDS - Fraudulent Image Detection and Warning System with Explanations", "", ""),
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

    # DOCUMENT APPROVALS
    p_app_h = doc.add_paragraph()
    p_app_h.paragraph_format.space_before = Pt(18)
    r = p_app_h.add_run("DOCUMENT APPROVALS")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    p_app_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p_req = doc.add_paragraph("The following signatures are required for approval of this architectural document:")
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

    # REVISION HISTORY
    p_rev_h = doc.add_paragraph()
    p_rev_h.paragraph_format.space_before = Pt(16)
    r = p_rev_h.add_run("REVISION HISTORY")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True
    
    tbl_rev = doc.add_table(rows=2, cols=5)
    set_table_borders(tbl_rev, color="000000", sz="4")
    tbl_rev.alignment = WD_TABLE_ALIGNMENT.CENTER
    rev_headers = ["Version", "Date", "Comments", "Author", "Approval"]
    for i, h in enumerate(rev_headers):
        format_cell_text(tbl_rev.rows[0].cells[i], h, bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_rev.rows[0].cells[i], "E6E6E6")
    
    rev_vals = ["1.0", "15/10/2026", "Initial Architecture Design Document Release", "Hao, Pham Tan", "Eng. Toan, Ha Manh"]
    for i, val in enumerate(rev_vals):
        format_cell_text(tbl_rev.rows[1].cells[i], val, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER if i in [0,1,3,4] else WD_ALIGN_PARAGRAPH.LEFT)
        set_cell_background(tbl_rev.rows[1].cells[i], "FFFFFF")

    doc.add_page_break()

    # -------------------------------------------------------------
    # TABLE OF CONTENTS
    # -------------------------------------------------------------
    p_toc_h = doc.add_paragraph()
    r = p_toc_h.add_run("TABLE OF CONTENTS")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    p_toc_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    toc_items = [
        ("1. Introduction", "4"),
        ("   1.1. Purpose", "4"),
        ("   1.2. Document Reference", "4"),
        ("2. Project Reference", "4"),
        ("   2.1. Project Overview", "4"),
        ("   2.2. Business Driver", "5"),
        ("      2.2.1. Project Background and Motivation", "5"),
        ("      2.2.2. Proposed Solution", "5"),
        ("      2.2.3. Project Goals", "6"),
        ("      2.2.4. Key Features", "6"),
        ("3. Architecture Drivers", "7"),
        ("   3.1. High-level Requirements", "7"),
        ("   3.2. Architecture Driver Specification", "8"),
        ("      3.2.1. Use Case Entities", "8"),
        ("      3.2.2. Operational Use Cases (UC-01 to UC-08)", "10"),
        ("   3.3. Quality Attributes (QA01 to QA05 Scenarios)", "15"),
        ("4. Constraints", "17"),
        ("   4.1. Business Constraints", "17"),
        ("   4.2. Technical Constraints", "18"),
        ("5. Diagrams & Architectural Views", "19"),
        ("   5.1. Component and Connector View (C&C View)", "19"),
        ("      5.1.1. C&C View of Client", "19"),
        ("      5.1.2. C&C View of Server & Analytical Pipeline", "22"),
        ("   5.2. Module View", "25"),
        ("      5.2.1. Module View of Client", "25"),
        ("      5.2.2. Module View of Server", "27"),
        ("   5.3. Allocation View (Deployment & Process Mapping)", "29"),
        ("6. References", "32")
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
    # 1. INTRODUCTION
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    r = h1.add_run("1. Introduction")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("1.1. Purpose")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "This document establishes the official Architectural Design for the SFDS (Scam Fraud Detection System with Explanations) platform. It provides a formal, structured blueprint capturing the high-level system structures, architectural drivers, quality attribute utility trees, operational use cases, and multiple architectural views conforming to the SEI/CMU Software Architecture standard (Bass, Clements, & Kazman).")
    add_body_p(doc, "The target audience includes academic evaluators, project mentors, software architects, and full-stack developers. It guides ongoing implementation, ensuring that the multimodal AI pipeline, asynchronous API gateway, and privacy-preserving client interface operate cohesively.")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(12)
    r = h2.add_run("1.2. Document Reference")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    p_t1 = doc.add_paragraph("Table 1. Document References")
    p_t1.runs[0].font.name = "Times New Roman"
    p_t1.runs[0].font.bold = True
    p_t1.runs[0].font.size = Pt(11.5)

    tbl_t1 = doc.add_table(rows=4, cols=3)
    set_table_borders(tbl_t1, color="000000", sz="4")
    tbl_t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    t1_headers = ["No.", "Document Code", "Document Title & Scope"]
    for i, h in enumerate(t1_headers):
        format_cell_text(tbl_t1.rows[0].cells[i], h, bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t1.rows[0].cells[i], "E6E6E6")

    docs_ref = [
        ("1", "C1SE.06-Proposal_SFDS_v2.1.docx", "Project Proposal: Problem Statement, Scope, Objectives & Survey"),
        ("2", "C1SE.06_ProjectPlan_SFDS_v1.0.docx", "Project Management Plan: 6 Sprints, Jira WBS (SFDS-1..42), Budget & Risks"),
        ("3", "C1SE.06_SRS_SFDS_v1.0.docx", "Software Requirements Specification: Functional & Non-Functional Requirements")
    ]
    for r_idx, d in enumerate(docs_ref):
        row = tbl_t1.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0,1] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    # -------------------------------------------------------------
    # 2. PROJECT REFERENCE
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    p = h1.paragraph_format
    p.space_before = Pt(16)
    r = h1.add_run("2. Project Reference")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("2.1. Project Overview")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "SFDS is an intelligent, explainable cybersecurity platform engineered to detect and analyze visual and textual fraud in Vietnamese cyberspace. Designed with a privacy-first philosophy, SFDS allows regular citizens to inspect digital content without mandatory account creation while providing an enterprise-grade administrative portal for threat intelligence governance.")

    p_t2 = doc.add_paragraph("Table 2. Development Team Organization")
    p_t2.runs[0].font.name = "Times New Roman"
    p_t2.runs[0].font.bold = True
    p_t2.runs[0].font.size = Pt(11.5)

    tbl_t2 = doc.add_table(rows=5, cols=3)
    set_table_borders(tbl_t2, color="000000", sz="4")
    tbl_t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    t2_headers = ["Member Name", "Project Role", "Architectural Ownership & Responsibilities"]
    for i, h in enumerate(t2_headers):
        format_cell_text(tbl_t2.rows[0].cells[i], h, bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t2.rows[0].cells[i], "E6E6E6")

    team_roles = [
        ("Hao, Pham Tan", "Project Leader / Scrum Master", "Backend Core Ownership (FastAPI, JWT Auth, Docker, Consensus Fusion Logic)."),
        ("Nhung, Dao Thi My", "QA Lead / UI-UX Designer", "Quality Assurance, UI/UX Wireframes, Test Case Design, UAT, Documentation."),
        ("Nam, Tran Hoang Nhat", "Frontend Developer", "Frontend Ownership (React 18, Vite, Canvas Bounding Box, LocalStorage Engine)."),
        ("Tuan, Nguyen Phan Duc", "AI Lead / Full-stack Developer", "AI Pipeline Ownership (Tesseract OCR, PhishVN URL Model, ResNet-18, ELA).")
    ]
    for r_idx, d in enumerate(team_roles):
        row = tbl_t2.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("2.2. Business Driver")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True

    add_body_p(doc, "2.2.1. Project Background and Motivation:\nDigital financial fraud via image artifacts has grown exponentially in Vietnam. Scammers frequently synthesize fraudulent bank transfer confirmations (fake payment bills), forge judicial summonses or police warrants, and distribute phishing QR codes. Everyday consumers lack digital forensics tools, and traditional antivirus or browser shields only verify plain domain names without interpreting images or localized Vietnamese text.")
    add_body_p(doc, "2.2.2. Proposed Solution:\nSFDS provides a comprehensive, multi-source visual scanner. By ingesting an image, PDF, or text snippet, SFDS extracts Vietnamese text, parses QR targets, analyzes 21 lexical features of embedded URLs (PhishVN), performs JPEG Error Level Analysis (ELA), and evaluates visual layout similarity (ResNet-18). The core Multimodal Chain-of-Thought (CoT) Reasoning Engine combines these signals into a calibrated risk score (0-100) with intuitive visual evidence.")
    add_body_p(doc, "2.2.3. Project Goals:\n• Provide automated, instant fraud risk scoring (< 3.0s latency) with high precision.\n• Deconstruct threat reasons into human-readable evidence (Text semantics, URL threat, Image manipulation traces).\n• Guarantee end-user privacy through zero-PII guest inspection and localized browser caching.\n• Deliver modular AI pipelines capable of hot-swapping deep learning checkpoints without disrupting web service availability.")
    add_body_p(doc, "2.2.4. Key Features:\n• Multi-source Ingestion: Images (JPG/PNG/WEBP/BMP), embedded QR decoding, raw text paste (up to 20,000 chars), PDF documents (up to 10 pages), and direct URLs.\n• Explainable AI (XAI) Console: Calibrated risk gauge (Safe 0-25, Suspicious 26-59, Dangerous 60-100), highlighted bounding boxes, and component score breakdown.\n• Interactive Safety Assistant: Conversational remediation module advising users on next steps (e.g. reporting to bank, securing credentials).\n• Administrative Portal: RBAC-governed dashboard for dataset curation, model checkpoint inspection, evaluation metrics, and audit logs.")

    doc.add_page_break()

    # -------------------------------------------------------------
    # 3. ARCHITECTURE DRIVERS
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    r = h1.add_run("3. Architecture Drivers")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("3.1. High-level Requirements")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "The architectural design is driven by key stakeholders and operational capabilities:")
    add_body_p(doc, "• End User (Guest):\n  - Multi-source scanning (Image, Text, URL, PDF, QR)\n  - Real-time risk scoring and visual bounding box highlighting\n  - Interactive Safety Assistant Q&A\n  - Local inspection history retrieval (up to 50 items)")
    add_body_p(doc, "• Administrator:\n  - Secure JWT authentication and session management\n  - AI training dataset management and export\n  - Model checkpoint monitoring and evaluation metrics review\n  - System security and audit trail logging")
    add_body_p(doc, "• External / Subsystem Drivers:\n  - Tesseract OCR Vietnamese text recognition (vie)\n  - PhishVN lexical URL classifier (21 features)\n  - ResNet-18 visual layout classifier\n  - OpenCV forensic engine (ELA & EXIF metadata)")

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists("arch_diagrams/fig1_system_context.png"):
        p.add_run().add_picture("arch_diagrams/fig1_system_context.png", width=Inches(6.0))
        
    p_fig1 = doc.add_paragraph("Figure 1. System Context Diagram")
    p_fig1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fig1.runs[0].font.name = "Times New Roman"
    p_fig1.runs[0].font.italic = True
    p_fig1.runs[0].font.size = Pt(11)

    # 3.2 USE CASE ENTITIES
    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("3.2. Architecture Driver Specification")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    h3 = doc.add_heading(level=3)
    r = h3.add_run("3.2.1. Use Case Entities")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True

    entity_tables = [
        ("Table 3. Entity 1: Multi-source Media Input", [
            ("ID", "E01"),
            ("Title", "Input Media Sensor / Stream"),
            ("Description", "Digital media artifacts uploaded by users (Image files, PDF documents, QR snapshots, raw text)."),
            ("Provides Assumptions", "Transmits raw binary files or UTF-8 text strings to the API gateway."),
            ("Requires Assumptions", "Files must comply with supported formats (JPG, PNG, WEBP, PDF) and 15MB size ceiling."),
            ("Identified Use Cases", "Captures and transmits file payloads to the Backend API for ingestion.")
        ]),
        ("Table 4. Entity 2: AI & Analytical Processing Layer", [
            ("ID", "E02"),
            ("Title", "AI Inference & Forensics Engine"),
            ("Description", "Subsystem comprising Tesseract OCR, PhishVN classifier, ResNet-18, and OpenCV ELA worker."),
            ("Provides Assumptions", "Processes raw media into structured analytical metadata (text, bounding boxes, probabilities)."),
            ("Requires Assumptions", "Pre-trained checkpoints (ResNet-18 pt, PhishVN joblib, Tesseract traineddata) must be loaded."),
            ("Identified Use Cases", "Extracts text, predicts phishing risk, detects image tampering, and delivers signals to CoT engine.")
        ]),
        ("Table 5. Entity 3: End User (Guest)", [
            ("ID", "E03"),
            ("Title", "End User / Public Citizen"),
            ("Description", "Primary consumer operating the web application to verify suspicious digital materials."),
            ("Provides Assumptions", "Submits unverified images or messages for security inspection."),
            ("Requires Assumptions", "Receives rapid, clear, and actionable explanation reports without login barriers."),
            ("Identified Use Cases", "Upload Media, View Risk Score, Inspect Bounding Boxes, Interact with Safety Assistant.")
        ]),
        ("Table 6. Entity 4: System Administrator", [
            ("ID", "E04"),
            ("Title", "System Administrator"),
            ("Description", "Privileged actor managing AI models, training datasets, and system configuration."),
            ("Provides Assumptions", "Holds authorized administrative credentials verified by PBKDF2 and JWT tokens."),
            ("Requires Assumptions", "Backend provides administrative REST endpoints for governance and auditing."),
            ("Identified Use Cases", "Login/Logout, Manage Datasets, Review Model Evaluations, Inspect System Audit Logs.")
        ]),
        ("Table 7. Entity 5: Backend Application Server", [
            ("ID", "E05"),
            ("Title", "FastAPI Core Application Server"),
            ("Description", "Central coordination engine orchestrating requests, AI pipeline execution, and data persistence."),
            ("Provides Assumptions", "Provides secure, asynchronous RESTful API endpoints and executes CoT reasoning."),
            ("Requires Assumptions", "Persistent database (SQLite/MySQL) and local scratch file system are accessible."),
            ("Identified Use Cases", "Execute Ingestion, Run Soft Consensus Fusion, Build Explanations, Persist Audit Logs.")
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

    # 3.2.2 OPERATIONAL USE CASES
    h3 = doc.add_heading(level=3)
    r = h3.add_run("3.2.2. Operational Use Cases")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True

    op_use_cases = [
        ("Table 8. Use Case 1: Multi-source Media Ingestion & Preprocessing", [
            ("ID", "UC-01"),
            ("Title", "Multi-source Media Ingestion & Preprocessing"),
            ("Description", "The system receives diverse user media (image, PDF, raw text), validates file magic bytes, and prepares memory buffers."),
            ("Entities Involved", "Actors: End User; Systems: FastAPI Gateway, MagicByteValidator, Temp Storage."),
            ("Preconditions", "1. User has navigated to Scan page. 2. File size is below 15MB."),
            ("Primary Flow", "1. User uploads image/PDF or pastes text.\n2. Gateway validates MIME magic bytes (python-magic).\n3. Valid files are buffered in isolated scratch storage.\n4. Router dispatches tasks to OCR and Forensics pipelines."),
            ("Postconditions", "Sanitized media payload is prepared for downstream analytical inference."),
            ("Alternate Flows", "1. Unsupported extension or fake MIME type: Return 400 Bad Request.\n2. Exceeds 15MB: Return 413 Payload Too Large.")
        ]),
        ("Table 9. Use Case 2: Vietnamese OCR & QR Code Decoding", [
            ("ID", "UC-02"),
            ("Title", "Vietnamese OCR & QR Code Decoding"),
            ("Description", "Extracts accented Vietnamese textual content and bounding coordinates, and decodes payment/URL QR codes."),
            ("Entities Involved", "Systems: Tesseract OCR Engine (vie), Pillow, Pyzbar QR Decoder."),
            ("Preconditions", "Preprocessed image buffer is available in memory."),
            ("Primary Flow", "1. Pillow normalizes color channels and contrast.\n2. Pyzbar scans for 2D barcode / QR matrices.\n3. Tesseract executes OCR extraction with vie+eng language models.\n4. System extracts word bounding boxes and raw string contents."),
            ("Postconditions", "Text string and decoded QR links are forwarded to Risk Engine and PhishVN."),
            ("Alternate Flows", "1. Unreadable/blurry text: Output empty text string, flag low-contrast warning.")
        ]),
        ("Table 10. Use Case 3: PhishVN Lexical URL Risk Analysis", [
            ("ID", "UC-03"),
            ("Title", "PhishVN Lexical URL Risk Analysis"),
            ("Description", "Extracts embedded URLs from OCR text or decoded QR codes and computes phishing probability based on 21 lexical features."),
            ("Entities Involved", "Systems: URL Extractor, PhishVN Feature Extractor, HistGradientBoosting Model."),
            ("Preconditions", "Extracted text or QR codes contain one or more URL strings."),
            ("Primary Flow", "1. Regex parses URL strings from OCR output.\n2. Extracts 21 lexical features (length, subdomains, entropy, special chars).\n3. HistGradientBoosting model predicts phishing probability.\n4. Normalizes URL threat score (0-100) and marks suspicious tokens."),
            ("Postconditions", "URL threat score and feature breakdown are attached to analysis context."),
            ("Alternate Flows", "1. No URLs detected: Set URL risk score to 0 and mark model unavailable.")
        ]),
        ("Table 11. Use Case 4: Visual Tampering & ELA Forensics", [
            ("ID", "UC-04"),
            ("Title", "Visual Tampering & ELA Forensics"),
            ("Description", "Applies Error Level Analysis (ELA) to detect JPEG resaving discrepancies and inspects camera metadata."),
            ("Entities Involved", "Systems: OpenCV ELA Analyzer, Pillow EXIF Reader, ResNet-18 Model."),
            ("Preconditions", "Input media is a JPEG/PNG image."),
            ("Primary Flow", "1. Generates resaved reference image at 90% JPEG quality.\n2. Computes pixel difference matrix to highlight inconsistent compression.\n3. Reads EXIF metadata tags to verify editing software signatures.\n4. ResNet-18 infers layout probability with calibrated temperature (T=1.8)."),
            ("Postconditions", "Visual forensic score and anomaly flags are added to context."),
            ("Alternate Flows", "1. Image format lacks EXIF: Log missing EXIF flag without penalizing score.")
        ]),
        ("Table 12. Use Case 5: Multimodal Soft Consensus Fusion", [
            ("ID", "UC-05"),
            ("Title", "Multimodal Soft Consensus Fusion"),
            ("Description", "Synthesizes multi-source signals (text keywords, PhishVN, visual forensics, ResNet-18) via weighted soft voting."),
            ("Entities Involved", "Systems: Multimodal CoT Reasoning Engine, Rule-based Risk Engine."),
            ("Preconditions", "All individual analytical modules have returned their respective signal scores."),
            ("Primary Flow", "1. Domain Gating checks for everyday photo / source code patterns.\n2. Identifies primary threat signals (Text, URL, CoT) and secondary signals (ELA, ResNet).\n3. Computes weighted consensus score (0-100) preventing uncalibrated extremes.\n4. Maps score to safety tiers: Safe (0-25), Suspicious (26-59), Dangerous (60-100)."),
            ("Postconditions", "Final calibrated risk score and level are generated for client delivery."),
            ("Alternate Flows", "1. Domain Gating confirms benign everyday photo: Force safe score (<=15).")
        ]),
        ("Table 13. Use Case 6: Interactive Safety Guidance & Remediation", [
            ("ID", "UC-06"),
            ("Title", "Interactive Safety Guidance & Remediation"),
            ("Description", "Generates context-aware security advice and provides interactive conversational assistance for victims."),
            ("Entities Involved", "Actors: End User; Systems: SafetyAssistant, ExplanationBuilder."),
            ("Preconditions", "Scan result and threat indicators have been calculated."),
            ("Primary Flow", "1. ExplanationBuilder synthesizes top threat signals into plain Vietnamese copy.\n2. Formulates 3 actionable immediate countermeasures.\n3. User clicks quick questions or enters customized remediation query.\n4. SafetyAssistant answers query based strictly on current scan context."),
            ("Postconditions", "User receives actionable advice to prevent financial or identity loss."),
            ("Alternate Flows", "1. User submits off-topic query: Assistant redirects to fraud remediation.")
        ]),
        ("Table 14. Use Case 7: Privacy-first Guest History Management", [
            ("ID", "UC-07"),
            ("Title", "Privacy-first Guest History Management"),
            ("Description", "Stores inspection records locally on the user's web browser without requiring account creation."),
            ("Entities Involved", "Actors: End User; Systems: React Client, HTML5 localStorage."),
            ("Preconditions", "Scan response is returned from backend."),
            ("Primary Flow", "1. React client serializes inspection summary into JSON.\n2. Stores record in browser localStorage under dedicated key.\n3. Maintains FIFO cap of 50 recent inspection reports.\n4. User navigates to History tab to review past scans or clear history."),
            ("Postconditions", "Inspection history is preserved locally on device; server stores zero guest PII."),
            ("Alternate Flows", "1. LocalStorage quota exceeded: Automatically purge oldest records.")
        ]),
        ("Table 15. Use Case 8: Administrative Model & Dataset Governance", [
            ("ID", "UC-08"),
            ("Title", "Administrative Model & Dataset Governance"),
            ("Description", "Allows authenticated administrators to manage AI datasets, inspect model evaluations, and audit logs."),
            ("Entities Involved", "Actors: Administrator; Systems: FastAPI Admin Endpoints, SQLAlchemy, MySQL."),
            ("Preconditions", "Administrator has successfully authenticated via /login (JWT Bearer Token)."),
            ("Primary Flow", "1. Admin submits credentials to /login endpoint.\n2. Server verifies PBKDF2 hash and issues signed JWT.\n3. Admin accesses /training-dataset, /model-evaluations, and /system-logs.\n4. Updates dynamic scam keyword weights and exports audit reports."),
            ("Postconditions", "System configurations and audit logs are safely updated in persistent database."),
            ("Alternate Flows", "1. Expired/Invalid token: Return 401 Unauthorized and redirect to login.")
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

    # 3.3 QUALITY ATTRIBUTES
    h2 = doc.add_heading(level=2)
    r = h2.add_run("3.3. Quality Attributes")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "Quality attributes are specified using standardized SEI concrete scenarios consisting of six parts: Stimulus, Source, Environment, Artifact, Response, and Response Measure.")

    qa_scenarios = [
        ("Table 16. Quality Attribute 1: Performance / Latency (QA01)", [
            ("ID", "QA01"),
            ("Quality Attribute", "Performance (Latency & Throughput)"),
            ("Stimulus", "End user uploads a multi-source artifact (3MB image with Vietnamese text, QR code, and URL)."),
            ("Source of Stimulus", "End User Web Client."),
            ("Environment", "System under normal concurrent load (10-20 concurrent requests)."),
            ("Artifact Stimulated", "FastAPI Router, Tesseract OCR, PhishVN, ResNet-18."),
            ("Response", "Server parses image, decodes QR, runs model inference, builds explanation, and returns JSON payload."),
            ("Response Measure", "End-to-end response latency is strictly under 3.0 seconds (P95 latency < 2.5s).")
        ]),
        ("Table 17. Quality Attribute 2: Security & Privacy / Zero-PII (QA02)", [
            ("ID", "QA02"),
            ("Quality Attribute", "Security & Data Privacy"),
            ("Stimulus", "A user uploads an image containing confidential banking account numbers or personal invoices."),
            ("Source of Stimulus", "Public End User."),
            ("Environment", "Normal operational guest scan mode."),
            ("Artifact Stimulated", "File Upload Sandbox, MySQL Database, LocalStorage."),
            ("Response", "System processes image in temporary memory, scrubs personal identifiers, and preserves zero guest PII on server."),
            ("Response Measure", "100% of guest images are deleted from server scratch space after inference; 0 PII stored in MySQL.")
        ]),
        ("Table 18. Quality Attribute 3: Modularity & Hot-Swapping (QA03)", [
            ("ID", "QA03"),
            ("Quality Attribute", "Modularity & Extensibility"),
            ("Stimulus", "Engineering team upgrades the image classifier from ResNet-18 to a vision-language model (e.g., Qwen2.5-VL)."),
            ("Source of Stimulus", "AI Development Team."),
            ("Environment", "Staging development and maintenance phase."),
            ("Artifact Stimulated", "vlm_image_analyzer.py, reasoning_engine.py."),
            ("Response", "Developer updates the model checkpoint path or switches environment variable USE_VLM_ANALYZER=true without rewriting REST APIs."),
            ("Response Measure", "Integration takes <= 4 developer-hours with zero breaking changes to frontend client contract.")
        ]),
        ("Table 19. Quality Attribute 4: Maintainability (QA04)", [
            ("ID", "QA04"),
            ("Quality Attribute", "Maintainability & Code Health"),
            ("Stimulus", "A false-positive keyword or miscalibrated risk weight is identified in the rule-based risk engine."),
            ("Source of Stimulus", "QA Team / User Feedback."),
            ("Environment", "Operational production environment."),
            ("Artifact Stimulated", "risk_engine.py / Dynamic Admin Keywords Table."),
            ("Response", "Administrator updates keyword weight dynamically on Admin Portal or developer adjusts dictionary in code."),
            ("Response Measure", "Time to deploy fix is under 2 hours; automated test suite (pytest) executes within 15 seconds.")
        ]),
        ("Table 20. Quality Attribute 5: Availability & Fault Tolerance (QA05)", [
            ("ID", "QA05"),
            ("Quality Attribute", "Availability & Resilience"),
            ("Stimulus", "External dependency failure (e.g. MySQL service temporarily restarts, or OCR fails on corrupt file)."),
            ("Source of Stimulus", "Internal system fault or malformed payload."),
            ("Environment", "Runtime production execution."),
            ("Artifact Stimulated", "Database Connection Pool, API Error Handlers."),
            ("Response", "FastAPI catches exception gracefully, falls back to SQLite/cached baseline, and returns structured user-friendly message."),
            ("Response Measure", "System uptime >= 99.0%; no unhandled 500 server crash; client receives actionable error toast.")
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

    # -------------------------------------------------------------
    # 4. CONSTRAINTS
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    r = h1.add_run("4. Constraints")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("4.1. Business Constraints")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    p_t21 = doc.add_paragraph("Table 21. Business Constraints Matrix")
    p_t21.runs[0].font.name = "Times New Roman"
    p_t21.runs[0].font.bold = True
    p_t21.runs[0].font.size = Pt(11.5)

    tbl_t21 = doc.add_table(rows=5, cols=3)
    set_table_borders(tbl_t21, color="000000", sz="4")
    tbl_t21.alignment = WD_TABLE_ALIGNMENT.CENTER
    t21_headers = ["Constraint Domain", "Constraint Description", "Guidelines for Acceptance"]
    for i, h in enumerate(t21_headers):
        format_cell_text(tbl_t21.rows[0].cells[i], h, bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(tbl_t21.rows[0].cells[i], "E6E6E6")

    biz_constraints = [
        ("Economic Budget", "Student research grant with budget cap under $350 USD for hosting and compute.", "Utilize local workstations for training; deploy on free-tier AWS EC2 and open-source libraries."),
        ("Environmental / Input", "OCR and model accuracy depend on user image resolution and lighting contrast.", "Implement OpenCV preprocessing (deskewing, adaptive thresholding) to handle low-quality photos."),
        ("Ethical & Privacy", "Handling potentially sensitive banking screenshots and personal chat logs.", "Anonymize all benchmark data; enforce zero-server-storage for guest inspection images."),
        ("Social & Public Adoption", "Non-technical citizens must easily understand danger levels without confusion.", "Implement traffic-light visual indicators (Green/Yellow/Red) and plain Vietnamese explanations.")
    ]
    for r_idx, d in enumerate(biz_constraints):
        row = tbl_t21.rows[r_idx + 1]
        for c_idx, val in enumerate(d):
            format_cell_text(row.cells[c_idx], val, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(row.cells[c_idx], "FFFFFF")

    h2 = doc.add_heading(level=2)
    p = h2.paragraph_format
    p.space_before = Pt(14)
    r = h2.add_run("4.2. Technical Constraints")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True
    
    add_body_p(doc, "• Programming Languages: Python 3.12 (Backend & AI Pipelines), JavaScript ECMAScript 2022 (Frontend).\n• Web Frameworks: FastAPI 0.110+ (Uvicorn ASGI server), React 18 with Vite bundling.\n• AI / Machine Learning: PyTorch 2.4, Scikit-Learn 1.5, Tesseract OCR 5.3 (vie+eng traineddata), OpenCV-Python 4.10, Pillow 10.4.\n• Persistence & Database: SQLAlchemy 2.0 ORM, SQLite (local development / testing), MySQL 8.0 (production).\n• Security & Auth: python-jose (JWT Bearer Token), passlib (PBKDF2-HMAC-SHA256 password hashing), python-magic.\n• Infrastructure: Docker, Docker Compose, Git / GitHub Actions CI/CD.")

    doc.add_page_break()

    # -------------------------------------------------------------
    # 5. DIAGRAMS & ARCHITECTURAL VIEWS
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    r = h1.add_run("5. Diagrams & Architectural Views")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    h2 = doc.add_heading(level=2)
    r = h2.add_run("5.1. Component and Connector View (C&C View)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True

    h3 = doc.add_heading(level=3)
    r = h3.add_run("5.1.1. C&C View of Client")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists("arch_diagrams/fig2_cc_client.png"):
        p.add_run().add_picture("arch_diagrams/fig2_cc_client.png", width=Inches(5.5))
        
    p_fig2 = doc.add_paragraph("Figure 2. Component & Connector (C&C) View of Client")
    p_fig2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fig2.runs[0].font.name = "Times New Roman"
    p_fig2.runs[0].font.italic = True
    p_fig2.runs[0].font.size = Pt(11)

    add_body_p(doc, "Prose:\nThe Client architecture is implemented as a single-page application (SPA) in React 18. Users interact through Page Containers (e.g. ScanPage, AdminPage, HistoryPage), which aggregate specialized UI Components (UploadDropzone, CanvasHighlight, SafetyAssistantWidget). Client State Services (useAppController, localStorageManager) encapsulate API communication via Axios and synchronize inspection history to browser storage. Structured JSON responses from the FastAPI backend are rendered dynamically into risk gauges, visual bounding boxes, and explanation cards.")
    add_body_p(doc, "Roles and Responsibilities:\n• End User: Submits media, views risk levels, inspects highlighted bounding boxes, and asks remediation questions.\n• Page Containers (React): Orchestrates view hierarchy, coordinates UI components, and delegates asynchronous API calls.\n• UI Components: Reusable visualization elements (drag-and-drop dropzone, canvas coordinate overlay, score meter).\n• Services & Hooks: Encapsulates REST API calls, manages JWT authorization headers, and manages localStorage persistence.\n• Backend Server: Receives multipart media requests and responds with structured risk assessment JSON payloads.")

    h3 = doc.add_heading(level=3)
    p = h3.paragraph_format
    p.space_before = Pt(14)
    r = h3.add_run("5.1.2. C&C View of Server & Analytical Pipeline")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists("arch_diagrams/fig3_cc_server.png"):
        p.add_run().add_picture("arch_diagrams/fig3_cc_server.png", width=Inches(6.0))
        
    p_fig3 = doc.add_paragraph("Figure 3. Component & Connector (C&C) View of Server")
    p_fig3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fig3.runs[0].font.name = "Times New Roman"
    p_fig3.runs[0].font.italic = True
    p_fig3.runs[0].font.size = Pt(11)

    add_body_p(doc, "Prose:\nThe Server leverages FastAPI's asynchronous ASGI framework to achieve high throughput and low latency. Incoming requests pass through security middleware (magic byte validation, CORS, JWT authentication). The Multimodal CoT Reasoning Engine coordinates inference across four specialized sub-engines: Tesseract OCR (text extraction), PhishVN (21 lexical URL features), ResNet-18 (visual layout classifier with temperature calibration T=1.8), and OpenCV (Error Level Analysis). The Soft Consensus Fusion module synthesizes these signals into a calibrated risk score, while ExplanationBuilder and SafetyAssistant generate conversational remediation guidance.")
    add_body_p(doc, "Roles and Responsibilities:\n• API Request Router: Validates HTTP inputs, enforces rate limits, verifies file bytes, and dispatches requests.\n• Multimodal CoT Reasoning Engine: Executes domain gating and synthesizes multi-source evidence into structured explanations.\n• AI Inference Pipelines: Dedicated workers executing Tesseract C-bindings, Scikit-learn HistGB inference, and PyTorch forward passes.\n• Application Services: Business logic layers handling safety recommendations, audit logging, and dataset queries.\n• Database Engine: SQLAlchemy ORM layer interacting with SQLite (local development) and MySQL 8.0 (production).")

    doc.add_page_break()

    # 5.2 MODULE VIEW
    h2 = doc.add_heading(level=2)
    r = h2.add_run("5.2. Module View")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True

    h3 = doc.add_heading(level=3)
    r = h3.add_run("5.2.1. Module View of Client")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists("arch_diagrams/fig4_module_client.png"):
        p.add_run().add_picture("arch_diagrams/fig4_module_client.png", width=Inches(5.8))
        
    p_fig4 = doc.add_paragraph("Figure 4. Module View of Client")
    p_fig4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fig4.runs[0].font.name = "Times New Roman"
    p_fig4.runs[0].font.italic = True
    p_fig4.runs[0].font.size = Pt(11)

    add_body_p(doc, "Prose & Module Layering:\nThe Client module structure enforces strict separation of concerns across three distinct layers:\n1. Page View Modules: Root view controllers (ScanPage, HistoryPage, AdminPage, AuthPage, OverviewPage) mapped to application routes.\n2. Reusable Component Modules: Stateless presentation units (UploadDropzone, CanvasBoundingBox, ScoreMeterBar, SafetyAssistantWidget, TechnicalBreakdown) focused exclusively on rendering and local UI interactions.\n3. State & Service Modules: Custom React hooks (useAppController) and utility modules (localStorageManager, apiClient) encapsulating network I/O, error handling, and browser cache serialization.")

    h3 = doc.add_heading(level=3)
    p = h3.paragraph_format
    p.space_before = Pt(14)
    r = h3.add_run("5.2.2. Module View of Server")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists("arch_diagrams/fig5_module_server.png"):
        p.add_run().add_picture("arch_diagrams/fig5_module_server.png", width=Inches(6.0))
        
    p_fig5 = doc.add_paragraph("Figure 5. Module View of Server")
    p_fig5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fig5.runs[0].font.name = "Times New Roman"
    p_fig5.runs[0].font.italic = True
    p_fig5.runs[0].font.size = Pt(11)

    add_body_p(doc, "Prose & Module Layering:\nThe Server codebase is organized into four clean architectural tiers:\n1. API Routing & Middleware Layer (backend/app/main.py): FastAPI application routing, JWT security verification, and magic byte validation.\n2. Analytical & Machine Learning Layer (backend/app/ai/, backend/app/ocr/, backend/app/visual/): Independent inference modules (tesseract ocr_service, phishvn_url_model, phishing_model ResNet-18, visual_forensics ELA/EXIF).\n3. Reasoning & Business Logic Layer (backend/app/risk/): Reasoning orchestration (reasoning_engine, risk_engine, explanation_builder, safety_assistant).\n4. Data Persistence Layer (backend/app/db/): SQLAlchemy database connection engine (database.py), ORM entity definitions (models.py), and relational schema DDL (schema.sql).")

    doc.add_page_break()

    # 5.3 ALLOCATION VIEW
    h2 = doc.add_heading(level=2)
    r = h2.add_run("5.3. Allocation View (Deployment & Process Mapping)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.5)
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists("arch_diagrams/fig6_allocation_view.png"):
        p.add_run().add_picture("arch_diagrams/fig6_allocation_view.png", width=Inches(5.8))
        
    p_fig6 = doc.add_paragraph("Figure 6. Allocation / Deployment View")
    p_fig6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fig6.runs[0].font.name = "Times New Roman"
    p_fig6.runs[0].font.italic = True
    p_fig6.runs[0].font.size = Pt(11)

    add_body_p(doc, "Prose:\nThe Allocation View illustrates how software execution units map onto physical nodes and containerized environments:\n• Client Tier (User Workstation): The React SPA executes within standard web browser runtimes (Chrome, Firefox, Safari, Edge). UI rendering, canvas bounding box math, and local history persistence execute on the client device, offloading UI compute from the server.\n• Application Server Node (Docker / Linux VM): The backend services execute inside an isolated Docker container on Python 3.12. The Uvicorn ASGI server binds to port 8000. It manages isolated scratch directories (uploads/) and hosts neural network checkpoints (models/phishing_resnet18.pt, models/phishvn_url_histgb.joblib) and Tesseract linguistic models (tessdata/vie.traineddata).\n• Persistence Node: In development, SQLite provides low-overhead embedded persistence (scam_detector.db). In staging/production, MySQL 8.0 operates within a dedicated container accessible via TCP port 3306, managed through SQLAlchemy connection pooling.")
    add_body_p(doc, "Roles and Responsibilities:\n• Web Browser Runtime: Renders presentation views, manages canvas overlays, and provides secure client localStorage.\n• FastAPI ASGI Container: Orchestrates REST endpoints, manages background worker threads for AI models, and verifies security tokens.\n• Scratch File System: Ephemeral directory handling image and PDF buffers with automated post-analysis garbage collection.\n• Database Container: Stores administrative users, scam categories, dataset manifests, and system audit logs.")

    doc.add_page_break()

    # -------------------------------------------------------------
    # 6. REFERENCES
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    r = h1.add_run("6. References")
    r.font.name = "Times New Roman"
    r.font.size = Pt(15)
    r.font.bold = True
    
    p_t22 = doc.add_paragraph("Table 22. Academic & Architectural References")
    p_t22.runs[0].font.name = "Times New Roman"
    p_t22.runs[0].font.bold = True
    p_t22.runs[0].font.size = Pt(11.5)

    tbl_t22 = doc.add_table(rows=8, cols=3)
    set_table_borders(tbl_t22, color="000000", sz="4")
    tbl_t22.alignment = WD_TABLE_ALIGNMENT.CENTER
    t22_headers = ["No.", "Standard / Reference", "Full Citation & Documentation Source"]
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

    # Save Document
    out_name = "C1SE.06_ArchitectureDesign_SFDS_v1.0.docx"
    doc.save(out_name)
    print(f"Successfully generated: {out_name}")

if __name__ == "__main__":
    create_architecture_doc()

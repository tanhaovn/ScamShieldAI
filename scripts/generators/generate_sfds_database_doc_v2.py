# -*- coding: utf-8 -*-
"""
Script to generate official Capstone Database Design Document (.docx)
Matching the exact StoreLens Capstone Cover Page & Approval Structure.
Project: SFDS (Scam Fraud Detection System with Explanations)
Team: C1SE.06 - CMU-SE 450 - Duy Tan University
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

            if c_idx in [0] or val in ["PK", "FK", "Index", "Required", "Optional", "Default: 0", "Default: Date.now"]:
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
    # PAGE 1: EXACT STORELENS COVER PAGE
    # =========================================================================
    logo_path = "extracted_media/image_1.png"
    if os.path.exists(logo_path):
        p_logo = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
        p_logo.add_run().add_picture(logo_path, width=Inches(3.2))

    add_p(doc, "International School", bold=True, font_size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    add_p(doc, "Capstone Project 1", bold=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p(doc, "CMU-SE 450 – C1SE.06", bold=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    add_p(doc, "Database Design", bold=True, font_size=22, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    add_p(doc, "Version 1.0", bold=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p(doc, "Date: Nov 4th, 2026", italic=True, font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    add_p(doc, "SFDS", bold=True, font_size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p(doc, "Scam Fraud Detection System with Explanations", italic=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)

    add_p(doc, "Created by", bold=True, font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    add_p(doc, "Hao, Pham Tan\nNhung, Dao Thi My\nNam, Tran Hoang Nhat\nTuan, Nguyen Phan Duc", font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14, line_spacing=1.2)

    add_p(doc, "Approved by", bold=True, font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    add_p(doc, "Eng. Toan, Ha Manh", font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)

    # Signature lines on cover page matching template
    add_p(doc, "Database Design Review Panel Representative:", bold=True, font_size=11, space_before=10, space_after=6)
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

    # Master Project Info Table
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
            # Merge cells 1, 2, 3
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
    fill_row(proj_table, 5, "Scrum master / Leader", "Hao, Pham Tan   Email: phamtanhao1909@gmail.com   Tel: 0961 651 933   ID: 29219020823")
    fill_row(proj_table, 6, "Product Owner / QA", "Nhung, Dao Thi My   Email: mynhung150905@gmail.com   Tel: 0376 415 338   ID: 29209200048")
    fill_row(proj_table, 7, "Partner Organization", "Duy Tan University")

    # Team members sub-header in row 8
    row8_cells = proj_table.rows[8].cells
    row8_cells[0].merge(row8_cells[1]).merge(row8_cells[2]).merge(row8_cells[3])
    row8_cells[0].text = ""
    p8 = row8_cells[0].paragraphs[0]
    p8.alignment = WD_ALIGN_PARAGRAPH.LEFT
    add_run(p8, "Team members:", bold=True, font_size=10.5)
    set_cell_bg(row8_cells[0], "E6E6E6")

    # Member rows 9, 10, 11 (and we add more rows)
    members_data = [
        ("1", "Hao, Pham Tan", "phamtanhao1909@gmail.com", "0961651933"),
        ("2", "Nhung, Dao Thi My", "mynhung150905@gmail.com", "0376415338"),
        ("3", "Nam, Tran Hoang Nhat", "trannamnhathoang@gmail.com", "0795798736"),
        ("4", "Tuan, Nguyen Phan Duc", "ductuan02072005@gmail.com", "0932442770")
    ]
    # Re-use rows 9, 10, 11 and add 1 row for 4th member
    # First, configure row 9 as header: No, Name, Email, Tel
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

    # Add 2 more rows for Nam and Tuan
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

    # Document Approvals Table
    add_p(doc, "DOCUMENT APPROVALS", bold=True, font_size=12, space_before=6, space_after=4)
    add_p(doc, "The following signatures are required for approval of this document.", italic=True, font_size=10.5, space_after=4)
    approvals_data = [
        ["Hao, Pham Tan\nStudent ID: 29219020823\nScrum Master / Leader", "Signature: _______________", "Date: 04/11/2026"],
        ["Nhung, Dao Thi My\nStudent ID: 29209200048\nProduct Owner / QA Lead", "Signature: _______________", "Date: 04/11/2026"],
        ["Nam, Tran Hoang Nhat\nStudent ID: 29219423638\nFrontend Developer", "Signature: _______________", "Date: 04/11/2026"],
        ["Tuan, Nguyen Phan Duc\nStudent ID: 29211151140\nAI Lead", "Signature: _______________", "Date: 04/11/2026"],
        ["Eng. Ha Manh Toan\nProject Mentor\nDuy Tan University", "Signature: _______________", "Date: 04/11/2026"]
    ]
    create_styled_table(doc, ["Stakeholder", "Signature", "Date"], approvals_data, col_widths=[3.2, 2.0, 1.3])

    # Database Design Document Header Meta Table
    add_p(doc, "DATABASE DESIGN DOCUMENT", bold=True, font_size=12, space_before=6, space_after=4)
    meta_data = [
        ["Document Title", "Database Design Document (SFDS)"],
        ["Author(s)", "Hao, Pham Tan"],
        ["Date", "Nov 4th, 2026"],
        ["File name:", "C1SE.06_DatabaseDesign_v1.0.docx"]
    ]
    create_styled_table(doc, ["Attribute", "Specification"], meta_data, col_widths=[2.0, 4.5])

    # Revision History
    add_p(doc, "REVISION HISTORY", bold=True, font_size=12, space_before=6, space_after=4)
    rev_data = [
        ["1.0", "Nov 4th, 2026", "Official Database Design Document for SFDS Capstone", "Hao, Pham Tan", "Eng. Ha Manh Toan"]
    ]
    create_styled_table(doc, ["Version", "Date", "Comments", "Author", "Approval"], rev_data, col_widths=[0.8, 1.2, 2.7, 1.0, 1.0])

    doc.add_page_break()

    # =========================================================================
    # PAGE 3: TABLE OF CONTENTS
    # =========================================================================
    add_p(doc, "TABLE OF CONTENTS", bold=True, font_size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)
    toc_items = [
        ("1. Introduction", "4"),
        ("   1.1 Purpose", "4"),
        ("   1.2 Scope", "4"),
        ("   1.3 Introduction about Relational Database Management System (MySQL & SQLite)", "4"),
        ("2. Database Diagram", "6"),
        ("   2.1 Table Overview", "6"),
        ("   2.2 Table Relationship Diagram (ERD)", "7"),
        ("3. Database Design for Sprint", "9"),
        ("   3.1 Table users", "9"),
        ("   3.2 Table auth_identities", "10"),
        ("   3.3 Table scam_categories", "11"),
        ("   3.4 Table scan_history", "12"),
        ("   3.5 Table incidents", "14"),
        ("   3.6 Table scam_keywords", "15"),
        ("   3.7 Table training_dataset", "16"),
        ("   3.8 Table ai_models", "17"),
        ("   3.9 Table model_evaluations", "18"),
        ("   3.10 Table system_activity_logs", "19"),
        ("4. Hardware and software Requirements", "20"),
        ("   4.1 System Technology Attributes", "20"),
        ("   4.2 Database Storage & Capacity Estimation", "21"),
        ("   4.3 Data Security, Backup and Recovery Policy", "22")
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
    add_p(doc, (
        "The Database Design maps the logical data model to the target database management system with strict consideration "
        "to the system's performance requirements. The Database Design converts logical or conceptual data constructs to physical "
        "data constructs (tables, columns, indexes, foreign keys, and constraints) of the target Database Management System."
    ), space_after=6)

    add_p(doc, "1.1 Purpose", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "The purpose of the Database Design is to ensure that every database transaction meets or exceeds its performance requirements. "
        "This document takes into account data and transaction volume to produce a schema and environment that will meet necessary performance."
    ), space_after=6)

    add_p(doc, "1.2 Scope", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "The Database Design Document has the following objectives:\n"
        "• To describe the design of a database, that is, a collection of related data stored in one or more computerized files "
        "that can be accessed by users or developers via a DBMS.\n"
        "• To serve as a basis for implementing the database and related software units. It provides the acquirer visibility into the design "
        "and provides information necessary for software development."
    ), space_after=6)

    add_p(doc, "1.3 Introduction about Relational Database Management System (MySQL & SQLite)", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "MySQL is an open-source relational database management system (RDBMS) that stores data in structured tables composed of rows and columns. "
        "It uses Structured Query Language (SQL) to define, manipulate, and query data. Unlike NoSQL document databases, MySQL enforces strict "
        "ACID (Atomicity, Consistency, Isolation, Durability) transactions, making it exceptionally well-suited for forensic investigations, "
        "audit tracking, and fraud classification where referential integrity and zero data loss are mandatory.\n\n"
        "In the SFDS platform, data is organized across 10 normalized tables. MySQL 8.0 powers high-throughput production workloads, while SQLite 3 "
        "provides seamless offline and local development capabilities via SQLAlchemy ORM. Native JSON support in MySQL 8.0 allows storing structured "
        "relational records (user IDs, timestamps, calibrated risk scores) alongside flexible semi-structured JSON payloads (extracted OCR bounding "
        "boxes, forensic flags, and step-by-step Chain-of-Thought explanations) without sacrificing relational guarantees."
    ), space_after=6)

    doc.add_page_break()

    # =========================================================================
    # SECTION 2: DATABASE DIAGRAM
    # =========================================================================
    add_p(doc, "2. Database Diagram", bold=True, font_size=16, space_before=12, space_after=8)
    add_p(doc, "2.1 Table Overview", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 1. Table Overview", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)

    table_overview_data = [
        ["users", "Stores login accounts, credentials, and role-based permissions ('user', 'sme', 'admin')."],
        ["auth_identities", "Links internal user accounts to external OAuth providers (Google, Zalo) for Single Sign-On."],
        ["scam_categories", "Standardized taxonomy catalog defining cyber fraud categories (phishing, impersonation, fake invoice)."],
        ["scan_history", "Stores forensic scan transactions: input modalities (URL, text, screenshot), risk scores, and AI explanations."],
        ["incidents", "Manages reported fraud cases, triage workflow statuses ('moi', 'dang_xu_ly', 'da_xu_ly'), and assignees."],
        ["scam_keywords", "Dictionary of Vietnamese fraud phrases, regex patterns, and risk contribution weights."],
        ["training_dataset", "Anonymized, verified image and text sample repository utilized for periodic AI model retraining."],
        ["ai_models", "Model registry cataloging deployed AI engine versions (PhishVN, ResNet-18, CoT reasoning) and active status."],
        ["model_evaluations", "Benchmark evaluation metrics (Macro F1, Recall, False Alarm Rate, Explanation Usefulness) for AI models."],
        ["system_activity_logs", "Security audit trail recording administrative actions, rule modifications, and system events."]
    ]
    create_styled_table(doc, ["Collection / Table Name", "Short Description"], table_overview_data, col_widths=[2.0, 4.5])

    add_p(doc, "2.2 Table Relationship Diagram", bold=True, font_size=14, space_before=12, space_after=4)
    add_p(doc, (
        "Figure 1 illustrates the Table Relationship Diagram (ERD) of the SFDS database, depicting all 10 tables, primary keys, "
        "foreign keys, and relational cardinality."
    ), space_after=6)

    erd_image_path = "arch_diagrams/fig_sfds_erd.png"
    if os.path.exists(erd_image_path):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=4)
        p_img.add_run().add_picture(erd_image_path, width=Inches(6.4))
        add_p(doc, "Figure 1. Table Relationship Diagram (ERD)", bold=True, italic=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

    doc.add_page_break()

    # =========================================================================
    # SECTION 3: DATABASE DESIGN FOR SPRINT (DATA DICTIONARY)
    # =========================================================================
    add_p(doc, "3. Database Design for Sprint", bold=True, font_size=16, space_before=12, space_after=8)

    # 3.1 users
    add_p(doc, "3.1 Table users", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 2. Table users", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    users_dict = [
        ["1", "id", "INT", "Primary key, Auto-Increment", "Unique auto-generated identifier for the user."],
        ["2", "email", "VARCHAR(255)", "Required, Unique", "The user's login email address."],
        ["3", "password_hash", "VARCHAR(255)", "Required", "Bcrypt-hashed password string."],
        ["4", "full_name", "VARCHAR(255)", "Optional", "The full name of the user."],
        ["5", "role", "ENUM('user','admin')", "Default: 'user'", "Role-based access level governing system permissions."],
        ["6", "is_active", "BOOLEAN", "Default: true", "Flag indicating whether the account is active."],
        ["7", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the account was created."],
        ["8", "updated_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp of the last profile update."]
    ]
    create_styled_table(doc, ["Id", "Field", "Type", "Constraint", "Description"], users_dict, col_widths=[0.5, 1.4, 1.3, 1.6, 1.7])

    # 3.2 auth_identities
    add_p(doc, "3.2 Table auth_identities", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 3. Table auth_identities", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    auth_dict = [
        ["1", "id", "INT", "Primary key, Auto-Increment", "Unique identifier for external identity binding."],
        ["2", "user_id", "INT", "Required, Foreign Key", "References users(id) ON DELETE CASCADE."],
        ["3", "provider", "VARCHAR(50)", "Required", "Name of OAuth provider (e.g., 'google', 'zalo')."],
        ["4", "provider_subject", "VARCHAR(255)", "Required", "Unique subject ID issued by the OAuth provider."],
        ["5", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when OAuth identity was linked."]
    ]
    create_styled_table(doc, ["Id", "Field", "Type", "Constraint", "Description"], auth_dict, col_widths=[0.5, 1.4, 1.3, 1.6, 1.7])

    # 3.3 scam_categories
    add_p(doc, "3.3 Table scam_categories", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 4. Table scam_categories", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    cat_dict = [
        ["1", "id", "INT", "Primary key, Auto-Increment", "Unique category identifier."],
        ["2", "code", "VARCHAR(50)", "Required, Unique", "Slug code (e.g., 'phishing', 'fake_invoice')."],
        ["3", "display_name", "VARCHAR(150)", "Required", "Human-readable Vietnamese category name."],
        ["4", "description", "TEXT", "Optional", "Detailed description of the scam tactics."]
    ]
    create_styled_table(doc, ["Id", "Field", "Type", "Constraint", "Description"], cat_dict, col_widths=[0.5, 1.4, 1.3, 1.6, 1.7])

    # 3.4 scan_history
    add_p(doc, "3.4 Table scan_history", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 5. Table scan_history", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    scan_dict = [
        ["1", "id", "INT", "Primary key, Auto-Increment", "Unique scan transaction identifier."],
        ["2", "user_id", "INT", "Required, Foreign Key", "References users(id) ON DELETE CASCADE."],
        ["3", "image_url", "VARCHAR(1024)", "Optional", "Storage URL of suspicious screenshot image."],
        ["4", "original_filename", "VARCHAR(512)", "Optional", "Original file name uploaded by the user."],
        ["5", "extracted_text", "LONGTEXT", "Optional", "Full Vietnamese text extracted via Tesseract OCR."],
        ["6", "scam_category_id", "INT", "Optional, Foreign Key", "References scam_categories(id) ON DELETE SET NULL."],
        ["7", "risk_score", "INT", "Required, Range: 0-100", "Calibrated soft-voting multimodal risk score."],
        ["8", "risk_level", "ENUM('an_toan','nghi_ngo','nguy_hiem')", "Required", "Categorical risk classification level."],
        ["9", "explanation", "TEXT", "Optional", "Synthesized plain-language reasoning explanation."],
        ["10", "highlighted_regions", "LONGTEXT / JSON", "Optional", "JSON coordinates and flagged terms in proof."],
        ["11", "suggested_action", "TEXT", "Optional", "Actionable prevention recommendations for user."],
        ["12", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the scan was executed."]
    ]
    create_styled_table(doc, ["Id", "Field", "Type", "Constraint", "Description"], scan_dict, col_widths=[0.5, 1.4, 1.3, 1.6, 1.7])

    # 3.5 incidents
    add_p(doc, "3.5 Table incidents", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 6. Table incidents", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    incidents_dict = [
        ["1", "id", "INT", "Primary key, Auto-Increment", "Unique incident ticket identifier."],
        ["2", "sme_user_id", "INT", "Required, Foreign Key", "References users(id) ON DELETE CASCADE."],
        ["3", "scan_history_id", "INT", "Required, Foreign Key", "References scan_history(id) ON DELETE CASCADE."],
        ["4", "status", "ENUM('moi','dang_xu_ly','da_xu_ly','bo_qua')", "Default: 'moi'", "Investigation workflow lifecycle state."],
        ["5", "assigned_to", "VARCHAR(255)", "Optional", "Name of assigned forensic investigator."],
        ["6", "notes", "TEXT", "Optional", "Resolution notes and investigative remarks."],
        ["7", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when incident was created."],
        ["8", "updated_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp of the last status update."]
    ]
    create_styled_table(doc, ["Id", "Field", "Type", "Constraint", "Description"], incidents_dict, col_widths=[0.5, 1.4, 1.3, 1.6, 1.7])

    # 3.6 scam_keywords
    add_p(doc, "3.6 Table scam_keywords", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 7. Table scam_keywords", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    kw_dict = [
        ["1", "id", "INT", "Primary key, Auto-Increment", "Unique keyword identifier."],
        ["2", "keyword", "VARCHAR(255)", "Required", "Vietnamese fraud keyword or regex pattern."],
        ["3", "category", "VARCHAR(100)", "Required", "Fraud category associated with keyword."],
        ["4", "weight", "INT", "Default: 10", "Risk score contribution weight (5-25 points)."],
        ["5", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when rule was registered."]
    ]
    create_styled_table(doc, ["Id", "Field", "Type", "Constraint", "Description"], kw_dict, col_widths=[0.5, 1.4, 1.3, 1.6, 1.7])

    # 3.7 training_dataset
    add_p(doc, "3.7 Table training_dataset", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 8. Table training_dataset", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    train_dict = [
        ["1", "id", "INT", "Primary key, Auto-Increment", "Unique dataset sample identifier."],
        ["2", "image_url", "VARCHAR(1024)", "Required", "Storage path to curated training image/text."],
        ["3", "scam_category_id", "INT", "Optional, Foreign Key", "References scam_categories(id) ON DELETE SET NULL."],
        ["4", "is_anonymized", "BOOLEAN", "Default: false", "Flag confirming PII has been redacted."],
        ["5", "is_verified", "BOOLEAN", "Default: false", "Flag indicating ground truth label is verified."],
        ["6", "uploaded_by", "INT", "Required, Foreign Key", "References users(id) ON DELETE CASCADE."],
        ["7", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when sample was added."]
    ]
    create_styled_table(doc, ["Id", "Field", "Type", "Constraint", "Description"], train_dict, col_widths=[0.5, 1.4, 1.3, 1.6, 1.7])

    # 3.8 ai_models
    add_p(doc, "3.8 Table ai_models", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 9. Table ai_models", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    ai_dict = [
        ["1", "id", "INT", "Primary key, Auto-Increment", "Unique AI model identifier."],
        ["2", "version_name", "VARCHAR(100)", "Required, Unique", "Model version (e.g., 'PhishVN-v1.2', 'ResNet18-v2.0')."],
        ["3", "description", "TEXT", "Optional", "Model architecture, hyperparameters, and dataset."],
        ["4", "is_active", "BOOLEAN", "Default: false", "Flag indicating if model is currently serving traffic."],
        ["5", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when checkpoint was registered."]
    ]
    create_styled_table(doc, ["Id", "Field", "Type", "Constraint", "Description"], ai_dict, col_widths=[0.5, 1.4, 1.3, 1.6, 1.7])

    # 3.9 model_evaluations
    add_p(doc, "3.9 Table model_evaluations", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 10. Table model_evaluations", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    eval_dict = [
        ["1", "id", "INT", "Primary key, Auto-Increment", "Unique benchmark evaluation identifier."],
        ["2", "ai_model_id", "INT", "Required, Foreign Key", "References ai_models(id) ON DELETE CASCADE."],
        ["3", "macro_f1", "DECIMAL(5,4)", "Optional", "Macro F1-score across validation test set."],
        ["4", "recall", "DECIMAL(5,4)", "Optional", "Detection recall rate on true fraud samples."],
        ["5", "false_alarm_rate", "DECIMAL(5,4)", "Optional", "False positive alarm rate on benign samples."],
        ["6", "explanation_usefulness", "DECIMAL(5,4)", "Optional", "Expert score assessing clarity of explanations."],
        ["7", "evaluated_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when evaluation was executed."]
    ]
    create_styled_table(doc, ["Id", "Field", "Type", "Constraint", "Description"], eval_dict, col_widths=[0.5, 1.4, 1.3, 1.6, 1.7])

    # 3.10 system_activity_logs
    add_p(doc, "3.10 Table system_activity_logs", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 11. Table system_activity_logs", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    log_dict = [
        ["1", "id", "INT", "Primary key, Auto-Increment", "Unique log entry identifier."],
        ["2", "admin_id", "INT", "Optional, Foreign Key", "References users(id) ON DELETE SET NULL."],
        ["3", "action_type", "VARCHAR(100)", "Required", "Action type (e.g., 'UPDATE_RULE', 'TRIAGE_CASE')."],
        ["4", "description", "TEXT", "Optional", "Detailed description of administrative changes."],
        ["5", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when action occurred."]
    ]
    create_styled_table(doc, ["Id", "Field", "Type", "Constraint", "Description"], log_dict, col_widths=[0.5, 1.4, 1.3, 1.6, 1.7])

    doc.add_page_break()

    # =========================================================================
    # SECTION 4: HARDWARE AND SOFTWARE REQUIREMENTS
    # =========================================================================
    add_p(doc, "4. Hardware and software Requirements", bold=True, font_size=16, space_before=12, space_after=8)
    add_p(doc, (
        "This section provides an overview of hardware and software requirements. "
        "Below are descriptions of the technological components of the Scam Fraud Detection System with Explanations (SFDS):"
    ), space_after=6)

    add_p(doc, "Table 12. Attributes of Scam Fraud Detection Application", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    tech_data = [
        ["Database", "MySQL 8.0 Community Server (Production, InnoDB Engine, utf8mb4)\nSQLite 3.42 (Local Dev & Testing)\nSQLAlchemy 2.0 ORM + Alembic"],
        ["Software", "Frontend: React 18, Vite 5, Tailwind CSS, Recharts\nBackend: Python 3.12, FastAPI, Uvicorn (ASGI)\nAI Core: PyTorch, Scikit-Learn, OpenCV"],
        ["Hardware", "Cloud / Backend Server (8 Cores, 16 GB RAM, 256 GB NVMe SSD)\nClient Workstations (Modern Web Browser, 4 GB RAM minimum)"],
        ["Library", "Frameworks: FastAPI, React 18, Tailwind CSS\nAI Models: PhishVN (HistGB), ResNet-18, Tesseract OCR 5.3 (vie+eng)"]
    ]
    create_styled_table(doc, ["Attributes", "Descriptions"], tech_data, col_widths=[2.0, 4.5])

    # Save logic with fallback
    target_names = [
        "C1SE.06_DatabaseDesign_SFDS_v1.0.docx",
        "C1SE.06_DatabaseDesign_SFDS_v1.1.docx",
        "C1SE.06_DatabaseDesign_SFDS_v1.2.docx"
    ]
    saved_file = None
    for fname in target_names:
        try:
            doc.save(fname)
            saved_file = fname
            print(f"Successfully generated: {fname}")
            break
        except PermissionError:
            continue

    if not saved_file:
        fallback = "C1SE.06_DatabaseDesign_SFDS_v1.3.docx"
        doc.save(fallback)
        print(f"Generated fallback: {fallback}")

if __name__ == "__main__":
    generate_document()

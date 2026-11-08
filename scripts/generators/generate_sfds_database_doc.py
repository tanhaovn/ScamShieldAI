# -*- coding: utf-8 -*-
"""
Script to generate the official Capstone Database Design Document (.docx)
Project: SFDS (Scam Fraud Detection System with Explanations)
Course: CMU-SE 450 - C1SE.06 - Duy Tan University
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

def add_p(doc, text="", style='Normal', space_before=0, space_after=6, line_spacing=1.25, align=WD_ALIGN_PARAGRAPH.LEFT, bold=False, italic=False, font_size=13, color=RGBColor(0,0,0)):
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
            
            # Align center for index / short codes / timestamps, left for text
            if c_idx in [0] or val in ["PK", "FK", "Index", "Required", "Optional", "Default: 0", "Default: Date.now"]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT

            # Bold field names or PK/FK
            is_bold = (c_idx == 1 and len(row_data) >= 5) or (c_idx == 0 and len(row_data) < 4)
            add_run(p, str(val), bold=is_bold, font_size=10.5, color=RGBColor(0,0,0))
            set_cell_bg(row_cells[c_idx], "FFFFFF")
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=100, right=100)
            row_cells[c_idx].vertical_alignment = WD_ALIGN_VERTICAL.TOP

    if col_widths:
        for row in table.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = Inches(width)

    add_p(doc, "", space_before=0, space_after=6)
    return table

def generate_document():
    doc = docx.Document()

    # Configure Margins: Top=1", Bottom=1", Left=1", Right=1"
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)

    # -------------------------------------------------------------
    # COVER PAGE
    # -------------------------------------------------------------
    # DTU Logo
    logo_path = "extracted_media/image_1.png"
    if os.path.exists(logo_path):
        p_logo = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)
        p_logo.add_run().add_picture(logo_path, width=Inches(3.2))

    add_p(doc, "DUY TAN UNIVERSITY", bold=True, font_size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    add_p(doc, "SCHOOL OF COMPUTER SCIENCE", bold=True, font_size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p(doc, "CAPSTONE PROJECT 1 – CMU-SE 450", bold=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)

    add_p(doc, "DATABASE DESIGN DOCUMENT", bold=True, font_size=20, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
    add_p(doc, "SFDS: SCAM FRAUD DETECTION SYSTEM WITH EXPLANATIONS", bold=True, font_size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    add_p(doc, "Hệ Thống Nhận Diện Lừa Đảo Đa Phương Thức Kèm Giải Thích Trực Quan", italic=True, font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=20)

    add_p(doc, "Class: CMU-SE 450 – Group: C1SE.06", bold=True, font_size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_p(doc, "Version: 1.0  |  Date: November 2026", font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=20)

    # Project Information Box
    add_p(doc, "PROJECT INFORMATION", bold=True, font_size=12, space_before=10, space_after=4)
    proj_info_data = [
        ["Project Acronym", "SFDS"],
        ["Project Title", "Scam Fraud Detection System with Explanations (SFDS)"],
        ["Start Date", "02/09/2026"],
        ["End Date", "15/12/2026"],
        ["Lead Institution", "School of Computer Science, Duy Tan University (DTU)"],
        ["Project Mentor", "Eng. Ha Manh Toan (Email: lhttuy@gmail.com)"],
        ["Scrum Master / Leader", "Pham Tan Hao (ID: 29219020823, Tel: 0961651933, Email: phamtanhao1909@gmail.com)"],
        ["Partner Organization", "Duy Tan University (DTU)"]
    ]
    create_styled_table(doc, ["Field", "Information"], proj_info_data, col_widths=[2.2, 4.3])

    # Team Members Table
    add_p(doc, "TEAM MEMBERS", bold=True, font_size=12, space_before=8, space_after=4)
    team_data = [
        ["1", "Pham Tan Hao", "phamtanhao1909@gmail.com", "0961651933", "29219020823", "Leader / Scrum Master / Full-stack"],
        ["2", "Dao Thi My Nhung", "mynhung150905@gmail.com", "0376415338", "29209200048", "QA Lead / UI-UX Designer"],
        ["3", "Tran Hoang Nhat Nam", "trannamnhathoang@gmail.com", "0795798736", "29219423638", "Frontend Dev / Technical Writer"],
        ["4", "Nguyen Phan Duc Tuan", "ductuan02072005@gmail.com", "0932442770", "29211151140", "AI Lead / Full-stack Dev"]
    ]
    create_styled_table(doc, ["No.", "Name", "Email", "Phone", "Student ID", "Role"], team_data, col_widths=[0.5, 1.4, 1.6, 1.0, 1.0, 1.5])

    # Approvals Table
    add_p(doc, "DOCUMENT APPROVALS", bold=True, font_size=12, space_before=8, space_after=4)
    approval_data = [
        ["Pham Tan Hao\nStudent ID: 29219020823\nProject Leader / Scrum Master", "Signature: _______________", "Date: 04/11/2026"],
        ["Dao Thi My Nhung\nStudent ID: 29209200048\nQA Lead", "Signature: _______________", "Date: 04/11/2026"],
        ["Tran Hoang Nhat Nam\nStudent ID: 29219423638\nFrontend Developer", "Signature: _______________", "Date: 04/11/2026"],
        ["Nguyen Phan Duc Tuan\nStudent ID: 29211151140\nAI Lead", "Signature: _______________", "Date: 04/11/2026"],
        ["Eng. Ha Manh Toan\nProject Mentor\nDuy Tan University", "Signature: _______________", "Date: 04/11/2026"]
    ]
    create_styled_table(doc, ["Stakeholder", "Signature", "Date"], approval_data, col_widths=[3.2, 2.0, 1.3])

    # Revision History
    add_p(doc, "REVISION HISTORY", bold=True, font_size=12, space_before=8, space_after=4)
    rev_data = [
        ["1.0", "04/11/2026", "Official Database Design Document for SFDS Capstone Project", "Pham Tan Hao", "Eng. Ha Manh Toan"]
    ]
    create_styled_table(doc, ["Version", "Date", "Comments", "Author", "Approval"], rev_data, col_widths=[0.8, 1.1, 2.8, 1.1, 1.2])

    doc.add_page_break()

    # -------------------------------------------------------------
    # TABLE OF CONTENTS
    # -------------------------------------------------------------
    add_p(doc, "TABLE OF CONTENTS", bold=True, font_size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)
    toc_items = [
        ("1. Introduction", "3"),
        ("   1.1 Purpose", "3"),
        ("   1.2 Scope", "3"),
        ("   1.3 Introduction about Relational Database Management System (MySQL & SQLite)", "3"),
        ("2. Database Diagram", "5"),
        ("   2.1 Table Overview", "5"),
        ("   2.2 Table Relationship Diagram (ERD)", "6"),
        ("3. Database Design for Sprint", "8"),
        ("   3.1 Table users", "8"),
        ("   3.2 Table auth_identities", "9"),
        ("   3.3 Table scam_categories", "10"),
        ("   3.4 Table scan_history", "11"),
        ("   3.5 Table incidents", "13"),
        ("   3.6 Table scam_keywords", "14"),
        ("   3.7 Table training_dataset", "15"),
        ("   3.8 Table ai_models", "16"),
        ("   3.9 Table model_evaluations", "17"),
        ("   3.10 Table system_activity_logs", "18"),
        ("4. Hardware and Software Requirements", "19"),
        ("   4.1 System Technology Attributes", "19"),
        ("   4.2 Database Storage & Capacity Estimation", "20"),
        ("   4.3 Data Security, Backup and Recovery Policy", "21")
    ]
    for title, page in toc_items:
        p_toc = add_p(doc, space_after=3, line_spacing=1.15)
        add_run(p_toc, title, bold=("." not in title[:3]), font_size=12)
        # dot leader
        dots_count = max(5, 75 - len(title))
        add_run(p_toc, " " + "." * dots_count + " ", font_size=11, color=RGBColor(120, 120, 120))
        add_run(p_toc, page, bold=True, font_size=12)

    doc.add_page_break()

    # -------------------------------------------------------------
    # SECTION 1: INTRODUCTION
    # -------------------------------------------------------------
    add_p(doc, "1. Introduction", bold=True, font_size=16, space_before=12, space_after=8)
    add_p(doc, (
        "The Database Design document maps the logical data model of the Scam Fraud Detection System with Explanations (SFDS) "
        "to the physical target database management systems with strict consideration to data integrity, transactional throughput, "
        "and sub-second retrieval performance. The Database Design converts conceptual and business entities—such as citizens, "
        "multimodal inspection requests, AI inference scores, digital forensics artifacts, incidents, and threat taxonomy—into "
        "highly normalized and optimized physical database structures."
    ), space_after=6)

    add_p(doc, "1.1 Purpose", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "The primary purpose of the Database Design is to ensure that every database transaction executed across the SFDS platform "
        "meets or exceeds strict operational performance, security, and reliability requirements. Specifically, the database design:"
    ), space_after=4)
    add_p(doc, "• Establishes a robust, normalized relational schema supporting multi-tenant citizens, corporate security teams (SMEs), and system administrators.", space_after=3)
    add_p(doc, "• Enables ultra-low latency persistence (< 50ms) for high-frequency scan queries containing multi-modal outputs (extracted OCR strings, visual brand classifications, and JSON reasoning trees).", space_after=3)
    add_p(doc, "• Enforces strict referential integrity (Foreign Key cascading, indexing on user and category relationships) to prevent orphaned audit logs or orphaned forensic proofs.", space_after=3)
    add_p(doc, "• Provides an immutable audit trail for forensic incident triage, false positive appeals, and administrative model performance benchmarking.", space_after=6)

    add_p(doc, "1.2 Scope", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "The scope of this document encompasses the entire data architecture of the SFDS platform, including:"
    ), space_after=4)
    add_p(doc, "1. Physical Schema Architecture: Definition of all 10 core relational tables implemented across MySQL 8.0 (production server) and SQLite 3 (local development and offline verification).", space_after=3)
    add_p(doc, "2. Object-Relational Mapping (ORM): Implementation of SQLAlchemy 2.0 models bridging Python/FastAPI data access layers to physical database tables.", space_after=3)
    add_p(doc, "3. Entity-Relationship Diagram (ERD): Visual mapping of primary keys, foreign keys, cardinality (1:1, 1:N), and indexing strategies.", space_after=3)
    add_p(doc, "4. Data Dictionary: Comprehensive tabular definitions specifying column names, data types, physical constraints, and business domain descriptions for every attribute.", space_after=3)
    add_p(doc, "5. Capacity, Storage & Recovery: Quantitative projections of transaction volume, storage growth rates, and backup/restore protocols.", space_after=6)

    add_p(doc, "1.3 Introduction about Relational Database Management System (MySQL & SQLite with SQLAlchemy)", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "Unlike unstructured document databases (such as MongoDB), fraud detection and security forensics systems mandate "
        "rigorous ACID (Atomicity, Consistency, Isolation, Durability) guarantees. Financial, legal, and cybercrime incident logs "
        "require strict relational consistency, schema enforcement, and relational integrity between reported scams, verified categories, "
        "and investigative findings. Therefore, SFDS adopts a high-performance relational database architecture powered by MySQL 8.0 "
        "in production and SQLite 3 in lightweight local/testing environments, orchestrated via SQLAlchemy 2.0 ORM."
    ), space_after=6)
    add_p(doc, (
        "Key advantages of this architecture for SFDS include:"
    ), space_after=4)
    add_p(doc, "• ACID Guarantees: Every scan log, user authentication event, and admin triage status change is committed durably, eliminating data corruption risks during sudden server restarts.", space_after=3)
    add_p(doc, "• Hybrid Relational & JSON Capabilities: MySQL 8.0 provides native JSON data types, enabling SFDS to store structured relational columns (user_id, risk_score) alongside flexible semi-structured JSON payloads (highlighted_terms, visual_flags, CoT reasoning steps) within the same table without compromising relational integrity.", space_after=3)
    add_p(doc, "• Dual-Database Portability: SQLAlchemy 2.0 abstracts SQL dialect differences, allowing the exact same application code to operate seamlessly over SQLite (zero-configuration development) and enterprise MySQL 8.0 (high-concurrency deployment) without modifying any business logic.", space_after=6)

    doc.add_page_break()

    # -------------------------------------------------------------
    # SECTION 2: DATABASE DIAGRAM
    # -------------------------------------------------------------
    add_p(doc, "2. Database Diagram", bold=True, font_size=16, space_before=12, space_after=8)
    
    add_p(doc, "2.1 Table Overview", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "The SFDS database schema comprises 10 primary relational tables designed to support user authentication, multimodal scan "
        "processing, community feedback, threat taxonomy, training dataset curation, AI model evaluation, and administrative audit logging. "
        "Table 1 outlines the operational role and description of each table."
    ), space_after=6)

    table_overview_data = [
        ["users", "Stores credentials, personal profiles, RBAC roles ('user', 'sme', 'admin'), and account activation status."],
        ["auth_identities", "Links internal user accounts to external OAuth providers (Google, Zalo, OpenID Connect) for Single Sign-On."],
        ["scam_categories", "Standardized taxonomy catalog defining cyber fraud categories (phishing, impersonation, fake invoice, loan trap)."],
        ["scan_history", "Primary forensic repository recording multimodal inputs (URL, text, screenshot), risk scores, and AI explanations."],
        ["incidents", "Incident management queue tracking reported scams, investigation statuses ('moi', 'dang_xu_ly', 'da_xu_ly'), and assignees."],
        ["scam_keywords", "Vietnamese fraud lexicon dictionary containing sensitive phrases, regex patterns, and risk contribution weights."],
        ["training_dataset", "Anonymized, verified image and text sample repository utilized for periodic AI model retraining and fine-tuning."],
        ["ai_models", "Model registry cataloging deployed AI engine versions (PhishVN, ResNet-18, CoT Reasoning) and activation flags."],
        ["model_evaluations", "Benchmark evaluation metrics (Macro F1, Recall, False Alarm Rate, Explanation Usefulness) for each AI model."],
        ["system_activity_logs", "Security audit trail recording administrative actions, rule modifications, and system configuration events."]
    ]
    add_p(doc, "Table 1. SFDS Database Table Overview", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    create_styled_table(doc, ["Table Name", "Short Operational Description"], table_overview_data, col_widths=[2.0, 4.5])

    add_p(doc, "2.2 Table Relationship Diagram (ERD)", bold=True, font_size=14, space_before=12, space_after=4)
    add_p(doc, (
        "The Entity-Relationship Diagram (ERD) defines the structural relationships and foreign key dependencies connecting all 10 tables "
        "within the SFDS database. Figure 1 illustrates the complete physical entity relationship model."
    ), space_after=6)

    erd_image_path = "arch_diagrams/fig_sfds_erd.png"
    if os.path.exists(erd_image_path):
        p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=4)
        p_img.add_run().add_picture(erd_image_path, width=Inches(6.4))
        add_p(doc, "Figure 1. SFDS Entity-Relationship Diagram (ERD)", bold=True, italic=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

    add_p(doc, (
        "Relational Cardinality & Referential Integrity Narrative:"
    ), bold=True, space_after=3)
    add_p(doc, "• users (1) to auth_identities (N): A single user account can bind multiple external OAuth credentials (e.g., Google or email/password). Deletion of a user cascades to remove all associated authentication identities (ON DELETE CASCADE).", space_after=3)
    add_p(doc, "• users (1) to scan_history (N): Each multimodal inspection record is bound to the requesting user account (or default guest account). Deleting a user purges their scan history unless archived.", space_after=3)
    add_p(doc, "• scam_categories (1) to scan_history (N): Each scan verdict is categorized into a verified scam category. Deleting a category sets the category reference in historical scans to NULL (ON DELETE SET NULL), preserving the scan data.", space_after=3)
    add_p(doc, "• scan_history (1) to incidents (1): An incident is created from an anomalous scan record. If the scan record is deleted, the corresponding incident entry is removed (ON DELETE CASCADE).", space_after=3)
    add_p(doc, "• users (1) to incidents (N): Corporate security officers (sme_user_id) can manage multiple assigned incident cases.", space_after=3)
    add_p(doc, "• scam_categories (1) to training_dataset (N): Training samples are classified under defined fraud categories.", space_after=3)
    add_p(doc, "• ai_models (1) to model_evaluations (N): Each AI model version maintains a historical track record of quantitative evaluation benchmarks.", space_after=3)
    add_p(doc, "• users (1) to system_activity_logs (N): Administrative personnel generate immutable activity log entries. If an administrator account is deleted, the log entry preserves the historical record with admin_id set to NULL.", space_after=6)

    doc.add_page_break()

    # -------------------------------------------------------------
    # SECTION 3: DATABASE DESIGN FOR SPRINT (DATA DICTIONARY)
    # -------------------------------------------------------------
    add_p(doc, "3. Database Design for Sprint", bold=True, font_size=16, space_before=12, space_after=8)
    add_p(doc, (
        "This section details the physical schema dictionary for all 10 tables implemented across the SFDS development sprints. "
        "Each dictionary specifies column identifiers, data types, physical constraints, default values, and operational descriptions."
    ), space_after=6)

    # 3.1 users
    add_p(doc, "3.1 Table users", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 2. Data Dictionary for Table 'users'", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    users_dict = [
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique auto-generated internal identifier for each user."],
        ["2", "email", "VARCHAR(255)", "Required, Unique, Index", "User login email address, uniquely indexed for fast credential lookup."],
        ["3", "password_hash", "VARCHAR(255)", "Required", "Bcrypt-hashed and salted password string."],
        ["4", "full_name", "VARCHAR(255)", "Optional", "User's display or legal full name."],
        ["5", "role", "ENUM('user','sme','admin')", "Required, Default: 'user'", "Role-based access level governing system permissions."],
        ["6", "is_active", "BOOLEAN", "Required, Default: true", "Flag indicating whether the account is currently enabled."],
        ["7", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the user account was initially registered."],
        ["8", "updated_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when account profile was last modified."]
    ]
    create_styled_table(doc, ["No.", "Field", "Type", "Constraint", "Description"], users_dict, col_widths=[0.5, 1.3, 1.4, 1.7, 1.6])

    # 3.2 auth_identities
    add_p(doc, "3.2 Table auth_identities", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 3. Data Dictionary for Table 'auth_identities'", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    auth_dict = [
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique identifier for the external OAuth binding."],
        ["2", "user_id", "INT", "Required, Foreign Key, Index", "References users(id) ON DELETE CASCADE."],
        ["3", "provider", "VARCHAR(50)", "Required", "Name of OAuth identity provider ('google', 'zalo', 'facebook')."],
        ["4", "provider_subject", "VARCHAR(255)", "Required", "Unique subject identifier (OpenID sub) provided by the OAuth service."],
        ["5", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the external account binding was created."]
    ]
    create_styled_table(doc, ["No.", "Field", "Type", "Constraint", "Description"], auth_dict, col_widths=[0.5, 1.4, 1.4, 1.7, 1.5])

    # 3.3 scam_categories
    add_p(doc, "3.3 Table scam_categories", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 4. Data Dictionary for Table 'scam_categories'", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    cat_dict = [
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique identifier for the fraud category."],
        ["2", "code", "VARCHAR(50)", "Required, Unique, Index", "Machine-readable slug code (e.g., 'phishing', 'fake_invoice', 'impersonation')."],
        ["3", "display_name", "VARCHAR(150)", "Required", "Human-friendly Vietnamese category name displayed on UI."],
        ["4", "description", "TEXT", "Optional", "Detailed description of the scam pattern and typical attack vectors."]
    ]
    create_styled_table(doc, ["No.", "Field", "Type", "Constraint", "Description"], cat_dict, col_widths=[0.5, 1.4, 1.4, 1.7, 1.5])

    # 3.4 scan_history
    add_p(doc, "3.4 Table scan_history", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 5. Data Dictionary for Table 'scan_history'", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    scan_dict = [
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique identifier for each scan transaction."],
        ["2", "user_id", "INT", "Required, Foreign Key, Index", "References users(id) ON DELETE CASCADE."],
        ["3", "input_type", "ENUM('text','image','url','audio')", "Required", "Modality type submitted by the citizen."],
        ["4", "image_url", "VARCHAR(1024)", "Optional", "Storage URL or relative path of the uploaded screenshot."],
        ["5", "original_filename", "VARCHAR(512)", "Optional", "Original file name uploaded by user before sanitization."],
        ["6", "extracted_text", "LONGTEXT", "Optional", "Full Vietnamese/English text extracted via Tesseract OCR."],
        ["7", "scam_category_id", "INT", "Optional, Foreign Key", "References scam_categories(id) ON DELETE SET NULL."],
        ["8", "risk_score", "INT", "Required, Range: 0-100", "Calibrated soft-voting multimodal risk score."],
        ["9", "text_risk_score", "INT", "Default: 0", "Risk score derived specifically from linguistic/keyword analysis."],
        ["10", "visual_risk_score", "INT", "Default: 0", "Risk score derived from ResNet-18 logo & ELA forensics."],
        ["11", "risk_level", "ENUM('an_toan','nghi_ngo','nguy_hiem')", "Required", "Categorical risk classification displayed to citizens."],
        ["12", "scam_type", "VARCHAR(100)", "Optional", "Specific identified threat variant (e.g., 'mạo danh ngân hàng')."],
        ["13", "explanation", "TEXT", "Optional", "Synthesized plain-language reasoning explanation generated by CoT."],
        ["14", "highlighted_terms", "JSON", "Optional", "Structured JSON list of suspicious keywords and flagged coordinates."],
        ["15", "visual_flags", "JSON", "Optional", "Structured JSON forensic flags (EXIF anomalies, ELA compression score)."],
        ["16", "suggested_action", "TEXT", "Optional", "Actionable mitigation recommendations provided to citizen."],
        ["17", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP, Index", "Timestamp when the scan was executed."]
    ]
    create_styled_table(doc, ["No.", "Field", "Type", "Constraint", "Description"], scan_dict, col_widths=[0.4, 1.4, 1.4, 1.6, 1.7])

    # 3.5 incidents
    add_p(doc, "3.5 Table incidents", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 6. Data Dictionary for Table 'incidents'", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    incidents_dict = [
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique incident ticket identifier."],
        ["2", "sme_user_id", "INT", "Required, Foreign Key, Index", "References users(id) ON DELETE CASCADE (investigating SME)."],
        ["3", "scan_history_id", "INT", "Required, Foreign Key, Index", "References scan_history(id) ON DELETE CASCADE."],
        ["4", "status", "ENUM('moi','dang_xu_ly','da_xu_ly','bo_qua')", "Required, Default: 'moi'", "Investigation workflow lifecycle state."],
        ["5", "assigned_to", "VARCHAR(255)", "Optional", "Name or email of assigned forensic investigator."],
        ["6", "notes", "TEXT", "Optional", "Internal notes and resolution findings documented by investigator."],
        ["7", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the incident was flagged or created."],
        ["8", "updated_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp of the last status update."]
    ]
    create_styled_table(doc, ["No.", "Field", "Type", "Constraint", "Description"], incidents_dict, col_widths=[0.5, 1.4, 1.4, 1.6, 1.6])

    # 3.6 scam_keywords
    add_p(doc, "3.6 Table scam_keywords", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 7. Data Dictionary for Table 'scam_keywords'", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    kw_dict = [
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique identifier for the fraud keyword/pattern."],
        ["2", "keyword", "VARCHAR(255)", "Required, Index", "Vietnamese keyword phrase or regex pattern (e.g., 'mã OTP', 'lệnh bắt')."],
        ["3", "category", "VARCHAR(100)", "Required", "Fraud category associated with this keyword."],
        ["4", "weight", "INT", "Required, Default: 10", "Risk score contribution weight (5-25 points)."],
        ["5", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the keyword rule was created."]
    ]
    create_styled_table(doc, ["No.", "Field", "Type", "Constraint", "Description"], kw_dict, col_widths=[0.5, 1.4, 1.4, 1.6, 1.6])

    # 3.7 training_dataset
    add_p(doc, "3.7 Table training_dataset", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 8. Data Dictionary for Table 'training_dataset'", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    train_dict = [
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique identifier for the dataset sample."],
        ["2", "image_url", "VARCHAR(1024)", "Required", "Relative storage path to the curated training image/text."],
        ["3", "scam_category_id", "INT", "Optional, Foreign Key", "References scam_categories(id) ON DELETE SET NULL."],
        ["4", "is_anonymized", "BOOLEAN", "Required, Default: false", "Flag verifying that PII has been masked or redacted."],
        ["5", "is_verified", "BOOLEAN", "Required, Default: false", "Flag indicating ground-truth label has been verified by expert."],
        ["6", "uploaded_by", "INT", "Required, Foreign Key", "References users(id) ON DELETE CASCADE (uploader)."],
        ["7", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when sample was added to retraining pool."]
    ]
    create_styled_table(doc, ["No.", "Field", "Type", "Constraint", "Description"], train_dict, col_widths=[0.5, 1.4, 1.4, 1.6, 1.6])

    # 3.8 ai_models
    add_p(doc, "3.8 Table ai_models", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 9. Data Dictionary for Table 'ai_models'", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    ai_dict = [
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique model registration identifier."],
        ["2", "version_name", "VARCHAR(100)", "Required, Unique", "Semantic model version string (e.g., 'PhishVN-v1.2', 'ResNet18-VNBrand-v2.0')."],
        ["3", "description", "TEXT", "Optional", "Model architecture description, training parameters, and dataset provenance."],
        ["4", "is_active", "BOOLEAN", "Required, Default: false", "Flag denoting whether this model is actively serving live API inference."],
        ["5", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the model checkpoint was registered."]
    ]
    create_styled_table(doc, ["No.", "Field", "Type", "Constraint", "Description"], ai_dict, col_widths=[0.5, 1.4, 1.4, 1.6, 1.6])

    # 3.9 model_evaluations
    add_p(doc, "3.9 Table model_evaluations", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 10. Data Dictionary for Table 'model_evaluations'", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    eval_dict = [
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique evaluation benchmark identifier."],
        ["2", "ai_model_id", "INT", "Required, Foreign Key, Index", "References ai_models(id) ON DELETE CASCADE."],
        ["3", "macro_f1", "DECIMAL(5,4)", "Optional", "Macro-averaged F1 score achieved across test benchmarks (0.0000 - 1.0000)."],
        ["4", "recall", "DECIMAL(5,4)", "Optional", "Fraud detection recall rate on true malicious sample sets."],
        ["5", "false_alarm_rate", "DECIMAL(5,4)", "Optional", "False positive alarm rate on benign domain and message test sets."],
        ["6", "explanation_usefulness", "DECIMAL(5,4)", "Optional", "Human expert score assessing quality and clarity of generated CoT explanations."],
        ["7", "evaluated_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the benchmark evaluation was executed."]
    ]
    create_styled_table(doc, ["No.", "Field", "Type", "Constraint", "Description"], eval_dict, col_widths=[0.5, 1.4, 1.4, 1.6, 1.6])

    # 3.10 system_activity_logs
    add_p(doc, "3.10 Table system_activity_logs", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 11. Data Dictionary for Table 'system_activity_logs'", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    log_dict = [
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique activity log entry identifier."],
        ["2", "admin_id", "INT", "Optional, Foreign Key, Index", "References users(id) ON DELETE SET NULL (responsible administrator)."],
        ["3", "action_type", "VARCHAR(100)", "Required", "Action classifier (e.g., 'UPDATE_KEYWORD', 'RETRAIN_MODEL', 'RESOLVE_INCIDENT')."],
        ["4", "description", "TEXT", "Optional", "Detailed description of configuration parameter changes or affected entities."],
        ["5", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP, Index", "Timestamp when the administrative action occurred."]
    ]
    create_styled_table(doc, ["No.", "Field", "Type", "Constraint", "Description"], log_dict, col_widths=[0.5, 1.4, 1.4, 1.6, 1.6])

    doc.add_page_break()

    # -------------------------------------------------------------
    # SECTION 4: HARDWARE AND SOFTWARE REQUIREMENTS
    # -------------------------------------------------------------
    add_p(doc, "4. Hardware and Software Requirements", bold=True, font_size=16, space_before=12, space_after=8)
    add_p(doc, (
        "This section defines the hardware and software technology stack supporting the SFDS database, transactional storage sizing, "
        "and data protection/recovery specifications."
    ), space_after=6)

    add_p(doc, "4.1 System Technology Attributes", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, "Table 12. System Attributes and Technology Components for SFDS Platform", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    tech_data = [
        ["Database", "Production: MySQL 8.0 Community Server (InnoDB Engine, utf8mb4 encoding)\nLocal Development: SQLite 3.42 (WAL mode enabled)\nORM Layer: SQLAlchemy 2.0.35 + Alembic 1.13 Migration Tool"],
        ["Backend Software", "Runtime: Python 3.12 (64-bit)\nWeb Framework: FastAPI 0.115.0 (ASGI)\nServer Gateway: Uvicorn 0.30.6 (Async I/O)\nSecurity: PyJWT 2.9.0, Passlib/Bcrypt 4.0"],
        ["Frontend Software", "Framework: React 18 (Single Page Application)\nBuild Tool: Vite 5.x\nStyling & Charts: Tailwind CSS 3.4, Lucide Icons, Recharts 2.x\nHTTP Client: Axios 1.7 with JWT interceptors"],
        ["AI & Forensics Core", "Deep Learning: PyTorch 2.4.1 (ResNet-18 Transfer Learning)\nOCR Engine: Tesseract OCR 5.3 (vie + eng traineddata)\nMachine Learning: Scikit-Learn 1.5.2 (HistGradientBoosting PhishVN)\nImage Forensics: OpenCV 4.10 (Error Level Analysis - ELA) & PIL"],
        ["Hardware Requirements", "Application/DB Server: Intel Xeon / Core i7 (8 Cores, 3.2 GHz+), 16 GB DDR4 RAM, 256 GB NVMe SSD storage.\nEdge / Client Devices: Modern Web Browser (Google Chrome 110+, Safari 16+, Edge, Firefox), Minimum 4 GB RAM, 1080p display."]
    ]
    create_styled_table(doc, ["Attributes", "Descriptions and Specifications"], tech_data, col_widths=[2.0, 4.5])

    add_p(doc, "4.2 Database Storage & Capacity Estimation", bold=True, font_size=14, space_before=12, space_after=4)
    add_p(doc, (
        "To guarantee sustained sub-second performance throughout the system lifecycle, storage capacity is projected based on expected "
        "scan volumes and forensic evidence storage:"
    ), space_after=4)
    add_p(doc, "• Average Scan Record Size: 1 record in `scan_history` averages ~4 KB (metadata, risk scores, OCR text up to 2 KB, JSON reasoning breadcrumbs). Uploaded screenshot images average ~350 KB, compressed and stored in local object storage (`/uploads/`).", space_after=3)
    add_p(doc, "• Monthly Transaction Volume: Assuming an initial rollout serving 10,000 public scan queries and 200 incident escalations per month:", space_after=3)
    add_p(doc, "   - Monthly Relational DB Growth: 10,000 * 4 KB = ~40 MB/month (~480 MB/year).", space_after=3)
    add_p(doc, "   - Monthly Screenshot Media Growth: 10,000 * 350 KB = ~3.5 GB/month (~42 GB/year).", space_after=3)
    add_p(doc, "• Sizing Conclusion: A 256 GB NVMe SSD volume provides ample headroom for more than 5 years of continuous operational growth without requiring aggressive data archiving.", space_after=6)

    add_p(doc, "4.3 Data Security, Backup and Recovery Policy", bold=True, font_size=14, space_before=8, space_after=4)
    add_p(doc, (
        "In compliance with OWASP ASVS and Vietnamese cyber safety guidelines, the SFDS database enforces three levels of security:"
    ), space_after=4)
    add_p(doc, "1. Access Control & Encryption: Database connections require TLS 1.3 encryption. Passwords use Bcrypt with a work factor of 12. Root database accounts are restricted to local socket connections (`localhost`).", space_after=3)
    add_p(doc, "2. Automated Backup Strategy: Production MySQL databases execute nightly physical dumps (`mysqldump`) with `--single-transaction --quick`. Backup archives are compressed, AES-256 encrypted, and replicated offsite.", space_after=3)
    add_p(doc, "3. Disaster Recovery Objective: Recovery Point Objective (RPO) is established at <= 24 hours, and Recovery Time Objective (RTO) is <= 15 minutes, ensuring minimal disruption in the event of hardware failure.", space_after=8)

    # Save document
    output_filename = "C1SE.06_DatabaseDesign_SFDS_v1.0.docx"
    try:
        doc.save(output_filename)
        print(f"Successfully generated: {output_filename}")
    except PermissionError:
        alt_filename = "C1SE.06_DatabaseDesign_SFDS_v1.1.docx"
        doc.save(alt_filename)
        print(f"File locked by Word. Successfully generated alternate version: {alt_filename}")

if __name__ == "__main__":
    generate_document()

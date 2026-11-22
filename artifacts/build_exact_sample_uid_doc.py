import os
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def set_repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    tblHeader = parse_xml(f'<w:tblHeader {nsdecls("w")} w:val="true"/>')
    trPr.append(tblHeader)

def prevent_row_split(row):
    trPr = row._tr.get_or_add_trPr()
    cantSplit = parse_xml(f'<w:cantSplit {nsdecls("w")}/>')
    trPr.append(cantSplit)

def create_screen_table(doc, screen_name, rows_data):
    # Table has 5 columns: No. | Field name | Type | Require | Target
    # Row 0: Screen Name (Merged across 5 columns)
    # Row 1: Header (No. | Field name | Type | Require | Target)
    # Rows 2..N: Data
    table = doc.add_table(rows=len(rows_data) + 2, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="B0B0B0", sz="4")

    # Merge Row 0
    cell_0 = table.rows[0].cells[0]
    for c in table.rows[0].cells[1:]:
        cell_0.merge(c)
    cell_0.text = screen_name
    set_cell_background(cell_0, "E8EBF0")
    set_cell_margins(cell_0, top=140, bottom=140, left=150, right=150)
    p0 = cell_0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run0 = p0.runs[0]
    run0.font.bold = True
    run0.font.size = Pt(10.5)
    run0.font.name = "Arial"
    run0.font.color.rgb = RGBColor(30, 40, 60)
    prevent_row_split(table.rows[0])
    set_repeat_header(table.rows[0])

    # Header Row 1
    headers = ["No.", "Field name", "Type", "Require", "Target"]
    set_repeat_header(table.rows[1])
    prevent_row_split(table.rows[1])
    for idx, h_text in enumerate(headers):
        cell = table.rows[1].cells[idx]
        cell.text = h_text
        set_cell_background(cell, "F2F4F8")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.runs[0]
        run.font.bold = True
        run.font.size = Pt(9.5)
        run.font.name = "Arial"
        run.font.color.rgb = RGBColor(20, 20, 20)

    # Data Rows
    col_widths = [Inches(0.5), Inches(1.3), Inches(1.1), Inches(2.2), Inches(1.9)]
    for r_idx, row_values in enumerate(rows_data, start=2):
        row = table.rows[r_idx]
        prevent_row_split(row)
        bg = "FAFAFA" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_values):
            cell = row.cells[c_idx]
            cell.text = str(val)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=90, bottom=90, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.size = Pt(9)
                run.font.name = "Arial"
                run.font.color.rgb = RGBColor(40, 40, 40)

    # Set column widths
    for row in table.rows:
        for c_idx, width in enumerate(col_widths):
            row.cells[c_idx].width = width

    return table

def generate_exact_uid_document(output_docx_path):
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    logo_path = Path("artifacts/database-doc-fix/word/media/image1.png")

    # -------------------------------------------------------------
    # COVER PAGE (EXACT SAME AS SAMPLE)
    # -------------------------------------------------------------
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_after = Pt(16)
    if logo_path.exists():
        p_logo.add_run().add_picture(str(logo_path), width=Inches(3.3))

    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_hdr = p_header.add_run("International School\nCapstone Project 1\nCMU-SE 450 – C1SE.06\n")
    r_hdr.font.bold = True
    r_hdr.font.size = Pt(13)
    r_hdr.font.color.rgb = RGBColor(140, 20, 20)

    p_doc_type = doc.add_paragraph()
    p_doc_type.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_doc_type.paragraph_format.space_before = Pt(18)
    p_doc_type.paragraph_format.space_after = Pt(4)
    r_dt = p_doc_type.add_run("User Interface Design")
    r_dt.font.bold = True
    r_dt.font.size = Pt(22)
    r_dt.font.color.rgb = RGBColor(160, 20, 20)

    p_ver = doc.add_paragraph()
    p_ver.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_v = p_ver.add_run("Version 1.0\nDate: Nov 18th, 2026\n")
    r_v.font.size = Pt(11)
    r_v.font.italic = True
    r_v.font.color.rgb = RGBColor(80, 80, 80)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(14)
    p_title.paragraph_format.space_after = Pt(20)
    r_t = p_title.add_run("Fraudulent Image Detection and Warning System with Explanations")
    r_t.font.bold = True
    r_t.font.size = Pt(15)
    r_t.font.color.rgb = RGBColor(20, 40, 80)

    p_people = doc.add_paragraph()
    p_people.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cb = p_people.add_run("Created by\n")
    r_cb.font.bold = True
    r_cb.font.size = Pt(11)
    r_names = p_people.add_run("Hao, Pham Tan\nNhung, Dao Thi My\nNam, Tran Hoang Nhat\nTuan, Nguyen Phan Duc\n\n")
    r_names.font.size = Pt(11)

    r_ab = p_people.add_run("Approved by\n")
    r_ab.font.bold = True
    r_ab.font.size = Pt(11)
    r_m = p_people.add_run("ThS. Toan, Ha Manh\n\n")
    r_m.font.size = Pt(11)

    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sign.paragraph_format.space_before = Pt(10)
    r_sign1 = p_sign.add_run("User Interface Design Review Panel Representative:\nName\t\t\t\tSignature\t\tDate\n\n")
    r_sign1.font.size = Pt(10)
    r_sign2 = p_sign.add_run("Capstone Project 1 - Mentor:\nName\t\t\t\tSignature\t\tDate\n")
    r_sign2.font.size = Pt(10)

    doc.add_page_break()

    # -------------------------------------------------------------
    # PROJECT INFORMATION (EXACT SAME AS SAMPLE)
    # -------------------------------------------------------------
    doc.add_paragraph().paragraph_format.space_before = Pt(10)
    p_pi = doc.add_paragraph()
    r_pi = p_pi.add_run("PROJECT INFORMATION")
    r_pi.font.bold = True
    r_pi.font.size = Pt(12)

    t_proj = doc.add_table(rows=14, cols=4)
    t_proj.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_proj, color="B0B0B0", sz="4")

    # Format helpers for project info
    def merge_row(row_idx, label, val):
        cell_0 = t_proj.rows[row_idx].cells[0]
        cell_1 = t_proj.rows[row_idx].cells[1]
        for c in t_proj.rows[row_idx].cells[2:]:
            cell_1.merge(c)
        cell_0.text = label
        cell_1.text = val
        set_cell_background(cell_0, "F5F5F5")
        set_cell_margins(cell_0, 80, 80, 100, 100)
        set_cell_margins(cell_1, 80, 80, 100, 100)
        cell_0.paragraphs[0].runs[0].font.bold = True
        cell_0.paragraphs[0].runs[0].font.size = Pt(9)
        cell_1.paragraphs[0].runs[0].font.size = Pt(9)

    merge_row(0, "Project acronym", "SFDS")
    merge_row(1, "Project Title", "“SFDS” – Fraudulent Image Detection and Warning System with Explanations")

    t_proj.rows[2].cells[0].text = "Start Date"
    t_proj.rows[2].cells[1].text = "23 Aug 2026"
    t_proj.rows[2].cells[2].text = "End Date"
    t_proj.rows[2].cells[3].text = "22 Dec 2026"
    for idx in [0, 2]:
        set_cell_background(t_proj.rows[2].cells[idx], "F5F5F5")
        t_proj.rows[2].cells[idx].paragraphs[0].runs[0].font.bold = True
        t_proj.rows[2].cells[idx].paragraphs[0].runs[0].font.size = Pt(9)
        t_proj.rows[2].cells[idx+1].paragraphs[0].runs[0].font.size = Pt(9)

    merge_row(3, "Lead Institution", "International School, Duy Tan University")
    merge_row(4, "Project Mentor", "ThS. Toan, Ha Manh")
    merge_row(5, "Product Owner / Project Leader & contact details", "Hao, Pham Tan  Email: phamtanhao1909@gmail.com  Tel: 0961651933  ID: 29219020823")
    merge_row(6, "Scrum master", "Hao, Pham Tan")
    merge_row(7, "Partner Organization", "Duy Tan University")
    merge_row(8, "Project Web URL", "https://scamshield.local / Render Cloud Deployment")

    # Team members header
    t_proj.rows[9].cells[0].text = "No."
    t_proj.rows[9].cells[1].text = "Team members"
    t_proj.rows[9].cells[2].text = "Email"
    t_proj.rows[9].cells[3].text = "Tel"
    for c in t_proj.rows[9].cells:
        set_cell_background(c, "E8EBF0")
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.size = Pt(9)

    members = [
        ("1", "Hao, Pham Tan (29219020823)", "phamtanhao1909@gmail.com", "0961651933"),
        ("2", "Nhung, Dao Thi My (29209200048)", "mynhung150905@gmail.com", "0376415338"),
        ("3", "Nam, Tran Hoang Nhat (29219423638)", "trannamnhathoang@gmail.com", "0795798736"),
        ("4", "Tuan, Nguyen Phan Duc (29211151140)", "ductuan02072005@gmail.com", "0932442770"),
    ]
    for m_idx, (num, name, email, tel) in enumerate(members, start=10):
        t_proj.rows[m_idx].cells[0].text = num
        t_proj.rows[m_idx].cells[1].text = name
        t_proj.rows[m_idx].cells[2].text = email
        t_proj.rows[m_idx].cells[3].text = tel
        for c in t_proj.rows[m_idx].cells:
            c.paragraphs[0].runs[0].font.size = Pt(9)

    # DOCUMENT APPROVALS
    doc.add_paragraph().paragraph_format.space_before = Pt(14)
    p_da = doc.add_paragraph()
    r_da = p_da.add_run("DOCUMENT APPROVALS\nThe following signatures are required for approval of this document.")
    r_da.font.bold = True
    r_da.font.size = Pt(10)

    t_app = doc.add_table(rows=6, cols=3)
    t_app.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_app, color="B0B0B0", sz="4")
    t_app.rows[0].cells[0].text = "Name / Role"
    t_app.rows[0].cells[1].text = "Signature"
    t_app.rows[0].cells[2].text = "Date"
    for c in t_app.rows[0].cells:
        set_cell_background(c, "E8EBF0")
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.size = Pt(9)

    app_list = [
        "ThS. Toan, Ha Manh - Mentor",
        "Hao, Pham Tan - Student ID: 29219020823 - Scrum Master",
        "Nhung, Dao Thi My - Student ID: 29209200048 - Team Member",
        "Nam, Tran Hoang Nhat - Student ID: 29219423638 - Team Member",
        "Tuan, Nguyen Phan Duc - Student ID: 29211151140 - Team Member",
    ]
    for idx, person in enumerate(app_list, start=1):
        t_app.rows[idx].cells[0].text = person
        t_app.rows[idx].cells[1].text = ""
        t_app.rows[idx].cells[2].text = "18/11/2026"
        for c in t_app.rows[idx].cells:
            c.paragraphs[0].runs[0].font.size = Pt(8.5)

    # REVISION HISTORY
    doc.add_paragraph().paragraph_format.space_before = Pt(14)
    p_rh = doc.add_paragraph()
    r_rh = p_rh.add_run("REVISION HISTORY")
    r_rh.font.bold = True
    r_rh.font.size = Pt(10)

    t_rev = doc.add_table(rows=3, cols=5)
    t_rev.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_rev, color="B0B0B0", sz="4")
    t_rev.rows[0].cells[0].text = "Version"
    t_rev.rows[0].cells[1].text = "Date"
    t_rev.rows[0].cells[2].text = "Comments"
    t_rev.rows[0].cells[3].text = "Author"
    t_rev.rows[0].cells[4].text = "Approval"
    for c in t_rev.rows[0].cells:
        set_cell_background(c, "E8EBF0")
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.size = Pt(9)

    rev_data = [
        ("1.0", "15/10/2026", "Initial Release of UI Design", "Dao Thi My Nhung", "Pham Tan Hao"),
        ("2.0", "18/11/2026", "Official Document aligned with actual codebase", "Pham Tan Hao", "ThS. Ha Manh Toan"),
    ]
    for idx, (ver, dt, comm, auth, appr) in enumerate(rev_data, start=1):
        t_rev.rows[idx].cells[0].text = ver
        t_rev.rows[idx].cells[1].text = dt
        t_rev.rows[idx].cells[2].text = comm
        t_rev.rows[idx].cells[3].text = auth
        t_rev.rows[idx].cells[4].text = appr
        for c in t_rev.rows[idx].cells:
            c.paragraphs[0].runs[0].font.size = Pt(8.5)

    doc.add_page_break()

    # -------------------------------------------------------------
    # TABLE OF CONTENTS
    # -------------------------------------------------------------
    p_toc = doc.add_paragraph()
    r_toc = p_toc.add_run("TABLE OF CONTENTS")
    r_toc.font.bold = True
    r_toc.font.size = Pt(12)

    toc_items = [
        ("1. Introduction", "1"),
        ("  1.1. Purpose", "1"),
        ("  1.2. Scope", "1"),
        ("2. Interface Design", "2"),
        ("  2.1 Login", "2"),
        ("  2.2 Overview", "4"),
        ("  2.3 Multi-Source Scan", "6"),
        ("  2.4 Scan Result & Explanation", "8"),
        ("  2.5 Scan Feedback", "10"),
        ("  2.6 Scan History", "12"),
        ("  2.7 Model Evaluation & Benchmark Dashboard", "14"),
        ("  2.8 Scam Keywords Management", "16"),
        ("  2.9 Training Dataset Management", "18"),
        ("  2.10 AI Models Management", "20"),
        ("  2.11 Visitor Devices Map", "22"),
    ]
    t_toc = doc.add_table(rows=len(toc_items), cols=2)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, (item, pg) in enumerate(toc_items):
        t_toc.rows[i].cells[0].text = item
        t_toc.rows[i].cells[1].text = pg
        p_item = t_toc.rows[i].cells[0].paragraphs[0]
        p_pg = t_toc.rows[i].cells[1].paragraphs[0]
        p_pg.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_item.runs[0].font.size = Pt(9.5)
        p_pg.runs[0].font.size = Pt(9.5)
        if not item.startswith("  "):
            p_item.runs[0].font.bold = True
            p_pg.runs[0].font.bold = True
    set_table_borders(t_toc, color="FFFFFF")

    doc.add_page_break()

    # -------------------------------------------------------------
    # 1. INTRODUCTION (EXACT SAME AS SAMPLE)
    # -------------------------------------------------------------
    doc.add_heading("1. Introduction", level=1)
    
    doc.add_heading("1.1. Purpose", level=2)
    doc.add_paragraph("This specification covers the following aspects:")
    doc.add_paragraph(
        "The documentation provides a detailed description of the user interface (UI) and system design for the "
        "“SFDS – Fraudulent Image Detection and Warning System with Explanations” platform. It explains how the system supports "
        "users and cyber-fraud investigators in detecting fraudulent visual artifacts, phishing messages, deceptive URLs, and fake "
        "invoices through AI-driven multi-modal analytics, enabling data-driven decisions to prevent scams, protect citizens from financial loss, "
        "and provide transparent, explainable evidence."
    )
    doc.add_paragraph(
        "With this documentation, the development team can clearly understand the structure, modules, and design details required "
        "to build a consistent, scalable, and user-friendly solution for real-time scam detection and forensic explanation."
    )

    doc.add_heading("1.2. Scope", level=2)
    doc.add_paragraph(
        "This document presents an overview of the software modules and stages related to multi-source input ingestion, "
        "OCR text extraction, visual forensics (EXIF, Error Level Analysis, Deepfake detection), convolutional neural network Grad-CAM "
        "heatmap overlays, natural language explanations, and administrative management dashboards. It describes the complete "
        "interface architecture, covering both functional and non-functional requirements, and provides justifications for the chosen design decisions."
    )
    doc.add_paragraph("The focus is on:")
    doc.add_paragraph("• Real-time multi-modal scanning and risk estimation from images, QR codes, messages, URLs, and PDF documents.")
    doc.add_paragraph("• Transparent AI visual explanations with Grad-CAM heatmaps, highlighted OCR terms, and plain-language reasoning.")
    doc.add_paragraph("• Privacy-first guest mode with local device storage (localStorage) and frictionless usage without mandatory login.")
    doc.add_paragraph("• Comprehensive administrative control for live rule management, dataset curation, automated model benchmarking, and geographical device tracking.")

    doc.add_page_break()

    # -------------------------------------------------------------
    # 2. INTERFACE DESIGN (EXACT FORMAT WITH TABLE 1..11)
    # -------------------------------------------------------------
    doc.add_heading("2. Interface Design", level=1)

    # 2.1 Login
    doc.add_heading("2.1 Login", level=2)
    p = doc.add_paragraph("Figure 1. UI Login")
    p.runs[0].font.italic = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Table 1. Description UI Login")

    t1_rows = [
        ["1", "heading", "Text Heading", "Font-weight: Bold; Text: \"Administrator sign in\" (Translation of \"Đăng nhập quản trị\")", "Display the form's title"],
        ["2", "subheading", "Text Subheading", "Text: \"Restricted administrator area\" (Translation of \"Khu vực dành riêng cho quản trị viên\")", "Provide brief instruction to the user"],
        ["3", "emailInput", "Input Field", "Placeholder text: \"admin@scamdetector.local\"; Has email icon; Full-width", "Allow admin to enter their email"],
        ["4", "passwordInput", "Input Field", "Placeholder text: \"Enter password\"; Has lock icon; Password visibility toggle", "Allow admin to enter password"],
        ["5", "rememberMeCheckbox", "Checkbox", "Text: \"Remember session\"; Positioned below fields", "Maintain login session on device"],
        ["6", "signInButton", "Button", "Full-width; Solid Purple/Indigo background; Text: \"Sign In\" (Translation of \"Đăng nhập\")", "Submit credentials for JWT authentication"],
        ["7", "googleSsoButton", "SSO Button", "Full-width; Outline button; Google icon; Text: \"Sign in with Google\"", "Authenticate via Google OAuth 2.0 Single Sign-On"],
        ["8", "brandLogo", "Logo + Text", "Positioned top; Icon Shield + Text: \"Scam Shield AI\"", "Display brand identity and system emblem"],
        ["9", "brandTagline", "Text", "Text: \"Multi-Source Cyber Fraud Defense with AI Explanations\"", "Display platform mission tagline"],
        ["10", "guestReturnLink", "Text Link", "Text: \"← Return to public scanner\" (Translation of \"Quay lại trang quét\"); Left-aligned", "Navigate user back to public scan overview"],
    ]
    create_screen_table(doc, "Login", t1_rows)
    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # 2.2 Overview
    doc.add_heading("2.2 Overview", level=2)
    p = doc.add_paragraph("Figure 2. UI Overview")
    p.runs[0].font.italic = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Table 2. Description UI Overview")

    t2_rows = [
        ["1", "topNavbar", "Navigation", "Links: \"Overview\", \"Scan Check\", \"History\", \"Admin Portal\"; Brand Logo; Status Radar", "Provide main navigation across system"],
        ["2", "statusRadar", "Status Widget", "Pulsing radar ring; States: Online (Green), Waking (Amber), Offline (Red)", "Display real-time AI backend health status"],
        ["3", "heroHeading", "Text Heading", "Font-weight: Bold; Text: \"Your safer space for everyday digital life\"", "Display the primary protective greeting"],
        ["4", "heroSubheading", "Text Subheading", "Text: \"Analyze images, suspicious messages, links, or PDF files to detect scams instantly\"", "Explain the platform's multi-modal capabilities"],
        ["5", "startScanButton", "Button", "Large primary button; Pulse glow; Text: \"Start Scam Check\" (Translation of \"Bắt đầu kiểm tra\")", "Directly route user to the interactive scanner"],
        ["6", "featureCard1", "Feature Card", "Title: \"Image & Bills\"; Description: \"OCR text extraction, ELA manipulation, Grad-CAM heatmaps\"", "Highlight fake screenshot and bill detection"],
        ["7", "featureCard2", "Feature Card", "Title: \"Messages & OTP\"; Description: \"Urgency detection, psychological pressure, bank impersonation\"", "Highlight SMS/Zalo scam message analysis"],
        ["8", "featureCard3", "Feature Card", "Title: \"Links & Domains\"; Description: \"PhishVN 21 lexical features, Google Safe Browsing verification\"", "Highlight malicious link and typo-squatting detection"],
        ["9", "featureCard4", "Feature Card", "Title: \"PDF Documents\"; Description: \"Multi-page parsing, embedded QR decoding, scanned document OCR\"", "Highlight document and invoice fraud detection"],
        ["10", "localSummaryStats", "Data Cards", "Metrics: Total Local Checks, Flagged Warnings, Safe Files; Stored in localStorage", "Display transparent summary of client-side history"],
    ]
    create_screen_table(doc, "Overview", t2_rows)
    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # 2.3 Multi-Source Scan
    doc.add_heading("2.3 Multi-Source Scan", level=2)
    p = doc.add_paragraph("Figure 3. UI Multi-Source Scan")
    p.runs[0].font.italic = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Table 3. Description UI Multi-Source Scan")

    t3_rows = [
        ["1", "sourceTabs", "Tab Group", "Tabs: \"Image & QR\", \"Message\", \"Link\", \"PDF document\"; Active state indicator", "Select the input channel for forensic analysis"],
        ["2", "scanViewportHUD", "HUD Canvas", "Square scanning frame; Reticle crosshairs; HUD corners; Animated beam sweep", "Provide high-tech targeting viewport for uploaded proof"],
        ["3", "dropzoneArea", "Dropzone", "Dotted border; Icon Upload; Text: \"Drag & drop image or click to browse (JPG, PNG, up to 15MB)\"", "Allow file selection from user device"],
        ["4", "webcamButton", "Button", "Camera icon; Text: \"Capture with Camera\" (Translation of \"Chụp ảnh từ camera\")", "Trigger physical camera stream to snap proof"],
        ["5", "messageTextarea", "Input Field", "Visible when \"Message\" tab active; Placeholder: \"Paste suspicious SMS or chat message...\"", "Enter text content for NLP rule matching"],
        ["6", "urlInputField", "Input Field", "Visible when \"Link\" tab active; Placeholder: \"https://bank-login-scam.com\"", "Enter target URL for PhishVN lexical examination"],
        ["7", "pdfUploadDropzone", "Dropzone", "Visible when \"PDF\" tab active; Accepts .pdf up to 10 pages / 15MB", "Upload invoice or official announcement PDF"],
        ["8", "quickPresetChips", "Chip Group", "Chips: \"Fake Transfer Receipt\", \"OTP Account Threat\", \"Phishing Link\", \"Job Scam\"", "Populate real-world test cases with one click"],
        ["9", "scanSubmitButton", "Button", "Text: \"Analyze Risk\" (Translation of \"Quét ngay\"); Loading spinner during analysis", "Execute multi-modal inference pipeline"],
        ["10", "resetScanButton", "Button", "Outline button; Text: \"Reset / Clear\"", "Clear viewport and reset inputs"],
    ]
    create_screen_table(doc, "Multi-Source Scan", t3_rows)
    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # 2.4 Scan Result & Explanation
    doc.add_heading("2.4 Scan Result & Explanation", level=2)
    p = doc.add_paragraph("Figure 4. UI Scan Result & Explanation")
    p.runs[0].font.italic = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Table 4. Description UI Scan Result & Explanation")

    t4_rows = [
        ["1", "riskLevelBadge", "Status Badge", "3 States: \"Safe\" (Green), \"Review\" (Amber), \"Dangerous\" (Red)", "Convey instant categorical hazard assessment"],
        ["2", "riskScoreGauge", "Radial Meter", "0-100 scale; Dynamic arc color matching danger level", "Display calibrated composite soft-voting risk score"],
        ["3", "textSubScore", "Score Indicator", "Text: \"Text Risk: X/100\"; Measures OCR text & fraud keyword patterns", "Show risk contribution from textual content"],
        ["4", "visualSubScore", "Score Indicator", "Text: \"Visual Risk: Y/100\"; Measures ELA, EXIF, and deepfake signals", "Show risk contribution from visual manipulation"],
        ["5", "gradCamHeatmapView", "Image Viewer", "Side-by-side comparison of original image and ResNet-18 Grad-CAM heat overlay", "Pinpoint convolutional activation areas triggering phishing label"],
        ["6", "ocrHighlightedText", "Text Box", "Extracted Vietnamese OCR text with red/amber badges highlighting flagged phrases", "Demonstrate exact phrases that triggered fraud detection"],
        ["7", "domainIntelCard", "Info Card", "Displays target URL candidate, PhishVN lexical risk, and Google Safe Browsing state", "Provide background domain reputation check"],
        ["8", "aiExplanationCard", "Callout Card", "Synthesized plain-language reasoning generated by VLM and rule engine", "Explain why the item is dangerous in plain Vietnamese"],
        ["9", "actionChecklist", "Action List", "Checklist: \"Do not transfer money\", \"Do not share OTP\", \"Contact bank hotline\"", "Advise concrete protective steps for the user"],
        ["10", "exportPdfButton", "Button", "Download icon; Text: \"Export Safety Report (PDF)\"", "Generate downloadable forensic evidence summary"],
        ["11", "feedbackButton", "Outline Button", "Thumbs up/down icon; Text: \"Was this result accurate?\"", "Open validation modal to collect user feedback"],
    ]
    create_screen_table(doc, "Scan Result & Explanation", t4_rows)
    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # 2.5 Scan Feedback
    doc.add_heading("2.5 Scan Feedback", level=2)
    p = doc.add_paragraph("Figure 5. UI Scan Feedback")
    p.runs[0].font.italic = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Table 5. Description UI Scan Feedback")

    t5_rows = [
        ["1", "modalHeading", "Text Heading", "Font-weight: Bold; Text: \"Validate Scan Result\" (Translation of \"Xác nhận kết quả\")", "State objective of feedback prompt"],
        ["2", "verdictCorrect", "Radio Card", "Value: \"correct\"; Green check icon; Text: \"Accurate warning / Safe assessment\"", "Record user confirmation of correct detection"],
        ["3", "verdictFalseAlarm", "Radio Card", "Value: \"false_alarm\"; Amber warning icon; Text: \"False Alarm (Benign content)\"", "Report false positive on legitimate content"],
        ["4", "verdictMissedScam", "Radio Card", "Value: \"missed_scam\"; Red hazard icon; Text: \"Missed Scam (Dangerous content)\"", "Report false negative where scam was not flagged"],
        ["5", "noteTextarea", "Input Field", "Textarea; Placeholder: \"Describe what looked suspicious or why the alert was wrong...\"", "Collect qualitative remarks from the user"],
        ["6", "cancelButton", "Button", "Outline button; Text: \"Cancel\"", "Close modal without saving"],
        ["7", "submitFeedbackButton", "Button", "Solid blue/purple; Text: \"Submit Validation\" (Translation of \"Gửi phản hồi\")", "Persist user validation into scan_feedback database"],
    ]
    create_screen_table(doc, "Scan Feedback", t5_rows)
    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # 2.6 Scan History
    doc.add_heading("2.6 Scan History", level=2)
    p = doc.add_paragraph("Figure 6. UI Scan History")
    p.runs[0].font.italic = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Table 6. Description UI Scan History")

    t6_rows = [
        ["1", "pageHeading", "Text Heading", "Text: \"Scan History\" (Translation of \"Lịch sử kiểm tra\")", "Title of history inspection screen"],
        ["2", "severityFilterTabs", "Tabs", "Tabs: \"All\", \"Dangerous\", \"Review\", \"Safe\"; Displaying item counts", "Filter scan sessions by threat level"],
        ["3", "historyCardList", "Card List", "List of past scans with timestamp, file name, input type, and risk badge", "Browse past scan sessions saved in localStorage"],
        ["4", "detailDrawer", "Drawer View", "Slide-over panel displaying full image, Grad-CAM, OCR text, and AI reasoning", "Re-examine detailed forensic output of selected scan"],
        ["5", "clearHistoryButton", "Danger Button", "Text: \"Clear Local History\"; Confirmation modal prompt", "Permanently remove cached checks from device"],
        ["6", "exportHistoryButton", "Button", "Text: \"Export Data (.json / .csv)\"", "Backup local inspection history to file"],
    ]
    create_screen_table(doc, "Scan History", t6_rows)
    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # 2.7 Model Evaluation & Benchmark Dashboard
    doc.add_heading("2.7 Model Evaluation & Benchmark Dashboard", level=2)
    p = doc.add_paragraph("Figure 7. UI Model Evaluation & Benchmark Dashboard")
    p.runs[0].font.italic = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Table 7. Description UI Model Evaluation & Benchmark Dashboard")

    t7_rows = [
        ["1", "runBenchmarkButton", "Button", "Text: \"Run Automated Evaluation\"; Spinner during benchmark run", "Trigger full automated regression test on backend"],
        ["2", "kpiMacroF1", "KPI Card", "Title: \"Macro F1\"; Percentage metric (e.g. 91%); Color-coded progress ring", "Measure balanced accuracy across all 3 risk tiers"],
        ["3", "kpiRecall", "KPI Card", "Title: \"Recall\"; Percentage metric; Subtext: \"Missed alerts count\"", "Monitor sensitivity on genuine fraud instances"],
        ["4", "kpiFalseAlarmRate", "KPI Card", "Title: \"False Alarm Rate (FAR)\"; Subtext: \"Lower is better\"", "Track false positive rate on benign samples"],
        ["5", "kpiExactAccuracy", "KPI Card", "Title: \"Cases Passed\"; Value: \"13/14 (93%)\"", "Display exact 3-level match accuracy on test cases"],
        ["6", "confusionMatrixTable", "Matrix Grid", "3x3 table mapping Expected vs. Actual for Safe, Review, Dangerous", "Analyze inter-class confusion patterns"],
        ["7", "attentionCasesList", "List", "Cards showing failed regression cases with expected vs. actual scores", "Identify edge cases requiring dataset augmentation"],
        ["8", "manualEvaluationForm", "Form", "Inputs for model ID, Macro F1, Recall, FAR, and explanation usefulness", "Allow recording offline test benchmark metrics"],
    ]
    create_screen_table(doc, "Model Evaluation & Benchmark Dashboard", t7_rows)
    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # 2.8 Scam Keywords Management
    doc.add_heading("2.8 Scam Keywords Management", level=2)
    p = doc.add_paragraph("Figure 8. UI Scam Keywords Management")
    p.runs[0].font.italic = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Table 8. Description UI Scam Keywords Management")

    t8_rows = [
        ["1", "pageHeading", "Text Heading", "Text: \"Scam Keyword Management\" (Translation of \"Quản lý từ khóa lừa đảo\")", "Display live rule engine management title"],
        ["2", "keywordInput", "Input Field", "Required; Placeholder: \"Keyword or phrase (e.g. chuyển khoản gấp)\"", "Enter new Vietnamese fraud term or regex"],
        ["3", "categorySelect", "Dropdown", "Options: \"Phishing\", \"Impersonation\", \"Fake invoice\", \"Job scam\", \"Urgent threat\"", "Assign tactical category to keyword"],
        ["4", "weightInput", "Number Input", "Range: 1 to 50; Default value: 10", "Set risk score contribution weight"],
        ["5", "addKeywordButton", "Button", "Text: \"Add Rule\" (Translation of \"Thêm quy tắc\"); Solid button", "Insert new rule dynamically into scam_keywords table"],
        ["6", "activeRulesBadge", "Badge", "Text: \"X active rules\"; Top right corner", "Display count of live keyword rules currently active"],
        ["7", "rulesCardGrid", "Grid", "Cards displaying keyword term, category tag, and weight badge (+15)", "Audit and manage active live rules without redeploying"],
    ]
    create_screen_table(doc, "Scam Keywords Management", t8_rows)
    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # 2.9 Training Dataset Management
    doc.add_heading("2.9 Training Dataset Management", level=2)
    p = doc.add_paragraph("Figure 9. UI Training Dataset Management")
    p.runs[0].font.italic = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Table 9. Description UI Training Dataset Management")

    t9_rows = [
        ["1", "imageUrlInput", "Input Field", "Required; Placeholder: \"image_url or local storage path\"", "Enter image asset path for curated dataset"],
        ["2", "categoryDropdown", "Dropdown", "Options populated from scam_categories table", "Tag sample with official fraud classification"],
        ["3", "anonymizedCheckbox", "Checkbox", "Label: \"Anonymized\"; Confirms PII (identity, bank numbers) redacted", "Enforce legal privacy compliance on training data"],
        ["4", "verifiedCheckbox", "Checkbox", "Label: \"Verified\"; Confirms expert ground-truth validation", "Flag high-confidence training samples"],
        ["5", "addDatasetButton", "Button", "Text: \"Add Dataset\" (Translation of \"Thêm dataset\")", "Save sample into training_dataset database table"],
        ["6", "datasetTable", "Data List", "Columns: Category ID, Verification Status, Uploader ID", "Review inventory of model training and validation samples"],
    ]
    create_screen_table(doc, "Training Dataset Management", t9_rows)
    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # 2.10 AI Models Management
    doc.add_heading("2.10 AI Models Management", level=2)
    p = doc.add_paragraph("Figure 10. UI AI Models Management")
    p.runs[0].font.italic = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Table 10. Description UI AI Models Management")

    t10_rows = [
        ["1", "versionNameInput", "Input Field", "Required; Placeholder: \"version_name (e.g. PhishVN-v3.1)\"", "Enter unique registered version name"],
        ["2", "descriptionInput", "Input Field", "Placeholder: \"description (architecture, parameters, dataset)\"", "Enter model architecture and training configuration"],
        ["3", "isActiveCheckbox", "Checkbox", "Label: \"Active\"; Toggle production serving status", "Designate active model version for live inference"],
        ["4", "addModelButton", "Button", "Text: \"Add Model\" (Translation of \"Thêm mô hình\")", "Register new model entry into ai_models table"],
        ["5", "modelsList", "Card List", "Cards showing Version Name, Active Badge, and Registration Date", "Track version history and promote models to production"],
    ]
    create_screen_table(doc, "AI Models Management", t10_rows)
    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # 2.11 Visitor Devices Map
    doc.add_heading("2.11 Visitor Devices Map", level=2)
    p = doc.add_paragraph("Figure 11. UI Visitor Devices Map")
    p.runs[0].font.italic = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Table 11. Description UI Visitor Devices Map")

    t11_rows = [
        ["1", "leafletWorldMap", "Interactive Map", "Leaflet OpenStreetMap canvas; Zoom, Pan, and FitBounds controls", "Display geographical distribution of client devices"],
        ["2", "deviceMarker", "Circle Marker", "Circle marker with accuracy radius indicating approximate IP location", "Pin approximate network location of scanning visitor"],
        ["3", "markerTooltip", "Tooltip Popup", "Shows device name, OS platform, browser version, and approximate IP area", "Provide device details upon hover or tap"],
        ["4", "refreshDevicesButton", "Button", "Refresh icon; Text: \"Refresh\"", "Reload latest visitor records from database"],
        ["5", "deviceSidebarList", "Sidebar List", "Cards for all detected devices; Button \"All Devices\" for world overview", "Select individual device to focus and zoom map"],
        ["6", "deviceCardItem", "Card Item", "Displays device name, IP address, platform, visit counter, and last seen time", "Inspect visitor activity frequency and client info"],
        ["7", "openStreetMapLink", "Text Link", "Text: \"Open full map ↗\"; Opens OpenStreetMap with exact coordinates", "Open coordinates on native OpenStreetMap site"],
    ]
    create_screen_table(doc, "Visitor Devices Map", t11_rows)

    doc.save(output_docx_path)
    print(f"File created successfully: {output_docx_path}")

if __name__ == "__main__":
    out = r"D:\scam-detector\C1SE.06_UserInterfaceDesign_v1.0.docx"
    generate_exact_uid_document(out)

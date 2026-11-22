import os
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
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

def set_table_borders(table, color="B0B0B0", sz="4", val="single"):
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
    table = doc.add_table(rows=len(rows_data) + 2, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="B0B0B0", sz="4")

    # Row 0: Screen Name spanning across 5 columns
    cell_0 = table.rows[0].cells[0]
    for c in table.rows[0].cells[1:]:
        cell_0.merge(c)
    cell_0.text = screen_name
    set_cell_background(cell_0, "E2ECE8") # Soft green-gray
    set_cell_margins(cell_0, top=140, bottom=140, left=150, right=150)
    p0 = cell_0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run0 = p0.runs[0]
    run0.font.bold = True
    run0.font.size = Pt(10.5)
    run0.font.name = "Arial"
    run0.font.color.rgb = RGBColor(27, 77, 62) # DTU Green #1B4D3E
    prevent_row_split(table.rows[0])
    set_repeat_header(table.rows[0])

    # Row 1: Column Headers
    headers = ["No.", "Field name", "Type", "Require", "Target"]
    set_repeat_header(table.rows[1])
    prevent_row_split(table.rows[1])
    for idx, h_text in enumerate(headers):
        cell = table.rows[1].cells[idx]
        cell.text = h_text
        set_cell_background(cell, "EDF4F1")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.runs[0]
        run.font.bold = True
        run.font.size = Pt(9.5)
        run.font.name = "Arial"
        run.font.color.rgb = RGBColor(20, 20, 20)

    # Data Rows
    col_widths = [Inches(0.45), Inches(1.35), Inches(1.1), Inches(2.2), Inches(1.9)]
    for r_idx, row_values in enumerate(rows_data, start=2):
        row = table.rows[r_idx]
        prevent_row_split(row)
        bg = "F9FCFA" if r_idx % 2 == 1 else "FFFFFF"
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

    for row in table.rows:
        for c_idx, width in enumerate(col_widths):
            row.cells[c_idx].width = width

    return table

def build_complete_figma_uid():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    logo_path = Path("artifacts/database-doc-fix/word/media/image1.png")

    # ================= COVER PAGE =================
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
    r_t.font.color.rgb = RGBColor(27, 77, 62)

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

    # ================= PROJECT INFORMATION =================
    doc.add_paragraph().paragraph_format.space_before = Pt(10)
    p_pi = doc.add_paragraph()
    r_pi = p_pi.add_run("PROJECT INFORMATION")
    r_pi.font.bold = True
    r_pi.font.size = Pt(12)

    t_proj = doc.add_table(rows=14, cols=4)
    t_proj.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_proj, color="B0B0B0", sz="4")

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
        ("1.0", "15/10/2026", "Initial UI Design Specification", "Nhung, Dao Thi My", "Hao, Pham Tan"),
        ("2.0", "18/11/2026", "Official Document matching Figma Prototype", "Hao, Pham Tan", "ThS. Toan, Ha Manh"),
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

    # ================= TABLE OF CONTENTS =================
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
        ("  2.2 Register", "4"),
        ("  2.3 Dashboard", "6"),
        ("  2.4 Image Scan", "8"),
        ("  2.5 Scan History", "10"),
        ("  2.6 Training Dataset", "12"),
        ("  2.7 AI Models", "14"),
        ("  2.8 Model Evaluation", "16"),
        ("  2.9 System Activity Logs", "18"),
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

    # ================= 1. INTRODUCTION =================
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
    doc.add_paragraph("• Comprehensive administrative control for live rule management, dataset curation, automated model benchmarking, and system activity auditing.")

    doc.add_page_break()

    # ================= 2. INTERFACE DESIGN =================
    doc.add_heading("2. Interface Design", level=1)

    screen_data_map = [
        # (title, fig_num, fig_title, tbl_num, tbl_title, img_fname, rows)
        (
            "2.1 Login", 1, "UI Login", 1, "Description UI Login", "figma_1_login.png",
            [
                ["1", "brandBanner", "Image + Text", "Green left panel; Text: \"Welcome back!\" (Chào mừng bạn trở lại!)", "Display welcoming graphic and security motto"],
                ["2", "heading", "Text Heading", "Font-weight: Bold; Text: \"Log in\" (Đăng nhập)", "Display the login form title"],
                ["3", "accountInput", "Input Field", "Placeholder: \"Enter account\"; User icon (left); Full-width", "Allow user to enter login username/email"],
                ["4", "passwordInput", "Input Field", "Placeholder: \"Enter password\"; Lock icon (left); Visibility toggle", "Allow user to enter password securely"],
                ["5", "forgotPasswordLink", "Text Link", "Text: \"Forgot password?\" (Quên mật khẩu?); Right-aligned", "Direct user to password recovery flow"],
                ["6", "signInButton", "Button", "Full-width; Solid Forest Green background; Text: \"Log in\" (Đăng nhập)", "Submit credentials for authentication"],
                ["7", "signUpPrompt", "Text + Link", "Text: \"Don't have an account? REGISTER\" (Chưa có tài khoản? ĐĂNG KÝ)", "Navigate user to registration screen"],
            ]
        ),
        (
            "2.2 Register", 2, "UI Register", 2, "Description UI Register", "figma_2_register.png",
            [
                ["1", "brandBanner", "Image + Text", "Green left panel; Text: \"Protecting you against online fraud.\" (Bảo vệ bạn trước những trò lừa đảo.)", "Display system protection branding"],
                ["2", "heading", "Text Heading", "Font-weight: Bold; Text: \"Create an account\" (Tạo tài khoản)", "Display the registration form title"],
                ["3", "fullNameInput", "Input Field", "Placeholder: \"Enter full name\"; User icon (left)", "Accept user's display name"],
                ["4", "accountInput", "Input Field", "Placeholder: \"Enter username/account\"; Half-width", "Accept account login identifier"],
                ["5", "emailInput", "Input Field", "Placeholder: \"Enter email address\"; Half-width", "Accept user contact email"],
                ["6", "passwordInput", "Input Field", "Placeholder: \"Enter password\"; Masked with toggle icon", "Accept secret login password"],
                ["7", "confirmPasswordInput", "Input Field", "Placeholder: \"Re-enter password\"; Masked with toggle icon", "Confirm password matches accurately"],
                ["8", "signUpButton", "Button", "Full-width; Solid Forest Green; Text: \"REGISTER\" (ĐĂNG KÝ)", "Submit new user registration"],
                ["9", "signInPrompt", "Text + Link", "Text: \"Already have an account? LOG IN\" (Đã có tài khoản? ĐĂNG NHẬP)", "Navigate existing user to login screen"],
            ]
        ),
        (
            "2.3 Dashboard", 3, "UI Dashboard", 3, "Description UI Dashboard", "figma_3_dashboard.png",
            [
                ["1", "sidebarNav", "Navigation Menu", "Logo \"Scam Detector\"; Links: Overview, Image Scan, History, Dataset, Models, Logs", "Provide persistent side navigation"],
                ["2", "dashboardBanner", "Header Banner", "Gradient green background; Slogan: \"Digital safety starts with an inspected image.\"", "Highlight current system mission and welcome banner"],
                ["3", "kpiTotalScans", "KPI Card", "Title: \"Total Image Checks\"; Numerical metric with growth index", "Display total volume of scans performed"],
                ["4", "kpiFraudDetected", "KPI Card", "Title: \"Fraud Detections\"; Numerical metric of flagged threats", "Monitor threat detection frequency"],
                ["5", "kpiSafetyRate", "KPI Card", "Title: \"Safety Confidence Rate\"; Percentage metric (e.g. 98.4%)", "Evaluate proportion of benign verified checks"],
                ["6", "trafficChart", "Bar/Line Chart", "Interactive chart visualizing scan volume and detected fraud trends by day/week", "Analyze historical scam threat patterns"],
                ["7", "recentActivityTable", "Data Table", "Columns: ID, Source, Threat Type, Risk Score, Timestamp, Action", "Provide quick inspection of latest scan cases"],
            ]
        ),
        (
            "2.4 Image Scan", 4, "UI Image Scan", 4, "Description UI Image Scan", "figma_4_scan.png",
            [
                ["1", "pageHeaderBanner", "Section Banner", "Forest Green banner; Title: \"Image Inspection Room\" (Phòng kiểm định hình ảnh)", "Identify the scan workspace"],
                ["2", "uploadDropzone", "Dropzone Card", "Dotted border; Shield/Upload icon; Text: \"Upload image to inspect\" (Tải hình ảnh lên để quét)", "Accept JPG/PNG screenshot or bill file upload"],
                ["3", "selectFileButton", "Button", "Forest Green button; Text: \"Select Image from Device\"", "Open native OS file selector dialog"],
                ["4", "scanInspectorCard", "Data Panel", "Right panel; Displays image dimensions, OCR recognition status, and visual forensics", "Show forensic parameters of loaded proof"],
                ["5", "riskScoreGauge", "Meter Gauge", "Radial or bar score from 0 to 100; Color-coded by threat tier", "Display comprehensive multi-modal scam score"],
                ["6", "analyzeButton", "Action Button", "Text: \"Run Detection & Explain\" (Kiểm định ngay); Loading state", "Trigger AI OCR, ELA, and Grad-CAM pipeline"],
            ]
        ),
        (
            "2.5 Scan History", 5, "UI Scan History", 5, "Description UI Scan History", "figma_5_history.png",
            [
                ["1", "historyHeaderBanner", "Section Banner", "Forest Green banner; Title: \"Scan History\" (Lịch sử quét)", "Display title of history repository"],
                ["2", "searchFilterBar", "Input + Select", "Search input by file name / scan ID; Dropdown filter by threat level (All, Safe, Danger)", "Filter past scan records efficiently"],
                ["3", "historyDataTable", "Data Table", "Columns: Scan ID, Image Name, Input Type, Risk Score, Risk Level, Scanned Date, Action", "Display structured log of prior checks"],
                ["4", "riskLevelBadge", "Status Badge", "Badge: \"An toàn\" (Green), \"Nghi ngờ\" (Amber), \"Nguy hiểm\" (Red)", "Visual indicator of scan severity"],
                ["5", "viewDetailAction", "Action Link", "Text: \"View Detail\" (Xem chi tiết); Click opens forensic breakdown", "Open full OCR, Grad-CAM, and reasoning report"],
                ["6", "exportCsvButton", "Button", "Text: \"Export History (.csv)\"; Outline button", "Download past scan records for offline reporting"],
            ]
        ),
        (
            "2.6 Training Dataset", 6, "UI Training Dataset", 6, "Description UI Training Dataset", "figma_6_dataset.png",
            [
                ["1", "pageTitle", "Text Heading", "Title: \"Training Dataset Management\"", "Identify the curated dataset management module"],
                ["2", "imageUrlInput", "Input Field", "Placeholder: \"image_url or file path\"; Full-width", "Input image asset reference for model training"],
                ["3", "categorySelect", "Dropdown", "Options populated from scam_categories (Phishing, Fake invoice, etc.)", "Assign ground-truth scam category"],
                ["4", "anonymizedCheck", "Checkbox", "Label: \"Anonymized\"; Confirms PII has been redacted", "Certify compliance with data privacy regulations"],
                ["5", "verifiedCheck", "Checkbox", "Label: \"Verified\"; Confirms expert validation of label", "Mark verified sample for model training split"],
                ["6", "addDatasetButton", "Button", "Solid Forest Green; Text: \"Add Dataset\" (Thêm dataset)", "Save record into training_dataset table"],
                ["7", "datasetTable", "Data List", "Columns: ID, Image URL, Category, Verified Status, Uploaded By", "Review curated training samples inventory"],
            ]
        ),
        (
            "2.7 AI Models", 7, "UI AI Models", 7, "Description UI AI Models", "figma_7_models.png",
            [
                ["1", "pageTitle", "Text Heading", "Title: \"AI Models Management\"", "Identify model checkpoint management module"],
                ["2", "versionNameInput", "Input Field", "Placeholder: \"version_name (e.g. PhishVN-v3.1, ResNet18-v2)\"", "Register unique model version identifier"],
                ["3", "descriptionInput", "Input Field", "Placeholder: \"description (architecture, parameters, dataset)\"", "Record model architecture and training parameters"],
                ["4", "isActiveCheckbox", "Checkbox", "Label: \"Active\"; Toggle production inference state", "Mark model checkpoint to serve live traffic"],
                ["5", "addModelButton", "Button", "Solid Forest Green; Text: \"Add Model\" (Thêm mô hình)", "Save new AI model entry into ai_models table"],
                ["6", "modelsList", "Card List", "Cards showing Version Name, Active Badge, Description, Creation Date", "Manage active model lifecycle and deployment"],
            ]
        ),
        (
            "2.8 Model Evaluation", 8, "UI Model Evaluation", 8, "Description UI Model Evaluation", "figma_8_evaluation.png",
            [
                ["1", "pageTitle", "Text Heading", "Title: \"Model Evaluation & Benchmark\" (Đánh giá Model)", "Identify AI benchmark testing module"],
                ["2", "modelSelect", "Dropdown / Input", "Placeholder: \"ai_model_id\"; Selects registered checkpoint", "Bind evaluation record to specific model version"],
                ["3", "macroF1Input", "Number Input", "Placeholder: \"macro_f1 (e.g. 0.9125)\"", "Record Macro F1 multi-class classification score"],
                ["4", "recallInput", "Number Input", "Placeholder: \"recall (e.g. 0.9450)\"", "Record fraud detection recall rate"],
                ["5", "falseAlarmInput", "Number Input", "Placeholder: \"false_alarm_rate (e.g. 0.0320)\"", "Record false alarm rate on benign cases"],
                ["6", "usefulnessInput", "Number Input", "Placeholder: \"explanation_usefulness (e.g. 0.8800)\"", "Record expert score assessing explanation clarity"],
                ["7", "saveEvaluationBtn", "Button", "Solid Forest Green; Text: \"Save Evaluation\" (Lưu đánh giá)", "Persist benchmark metrics into model_evaluations table"],
                ["8", "evaluationHistory", "Data List", "Shows historical F1, Recall, FAR scores and evaluated date", "Audit model quality evolution across versions"],
            ]
        ),
        (
            "2.9 System Activity Logs", 9, "UI System Activity Logs", 9, "Description UI System Activity Logs", "figma_9_logs.png",
            [
                ["1", "pageTitle", "Text Heading", "Title: \"System Activity Logs\" (Nhật ký hệ thống)", "Identify security audit log module"],
                ["2", "actionTypeInput", "Input Field", "Placeholder: \"action_type (e.g. UPDATE_RULE, RETRAIN_MODEL)\"", "Input administrative event category"],
                ["3", "descriptionInput", "Input Field", "Placeholder: \"description of administrative change\"", "Input detailed operational remarks"],
                ["4", "addLogButton", "Button", "Solid Forest Green; Text: \"Add Log\" (Ghi nhật ký)", "Append audit record into system_activity_logs table"],
                ["5", "logsDataTable", "Data Table", "Columns: ID, Admin ID, Action Type, Description, Created Timestamp", "Review chronological administrative audit trail"],
            ]
        ),
    ]

    for title, f_num, f_title, t_num, t_title, img_fname, rows in screen_data_map:
        doc.add_heading(title, level=2)
        
        # Embed Figma high-res screenshot
        img_p = Path("artifacts/figma_clean_screens") / img_fname
        if img_p.exists():
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.add_run().add_picture(str(img_p), width=Inches(6.2))
        
        p_fig = doc.add_paragraph(f"Figure {f_num}. {f_title}")
        p_fig.runs[0].font.italic = True
        p_fig.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph(f"Table {t_num}. {t_title}")
        clean_name = title.split(" ", 1)[1] if " " in title else title
        create_screen_table(doc, clean_name, rows)
        doc.add_paragraph().paragraph_format.space_after = Pt(16)

    out_docx = r"D:\scam-detector\C1SE.06_UserInterfaceDesign_v1.0.docx"
    doc.save(out_docx)
    print("Successfully built exact Figma-aligned UID document:", out_docx)

if __name__ == "__main__":
    build_complete_figma_uid()

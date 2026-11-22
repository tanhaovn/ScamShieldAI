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

def set_cell_margins(cell, top=80, bottom=80, left=110, right=110):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="CCCCCC", sz="4", val="single"):
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

def format_custom_table(table, header_bg="1B4D3E", alt_bg="F9FCFA"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="B8C4C0")
    for r_idx, row in enumerate(table.rows):
        prevent_row_split(row)
        if r_idx == 0:
            set_repeat_header(row)
            for cell in row.cells:
                set_cell_background(cell, header_bg)
                set_cell_margins(cell, top=110, bottom=110, left=120, right=120)
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in p.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
                        run.font.size = Pt(8.5)
                        run.font.name = "Arial"
        else:
            bg = alt_bg if r_idx % 2 == 1 else "FFFFFF"
            for cell in row.cells:
                set_cell_background(cell, bg)
                set_cell_margins(cell, top=70, bottom=70, left=100, right=100)
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(8)
                        run.font.name = "Arial"
                        run.font.color.rgb = RGBColor(40, 40, 40)

def build_product_backlog_doc(out_path):
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    logo_path = Path("artifacts/database-doc-fix/word/media/image1.png")

    # ================= COVER PAGE =================
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_after = Pt(14)
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
    p_doc_type.paragraph_format.space_before = Pt(16)
    p_doc_type.paragraph_format.space_after = Pt(4)
    r_dt = p_doc_type.add_run("Product Backlog & Sprint Planning")
    r_dt.font.bold = True
    r_dt.font.size = Pt(22)
    r_dt.font.color.rgb = RGBColor(160, 20, 20)

    p_ver = doc.add_paragraph()
    p_ver.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_v = p_ver.add_run("Version 1.0\nDate: Nov 18th, 2026\nAgile / Scrum Backlog Specification\n")
    r_v.font.size = Pt(10.5)
    r_v.font.italic = True
    r_v.font.color.rgb = RGBColor(80, 80, 80)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(18)
    r_t = p_title.add_run("Fraudulent Image Detection and Warning System with Explanations (SFDS)")
    r_t.font.bold = True
    r_t.font.size = Pt(14)
    r_t.font.color.rgb = RGBColor(27, 77, 62)

    p_people = doc.add_paragraph()
    p_people.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cb = p_people.add_run("Submitted by\n")
    r_cb.font.bold = True
    r_cb.font.size = Pt(11)
    r_names = p_people.add_run("Hao, Pham Tan (Scrum Master)\nNhung, Dao Thi My\nNam, Tran Hoang Nhat\nTuan, Nguyen Phan Duc\n\n")
    r_names.font.size = Pt(10.5)

    r_ab = p_people.add_run("Approved by\n")
    r_ab.font.bold = True
    r_ab.font.size = Pt(11)
    r_m = p_people.add_run("ThS. Toan, Ha Manh (Project Mentor)\n\n")
    r_m.font.size = Pt(10.5)

    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sign.paragraph_format.space_before = Pt(10)
    r_sign1 = p_sign.add_run("Scrum Review Panel Representative:\nName\t\t\t\tSignature\t\tDate\n\n")
    r_sign1.font.size = Pt(9.5)
    r_sign2 = p_sign.add_run("Capstone Project 1 - Mentor:\nName\t\t\t\tSignature\t\tDate\n")
    r_sign2.font.size = Pt(9.5)

    doc.add_page_break()

    # ================= PROJECT METADATA =================
    doc.add_heading("PROJECT INFORMATION", level=2)
    t_proj = doc.add_table(rows=14, cols=4)
    set_table_borders(t_proj, color="B0B0B0", sz="4")

    def merge_row(row_idx, label, val):
        cell_0 = t_proj.rows[row_idx].cells[0]
        cell_1 = t_proj.rows[row_idx].cells[1]
        for c in t_proj.rows[row_idx].cells[2:]:
            cell_1.merge(c)
        cell_0.text = label
        cell_1.text = val
        set_cell_background(cell_0, "F5F5F5")
        set_cell_margins(cell_0, 70, 70, 90, 90)
        set_cell_margins(cell_1, 70, 70, 90, 90)
        cell_0.paragraphs[0].runs[0].font.bold = True
        cell_0.paragraphs[0].runs[0].font.size = Pt(8.5)
        cell_1.paragraphs[0].runs[0].font.size = Pt(8.5)

    merge_row(0, "Project acronym", "SFDS")
    merge_row(1, "Project Title", "“SFDS” – Fraudulent Image Detection and Warning System with Explanations")

    t_proj.rows[2].cells[0].text = "Start Date"
    t_proj.rows[2].cells[1].text = "18 Oct 2026"
    t_proj.rows[2].cells[2].text = "End Date"
    t_proj.rows[2].cells[3].text = "15 Dec 2026"
    for idx in [0, 2]:
        set_cell_background(t_proj.rows[2].cells[idx], "F5F5F5")
        t_proj.rows[2].cells[idx].paragraphs[0].runs[0].font.bold = True
        t_proj.rows[2].cells[idx].paragraphs[0].runs[0].font.size = Pt(8.5)
        t_proj.rows[2].cells[idx+1].paragraphs[0].runs[0].font.size = Pt(8.5)

    merge_row(3, "Lead Institution", "International School, Duy Tan University")
    merge_row(4, "Project Mentor", "ThS. Toan, Ha Manh")
    merge_row(5, "Scrum Master / Leader & contact", "Hao, Pham Tan  Email: phamtanhao1909@gmail.com  Tel: 0961651933  ID: 29219020823")
    merge_row(6, "Jira Backlog URL", "https://mynhung150905.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog")
    merge_row(7, "Partner Organization", "Duy Tan University")
    merge_row(8, "Total Story Points / Sprints", "289 Story Points across 6 Sprints (41 Work Items)")

    t_proj.rows[9].cells[0].text = "No."
    t_proj.rows[9].cells[1].text = "Team members"
    t_proj.rows[9].cells[2].text = "Email"
    t_proj.rows[9].cells[3].text = "Tel"
    for c in t_proj.rows[9].cells:
        set_cell_background(c, "E2ECE8")
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.size = Pt(8.5)

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
            c.paragraphs[0].runs[0].font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    doc.add_heading("DOCUMENT APPROVALS", level=2)
    t_app = doc.add_table(rows=6, cols=3)
    set_table_borders(t_app, color="B0B0B0", sz="4")
    t_app.rows[0].cells[0].text = "Name / Role"
    t_app.rows[0].cells[1].text = "Signature"
    t_app.rows[0].cells[2].text = "Date"
    for c in t_app.rows[0].cells:
        set_cell_background(c, "E2ECE8")
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.size = Pt(8.5)

    app_list = [
        "ThS. Toan, Ha Manh - Project Mentor",
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

    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    doc.add_heading("REVISION HISTORY", level=2)
    t_rev = doc.add_table(rows=3, cols=5)
    set_table_borders(t_rev, color="B0B0B0", sz="4")
    t_rev.rows[0].cells[0].text = "Version"
    t_rev.rows[0].cells[1].text = "Date"
    t_rev.rows[0].cells[2].text = "Comments"
    t_rev.rows[0].cells[3].text = "Author"
    t_rev.rows[0].cells[4].text = "Approval"
    for c in t_rev.rows[0].cells:
        set_cell_background(c, "E2ECE8")
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.size = Pt(8.5)

    rev_data = [
        ("1.0", "18/10/2026", "Initial Backlog Planning & Sprint 1-3 Setup", "Hao, Pham Tan", "ThS. Toan, Ha Manh"),
        ("2.0", "18/11/2026", "Mid-term Sprint Progress Update (Sprint 1-4 sync with Jira)", "Hao, Pham Tan", "ThS. Toan, Ha Manh"),
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
    doc.add_heading("TABLE OF CONTENTS", level=1)
    toc_items = [
        ("1. Introduction & Scrum Methodology", "1"),
        ("   1.1. Project Overview & Objectives", "1"),
        ("   1.2. Scrum Roles & Workflow", "1"),
        ("   1.3. Sprint Timeline & Milestones", "2"),
        ("2. Epic Definitions & Architecture Breakdown", "3"),
        ("   2.1. Epic 1: Infrastructure, Architecture & Database", "3"),
        ("   2.2. Epic 2: Visual Processing Core, Forensics & OCR", "3"),
        ("   2.3. Epic 3: AI Fraud Detection Models & PhishVN", "4"),
        ("   2.4. Epic 4: AI Explainability & Recommendations", "4"),
        ("   2.5. Epic 5: Frontend Interface & Admin Dashboard", "5"),
        ("   2.6. Epic 6: Testing, Quality Assurance & Deployment", "5"),
        ("3. Product Backlog (Master Jira User Story Table)", "6"),
        ("4. Sprint Execution & Backlog Details", "10"),
        ("   4.1. Sprint 1 (18 Oct – 24 Oct) - Infrastructure & Base Setup", "10"),
        ("   4.2. Sprint 2 (18 Oct – 28 Oct) - OCR, QR & PhishVN Integration", "11"),
        ("   4.3. Sprint 3 (29 Oct – 10 Nov) - ResNet18, VLM & Visual Forensics", "12"),
        ("   4.4. Sprint 4 (11 Nov – 21 Nov) - Admin System, Feedback & PDF", "13"),
        ("   4.5. Sprint 5 (22 Nov – 5 Dec) - Benchmark, Deepfake & Geo-map", "14"),
        ("   4.6. Sprint 6 (6 Dec – 15 Dec) - Production Hardening & UAT", "15"),
        ("5. Velocity & Burndown Summary", "16"),
    ]
    t_toc = doc.add_table(rows=len(toc_items), cols=2)
    for i, (item, pg) in enumerate(toc_items):
        t_toc.rows[i].cells[0].text = item
        t_toc.rows[i].cells[1].text = pg
        p_item = t_toc.rows[i].cells[0].paragraphs[0]
        p_pg = t_toc.rows[i].cells[1].paragraphs[0]
        p_pg.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_item.runs[0].font.size = Pt(9.5)
        p_pg.runs[0].font.size = Pt(9.5)
        if not item.startswith("   "):
            p_item.runs[0].font.bold = True
            p_pg.runs[0].font.bold = True
    set_table_borders(t_toc, color="FFFFFF")

    doc.add_page_break()

    # ================= 1. INTRODUCTION & SCRUM =================
    doc.add_heading("1. Introduction & Scrum Methodology", level=1)
    
    doc.add_heading("1.1. Project Overview & Objectives", level=2)
    doc.add_paragraph(
        "Hệ thống 'Fraudulent Image Detection and Warning System with Explanations' (SFDS) được phát triển nhằm giải quyết "
        "thách thức gia tăng của các thủ đoạn lừa đảo trực tuyến tại Việt Nam thông qua ảnh chụp màn hình giả mạo, tin nhắn đe dọa, "
        "biên lai chuyển tiền ngân hàng sửa đổi, đường link giả mạo và tài liệu PDF độc hại. Dự án kết hợp công nghệ xử lý ảnh (OCR, ELA, EXIF), "
        "học sâu (ResNet-18, PhishVN lexical analysis), mô hình ngôn ngữ thị giác (VLM) và hệ thống quy tắc ngữ nghĩa thời gian thực, "
        "cung cấp cảnh báo rủi ro định lượng và giải thích bằng chứng minh bạch cho người dùng."
    )

    doc.add_heading("1.2. Scrum Roles & Workflow", level=2)
    doc.add_paragraph(
        "Dự án áp dụng khung phương pháp Agile / Scrum theo chuẩn quản lý đồ án Capstone Đại học Duy Tân:\n"
        "• Scrum Master: Phạm Tấn Hảo (Điều phối Sprint, giải phóng trở ngại kỹ thuật, kiến trúc Backend).\n"
        "• Product Owner / Team Members: Đào Thị Mỹ Nhung (UI/UX, Frontend React), Trần Hoàng Nhật Nam (AI Models, PhishVN, ResNet-18), "
        "Nguyễn Phan Đức Tuấn (Backend APIs, Database, OCR, Security).\n"
        "• Project Mentor: ThS. Hà Mạnh Toàn (Thẩm định tiến độ, tư vấn kiến trúc và chuẩn mực đánh giá đồ án)."
    )

    doc.add_heading("1.3. Sprint Timeline & Milestones", level=2)
    doc.add_paragraph("Kế hoạch phát triển gồm 6 Sprint kế tiếp nhau kéo dài từ 18/10/2026 đến 15/12/2026:")
    
    t_sprints = doc.add_table(rows=7, cols=5)
    t_sprints.rows[0].cells[0].text = "Sprint No."
    t_sprints.rows[0].cells[1].text = "Timeline"
    t_sprints.rows[0].cells[2].text = "Committed Points"
    t_sprints.rows[0].cells[3].text = "Work Items"
    t_sprints.rows[0].cells[4].text = "Status (as of Nov 18)"
    
    s_rows = [
        ("Sprint 1", "18 Oct – 24 Oct", "50 pts", "7 items (SCRUM-1..8, 17..18)", "Done (100%)"),
        ("Sprint 2", "18 Oct – 28 Oct", "47 pts", "7 items (SCRUM-9, 15..16, 19..22)", "Done (100%)"),
        ("Sprint 3", "29 Oct – 10 Nov", "50 pts", "7 items (SCRUM-23..29)", "Done (100%)"),
        ("Sprint 4", "11 Nov – 21 Nov", "50 pts", "7 items (SCRUM-30..36)", "In Progress (16 Done / 34 Active)"),
        ("Sprint 5", "22 Nov – 05 Dec", "50 pts", "7 items (SCRUM-37..43)", "To Do (Ready for backlog)"),
        ("Sprint 6", "06 Dec – 15 Dec", "42 pts", "6 items (SCRUM-44..49)", "To Do (UAT & Deployment)"),
    ]
    for idx, (sp, time_val, pts, items, st) in enumerate(s_rows, start=1):
        t_sprints.rows[idx].cells[0].text = sp
        t_sprints.rows[idx].cells[1].text = time_val
        t_sprints.rows[idx].cells[2].text = pts
        t_sprints.rows[idx].cells[3].text = items
        t_sprints.rows[idx].cells[4].text = st
    format_custom_table(t_sprints, header_bg="1B4D3E")

    doc.add_page_break()

    # ================= 2. EPICS DEFINITIONS =================
    doc.add_heading("2. Epic Definitions & Architecture Breakdown", level=1)
    
    epics = [
        ("Epic 1: Hạ tầng và Cơ sở dữ liệu (Infrastructure & Database)", 
         "Bao gồm thiết lập cấu hình máy chủ FastAPI, cơ sở dữ liệu quan hệ (PostgreSQL trên Render và SQLite cục bộ), xác thực bảo mật JWT, Google OAuth 2.0 Single Sign-On, hệ thống log kiểm toán và theo dõi thiết bị truy cập."),
        ("Epic 2: Lõi Xử lý Ảnh & Trích xuất Dữ liệu (Visual Core & OCR)",
         "Bao gồm bộ công cụ trích xuất văn bản tiếng Việt Tesseract OCR 5.x, giải mã mã QR ẩn trong ảnh/tài liệu, phân tích siêu dữ liệu EXIF, phân tích mức độ lỗi nén (Error Level Analysis - ELA) và bóc tách tài liệu PDF nhiều trang."),
        ("Epic 3: Mô hình AI & Phát hiện lừa đảo (AI Models & PhishVN)",
         "Tích hợp mô hình học sâu ResNet-18 phân loại ảnh hóa đơn/chuyển khoản, bộ phân loại liên kết độc hại PhishVN v3.1 dựa trên 21 đặc trưng từ vựng (lexical features), công cụ kiểm tra danh tiếng Google Safe Browsing và bộ từ điển từ khóa tiếng Việt rủi ro cao."),
        ("Epic 4: Giải thích AI & Khuyến nghị an toàn (AI Explainability)",
         "Bao gồm lớp giải thích trực quan Grad-CAM trên mạng nơ-ron tích chập, tích hợp Vision-Language Model (VLM - SmolVLM/Gemini Flash) sinh lời giải thích suy luận tự nhiên bằng tiếng Việt và xây dựng danh mục hướng dẫn phòng vệ."),
        ("Epic 5: Giao diện người dùng & Quản trị (Frontend & Admin Dashboard)",
         "Xây dựng ứng dụng Single Page Application bằng React 18, Vite 5, bộ quét đa nguồn với khung ngắm HUD Radar, hiển thị kết quả trực quan, quản lý lịch sử quét cục bộ và toàn bộ hệ thống quản trị (Dataset, Models, Benchmark, Keywords, Visitor Map Leaflet)."),
        ("Epic 6: Kiểm thử, Tối ưu hóa & Triển khai (QA & Deployment)",
         "Thực thi bộ kiểm thử tự động Black-box regression suite trên 25 kịch bản, chạy đo đạc Benchmark tự động (Macro F1, Recall, FAR), kiểm thử chịu tải và đóng gói Docker container triển khai Production.")
    ]

    for title, desc in epics:
        doc.add_heading(title, level=2)
        doc.add_paragraph(desc)

    doc.add_page_break()

    # ================= 3. MASTER PRODUCT BACKLOG TABLE =================
    doc.add_heading("3. Product Backlog (Master Jira Backlog Table)", level=1)
    doc.add_paragraph("Bảng Master Product Backlog tổng hợp toàn bộ 41 hạng mục công việc từ Jira của nhóm dự án (SCRUM-1 đến SCRUM-49):")

    backlog_data = [
        # Id, Heading, As a, I want to, so that, Acceptance Criteria, Priority, Status, Type, Sprint, Pts, Assignee
        ["SCRUM-17", "Story 1: Thiết lập kiến trúc Backend & CSDL", "Backend Dev", "Thiết lập khung FastAPI và database models", "Hệ thống có nền tảng lưu trữ và API chuẩn REST", "FastAPI chạy ổn định, models ánh xạ đầy đủ 11 bảng CSDL", "High", "Done", "Story", "Sprint 1", "8", "Pham Tan Hao"],
        ["SCRUM-18", "Story 2: Thiết kế khung giao diện cơ bản", "UI Dev", "Xây dựng khung giao diện React và hệ thống điều hướng", "Người dùng có thể chuyển đổi giữa các màn hình ứng dụng", "Giao diện React chạy cổng 5173, Navbar hoạt động mượt mà", "High", "Done", "Story", "Sprint 1", "8", "Dao Thi My Nhung"],
        ["SCRUM-1", "Task 1: Cấu hình môi trường FastAPI & Docker", "DevOps", "Tạo Dockerfile và cấu hình môi trường Python 3.12", "Đảm bảo môi trường chạy đồng nhất trên dev và cloud", "Docker build thành công, requirements.txt cài đặt chuẩn xác", "Medium", "Done", "Task", "Sprint 1", "8", "Pham Tan Hao"],
        ["SCRUM-2", "Task 2: Thiết lập SQLAlchemy ORM & Schema", "Database Dev", "Khởi tạo kết nối SQLAlchemy hỗ trợ SQLite và PostgreSQL", "Ứng dụng linh hoạt chuyển đổi giữa dev cục bộ và production", "Kết nối DB tự động tạo bảng khi khởi động, không lỗi pool", "High", "Done", "Task", "Sprint 1", "8", "Nguyen Phan Duc Tuan"],
        ["SCRUM-6", "Task 3: Khởi tạo dự án Frontend React & Vite", "Frontend Dev", "Setup dự án React 18, Vite 5, Leaflet và styles", "Có nền tảng giao diện SPA tối ưu tốc độ tải trang", "Vite build hoàn tất, cấu hình theme sáng/tối và đa ngôn ngữ", "Medium", "Done", "Task", "Sprint 1", "8", "Tran Hoang Nhat Nam"],
        ["SCRUM-7", "Task 4: Cài đặt Tesseract OCR tiếng Việt", "AI Dev", "Cấu hình pytesseract và file ngôn ngữ vie.traineddata", "Backend có khả năng nhận dạng chữ tiếng Việt từ ảnh", "Trích xuất được văn bản có dấu từ ảnh thử nghiệm", "Medium", "Done", "Task", "Sprint 1", "5", "Tran Hoang Nhat Nam"],
        ["SCRUM-8", "Task 5: Thiết lập môi trường Pytest CI/CD", "QA Engineer", "Xây dựng cấu trúc tests/ và cấu hình pytest.ini", "Đảm bảo mã nguồn được tự động kiểm thử hồi quy", "Chạy lệnh pytest vượt qua toàn bộ ca test cơ sở", "Medium", "Done", "Task", "Sprint 1", "5", "Pham Tan Hao"],
        
        # Sprint 2
        ["SCRUM-9", "Story 3: Xử lý OCR & giải mã QR từ ảnh", "User", "Tải ảnh hóa đơn/tin nhắn để đọc văn bản và link QR", "Phát hiện nhanh nội dung ẩn và đường link độc hại trong mã", "OCR trích xuất chính xác >85% từ ngữ, tự động giải mã QR URL", "High", "Done", "Story", "Sprint 2", "8", "Nguyen Phan Duc Tuan"],
        ["SCRUM-15", "Story 4: Tích hợp mô hình URL PhishVN", "User", "Kiểm tra độ tin cậy của các đường link tìm thấy trong ảnh", "Cảnh báo sớm các tên miền lừa đảo, giả mạo ngân hàng", "Trích xuất 21 đặc trưng lexical, HistGradientBoosting phân loại", "High", "Done", "Story", "Sprint 2", "8", "Nguyen Phan Duc Tuan"],
        ["SCRUM-16", "Story 5: Xây dựng bộ quy tắc từ khóa lừa đảo", "Admin", "Quản lý từ điển cụm từ lừa đảo tiếng Việt kèm trọng số", "Risk Engine tính điểm chính xác theo ngữ cảnh áp lực", "Nhận diện từ khóa khẩn cấp, tài chính; cộng điểm tương ứng", "High", "Done", "Story", "Sprint 2", "5", "Pham Tan Hao"],
        ["SCRUM-19", "Story 6: Giao diện quét đa nguồn Multi-Source", "User", "Dùng giao diện quét hiện đại với 4 tab (Ảnh, Chữ, Link, PDF)", "Dễ dàng kiểm tra bất kỳ bằng chứng nghi vấn nào", "HUD Radar trực quan, drag-drop ảnh mượt mà, phản hồi nhanh", "High", "Done", "Story", "Sprint 2", "8", "Dao Thi My Nhung"],
        ["SCRUM-20", "Story 7: Xác thực JWT & Google OAuth SSO", "Admin", "Đăng nhập an toàn bằng tài khoản quản trị hoặc Google", "Bảo vệ các API cấu hình dữ liệu và theo dõi hệ thống", "Sinh token JWT hợp lệ, xác thực Google Token ID chuẩn xác", "High", "Done", "Story", "Sprint 2", "8", "Pham Tan Hao"],
        ["SCRUM-21", "Task 6: Viết kiểm thử hồi quy OCR & QR API", "QA Engineer", "Viết script tự động kiểm tra endpoint /check-image", "Đảm bảo luồng trích xuất chữ và giải mã QR không bị lỗi", "Test case bao phủ ảnh hóa đơn mẫu và ảnh chứa mã QR", "Medium", "Done", "Task", "Sprint 2", "5", "Pham Tan Hao"],
        ["SCRUM-22", "Task 7: Tối ưu tải ảnh & Chụp WebCam", "Frontend Dev", "Bổ sung tính năng chụp ảnh từ WebCam thiết bị", "Người dùng di động hoặc laptop có thể chụp trực tiếp màn hình", "Mở camera mượt mà, chụp và nạp ảnh vào khung quét tức thì", "Medium", "Done", "Task", "Sprint 2", "5", "Dao Thi My Nhung"],

        # Sprint 3
        ["SCRUM-23", "Story 8: Mô hình ResNet-18 phân loại ảnh", "AI Engineer", "Phân tích đặc trưng thị giác của ảnh chụp màn hình", "Nhận diện dấu vết giả mạo bố cục giao diện ngân hàng", "ResNet-18 trích xuất đặc trưng và dự đoán nhãn phishing", "High", "Done", "Story", "Sprint 3", "8", "Nguyen Phan Duc Tuan"],
        ["SCRUM-24", "Story 9: Tích hợp Google Safe Browsing API", "Security Dev", "Đối chiếu URL với cơ sở dữ liệu mối đe dọa toàn cầu", "Xác nhận uy tín tên miền từ nguồn dữ liệu chính thức", "API trả về danh sách mối đe dọa (Malware, Social Engineering)", "High", "Done", "Story", "Sprint 3", "5", "Nguyen Phan Duc Tuan"],
        ["SCRUM-25", "Story 10: Tích hợp Vision-Language Model (VLM)", "User", "Nhận lời giải thích chi tiết lý do ảnh bị coi là lừa đảo", "Hiểu rõ cơ chế rủi ro để không bị kẻ xấu lừa gạt", "VLM sinh giải thích tự nhiên, logic từ ảnh gốc và Grad-CAM", "High", "Done", "Story", "Sprint 3", "8", "Pham Tan Hao"],
        ["SCRUM-26", "Story 11: Module giám định pháp y ELA & EXIF", "Forensic Dev", "Phát hiện dấu hiệu chỉnh sửa cục bộ và phần mềm đồ họa", "Bóc trần ảnh biên lai chuyển tiền bị photoshop số tiền", "ELA hiển thị vùng nén bất thường, EXIF cảnh báo Canva/Photoshop", "High", "Done", "Story", "Sprint 3", "8", "Pham Tan Hao"],
        ["SCRUM-27", "Story 12: Giao diện kết quả quét & Khuyến nghị", "User", "Xem đồng hồ điểm rủi ro, phân loại mức độ và việc cần làm", "Có ngay hành động cụ thể để bảo vệ tài sản cá nhân", "Badge màu trực quan (An toàn/Nghi ngờ/Nguy hiểm), checklist rõ ràng", "High", "Done", "Story", "Sprint 3", "8", "Dao Thi My Nhung"],
        ["SCRUM-28", "Task 8: Bounding box highlight từ khóa trên ảnh", "Frontend Dev", "Vẽ khung viền đỏ xung quanh các từ khóa nhạy cảm trên ảnh", "Người dùng thấy rõ vị trí câu chữ có dấu hiệu lừa đảo", "Tọa độ SVG chính xác theo tỷ lệ ảnh gốc, tooltip giải thích", "Medium", "Done", "Task", "Sprint 3", "5", "Dao Thi My Nhung"],
        ["SCRUM-29", "Task 9: Kiểm thử tích hợp chuỗi phân tích đa tầng", "QA Engineer", "Kiểm thử phối hợp giữa Text Risk và Visual Risk", "Điểm rủi ro tổng hợp phản ánh cân bằng cả 2 khía cạnh", "Các luồng ảnh thuần chữ và ảnh photoshop cho điểm số chuẩn xác", "High", "Done", "Task", "Sprint 3", "8", "Pham Tan Hao"],

        # Sprint 4
        ["SCRUM-30", "Story 13: Admin Dashboard quản lý quy tắc", "Admin", "Xem danh sách và thêm mới từ khóa lừa đảo trực tiếp", "Cập nhật kịp thời chiêu thức lừa đảo mới mà không cần deploy", "Giao diện quản lý từ khóa, danh mục và trọng số hoạt động tốt", "High", "In Progress", "Story", "Sprint 4", "8", "Dao Thi My Nhung"],
        ["SCRUM-31", "Story 14: Hiển thị bản đồ nhiệt Grad-CAM", "User", "Xem bản đồ nhiệt trực quan vùng ảnh kích hoạt dự đoán AI", "Tăng tính minh bạch và độ tin cậy của mô hình học sâu", "Hiển thị ảnh Grad-CAM cạnh ảnh gốc, chú thích vùng tập trung", "High", "In Progress", "Story", "Sprint 4", "8", "Dao Thi My Nhung"],
        ["SCRUM-32", "Story 15: Module phân tích tài liệu PDF", "User", "Tải tệp PDF hóa đơn hoặc công văn thông báo nghi ngờ", "Bóc tách văn bản và mã QR trên các trang tài liệu PDF", "Hỗ trợ tệp PDF tối đa 10 trang, OCR trực tiếp các trang scan", "High", "Done", "Story", "Sprint 4", "8", "Nguyen Phan Duc Tuan"],
        ["SCRUM-33", "Story 16: CSDL tiếp nhận phản hồi người dùng", "Admin", "Lưu trữ đánh giá đúng/sai từ người dùng vào CSDL", "Thu thập dữ liệu kiểm định để huấn luyện cải tiến mô hình", "Bảng scan_feedback lưu trữ verdict, note, risk score đầy đủ", "High", "Done", "Story", "Sprint 4", "8", "Pham Tan Hao"],
        ["SCRUM-34", "Task 10: Tối ưu cấu hình CSDL Render Cloud", "Backend Dev", "Cấu hình connection pool psycopg cho PostgreSQL Render", "Hệ thống hoạt động ổn định khi nhiều người dùng cùng quét", "Tự động tái tạo kết nối, xử lý lỗi drop connection hiệu quả", "High", "In Progress", "Task", "Sprint 4", "8", "Pham Tan Hao"],
        ["SCRUM-35", "Task 11: Xây dựng Modal gửi phản hồi", "Frontend Dev", "Hộp thoại cho phép người dùng đánh giá kết quả quét", "Thu thập phản ánh cảnh báo sai hoặc lừa đảo bị bỏ sót", "Modal mở mượt mà sau khi có kết quả, gửi dữ liệu về API an toàn", "Medium", "In Progress", "Task", "Sprint 4", "5", "Dao Thi My Nhung"],
        ["SCRUM-36", "Task 12: Bộ kiểm thử Black-box regression", "QA Engineer", "Chạy tự động 25 kịch bản kiểm thử black-box qua HTTP", "Phát hiện sớm lỗi hồi quy trên toàn bộ hệ thống API", "Xuất báo cáo kết quả chi tiết dưới định dạng JSON", "Medium", "In Progress", "Task", "Sprint 4", "5", "Pham Tan Hao"],

        # Sprint 5
        ["SCRUM-37", "Story 17: Công cụ tự động đo Benchmark Model", "AI Engineer", "Chạy benchmark đánh giá Macro F1, Recall, FAR tự động", "Đánh giá chất lượng mô hình định lượng và khoa học", "Hiển thị Ma trận nhầm lẫn (Confusion Matrix) trên Dashboard", "High", "To Do", "Story", "Sprint 5", "8", "Nguyen Phan Duc Tuan"],
        ["SCRUM-38", "Story 18: Nâng cấp mô hình phát hiện Deepfake", "AI Engineer", "Phát hiện khuôn mặt bị hoán đổi hoặc tạo bởi generative AI", "Ngăn chặn lừa đảo mạo danh khuôn mặt người thân gọi video", "Mô hình deepfake phân tích tần số và kết cấu da đạt độ tin cậy cao", "High", "To Do", "Story", "Sprint 5", "8", "Nguyen Phan Duc Tuan"],
        ["SCRUM-39", "Story 19: Tinh chỉnh trọng số Soft-voting", "AI Engineer", "Tối ưu hóa công thức kết hợp Text Score và Visual Score", "Giảm tỷ lệ cảnh báo sai trên các mẫu ảnh đời thực", "FAR giảm xuống dưới 5%, độ nhạy trên các ca lừa đảo đạt >95%", "High", "To Do", "Story", "Sprint 5", "8", "Pham Tan Hao"],
        ["SCRUM-40", "Story 20: Giám sát thiết bị truy cập Leaflet Map", "Admin", "Xem bản đồ thế giới hiển thị các thiết bị đã quét", "Nắm bắt phạm vi phân bố và loại thiết bị người dùng sử dụng", "Tích hợp OpenStreetMap và Leaflet, hiển thị vị trí mạng IP gần đúng", "High", "To Do", "Story", "Sprint 5", "8", "Pham Tan Hao"],
        ["SCRUM-41", "Task 13: Xây dựng trang quản trị Device Map", "Frontend Dev", "Hiển thị danh sách thiết bị bên cạnh bản đồ tương tác", "Admin có thể nhấp chọn từng thiết bị để phóng to bản đồ", "Sidebar liệt kê thiết bị, click marker hiển thị tooltip chi tiết", "Medium", "To Do", "Task", "Sprint 5", "5", "Dao Thi My Nhung"],
        ["SCRUM-42", "Task 14: Kiểm thử chịu tải API với Locust", "QA Engineer", "Đo đạc khả năng đáp ứng đồng thời 50-100 người dùng", "Đảm bảo máy chủ không bị nghẽn khi có đột biến truy cập", "Thời gian phản hồi trung bình <2.5 giây dưới tải 50 VUs", "High", "To Do", "Task", "Sprint 5", "8", "Nguyen Phan Duc Tuan"],
        ["SCRUM-43", "Task 15: Kiểm thử bảo mật an toàn ứng dụng", "Security Dev", "Rà soát lỗ hổng OWASP Top 10, SQLi, XSS, Path Traversal", "Bảo vệ an toàn dữ liệu người dùng và hạ tầng máy chủ", "Mã nguồn đạt chuẩn bảo mật, không có lỗ hổng nghiêm trọng", "Medium", "To Do", "Task", "Sprint 5", "5", "Pham Tan Hao"],

        # Sprint 6
        ["SCRUM-44", "Story 21: Kiểm thử chấp nhận người dùng (UAT)", "Product Owner", "Cho người dùng thử nghiệm thực tế với 50 tình huống", "Đảm bảo tính dễ dùng và độ chính xác thực tế của hệ thống", "Khảo sát người dùng đạt điểm hài lòng SUS >80 điểm", "High", "To Do", "Story", "Sprint 6", "8", "Dao Thi My Nhung"],
        ["SCRUM-45", "Story 22: Tự động hóa triển khai Production", "DevOps", "Cấu hình CI/CD triển khai tự động lên Render qua Docker", "Hệ thống luôn được cập nhật phiên bản mới nhất an toàn", "Mỗi commit vào nhánh main tự động build và deploy trơn tru", "High", "To Do", "Story", "Sprint 6", "8", "Pham Tan Hao"],
        ["SCRUM-46", "Task 16: Tối ưu hóa hiệu năng phản hồi <1.5s", "Backend Dev", "Tối ưu hóa pipeline xử lý ảnh và caching kết quả OCR", "Người dùng nhận kết quả kiểm tra tức thì", "Thời gian phản hồi trung bình giảm còn dưới 1.5 giây", "High", "To Do", "Task", "Sprint 6", "8", "Pham Tan Hao"],
        ["SCRUM-47", "Task 17: Hoàn thiện tài liệu hướng dẫn sử dụng", "Technical Writer", "Viết cẩm nang hướng dẫn sử dụng cho người dân và Admin", "Người dùng dễ dàng tra cứu cách nhận diện lừa đảo", "Tài liệu minh họa chi tiết, hình ảnh chụp giao diện rõ ràng", "Medium", "To Do", "Task", "Sprint 6", "8", "Dao Thi My Nhung"],
        ["SCRUM-48", "Task 18: Tổng hợp số liệu đo đạc thực nghiệm", "AI Engineer", "Tổng hợp bảng số liệu Macro F1, Recall, FAR cho báo cáo", "Cung cấp bằng chứng thực nghiệm khoa học cho hội đồng", "Báo cáo thực nghiệm có đầy đủ biểu đồ so sánh và phân tích", "Medium", "To Do", "Task", "Sprint 6", "5", "Tran Hoang Nhat Nam"],
        ["SCRUM-49", "Task 19: Đóng gói mã nguồn & Kịch bản bảo vệ", "Scrum Master", "Rà soát toàn bộ repository, seed data và slide thuyết minh", "Đảm bảo buổi bảo vệ đồ án tốt nghiệp diễn ra hoàn hảo", "Slide thuyết trình ấn tượng, demo trực tiếp mượt mà", "High", "To Do", "Task", "Sprint 6", "5", "Nguyen Phan Duc Tuan"],
    ]

    t_backlog = doc.add_table(rows=len(backlog_data)+1, cols=9)
    t_backlog.rows[0].cells[0].text = "Jira ID"
    t_backlog.rows[0].cells[1].text = "Work Item Heading"
    t_backlog.rows[0].cells[2].text = "Type"
    t_backlog.rows[0].cells[3].text = "Sprint"
    t_backlog.rows[0].cells[4].text = "Points"
    t_backlog.rows[0].cells[5].text = "Priority"
    t_backlog.rows[0].cells[6].text = "Status"
    t_backlog.rows[0].cells[7].text = "Assignee"
    t_backlog.rows[0].cells[8].text = "Acceptance Criteria Summary"

    for idx, row in enumerate(backlog_data, start=1):
        t_backlog.rows[idx].cells[0].text = row[0]
        t_backlog.rows[idx].cells[1].text = row[1]
        t_backlog.rows[idx].cells[2].text = row[8]
        t_backlog.rows[idx].cells[3].text = row[9]
        t_backlog.rows[idx].cells[4].text = row[10]
        t_backlog.rows[idx].cells[5].text = row[6]
        t_backlog.rows[idx].cells[6].text = row[7]
        t_backlog.rows[idx].cells[7].text = row[11]
        t_backlog.rows[idx].cells[8].text = row[5]

    format_custom_table(t_backlog, header_bg="1B4D3E")

    doc.add_page_break()

    # ================= 4. SPRINT-BY-SPRINT BREAKDOWN =================
    doc.add_heading("4. Sprint Execution & Backlog Details", level=1)
    
    sprint_details = [
        ("4.1. Sprint 1 (18 Oct – 24 Oct) - Infrastructure & Base Setup", "Sprint 1", "50", "50", "Done", 
         "Thiết lập nền móng kiến trúc Backend FastAPI, cơ sở dữ liệu SQLAlchemy, khởi tạo khung giao diện React 18 và cài đặt công cụ OCR Tesseract."),
        ("4.2. Sprint 2 (18 Oct – 28 Oct) - OCR, QR & PhishVN Integration", "Sprint 2", "47", "47", "Done", 
         "Hoàn thiện luồng OCR trích xuất chữ tiếng Việt, tự động giải mã mã QR độc hại, tích hợp mô hình PhishVN kiểm tra URL và hoàn thiện giao diện quét HUD."),
        ("4.3. Sprint 3 (29 Oct – 10 Nov) - ResNet18, VLM & Visual Forensics", "Sprint 3", "50", "50", "Done", 
         "Tích hợp mô hình học sâu ResNet-18 phân loại ảnh, công cụ ELA & EXIF phát hiện ảnh sửa đổi, VLM sinh giải thích tự nhiên và vẽ bounding box tô sáng từ khóa."),
        ("4.4. Sprint 4 (11 Nov – 21 Nov) - Admin System, Feedback & PDF", "Sprint 4", "50", "16", "In Progress", 
         "Xây dựng Admin Dashboard quản lý từ khóa, hiển thị bản đồ nhiệt Grad-CAM, bóc tách tệp PDF nhiều trang và thu thập phản hồi người dùng."),
        ("4.5. Sprint 5 (22 Nov – 5 Dec) - Benchmark, Deepfake & Geo-map", "Sprint 5", "50", "0", "To Do", 
         "Xây dựng công cụ đo Benchmark tự động (Macro F1, Recall, FAR), nâng cấp mô hình Deepfake, tinh chỉnh trọng số soft-voting và bản đồ thiết bị Leaflet Map."),
        ("4.6. Sprint 6 (6 Dec – 15 Dec) - Production Hardening & UAT", "Sprint 6", "42", "0", "To Do", 
         "Kiểm thử chấp nhận người dùng (UAT), tối ưu hóa thời gian phản hồi dưới 1.5 giây, tự động hóa CI/CD Docker lên Render và chuẩn bị kịch bản bảo vệ đồ án.")
    ]

    for title, sp_name, comm_pts, done_pts, status, goal in sprint_details:
        doc.add_heading(title, level=2)
        p_goal = doc.add_paragraph()
        r_g = p_goal.add_run(f"Sprint Goal: {goal}\n")
        r_g.font.italic = True
        r_meta = p_goal.add_run(f"Committed Points: {comm_pts} pts | Completed Points: {done_pts} pts | Status: {status}")
        r_meta.font.bold = True
        r_meta.font.color.rgb = RGBColor(27, 77, 62)

        # Filter items for this sprint
        sp_items = [item for item in backlog_data if item[9] == sp_name]
        t_sp = doc.add_table(rows=len(sp_items)+1, cols=6)
        t_sp.rows[0].cells[0].text = "ID"
        t_sp.rows[0].cells[1].text = "User Story / Task Description"
        t_sp.rows[0].cells[2].text = "Type"
        t_sp.rows[0].cells[3].text = "Pts"
        t_sp.rows[0].cells[4].text = "Status"
        t_sp.rows[0].cells[5].text = "Assignee"
        
        for idx, it in enumerate(sp_items, start=1):
            t_sp.rows[idx].cells[0].text = it[0]
            t_sp.rows[idx].cells[1].text = it[1]
            t_sp.rows[idx].cells[2].text = it[8]
            t_sp.rows[idx].cells[3].text = it[10]
            t_sp.rows[idx].cells[4].text = it[7]
            t_sp.rows[idx].cells[5].text = it[11]
        format_custom_table(t_sp, header_bg="204060")
        doc.add_paragraph().paragraph_format.space_after = Pt(10)

    doc.add_page_break()

    # ================= 5. VELOCITY & BURNDOWN =================
    doc.add_heading("5. Velocity & Burndown Summary", level=1)
    doc.add_paragraph(
        "Tổng hợp tiến độ và năng suất (Velocity) của nhóm phát triển qua các Sprint:\n"
        "• Vận tốc trung bình (Average Velocity): ~49 Story Points / Sprint.\n"
        "• Tổng điểm Story Points toàn dự án: 289 Story Points.\n"
        "• Tỷ lệ hoàn thành lũy kế hiện tại (đến hết Sprint 3 và một phần Sprint 4): 163 / 289 points (~56.4%).\n"
        "• Dự báo tiến độ: Với tốc độ hoàn thành ổn định 47-50 points mỗi 10-14 ngày, dự án hoàn toàn đảm bảo tiến độ nghiệm thu đúng hạn vào ngày 15/12/2026."
    )

    t_velo = doc.add_table(rows=7, cols=5)
    t_velo.rows[0].cells[0].text = "Sprint"
    t_velo.rows[0].cells[1].text = "Committed"
    t_velo.rows[0].cells[2].text = "Completed"
    t_velo.rows[0].cells[3].text = "Velocity"
    t_velo.rows[0].cells[4].text = "Burndown Trend"

    v_data = [
        ("Sprint 1", "50 pts", "50 pts", "50 pts", "On schedule (100%)"),
        ("Sprint 2", "47 pts", "47 pts", "47 pts", "On schedule (100%)"),
        ("Sprint 3", "50 pts", "50 pts", "50 pts", "On schedule (100%)"),
        ("Sprint 4", "50 pts", "16 pts (active)", "Pending end date", "On track (Nov 21)"),
        ("Sprint 5", "50 pts", "0 pts (planned)", "Target: 50 pts", "Planned (Dec 05)"),
        ("Sprint 6", "42 pts", "0 pts (planned)", "Target: 42 pts", "Planned (Dec 15)"),
    ]
    for idx, row in enumerate(v_data, start=1):
        for c_idx, val in enumerate(row):
            t_velo.rows[idx].cells[c_idx].text = val
    format_custom_table(t_velo, header_bg="1B4D3E")

    doc.save(out_path)
    print("Successfully built Product Backlog Word document:", out_path)

if __name__ == "__main__":
    out_file = r"D:\scam-detector\C1SE.06_ProductBacklog_SprintPlanning_v1.0.docx"
    build_product_backlog_doc(out_file)

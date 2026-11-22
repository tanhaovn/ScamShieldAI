import os
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def create_element(name):
    return OxmlElement(name)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
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

def format_table(table, header_bg="8B0000", alt_bg="F9F9F9"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="CCCCCC")
    for r_idx, row in enumerate(table.rows):
        prevent_row_split(row)
        if r_idx == 0:
            set_repeat_header(row)
            for cell in row.cells:
                set_cell_background(cell, header_bg)
                set_cell_margins(cell, top=140, bottom=140, left=150, right=150)
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in p.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
                        run.font.size = Pt(9.5)
                        run.font.name = "Arial"
        else:
            bg = alt_bg if r_idx % 2 == 1 else "FFFFFF"
            for cell in row.cells:
                set_cell_background(cell, bg)
                set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(9)
                        run.font.name = "Arial"

def build_uid_document(output_path):
    doc = Document()
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # Styles setup
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Arial'
    font.size = Pt(10.5)
    font.color.rgb = RGBColor(40, 40, 40)

    logo_path = Path("artifacts/database-doc-fix/word/media/image1.png")
    
    # COVER PAGE
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if logo_path.exists():
        p_logo.add_run().add_picture(str(logo_path), width=Inches(3.2))
    
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("International School\nCapstone Project 1\nCMU-SE 450 – C1SE.06\n")
    r_inst.font.bold = True
    r_inst.font.size = Pt(13)
    r_inst.font.color.rgb = RGBColor(120, 20, 20)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(24)
    p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run("User Interface Design")
    r_title.font.bold = True
    r_title.font.size = Pt(24)
    r_title.font.color.rgb = RGBColor(160, 20, 20)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Version 1.0\nDate: November 18, 2026\n")
    r_sub.font.size = Pt(11)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(100, 100, 100)

    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_before = Pt(14)
    p_proj.paragraph_format.space_after = Pt(28)
    r_proj = p_proj.add_run("Fraudulent Image Detection and Warning System with Explanations (SFDS)")
    r_proj.font.bold = True
    r_proj.font.size = Pt(15)
    r_proj.font.color.rgb = RGBColor(20, 40, 80)

    p_subm = doc.add_paragraph()
    p_subm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_subm = p_subm.add_run("Submitted by:\n")
    r_subm.font.bold = True
    r_subm.font.size = Pt(11)
    r_names = p_subm.add_run("Hao, Pham Tan\nNhung, Dao Thi My\nNam, Tran Hoang Nhat\nTuan, Nguyen Phan Duc\n\n")
    r_names.font.size = Pt(11)

    r_app = p_subm.add_run("Approved by:\n")
    r_app.font.bold = True
    r_app.font.size = Pt(11)
    r_mentor = p_subm.add_run("Toan, Ha Manh")
    r_mentor.font.size = Pt(11)

    doc.add_page_break()

    # PROJECT INFORMATION & APPROVALS
    h_meta = doc.add_heading("PROJECT INFORMATION", level=2)
    h_meta.paragraph_format.space_after = Pt(8)
    
    t_info = doc.add_table(rows=6, cols=4)
    t_info.rows[0].cells[0].text = "Project acronym"
    t_info.rows[0].cells[1].text = "SFDS"
    t_info.rows[0].cells[2].text = "Project Title"
    t_info.rows[0].cells[3].text = "Fraudulent Image Detection and Warning System with Explanations"
    
    t_info.rows[1].cells[0].text = "Start Date"
    t_info.rows[1].cells[1].text = "23 Aug 2026"
    t_info.rows[1].cells[2].text = "End Date"
    t_info.rows[1].cells[3].text = "22 Dec 2026"
    
    t_info.rows[2].cells[0].text = "Lead Institution"
    t_info.rows[2].cells[1].text = "International School, Duy Tan University"
    t_info.rows[2].cells[2].text = "Project Mentor"
    t_info.rows[2].cells[3].text = "ThS. Toan, Ha Manh"
    
    t_info.rows[3].cells[0].text = "Scrum master / Leader"
    t_info.rows[3].cells[1].text = "Hao, Pham Tan (phamtanhao1909@gmail.com)"
    t_info.rows[3].cells[2].text = "Partner Organization"
    t_info.rows[3].cells[3].text = "Duy Tan University"

    t_info.rows[4].cells[0].text = "Team Members"
    t_info.rows[4].cells[1].text = "Hao, Pham Tan (29219020823)\nNhung, Dao Thi My (29209200048)"
    t_info.rows[4].cells[2].text = "Team Members"
    t_info.rows[4].cells[3].text = "Nam, Tran Hoang Nhat (29219423638)\nTuan, Nguyen Phan Duc (29211151140)"

    t_info.rows[5].cells[0].text = "Course & Code"
    t_info.rows[5].cells[1].text = "CMU-SE 450 – C1SE.06"
    t_info.rows[5].cells[2].text = "System Scope"
    t_info.rows[5].cells[3].text = "AI Multi-source Scam Detector & Explainer"
    format_table(t_info, header_bg="204060")

    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    doc.add_heading("DOCUMENT APPROVALS", level=2)
    t_app = doc.add_table(rows=6, cols=3)
    t_app.rows[0].cells[0].text = "Role / Stakeholder"
    t_app.rows[0].cells[1].text = "Signature"
    t_app.rows[0].cells[2].text = "Date"
    
    approvers = [
        "ThS. Toan, Ha Manh (Project Mentor)",
        "Hao, Pham Tan (Student ID: 29219020823 - Scrum Master)",
        "Nhung, Dao Thi My (Student ID: 29209200048 - UI/UX Designer)",
        "Nam, Tran Hoang Nhat (Student ID: 29219423638 - AI Engineer)",
        "Tuan, Nguyen Phan Duc (Student ID: 29211151140 - Backend Dev)"
    ]
    for idx, app_name in enumerate(approvers, start=1):
        t_app.rows[idx].cells[0].text = app_name
        t_app.rows[idx].cells[1].text = ""
        t_app.rows[idx].cells[2].text = "18/11/2026"
    format_table(t_app, header_bg="204060")

    doc.add_paragraph().paragraph_format.space_before = Pt(12)
    doc.add_heading("REVISION HISTORY", level=2)
    t_rev = doc.add_table(rows=3, cols=5)
    t_rev.rows[0].cells[0].text = "Version"
    t_rev.rows[0].cells[1].text = "Date"
    t_rev.rows[0].cells[2].text = "Comments"
    t_rev.rows[0].cells[3].text = "Author"
    t_rev.rows[0].cells[4].text = "Approval"

    t_rev.rows[1].cells[0].text = "0.9"
    t_rev.rows[1].cells[1].text = "15/10/2026"
    t_rev.rows[1].cells[2].text = "Initial UI mockups and scan workflow"
    t_rev.rows[1].cells[3].text = "Nhung, Dao Thi My"
    t_rev.rows[1].cells[4].text = "Hao, Pham Tan"

    t_rev.rows[2].cells[0].text = "1.0"
    t_rev.rows[2].cells[1].text = "18/11/2026"
    t_rev.rows[2].cells[2].text = "Official User Interface Design Document for SFDS Capstone"
    t_rev.rows[2].cells[3].text = "SFDS Dev Team"
    t_rev.rows[2].cells[4].text = "Eng. Ha Manh Toan"
    format_table(t_rev, header_bg="204060")

    doc.add_page_break()

    # TABLE OF CONTENTS
    h_toc = doc.add_heading("TABLE OF CONTENTS", level=1)
    h_toc.paragraph_format.space_after = Pt(12)
    toc_lines = [
        ("1. Introduction", "4"),
        ("   1.1 Purpose", "4"),
        ("   1.2 Scope", "4"),
        ("2. Interface Design", "5"),
        ("   2.1 Navigation & Global Topbar", "5"),
        ("   2.2 Overview / Home Interface (Trang chủ & Không gian an toàn số)", "6"),
        ("   2.3 Multi-Source Scan Interface (Giao diện Quét đa nguồn)", "7"),
        ("   2.4 Forensic Scan Results & Explanation (Kết quả Phân tích, Grad-CAM & Khuyến nghị)", "8"),
        ("   2.5 User Feedback Modal (Biểu mẫu Phản hồi độ chính xác)", "9"),
        ("   2.6 Scan History Interface (Lịch sử kiểm tra)", "10"),
        ("   2.7 Administrator Authentication (Đăng nhập Quản trị & Google SSO)", "11"),
        ("   2.8 Admin Evaluation & Benchmark Dashboard (Đánh giá chất lượng mô hình)", "12"),
        ("   2.9 Live Rule Engine – Scam Keywords Management (Quản lý từ khóa lừa đảo)", "13"),
        ("   2.10 Training Dataset Management (Quản lý tập dữ liệu huấn luyện)", "14"),
        ("   2.11 AI Model Version Management (Quản lý phiên bản mô hình AI)", "15"),
        ("   2.12 User Feedback Moderation (Kiểm duyệt phản hồi người dùng)", "16"),
        ("   2.13 Visitor Devices & Geolocation Map (Bản đồ thiết bị truy cập Leaflet)", "17"),
        ("   2.14 System Activity Logs (Nhật ký hoạt động hệ thống)", "18"),
        ("   2.15 User Profile Interface (Hồ sơ người dùng)", "19"),
        ("3. Non-Functional UI Requirements", "20"),
    ]
    t_toc = doc.add_table(rows=len(toc_lines), cols=2)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, (title, page) in enumerate(toc_lines):
        t_toc.rows[i].cells[0].text = title
        t_toc.rows[i].cells[1].text = page
        p0 = t_toc.rows[i].cells[0].paragraphs[0]
        p1 = t_toc.rows[i].cells[1].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if not title.startswith("   "):
            p0.runs[0].font.bold = True
            p1.runs[0].font.bold = True
    set_table_borders(t_toc, color="FFFFFF")

    doc.add_page_break()

    # CHAPTER 1: INTRODUCTION
    doc.add_heading("1. Introduction", level=1)
    
    doc.add_heading("1.1 Purpose", level=2)
    doc.add_paragraph(
        "Tài liệu User Interface Design (UID) mô tả cấu trúc, đặc tả thành phần và hành vi tương tác "
        "của hệ thống SFDS (Fraudulent Image Detection and Warning System with Explanations). "
        "Mục đích của tài liệu nhằm làm cơ sở thống nhất cho nhóm phát triển xây dựng giao diện người dùng "
        "thân thiện, trực quan, hỗ trợ người dân tự bảo vệ trước các thủ đoạn lừa đảo tinh vi, "
        "đồng thời cung cấp cho Quản trị viên/Chuyên gia an toàn mạng các công cụ trực quan hóa phân tích pháp y "
        "chuyên sâu (Grad-CAM, trích xuất OCR, ELA, ma trận nhầm lẫn và bản đồ thiết bị truy cập)."
    )

    doc.add_heading("1.2 Scope", level=2)
    doc.add_paragraph(
        "Tài liệu bao quát toàn diện ứng dụng Web Single Page Application (SPA) phát triển bằng React 18, Vite 5:\n"
        "• Chế độ Người dùng phổ thông (Guest Mode): Không bắt buộc đăng nhập, quét đa nguồn (ảnh chụp màn hình, "
        "mã QR, tin nhắn SMS/Zalo, URL lừa đảo, tài liệu PDF), giải thích nguyên nhân bằng thị giác (Grad-CAM, "
        "tô sáng văn bản OCR) và xuất báo cáo an toàn.\n"
        "• Chế độ Quản trị viên (Admin Mode): Xác thực bằng JWT / Google OAuth SSO, quản lý tập luật từ khóa tiếng Việt, "
        "quản lý tập dữ liệu huấn luyện, kiểm soát phiên bản mô hình AI, đo đạc Benchmark tự động (Macro F1, Recall, FAR), "
        "kiểm duyệt phản hồi và trực quan hóa bản đồ thiết bị truy cập trên nền OpenStreetMap (Leaflet)."
    )

    doc.add_page_break()

    # CHAPTER 2: INTERFACE DESIGN
    doc.add_heading("2. Interface Design", level=1)

    # 2.1 Navigation & Global Topbar
    doc.add_heading("2.1 Navigation & Global Topbar", level=2)
    doc.add_paragraph(
        "Thanh điều hướng toàn cục nằm ở phần đầu trang của ứng dụng, hỗ trợ chuyển đổi giữa các module chức năng, "
        "chuyển đổi giao diện Sáng/Tối (Dark/Light mode), song ngữ Anh - Việt, cùng Radar hiển thị trạng thái kết nối "
        "máy chủ phân tích AI trong thời gian thực."
    )
    p_f1 = doc.add_paragraph("Figure 1. UI Navigation & Topbar")
    p_f1.runs[0].font.italic = True
    p_f1.alignment = WD_ALIGN_PARAGRAPH.CENTER

    t1_data = [
        ["No.", "Field name", "Type", "Require", "Target"],
        ["1", "brandLogo", "Logo + Text Link", "Icon Shield + Text 'Scam Shield AI'", "Navigate to Home / Overview page"],
        ["2", "navOverview", "Nav Tab Link", "Text: 'Overview' (Tổng quan)", "Navigate to system introduction and overview"],
        ["3", "navScan", "Nav Tab Link", "Text: 'Scam check' (Kiểm tra); Scanner Icon", "Navigate to multi-source scan workspace"],
        ["4", "navHistory", "Nav Tab Link", "Text: 'History' (Lịch sử); Counter badge", "Open local / server scan history"],
        ["5", "navAdminLogin", "Button Link", "Text: 'Admin' (Quản trị); Lock icon", "Access restricted administrator portal"],
        ["6", "languageSelect", "Dropdown", "Options: 'Tiếng Việt', 'English'", "Instantly toggle application interface language"],
        ["7", "themeToggle", "Icon Button", "Sun / Moon icon; Active theme stored", "Toggle light and dark visual modes"],
        ["8", "statusRadar", "Radar Component", "Pulsing radar ring; States: Online/Waking/Offline", "Real-time indicator of AI backend availability"],
        ["9", "versionBadge", "Label Text", "Format: v1.0.0 · git_hash", "Display live build and commit reference"],
    ]
    t1 = doc.add_table(rows=len(t1_data), cols=5)
    for r_idx, row in enumerate(t1_data):
        for c_idx, val in enumerate(row):
            t1.rows[r_idx].cells[c_idx].text = val
    format_table(t1, header_bg="8B0000")
    p_t1 = doc.add_paragraph("Table 1. Description UI Navigation & Topbar")
    p_t1.runs[0].font.italic = True
    p_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 2.2 Overview Interface
    doc.add_heading("2.2 Overview / Home Interface (Trang chủ & Không gian an toàn số)", level=2)
    doc.add_paragraph(
        "Màn hình chính đóng vai trò chào đón người dùng, truyền tải thông điệp về an toàn số, giải thích ngắn gọn "
        "về các loại hình tấn công lừa đảo thường gặp và cung cấp nút bắt đầu quét nhanh chóng không cần đăng ký tài khoản."
    )
    p_f2 = doc.add_paragraph("Figure 2. UI Overview Page")
    p_f2.runs[0].font.italic = True
    p_f2.alignment = WD_ALIGN_PARAGRAPH.CENTER

    t2_data = [
        ["No.", "Field name", "Type", "Require", "Target"],
        ["1", "heroHeading", "Heading 1", "Bold; Text: 'Your safer space for everyday digital life'", "Welcome user and convey protective purpose"],
        ["2", "heroSubtitle", "Paragraph", "Explains multi-modal AI scam detection", "Provide high-level guidance for general public"],
        ["3", "startScanCTA", "Primary Button", "High-contrast with glow; Text: 'Start Scan Now'", "Guide users immediately into the Scan Page"],
        ["4", "featureImageCard", "Feature Card", "Image icon; Highlights OCR + ELA + Grad-CAM", "Introduce fake screenshot/bill detection"],
        ["5", "featureMessageCard", "Feature Card", "Chat icon; Highlights urgency & psych analysis", "Introduce OTP/SMS fraud message detection"],
        ["6", "featureUrlCard", "Feature Card", "Link icon; Highlights PhishVN + Safe Browsing", "Introduce fake bank/domain link detection"],
        ["7", "featurePdfCard", "Feature Card", "Doc icon; Highlights multi-page scan & QR parser", "Introduce suspicious document/invoice inspection"],
        ["8", "localSummaryStats", "Stats Grid", "Display count of checks stored on device", "Provide transparent overview of device storage"],
    ]
    t2 = doc.add_table(rows=len(t2_data), cols=5)
    for r_idx, row in enumerate(t2_data):
        for c_idx, val in enumerate(row):
            t2.rows[r_idx].cells[c_idx].text = val
    format_table(t2, header_bg="8B0000")
    p_t2 = doc.add_paragraph("Table 2. Description UI Overview Page")
    p_t2.runs[0].font.italic = True
    p_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 2.3 Multi-Source Scan Interface
    doc.add_heading("2.3 Multi-Source Scan Interface (Giao diện Quét đa nguồn)", level=2)
    doc.add_paragraph(
        "Khu vực quét chuyên sâu với giao diện mô phỏng khung ngắm Radar HUD, hỗ trợ 4 chế độ nạp dữ liệu: "
        "Ảnh chụp/QR, Tin nhắn văn bản, Đường link website và Tệp tài liệu PDF, kèm tính năng chụp trực tiếp bằng WebCam."
    )
    p_f3 = doc.add_paragraph("Figure 3. UI Multi-Source Scan Page")
    p_f3.runs[0].font.italic = True
    p_f3.alignment = WD_ALIGN_PARAGRAPH.CENTER

    t3_data = [
        ["No.", "Field name", "Type", "Require", "Target"],
        ["1", "tabImage", "Tab Selector", "Text: 'Image & QR'; Active indicator", "Switch scanner input to image/screenshot mode"],
        ["2", "tabText", "Tab Selector", "Text: 'Message / Text'", "Switch scanner input to plain message text"],
        ["3", "tabUrl", "Tab Selector", "Text: 'Website Link'", "Switch scanner input to URL domain analysis"],
        ["4", "tabPdf", "Tab Selector", "Text: 'PDF Document'", "Switch scanner input to PDF document file upload"],
        ["5", "scanViewport", "Interactive HUD", "Targeting reticle, lock corners, radar grid", "Display live upload preview and region markers"],
        ["6", "dropzoneUpload", "File Dropzone", "Accepts .png, .jpg, .jpeg up to 15MB", "Upload suspicious image from local device"],
        ["7", "cameraButton", "Secondary Button", "Camera icon; Text: 'Capture Photo'", "Open webcam interface to capture physical proof"],
        ["8", "textInputArea", "Textarea", "Placeholder: 'Paste suspicious message or SMS...'", "Enter raw textual content for scam evaluation"],
        ["9", "urlInputField", "Input Field", "URL validation; Placeholder: 'https://...'", "Input candidate web address for lexical analysis"],
        ["10", "pdfDropzone", "File Dropzone", "Accepts .pdf up to 10 pages / 15MB", "Upload digital or scanned invoice documents"],
        ["11", "sampleChips", "Chip Group", "Real-world presets: Fake bill, OTP threat, Phishing", "Allow instantaneous evaluation of sample cases"],
        ["12", "submitScanBtn", "Action Button", "Text: 'Analyze Risk'; Disabled during upload", "Trigger backend AI inference pipeline"],
    ]
    t3 = doc.add_table(rows=len(t3_data), cols=5)
    for r_idx, row in enumerate(t3_data):
        for c_idx, val in enumerate(row):
            t3.rows[r_idx].cells[c_idx].text = val
    format_table(t3, header_bg="8B0000")
    p_t3 = doc.add_paragraph("Table 3. Description UI Multi-Source Scan Page")
    p_t3.runs[0].font.italic = True
    p_t3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 2.4 Forensic Scan Results & Explanation
    doc.add_heading("2.4 Forensic Scan Results & Explanation (Kết quả Phân tích, Grad-CAM & Khuyến nghị)", level=2)
    doc.add_paragraph(
        "Khu vực trình bày kết quả sau khi AI phân tích: Điểm rủi ro tổng hợp (0-100), Phân loại mức cảnh báo, "
        "bản đồ nhiệt Grad-CAM định vị vùng nghi ngờ, văn bản OCR được đánh dấu từ khóa, lời giải thích AI tự nhiên và các hành động phòng ngừa."
    )
    p_f4 = doc.add_paragraph("Figure 4. UI Scan Results & Explainability")
    p_f4.runs[0].font.italic = True
    p_f4.alignment = WD_ALIGN_PARAGRAPH.CENTER

    t4_data = [
        ["No.", "Field name", "Type", "Require", "Target"],
        ["1", "riskLevelBadge", "Status Badge", "3 categorical states: Safe, Suspicious, Dangerous", "Immediate color-coded risk alert for users"],
        ["2", "riskScoreGauge", "Radial Meter", "0-100 scale; Green (0-39), Orange (40-69), Red (70+)", "Display quantitative calibrated risk score"],
        ["3", "textRiskScore", "Score Indicator", "Sub-score computed from OCR text and keywords", "Indicate risk level derived from textual signs"],
        ["4", "visualRiskScore", "Score Indicator", "Sub-score computed from ELA, EXIF, deepfake, Grad-CAM", "Indicate risk level derived from image manipulation"],
        ["5", "gradCamHeatmap", "Image Comparison", "Side-by-side heat overlay on convolutional features", "Highlight suspicious pixel regions for transparency"],
        ["6", "ocrHighlightedText", "Text Display Box", "Vietnamese text with highlighted red/amber keywords", "Show exact phrases triggering high fraud weight"],
        ["7", "urlIntelligenceBox", "Domain Card", "Shows domain age, PhishVN lexical score, Safe Browsing", "Alert impersonating domain structures"],
        ["8", "aiExplanationText", "Callout Box", "Natural language reasoning produced by VLM/Rule-Engine", "Explain why this case is considered fraudulent"],
        ["9", "actionChecklist", "Checklist", "Actionable advice: Do not send OTP, report bank, lock card", "Provide safe steps for victims to prevent damage"],
        ["10", "exportReportBtn", "Button", "Download icon; Text: 'Export Safety Report (PDF)'", "Generate downloadable audit report of the scan"],
        ["11", "feedbackTriggerBtn", "Outline Button", "Text: 'Was this result accurate?'", "Open feedback modal to confirm or dispute result"],
    ]
    t4 = doc.add_table(rows=len(t4_data), cols=5)
    for r_idx, row in enumerate(t4_data):
        for c_idx, val in enumerate(row):
            t4.rows[r_idx].cells[c_idx].text = val
    format_table(t4, header_bg="8B0000")
    p_t4 = doc.add_paragraph("Table 4. Description UI Scan Results & Explainability")
    p_t4.runs[0].font.italic = True
    p_t4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 2.5 User Feedback Modal
    doc.add_heading("2.5 User Feedback Modal (Biểu mẫu Phản hồi độ chính xác)", level=2)
    doc.add_paragraph(
        "Hộp thoại cho phép người dùng đóng góp ý kiến về độ chính xác của phán đoán (Kết quả đúng, Cảnh báo sai, Bỏ sót lừa đảo), "
        "phục vụ lưu trữ vào CSDL để Quản trị viên thẩm định và tinh chỉnh mô hình."
    )
    p_f5 = doc.add_paragraph("Figure 5. UI Scan Feedback Modal")
    p_f5.runs[0].font.italic = True
    p_f5.alignment = WD_ALIGN_PARAGRAPH.CENTER

    t5_data = [
        ["No.", "Field name", "Type", "Require", "Target"],
        ["1", "modalTitle", "Heading", "Text: 'Validate Detection Result'", "State the objective of the feedback dialog"],
        ["2", "verdictCorrect", "Radio Option", "Verdict: 'correct'; Green check icon", "User confirms the AI made a correct prediction"],
        ["3", "verdictFalseAlarm", "Radio Option", "Verdict: 'false_alarm'; Amber warning icon", "User reports a legitimate image was falsely flagged"],
        ["4", "verdictMissedScam", "Radio Option", "Verdict: 'missed_scam'; Red danger icon", "User reports a dangerous scam was missed by AI"],
        ["5", "noteTextarea", "Textarea", "Optional; Placeholder: 'Additional comments or context...'", "Capture contextual remarks from the user"],
        ["6", "cancelFeedbackBtn", "Secondary Button", "Text: 'Cancel'", "Dismiss modal without saving feedback"],
        ["7", "submitFeedbackBtn", "Primary Button", "Text: 'Submit Feedback'", "Save validation into scan_feedback database table"],
    ]
    t5 = doc.add_table(rows=len(t5_data), cols=5)
    for r_idx, row in enumerate(t5_data):
        for c_idx, val in enumerate(row):
            t5.rows[r_idx].cells[c_idx].text = val
    format_table(t5, header_bg="8B0000")
    p_t5 = doc.add_paragraph("Table 5. Description UI Scan Feedback Modal")
    p_t5.runs[0].font.italic = True
    p_t5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 2.6 Scan History Interface
    doc.add_heading("2.6 Scan History Interface (Lịch sử kiểm tra)", level=2)
    doc.add_paragraph(
        "Màn hình theo dõi các lượt kiểm tra đã thực hiện, cho phép xem lại chi tiết từng lượt quét, lọc theo mức độ nguy hiểm "
        "hoặc xóa sạch dữ liệu khỏi bộ nhớ trình duyệt."
    )
    p_f6 = doc.add_paragraph("Figure 6. UI Scan History Page")
    p_f6.runs[0].font.italic = True
    p_f6.alignment = WD_ALIGN_PARAGRAPH.CENTER

    t6_data = [
        ["No.", "Field name", "Type", "Require", "Target"],
        ["1", "filterRiskTabs", "Filter Tabs", "Options: All, Dangerous, Suspicious, Safe", "Filter previous scan list by severity level"],
        ["2", "scanHistoryList", "Card List", "List of saved scan cards (Timestamp, Score, Source)", "Browse previous inspection sessions"],
        ["3", "historyDetailView", "Detail Drawer", "Displays full original image, Grad-CAM, OCR text", "Re-examine forensic details of selected scan"],
        ["4", "clearHistoryBtn", "Danger Button", "Text: 'Clear All Local History'; Confirmation alert", "Erase all scan records stored in localStorage"],
        ["5", "exportHistoryBtn", "Secondary Button", "Export .json / .csv data backup", "Download personal check history to local device"],
    ]
    t6 = doc.add_table(rows=len(t6_data), cols=5)
    for r_idx, row in enumerate(t6_data):
        for c_idx, val in enumerate(row):
            t6.rows[r_idx].cells[c_idx].text = val
    format_table(t6, header_bg="8B0000")
    p_t6 = doc.add_paragraph("Table 6. Description UI Scan History Page")
    p_t6.runs[0].font.italic = True
    p_t6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 2.7 Administrator Authentication
    doc.add_heading("2.7 Administrator Authentication (Đăng nhập Quản trị & Google SSO)", level=2)
    doc.add_paragraph(
        "Cổng đăng nhập bảo mật dành cho Quản trị viên hệ thống để truy cập vào phân hệ quản trị, bảo vệ bằng JWT token "
        "và tích hợp xác thực một lần qua Google Single Sign-On (OAuth 2.0)."
    )
    p_f7 = doc.add_paragraph("Figure 7. UI Admin Login")
    p_f7.runs[0].font.italic = True
    p_f7.alignment = WD_ALIGN_PARAGRAPH.CENTER

    t7_data = [
        ["No.", "Field name", "Type", "Require", "Target"],
        ["1", "loginHeader", "Heading", "Text: 'Administrator Sign In'; Lock badge", "Identify administrator authentication portal"],
        ["2", "adminEmailInput", "Input Field", "Email format; Required; Placeholder: 'admin@...'", "Enter administrator account email"],
        ["3", "adminPasswordInput", "Input (Password)", "Required; Masked input with reveal eye icon", "Enter administrator password"],
        ["4", "submitLoginBtn", "Primary Button", "Text: 'Sign In'; Progress spinner during auth", "Authenticate credentials and issue JWT bearer"],
        ["5", "googleSsoBtn", "SSO Button", "Google logo; Text: 'Sign in with Google'", "Authenticate via external Google OAuth identity"],
        ["6", "backToPublicBtn", "Link Button", "Text: '← Return to public scanner'", "Navigate back to client overview"],
    ]
    t7 = doc.add_table(rows=len(t7_data), cols=5)
    for r_idx, row in enumerate(t7_data):
        for c_idx, val in enumerate(row):
            t7.rows[r_idx].cells[c_idx].text = val
    format_table(t7, header_bg="8B0000")
    p_t7 = doc.add_paragraph("Table 7. Description UI Admin Login")
    p_t7.runs[0].font.italic = True
    p_t7.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 2.8 Admin Evaluation & Benchmark Dashboard
    doc.add_heading("2.8 Admin Evaluation & Benchmark Dashboard (Đánh giá chất lượng mô hình)", level=2)
    doc.add_paragraph(
        "Bảng điều khiển khoa học giúp kỹ sư AI đo đạc chất lượng bộ phát hiện: Chạy kiểm thử hồi quy tự động, "
        "trực quan hóa Ma trận nhầm lẫn (Confusion Matrix), theo dõi Macro F1, Recall, Tỷ lệ cảnh báo sai (FAR) và liệt kê các ca cần chú ý."
    )
    p_f8 = doc.add_paragraph("Figure 8. UI Admin Model Evaluation & Benchmark")
    p_f8.runs[0].font.italic = True
    p_f8.alignment = WD_ALIGN_PARAGRAPH.CENTER

    t8_data = [
        ["No.", "Field name", "Type", "Require", "Target"],
        ["1", "runEvaluationBtn", "Primary Button", "Text: 'Run Automated Evaluation'; Spinner during run", "Trigger real-time benchmark suite on live backend"],
        ["2", "kpiMacroF1", "Metric Card", "Displays 3-class Macro F1 percentage score", "Evaluate balanced accuracy across all 3 risk levels"],
        ["3", "kpiRecall", "Metric Card", "Displays binary detection Recall on fraudulent samples", "Ensure hazardous fraud cases are not missed"],
        ["4", "kpiFalseAlarmRate", "Metric Card", "Displays False Alarm Rate (FAR) on benign samples", "Monitor and minimize false positive warnings"],
        ["5", "kpiPassedCases", "Metric Card", "Format: Passed/Total cases (e.g. 13/14, 93%)", "Summarize overall regression test performance"],
        ["6", "confusionMatrixGrid", "Data Table", "Rows: Expected labels; Columns: Detector output", "Examine classification confusion between 3 levels"],
        ["7", "attentionCasesList", "Item List", "Lists test case ID, expected label, actual label, text", "Highlight failed test cases for model retraining"],
        ["8", "manualEvaluationForm", "Form", "Inputs for model_id, macro_f1, recall, FAR, usefulness", "Save benchmark results to model_evaluations table"],
    ]
    t8 = doc.add_table(rows=len(t8_data), cols=5)
    for r_idx, row in enumerate(t8_data):
        for c_idx, val in enumerate(row):
            t8.rows[r_idx].cells[c_idx].text = val
    format_table(t8, header_bg="8B0000")
    p_t8 = doc.add_paragraph("Table 8. Description UI Admin Model Evaluation & Benchmark")
    p_t8.runs[0].font.italic = True
    p_t8.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 2.9 Live Rule Engine – Scam Keywords Management
    doc.add_heading("2.9 Live Rule Engine – Scam Keywords Management (Quản lý từ khóa lừa đảo)", level=2)
    doc.add_paragraph(
        "Giao diện quản lý bộ từ điển cụm từ lừa đảo tiếng Việt. Quản trị viên có thể thêm cụm từ mới kèm danh mục "
        "và trọng số rủi ro mà không cần dừng hay biên dịch lại hệ thống."
    )
    p_f9 = doc.add_paragraph("Figure 9. UI Scam Keywords Management")
    p_f9.runs[0].font.italic = True
    p_f9.alignment = WD_ALIGN_PARAGRAPH.CENTER

    t9_data = [
        ["No.", "Field name", "Type", "Require", "Target"],
        ["1", "keywordInput", "Input Field", "Required; Placeholder: 'Keyword or phrase...'", "Enter new Vietnamese fraud keyword or regex"],
        ["2", "categorySelect", "Dropdown", "Options: Phishing, Impersonation, Fake invoice, Urgent threat", "Assign tactical fraud category"],
        ["3", "weightInput", "Number Input", "Range: 1 to 50; Default: 10", "Set risk score contribution weight"],
        ["4", "addRuleBtn", "Button", "Text: 'Add Rule'", "Persist new rule into scam_keywords table"],
        ["5", "keywordRuleGrid", "Grid Cards", "Card displaying keyword, category tag, weight badge", "View and audit all live rule-engine entries"],
    ]
    t9 = doc.add_table(rows=len(t9_data), cols=5)
    for r_idx, row in enumerate(t9_data):
        for c_idx, val in enumerate(row):
            t9.rows[r_idx].cells[c_idx].text = val
    format_table(t9, header_bg="8B0000")
    p_t9 = doc.add_paragraph("Table 9. Description UI Scam Keywords Management")
    p_t9.runs[0].font.italic = True
    p_t9.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 2.10 Training Dataset Management
    doc.add_heading("2.10 Training Dataset Management (Quản lý tập dữ liệu huấn luyện)", level=2)
    doc.add_paragraph(
        "Phân hệ quản lý tập dữ liệu huấn luyện hình ảnh, lưu vết nguồn gốc tệp, xác nhận che mờ thông tin cá nhân (PII Redaction) "
        "và gắn nhãn kiểm định phục vụ tái huấn luyện mô hình học sâu."
    )
    p_f10 = doc.add_paragraph("Figure 10. UI Training Dataset Page")
    p_f10.runs[0].font.italic = True
    p_f10.alignment = WD_ALIGN_PARAGRAPH.CENTER

    t10_data = [
        ["No.", "Field name", "Type", "Require", "Target"],
        ["1", "datasetImageUrlInput", "Input Field", "Required; Storage URL or file path", "Enter URI of curated training sample"],
        ["2", "datasetCategorySelect", "Dropdown", "Options populated from scam_categories", "Bind dataset image to standardized scam category"],
        ["3", "anonymizedCheckbox", "Checkbox", "Required; Confirmation that PII has been redacted", "Certify compliance with user data privacy standards"],
        ["4", "verifiedCheckbox", "Checkbox", "Ground truth verification status", "Confirm expert validation of true label"],
        ["5", "addDatasetBtn", "Button", "Text: 'Add Dataset'", "Insert curated record into training_dataset table"],
        ["6", "datasetList", "Data List", "Category badge, Verified tag, Uploader ID", "Review inventory of model training data"],
    ]
    t10 = doc.add_table(rows=len(t10_data), cols=5)
    for r_idx, row in enumerate(t10_data):
        for c_idx, val in enumerate(row):
            t10.rows[r_idx].cells[c_idx].text = val
    format_table(t10, header_bg="8B0000")
    p_t10 = doc.add_paragraph("Table 10. Description UI Training Dataset Page")
    p_t10.runs[0].font.italic = True
    p_t10.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 2.11 AI Model Version Management
    doc.add_heading("2.11 AI Model Version Management (Quản lý phiên bản mô hình AI)", level=2)
    doc.add_paragraph(
        "Quản lý vòng đời các mô hình học máy (như PhishVN v3.1, ResNet-18, VLM Analyzer), kích hoạt checkpoint phục vụ suy luận thực tế."
    )
    p_f11 = doc.add_paragraph("Figure 11. UI AI Models Page")
    p_f11.runs[0].font.italic = True
    p_f11.alignment = WD_ALIGN_PARAGRAPH.CENTER

    t11_data = [
        ["No.", "Field name", "Type", "Require", "Target"],
        ["1", "versionNameInput", "Input Field", "Required; Unique version string (e.g. 'PhishVN-v3.1')", "Register new AI model checkpoint version"],
        ["2", "modelDescInput", "Textarea", "Architecture, weights, hyperparameters, dataset", "Document technical specification of model"],
        ["3", "activeModelCheckbox", "Checkbox", "Flag indicating active production serving status", "Toggle whether this model receives inference calls"],
        ["4", "addModelBtn", "Button", "Text: 'Add Model'", "Save model checkpoint entry in ai_models table"],
        ["5", "modelVersionList", "Item Cards", "Version name, active badge, creation timestamp", "Track and manage deployed AI model iterations"],
    ]
    t11 = doc.add_table(rows=len(t11_data), cols=5)
    for r_idx, row in enumerate(t11_data):
        for c_idx, val in enumerate(row):
            t11.rows[r_idx].cells[c_idx].text = val
    format_table(t11, header_bg="8B0000")
    p_t11 = doc.add_paragraph("Table 11. Description UI AI Models Page")
    p_t11.runs[0].font.italic = True
    p_t11.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 2.12 User Feedback Moderation
    doc.add_heading("2.12 User Feedback Moderation (Kiểm duyệt phản hồi người dùng)", level=2)
    doc.add_paragraph(
        "Trung tâm kiểm duyệt phản hồi do người dùng gửi về, giúp quản trị viên rà soát các trường hợp hệ thống cảnh báo nhầm "
        "hoặc phát hiện các biến thể lừa đảo mới chưa kịp cập nhật quy tắc."
    )
    p_f12 = doc.add_paragraph("Figure 12. UI Feedback Moderation Page")
    p_f12.runs[0].font.italic = True
    p_f12.alignment = WD_ALIGN_PARAGRAPH.CENTER

    t12_data = [
        ["No.", "Field name", "Type", "Require", "Target"],
        ["1", "refreshFeedbackBtn", "Secondary Button", "Icon refresh; Text: 'Refresh'", "Reload latest feedback records from database"],
        ["2", "feedbackCounter", "Pill Badge", "Displays total count of received validations", "Summarize incoming feedback backlog"],
        ["3", "feedbackCardStream", "Stream Cards", "Color cards: Green (Correct), Yellow (False alarm), Red (Missed)", "Present user feedback items chronologically"],
        ["4", "feedbackContextMeta", "Text Row", "Displays check ID, timestamp, input source, risk score", "Provide forensic context of original scan"],
        ["5", "feedbackUserNote", "Blockquote", "User's freeform remarks explaining why result was incorrect", "Read specific victim / user observations"],
        ["6", "feedbackStatusTag", "Status Tag", "Tags: 'Pending review' or 'Reviewed'", "Track moderation workflow of feedback cases"],
    ]
    t12 = doc.add_table(rows=len(t12_data), cols=5)
    for r_idx, row in enumerate(t12_data):
        for c_idx, val in enumerate(row):
            t12.rows[r_idx].cells[c_idx].text = val
    format_table(t12, header_bg="8B0000")
    p_t12 = doc.add_paragraph("Table 12. Description UI Feedback Moderation Page")
    p_t12.runs[0].font.italic = True
    p_t12.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 2.13 Visitor Devices & Geolocation Map
    doc.add_heading("2.13 Visitor Devices & Geolocation Map (Bản đồ thiết bị truy cập Leaflet)", level=2)
    doc.add_paragraph(
        "Bản đồ không gian mạng toàn cầu tích hợp thư viện Leaflet và OpenStreetMap. Tự động nhận diện thiết bị, hệ điều hành, "
        "trình duyệt và định vị vùng mạng IP gần đúng của các lượt truy cập."
    )
    p_f13 = doc.add_paragraph("Figure 13. UI Visitor Devices Map")
    p_f13.runs[0].font.italic = True
    p_f13.alignment = WD_ALIGN_PARAGRAPH.CENTER

    t13_data = [
        ["No.", "Field name", "Type", "Require", "Target"],
        ["1", "leafletMapCanvas", "Map Viewport", "Interactive OpenStreetMap (Zoom, Pan, FitBounds)", "Display geographical distribution of client devices"],
        ["2", "deviceLocationMarker", "Circle Marker", "Green circle with accuracy radius circle", "Pin approximate physical / network location of visitor"],
        ["3", "deviceMapTooltip", "Tooltip Popup", "Device name, OS platform, browser, coordinate", "Display device identity on hover or tap"],
        ["4", "deviceSidebarList", "Sidebar List", "List of recorded devices with 'All Devices' filter", "Select specific workstation to center and zoom map"],
        ["5", "deviceListItemCard", "Selectable Card", "Device title, IP address, visit counter, last seen time", "Track engagement frequency per visitor"],
        ["6", "openStreetMapExtLink", "Hyperlink", "Text: 'Open full map ↗'; Coordinates query", "Open exact location coordinates in OpenStreetMap external tab"],
    ]
    t13 = doc.add_table(rows=len(t13_data), cols=5)
    for r_idx, row in enumerate(t13_data):
        for c_idx, val in enumerate(row):
            t13.rows[r_idx].cells[c_idx].text = val
    format_table(t13, header_bg="8B0000")
    p_t13 = doc.add_paragraph("Table 13. Description UI Visitor Devices Map")
    p_t13.runs[0].font.italic = True
    p_t13.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 2.14 System Activity Logs
    doc.add_heading("2.14 System Activity Logs (Nhật ký hoạt động hệ thống)", level=2)
    doc.add_paragraph(
        "Nhật ký kiểm toán an ninh ghi nhận mọi thay đổi cấu hình, tạo mới quy tắc, chạy đánh giá mô hình hoặc thao tác của quản trị viên."
    )
    p_f14 = doc.add_paragraph("Figure 14. UI System Activity Logs Page")
    p_f14.runs[0].font.italic = True
    p_f14.alignment = WD_ALIGN_PARAGRAPH.CENTER

    t14_data = [
        ["No.", "Field name", "Type", "Require", "Target"],
        ["1", "actionTypeInput", "Input Field", "Required; Standard action slug (e.g. 'UPDATE_RULE')", "Specify administrative event category"],
        ["2", "logDescInput", "Textarea", "Details of setting modifications or forensic review", "Record audit trail description of the action"],
        ["3", "addLogBtn", "Button", "Text: 'Add Log Entry'", "Append audit record into system_activity_logs"],
        ["4", "auditLogTable", "Data List", "Columns: Action Type, Admin ID, Description, Timestamp", "Review historical administrative actions"],
    ]
    t14 = doc.add_table(rows=len(t14_data), cols=5)
    for r_idx, row in enumerate(t14_data):
        for c_idx, val in enumerate(row):
            t14.rows[r_idx].cells[c_idx].text = val
    format_table(t14, header_bg="8B0000")
    p_t14 = doc.add_paragraph("Table 14. Description UI System Activity Logs Page")
    p_t14.runs[0].font.italic = True
    p_t14.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 2.15 User Profile Interface
    doc.add_heading("2.15 User Profile Interface (Hồ sơ người dùng)", level=2)
    doc.add_paragraph(
        "Khu vực quản lý thông tin người dùng, xem tóm tắt quyền tài khoản và quản lý minh bạch không gian lưu trữ cục bộ trên máy."
    )
    p_f15 = doc.add_paragraph("Figure 15. UI User Profile Page")
    p_f15.runs[0].font.italic = True
    p_f15.alignment = WD_ALIGN_PARAGRAPH.CENTER

    t15_data = [
        ["No.", "Field name", "Type", "Require", "Target"],
        ["1", "profileAvatar", "Avatar Component", "User initial badge with role halo", "Display visual identifier of current identity"],
        ["2", "profileFullNameInput", "Input Field", "Editable full name string", "Allow updating display name"],
        ["3", "profileEmailDisplay", "Text Label", "Account email (read-only)", "Show active user login email"],
        ["4", "profileRoleBadge", "Status Badge", "Badge showing 'Guest' or 'Administrator'", "Identify user authorization tier"],
        ["5", "deviceStorageCard", "Summary Box", "Counts number of scan results stored locally", "Provide full transparency on client-side data"],
    ]
    t15 = doc.add_table(rows=len(t15_data), cols=5)
    for r_idx, row in enumerate(t15_data):
        for c_idx, val in enumerate(row):
            t15.rows[r_idx].cells[c_idx].text = val
    format_table(t15, header_bg="8B0000")
    p_t15 = doc.add_paragraph("Table 15. Description UI User Profile Page")
    p_t15.runs[0].font.italic = True
    p_t15.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_page_break()

    # CHAPTER 3: NON-FUNCTIONAL REQUIREMENTS
    doc.add_heading("3. Non-Functional UI Requirements", level=1)
    
    nf_reqs = [
        ("3.1 Responsive Design", "Giao diện hỗ trợ chuẩn thiết kế tương thích (Responsive Design) từ độ phân giải cao Desktop (1920x1080, 1440x900) đến Tablet (768px) và Smartphone (375px - 414px), đảm bảo người dùng có thể chụp và quét ảnh nhanh chóng ngay trên thiết bị di động."),
        ("3.2 Accessibility (WCAG 2.1 AA)", "Độ tương phản màu sắc đạt chuẩn tối thiểu 4.5:1 đối với văn bản thông thường. Tất cả các nút bấm, biểu tượng và input đều có thuộc tính aria-label, hỗ trợ người khuyết tật sử dụng trình đọc màn hình."),
        ("3.3 Theme Customization & Eye Protection", "Hệ thống hỗ trợ chuyển đổi linh hoạt chế độ Sáng (Light) và Tối (Dark mode). Chế độ tối sử dụng bảng màu dịu mắt (#121820) giúp giảm mỏi mắt khi chuyên gia phân tích làm việc ban đêm."),
        ("3.4 Bilingual Support (English / Vietnamese)", "Hỗ trợ chuyển đổi song ngữ tức thì (Vietnamese / English) toàn bộ nhãn, thông báo, giải thích AI và nút bấm mà không cần tải lại trang."),
        ("3.5 High Performance HUD & Visual Rendering", "Các hiệu ứng quét Radar, khung ngắm HUD và lớp phủ nhiệt Grad-CAM được tăng tốc phần cứng bằng GPU CSS (transform, opacity), đảm bảo tốc độ phản hồi mượt mà 60 FPS."),
        ("3.6 Privacy-First Anonymous Storage", "Đối với người dùng khách, toàn bộ hình ảnh và lịch sử quét lưu tại localStorage của trình duyệt, không tự ý lưu dữ liệu cá nhân lên máy chủ trừ khi người dùng chủ động gửi phản hồi."),
    ]
    
    t_nf = doc.add_table(rows=len(nf_reqs)+1, cols=3)
    t_nf.rows[0].cells[0].text = "No."
    t_nf.rows[0].cells[1].text = "Quality Attribute"
    t_nf.rows[0].cells[2].text = "Specification & Technical Target"
    
    for i, (attr, spec) in enumerate(nf_reqs, start=1):
        t_nf.rows[i].cells[0].text = str(i)
        t_nf.rows[i].cells[1].text = attr
        t_nf.rows[i].cells[2].text = spec
    format_table(t_nf, header_bg="204060")
    
    doc.save(output_path)
    print(f"Document successfully saved to: {output_path}")

if __name__ == "__main__":
    out_file = r"D:\scam-detector\C1SE.06_UserInterfaceDesign_v1.0.docx"
    build_uid_document(out_file)

# -*- coding: utf-8 -*-
"""
Script to generate C1SE.06_ProductBacklog_SFDS_v1.0.xlsx
Capstone Project: SFDS (Scam Fraud Detection System with Explanations)
Team: C1SE.06 - CMU-SE 450 - Duy Tan University
"""

import xlsxwriter

def create_backlog():
    filename = "C1SE.06_ProductBacklog_SFDS_v1.0.xlsx"
    workbook = xlsxwriter.Workbook(filename)

    # Define styles
    font_family = "Times New Roman"

    title_fmt = workbook.add_format({
        'font_name': font_family,
        'font_size': 16,
        'bold': True,
        'font_color': '#000000',
        'align': 'left',
        'valign': 'vcenter'
    })

    subtitle_fmt = workbook.add_format({
        'font_name': font_family,
        'font_size': 11,
        'italic': True,
        'font_color': '#444444',
        'align': 'left',
        'valign': 'vcenter'
    })

    header_fmt = workbook.add_format({
        'font_name': font_family,
        'font_size': 11,
        'bold': True,
        'font_color': '#000000',
        'bg_color': '#D9D9D9',
        'border': 1,
        'border_color': '#000000',
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True
    })

    cell_center = workbook.add_format({
        'font_name': font_family,
        'font_size': 10.5,
        'border': 1,
        'border_color': '#000000',
        'align': 'center',
        'valign': 'top'
    })

    cell_left = workbook.add_format({
        'font_name': font_family,
        'font_size': 10.5,
        'border': 1,
        'border_color': '#000000',
        'align': 'left',
        'valign': 'top',
        'text_wrap': True
    })

    cell_bold_left = workbook.add_format({
        'font_name': font_family,
        'font_size': 10.5,
        'bold': True,
        'border': 1,
        'border_color': '#000000',
        'align': 'left',
        'valign': 'top'
    })

    cell_right = workbook.add_format({
        'font_name': font_family,
        'font_size': 10.5,
        'border': 1,
        'border_color': '#000000',
        'align': 'right',
        'valign': 'top'
    })

    status_done = workbook.add_format({
        'font_name': font_family,
        'font_size': 10.5,
        'bold': True,
        'border': 1,
        'border_color': '#000000',
        'align': 'center',
        'valign': 'top',
        'bg_color': '#E2EFDA',
        'font_color': '#375623'
    })

    status_in_progress = workbook.add_format({
        'font_name': font_family,
        'font_size': 10.5,
        'bold': True,
        'border': 1,
        'border_color': '#000000',
        'align': 'center',
        'valign': 'top',
        'bg_color': '#FFF2CC',
        'font_color': '#7F6000'
    })

    status_todo = workbook.add_format({
        'font_name': font_family,
        'font_size': 10.5,
        'border': 1,
        'border_color': '#000000',
        'align': 'center',
        'valign': 'top',
        'bg_color': '#F2F2F2',
        'font_color': '#595959'
    })

    # Summary header style
    sec_header_fmt = workbook.add_format({
        'font_name': font_family,
        'font_size': 12,
        'bold': True,
        'font_color': '#000000',
        'bg_color': '#BFBFBF',
        'border': 1,
        'border_color': '#000000',
        'align': 'left',
        'valign': 'vcenter'
    })

    total_fmt = workbook.add_format({
        'font_name': font_family,
        'font_size': 11,
        'bold': True,
        'font_color': '#000000',
        'bg_color': '#D9D9D9',
        'border': 1,
        'border_color': '#000000',
        'align': 'right',
        'valign': 'vcenter'
    })

    # ==========================================
    # SHEET 1: PROJECT OVERVIEW
    # ==========================================
    ws_info = workbook.add_worksheet("Project Overview")
    ws_info.set_column('A:A', 4)
    ws_info.set_column('B:B', 22)
    ws_info.set_column('C:C', 35)
    ws_info.set_column('D:D', 20)
    ws_info.set_column('E:E', 25)
    ws_info.set_column('F:F', 18)

    ws_info.write('B2', "CAPSTONE PROJECT MANAGEMENT OVERVIEW", title_fmt)
    ws_info.write('B3', "Duy Tan University - School of Computer Science - CMU-SE 450", subtitle_fmt)

    ws_info.write('B5', "PROJECT INFORMATION", sec_header_fmt)
    ws_info.write('C5', "", sec_header_fmt)
    ws_info.write('D5', "", sec_header_fmt)
    ws_info.write('E5', "", sec_header_fmt)
    ws_info.write('F5', "", sec_header_fmt)

    info_rows = [
        ("Project Name", "Scam Fraud Detection System with Explanations (SFDS)"),
        ("Project Code", "CMU-SE 450 - C1SE.06"),
        ("Academic Year", "2024 - 2025 / Capstone Period"),
        ("Project Leader", "Pham Tan Hao (ID: 29219020823) - phamtanhao1909@gmail.com"),
        ("Project Mentor", "Eng. Ha Manh Toan (lhttuy@gmail.com)"),
        ("Core Stack", "FastAPI (Python 3.12), React 18 (Vite), PyTorch, Scikit-Learn, Tesseract OCR, SQLite/MySQL")
    ]
    for r_idx, (k, v) in enumerate(info_rows, start=6):
        ws_info.write(f'B{r_idx}', k, cell_bold_left)
        ws_info.write(f'C{r_idx}', v, cell_left)
        ws_info.write(f'D{r_idx}', "", cell_left)
        ws_info.write(f'E{r_idx}', "", cell_left)
        ws_info.write(f'F{r_idx}', "", cell_left)

    ws_info.write('B13', "TEAM MEMBERS & RESPONSIBILITIES", sec_header_fmt)
    ws_info.write('C13', "", sec_header_fmt)
    ws_info.write('D13', "", sec_header_fmt)
    ws_info.write('E13', "", sec_header_fmt)
    ws_info.write('F13', "", sec_header_fmt)

    team_headers = ["Member Name", "Student ID", "Project Role", "Email", "Phone"]
    for c_idx, h in enumerate(team_headers, start=1):
        ws_info.write(13, c_idx, h, header_fmt)

    team_data = [
        ("Pham Tan Hao", "29219020823", "Project Leader / Scrum Master / Full-stack", "phamtanhao1909@gmail.com", "0961651933"),
        ("Dao Thi My Nhung", "29209200048", "QA Lead / UI-UX Designer", "mynhung150905@gmail.com", "0376415338"),
        ("Tran Hoang Nhat Nam", "29219423638", "Frontend Developer / Technical Writer", "trannamnhathoang@gmail.com", "0795798736"),
        ("Nguyen Phan Duc Tuan", "29211151140", "AI Lead / Full-stack Developer", "ductuan02072005@gmail.com", "0932442770")
    ]
    for r_idx, row in enumerate(team_data, start=14):
        ws_info.write(r_idx, 1, row[0], cell_bold_left)
        ws_info.write(r_idx, 2, row[1], cell_center)
        ws_info.write(r_idx, 3, row[2], cell_left)
        ws_info.write(r_idx, 4, row[3], cell_left)
        ws_info.write(r_idx, 5, row[4], cell_center)

    ws_info.write('B20', "SPRINT SCHEDULE SUMMARY", sec_header_fmt)
    ws_info.write('C20', "", sec_header_fmt)
    ws_info.write('D20', "", sec_header_fmt)
    ws_info.write('E20', "", sec_header_fmt)
    ws_info.write('F20', "", sec_header_fmt)

    sprint_headers = ["Sprint", "Duration", "Target Milestone", "Est. Hours", "Status"]
    for c_idx, h in enumerate(sprint_headers, start=1):
        ws_info.write(20, c_idx, h, header_fmt)

    sprint_data = [
        ("Sprint 1", "Week 1 - Week 3", "Architecture Setup, Domain Gating, PhishVN & ResNet-18 baseline", 160, "Done"),
        ("Sprint 2", "Week 4 - Week 6", "OCR Engine, Risk Keyword Engine, Calibrated Consensus Fusion", 180, "Done"),
        ("Sprint 3", "Week 7 - Week 9", "React Scan Interface, Reasoning Visualizer, History & Feedback", 170, "In Progress"),
        ("Sprint 4", "Week 10 - Week 12", "Admin Intelligence Dashboard, Whitelist/Blacklist Manager, Report Export", 150, "To Do"),
        ("Sprint 5", "Week 13 - Week 15", "End-to-End Stress Testing, Security Hardening, Capstone Final Defense", 140, "To Do")
    ]
    for r_idx, row in enumerate(sprint_data, start=21):
        ws_info.write(r_idx, 1, row[0], cell_bold_left)
        ws_info.write(r_idx, 2, row[1], cell_center)
        ws_info.write(r_idx, 3, row[2], cell_left)
        ws_info.write(r_idx, 4, row[3], cell_right)
        st = row[4]
        if st == "Done":
            ws_info.write(r_idx, 5, st, status_done)
        elif st == "In Progress":
            ws_info.write(r_idx, 5, st, status_in_progress)
        else:
            ws_info.write(r_idx, 5, st, status_todo)

    ws_info.write(26, 1, "Total Project Estimated Hours", total_fmt)
    ws_info.write(26, 2, "", total_fmt)
    ws_info.write(26, 3, "", total_fmt)
    ws_info.write(26, 4, 800, total_fmt)
    ws_info.write(26, 5, "", total_fmt)

    # ==========================================
    # SHEET 2: PRODUCT BACKLOG (Matching user's template)
    # ==========================================
    ws_pb = workbook.add_worksheet("Product Backlog")
    
    # Set column widths
    ws_pb.set_column('A:A', 3)
    ws_pb.set_column('B:B', 10)  # Id
    ws_pb.set_column('C:C', 26)  # Heading
    ws_pb.set_column('D:D', 18)  # As a..
    ws_pb.set_column('E:E', 36)  # I want to ..
    ws_pb.set_column('F:F', 34)  # so that ..
    ws_pb.set_column('G:G', 46)  # Acceptance Criteria
    ws_pb.set_column('H:H', 22)  # Remarks
    ws_pb.set_column('I:I', 10)  # Priority
    ws_pb.set_column('J:J', 14)  # Status
    ws_pb.set_column('K:K', 14)  # Type
    ws_pb.set_column('L:L', 12)  # Project Id
    ws_pb.set_column('M:M', 12)  # Sprint No
    ws_pb.set_column('N:N', 14)  # Estimate (Hours)
    ws_pb.set_column('O:O', 20)  # Assignee

    # Title row as in sample (Row 5, B5)
    ws_pb.write('B5', "Product Backlog", title_fmt)

    # Header Row (Row 7, index 6)
    headers = [
        "Id", "Heading", "As a..", "I want to ..", "so that ..", 
        "Acceptance Criteria", "Remarks", "Priority", "Status", 
        "Type", "Project Id", "Sprint No", "Estimate\n(Hours)", "Assignee"
    ]
    for c_idx, h in enumerate(headers, start=1):
        ws_pb.write(6, c_idx, h, header_fmt)

    # Backlog Items (PB-01 to PB-20)
    backlog_data = [
        (
            "PB-01",
            "Project Architecture & Core Scaffolding",
            "System Engineer",
            "set up FastAPI backend framework, Vite React frontend, and database schema ORM",
            "the development team has a unified, stable environment to build multimodal detection modules.",
            "- FastAPI app initialized with CORS, Uvicorn, and structured routing.\n- React 18 (Vite) initialized with Tailwind CSS.\n- SQLite local DB & SQLAlchemy ORM configured.\n- CI/CD automated linting and pytest runners operational.",
            "Base architecture foundation",
            5, "Done", "Tech Spike", "C1SE.06", "Sprint 1", 36, "Pham Tan Hao"
        ),
        (
            "PB-02",
            "User & Admin Authentication",
            "User",
            "authenticate and obtain secure role-based session tokens (JWT)",
            "sensitive administrative dashboards and reporting actions are restricted to authorized personnel.",
            "- Public users can perform scans without login.\n- Admin login with username/password issues signed JWT.\n- Invalid credentials return HTTP 401 with informative error.\n- Token expiry and refresh token mechanisms validated.",
            "OWASP ASVS compliant",
            5, "Done", "User Story", "C1SE.06", "Sprint 1", 28, "Pham Tan Hao"
        ),
        (
            "PB-03",
            "PhishVN Lexical URL Detection Pipeline",
            "AI Engineer",
            "extract 21 lexical features from suspicious URLs and classify risk using HistGradientBoosting",
            "the system detects malicious URLs, credential harvesters, and deceptive subdomain tricks instantly.",
            "- Feature extraction pipeline extracts: URL length, entropy, IP address usage, punycode, hyphen count, sensitive tokens.\n- HistGradientBoosting model (joblib) outputs calibrated risk score [0, 1].\n- Execution completes in < 250ms per URL query.",
            "Trained on 100k+ VN URLs",
            5, "Done", "User Story", "C1SE.06", "Sprint 1", 48, "Nguyen Phan Duc Tuan"
        ),
        (
            "PB-04",
            "Domain Gating & Trusted Registry",
            "System",
            "pre-filter input domains against official whitelist (.gov.vn, official banks) and known blacklists",
            "benign government portals are never flagged falsely, and known malicious domains are blocked in 0ms.",
            "- Whitelist check recognizes official banking/gov domains (Vietcombank, MB, gov.vn) and forces safe gating.\n- Blacklist lookup matches known fraudulent domains and returns immediate risk level 100.\n- Lookup overhead < 10ms.",
            "Domain gating layer",
            5, "Done", "User Story", "C1SE.06", "Sprint 1", 24, "Pham Tan Hao"
        ),
        (
            "PB-05",
            "ResNet-18 Brand Impersonation Classifier",
            "AI Engineer",
            "analyze uploaded screenshots to detect counterfeit brand logos and deceptive visual layouts",
            "visual phishing attempts mimicking popular banking apps or e-wallets are detected even without text.",
            "- ResNet-18 CNN model processes image tensors (224x224).\n- Temperature Scaling (T=1.8) applied to calibrate raw logits into smooth probabilities.\n- Outputs brand classification confidence and visual fraud score.",
            "PyTorch Transfer Learning",
            5, "Done", "User Story", "C1SE.06", "Sprint 1", 44, "Nguyen Phan Duc Tuan"
        ),
        (
            "PB-06",
            "Forensics & Compression Artifact Analysis (ELA)",
            "Security Analyst",
            "apply Error Level Analysis (ELA) and EXIF metadata extraction on uploaded proof images",
            "digitally manipulated images, fake bank transfer receipts, and edited logos can be flagged.",
            "- ELA algorithm computes difference matrix between original and resaved JPEG.\n- Identifies high-frequency anomalies in text areas (fake balance/billings).\n- Extracts EXIF creation timestamps and camera/software signatures.",
            "OpenCV implementation",
            4, "Done", "User Story", "C1SE.06", "Sprint 2", 36, "Pham Tan Hao"
        ),
        (
            "PB-07",
            "Tesseract Vietnamese OCR Engine",
            "System",
            "extract text content from uploaded screenshots and scam message captures",
            "visual message evidence is converted into structured text for contextual linguistic risk evaluation.",
            "- Tesseract OCR configured with 'vie+eng' language packs.\n- Preprocessing pipeline: grayscale conversion, thresholding, noise removal.\n- Outputs extracted plain text with character confidence metrics.",
            "Tessdata Vietnamese",
            5, "Done", "User Story", "C1SE.06", "Sprint 2", 40, "Nguyen Phan Duc Tuan"
        ),
        (
            "PB-08",
            "Vietnamese Contextual Risk Keyword Engine",
            "AI Engineer",
            "detect urgent, coercive, and fraudulent language patterns in Vietnamese text",
            "scam scripts (mạo danh công an, đe dọa bắt giữ, nộp tiền phạt, khóa tài khoản) are pinpointed.",
            "- Keyword lexicon covers: impersonation, financial urgency, OTP capture, high-yield investment traps.\n- Regex matching extracts bank account numbers, OTP solicitations, and phone hotlines.\n- Outputs normalized keyword risk score [0, 1].",
            "Calibrated lexicon",
            5, "Done", "User Story", "C1SE.06", "Sprint 2", 32, "Dao Thi My Nhung"
        ),
        (
            "PB-09",
            "Chain-of-Thought (CoT) Multimodal Reasoning",
            "AI Engineer",
            "combine URL lexical signals, visual brand detection, and OCR text semantics via multi-step CoT",
            "the system reasons across all evidence sources to provide consistent, explainable fraud verdicts.",
            "- Implements multi-step deductive inference (Step 1: Domain, Step 2: Visual, Step 3: Text, Step 4: Consensus).\n- Soft Voting Consensus replaces crude max() function, preventing erratic 0% vs 98% jumps.\n- Produces confidence-weighted final risk score.",
            "Core reasoning engine",
            5, "Done", "User Story", "C1SE.06", "Sprint 2", 42, "Nguyen Phan Duc Tuan"
        ),
        (
            "PB-10",
            "Human-Readable Explanation Generator",
            "Citizen",
            "receive clear, plain-language explanations of why a submission was deemed dangerous or safe",
            "citizens without technical knowledge understand the specific deception techniques being used.",
            "- System generates bulleted explanations (e.g., 'Phát hiện tên miền giả mạo', 'Hối thúc chuyển khoản khẩn cấp').\n- Explanations are synchronized with detected entities (brand, keywords, domain age).\n- Vietnamese language output is grammatically natural and non-technical.",
            "SHAP/Rule synthesis",
            4, "Done", "User Story", "C1SE.06", "Sprint 2", 30, "Tran Hoang Nhat Nam"
        ),
        (
            "PB-11",
            "Multimodal Scan Submission Web Interface",
            "Citizen",
            "submit suspicious URLs, message text, and screenshots through a unified, responsive web portal",
            "citizens can easily verify threats across mobile browsers or desktop PCs within seconds.",
            "- Single-page application with 3 input modalities (URL input, Text area, Drag-and-drop Image upload).\n- Real-time client-side validation and file format checks (JPEG, PNG, WebP up to 10MB).\n- Loading skeleton and progress indicators during backend processing.",
            "React 18 + Vite SPA",
            5, "In Progress", "User Story", "C1SE.06", "Sprint 3", 40, "Tran Hoang Nhat Nam"
        ),
        (
            "PB-12",
            "Visual Explanation & Risk Gauge Dashboard",
            "Citizen",
            "view an interactive breakdown of risk factors (Risk Gauge, Radar Chart, Actionable Advice)",
            "I can make an immediate, informed decision whether to engage or discard the suspicious interaction.",
            "- Tri-color Risk Gauge: Safe (0-39%), Suspicious (40-69%), Dangerous (70-100%).\n- Radar chart showing risk distribution (Domain, Visual, Linguistic, Urgency).\n- Specific, actionable safety recommendations ('Không cung cấp OTP', 'Liên hệ ngân hàng qua hotline chính thức').",
            "Recharts visualization",
            4, "In Progress", "User Story", "C1SE.06", "Sprint 3", 38, "Tran Hoang Nhat Nam"
        ),
        (
            "PB-13",
            "Local Inspection History & Offline Cache",
            "Citizen",
            "review previous scan results and audit trails stored securely in my browser",
            "I can re-read warning evidence without re-uploading sensitive files or re-running API scans.",
            "- Inspection history persisted in browser localStorage (capped at 50 most recent records).\n- Clear history button with confirmation dialog.\n- Detailed modal view to reopen full reasoning breakdown for any past scan.",
            "Client-side persistence",
            3, "In Progress", "User Story", "C1SE.06", "Sprint 3", 26, "Tran Hoang Nhat Nam"
        ),
        (
            "PB-14",
            "Incident Feedback & False Positive Reporting",
            "Citizen",
            "submit community feedback or report false positive / false negative scan verdicts",
            "the system dataset can be continuously curated and audited by security engineers.",
            "- 'Báo cáo sai lệch' modal on scan result screen.\n- Captures user explanation, contact email (optional), and flagged classification error.\n- Feedback record stored in database with pending audit status.",
            "Feedback loop",
            3, "In Progress", "User Story", "C1SE.06", "Sprint 3", 28, "Dao Thi My Nhung"
        ),
        (
            "PB-15",
            "Admin Incident Triage & Verification Queue",
            "Security Analyst",
            "review reported incidents, inspect user feedback, and verify scam classifications",
            "malicious threat campaigns can be validated and added to active protection lists.",
            "- Admin view listing all citizen incident submissions with status filters (Pending, Reviewed, Dismissed).\n- Detailed view displaying original inputs, AI scores, and user remarks.\n- Action buttons to approve as confirmed scam or dismiss false alarm.",
            "Admin role required",
            4, "To Do", "User Story", "C1SE.06", "Sprint 4", 36, "Pham Tan Hao"
        ),
        (
            "PB-16",
            "Threat Intelligence & Real-time Metrics Dashboard",
            "Admin",
            "monitor overall system throughput, common scam categories, and detection accuracy KPIs",
            "I have real-time visibility into prevailing fraud tactics and system operational health.",
            "- Overview metrics: Total Scans, Confirmed Scams %, Average Response Time (ms), False Positive Rate.\n- Time-series charts of daily scan volume and risk distribution.\n- Top targeted brands leaderboard (e.g., Vietcombank, Techcombank, VNeID).",
            "Analytics dashboard",
            4, "To Do", "User Story", "C1SE.06", "Sprint 4", 34, "Pham Tan Hao"
        ),
        (
            "PB-17",
            "Dynamic Whitelist & Blacklist Manager",
            "Admin",
            "dynamically add, update, or remove domain rules, keywords, and trusted brand signatures",
            "the system can instantly counter emerging zero-day phishing domains without redeploying code.",
            "- CRUD interface for domain whitelist and blacklist.\n- Add custom regex patterns and high-risk keywords with associated weight.\n- Instant cache invalidation to reflect updates immediately in active inference.",
            "Dynamic config manager",
            4, "To Do", "User Story", "C1SE.06", "Sprint 4", 30, "Nguyen Phan Duc Tuan"
        ),
        (
            "PB-18",
            "Detailed Incident Audit Report Export (PDF / CSV)",
            "Security Analyst",
            "export formal fraud investigation reports containing digital evidence and AI audit trail",
            "citizens or legal authorities can use the standardized report as evidence for cybercrime complaints.",
            "- Generates downloadable PDF report with timestamp, risk scores, forensic highlights, and prevention advice.\n- Export tabular incident logs to CSV for external security analysis.\n- Standardized header including DTU C1SE.06 verification signature.",
            "Report generator",
            3, "To Do", "User Story", "C1SE.06", "Sprint 4", 28, "Dao Thi My Nhung"
        ),
        (
            "PB-19",
            "Rate Limiting, Security Hardening & OWASP Compliance",
            "System Engineer",
            "implement API rate limiting, payload sanitization, and CORS security policies",
            "the public-facing API is protected against DDoS attacks, automated scraping, and injection vectors.",
            "- SlowAPI rate limiter restricts IP clients to 30 requests per minute.\n- Strict file mime-type and magic-byte validation on image uploads.\n- CORS configuration restricts allowed origins.\n- SQL injection and XSS defenses verified via OWASP ZAP scanning.",
            "Security hardening",
            5, "To Do", "Enabler", "C1SE.06", "Sprint 5", 32, "Pham Tan Hao"
        ),
        (
            "PB-20",
            "End-to-End Stress Testing & Model Calibration Validation",
            "QA Lead",
            "conduct regression testing, load testing (50 concurrent users), and verify balanced score distribution",
            "the deployed system operates stably, accurately, and reliably during Capstone final defense.",
            "- Comprehensive pytest suite (unit, integration, multimodal reasoning) achieves > 85% coverage.\n- Locust load test verifies p95 latency < 3.0s under 50 concurrent requests.\n- Calibration test verifies no extreme 0%/98% bipolar spikes on ambiguous inputs.",
            "QA verification suite",
            5, "To Do", "Tech Spike", "C1SE.06", "Sprint 5", 38, "Dao Thi My Nhung"
        )
    ]

    for r_idx, row in enumerate(backlog_data, start=7):
        ws_pb.write(r_idx, 1, row[0], cell_bold_left)
        ws_pb.write(r_idx, 2, row[1], cell_bold_left)
        ws_pb.write(r_idx, 3, row[2], cell_left)
        ws_pb.write(r_idx, 4, row[3], cell_left)
        ws_pb.write(r_idx, 5, row[4], cell_left)
        ws_pb.write(r_idx, 6, row[5], cell_left)
        ws_pb.write(r_idx, 7, row[6], cell_left)
        ws_pb.write(r_idx, 8, row[7], cell_center)
        
        st = row[8]
        if st == "Done":
            ws_pb.write(r_idx, 9, st, status_done)
        elif st == "In Progress":
            ws_pb.write(r_idx, 9, st, status_in_progress)
        else:
            ws_pb.write(r_idx, 9, st, status_todo)

        ws_pb.write(r_idx, 10, row[9], cell_center)
        ws_pb.write(r_idx, 11, row[10], cell_center)
        ws_pb.write(r_idx, 12, row[11], cell_center)
        ws_pb.write(r_idx, 13, row[12], cell_right)
        ws_pb.write(r_idx, 14, row[13], cell_left)

    total_row_idx = len(backlog_data) + 7
    ws_pb.write(total_row_idx, 1, "Total", total_fmt)
    for c in range(2, 13):
        ws_pb.write(total_row_idx, c, "", total_fmt)
    ws_pb.write_formula(total_row_idx, 13, f'=SUM(N8:N{total_row_idx})', total_fmt)
    ws_pb.write(total_row_idx, 14, "", total_fmt)

    # ==========================================
    # SPRINT BACKLOG TABS (Sprint 1 to Sprint 5)
    # ==========================================
    sprint_details = [
        ("Sprint 1", "Sprint 1 - Foundation & AI Models", [
            ("TS-01-01", "PB-01", "Setup FastAPI boilerplate, CORS, routing and logging", "Pham Tan Hao", 16, 16, "Done"),
            ("TS-01-02", "PB-01", "Initialize React 18 SPA with Vite and Tailwind", "Tran Hoang Nhat Nam", 12, 12, "Done"),
            ("TS-01-03", "PB-01", "Configure SQLite DB and SQLAlchemy schema definitions", "Pham Tan Hao", 8, 8, "Done"),
            ("TS-01-04", "PB-02", "Implement JWT auth endpoints and password hashing", "Pham Tan Hao", 18, 18, "Done"),
            ("TS-01-05", "PB-02", "Design AuthPage and token management in frontend", "Tran Hoang Nhat Nam", 10, 10, "Done"),
            ("TS-01-06", "PB-03", "Build 21-feature URL lexical extraction module", "Nguyen Phan Duc Tuan", 24, 24, "Done"),
            ("TS-01-07", "PB-03", "Train & export HistGradientBoosting PhishVN model", "Nguyen Phan Duc Tuan", 24, 24, "Done"),
            ("TS-01-08", "PB-04", "Implement domain gating whitelist/blacklist engine", "Pham Tan Hao", 14, 14, "Done"),
            ("TS-01-09", "PB-04", "Verify domain normalization & punycode handling", "Dao Thi My Nhung", 10, 10, "Done"),
            ("TS-01-10", "PB-05", "Fine-tune ResNet-18 model for Vietnamese brand logos", "Nguyen Phan Duc Tuan", 28, 28, "Done"),
            ("TS-01-11", "PB-05", "Apply temperature scaling (T=1.8) on PyTorch logits", "Nguyen Phan Duc Tuan", 16, 16, "Done")
        ]),
        ("Sprint 2", "Sprint 2 - OCR, Risk & Reasoning", [
            ("TS-02-01", "PB-06", "Implement OpenCV ELA forensics calculation pipeline", "Pham Tan Hao", 20, 20, "Done"),
            ("TS-02-02", "PB-06", "Extract image EXIF metadata and software markers", "Pham Tan Hao", 16, 16, "Done"),
            ("TS-02-03", "PB-07", "Integrate Tesseract OCR 5.x with Vietnamese tessdata", "Nguyen Phan Duc Tuan", 22, 22, "Done"),
            ("TS-02-04", "PB-07", "Add image pre-processing (adaptive thresholding, denoise)", "Nguyen Phan Duc Tuan", 18, 18, "Done"),
            ("TS-02-05", "PB-08", "Compile comprehensive Vietnamese scam fraud lexicon", "Dao Thi My Nhung", 18, 18, "Done"),
            ("TS-02-06", "PB-08", "Implement regex pattern matching for bank accounts & OTP", "Dao Thi My Nhung", 14, 14, "Done"),
            ("TS-02-07", "PB-09", "Develop Chain-of-Thought (CoT) 4-step reasoning logic", "Nguyen Phan Duc Tuan", 24, 24, "Done"),
            ("TS-02-08", "PB-09", "Implement soft consensus fusion to eliminate 0%/98% jumps", "Nguyen Phan Duc Tuan", 18, 18, "Done"),
            ("TS-02-09", "PB-10", "Create dynamic human-readable explanation builder", "Tran Hoang Nhat Nam", 18, 18, "Done"),
            ("TS-02-10", "PB-10", "Build unit tests for explanation text consistency", "Dao Thi My Nhung", 12, 12, "Done")
        ]),
        ("Sprint 3", "Sprint 3 - Frontend SPA & UI-UX", [
            ("TS-03-01", "PB-11", "Build ScanPage UI with multi-tab input (URL/Text/Image)", "Tran Hoang Nhat Nam", 22, 18, "In Progress"),
            ("TS-03-02", "PB-11", "Implement drag-and-drop screenshot uploader with preview", "Tran Hoang Nhat Nam", 18, 14, "In Progress"),
            ("TS-03-03", "PB-12", "Develop dynamic Risk Gauge component with color transitions", "Tran Hoang Nhat Nam", 20, 16, "In Progress"),
            ("TS-03-04", "PB-12", "Render multimodal evidence cards and safety suggestions", "Dao Thi My Nhung", 18, 12, "In Progress"),
            ("TS-03-05", "PB-13", "Implement localStorage cache for recent 50 scans", "Tran Hoang Nhat Nam", 14, 10, "In Progress"),
            ("TS-03-06", "PB-13", "Build HistoryPage with search, filter and detail replay", "Tran Hoang Nhat Nam", 12, 8, "In Progress"),
            ("TS-03-07", "PB-14", "Create incident feedback modal and API endpoint", "Dao Thi My Nhung", 16, 10, "In Progress"),
            ("TS-03-08", "PB-14", "Implement feedback validation and confirmation toasts", "Dao Thi My Nhung", 12, 8, "In Progress")
        ]),
        ("Sprint 4", "Sprint 4 - Admin Platform & Reports", [
            ("TS-04-01", "PB-15", "Build Admin incident review table with pagination and filter", "Pham Tan Hao", 20, 0, "To Do"),
            ("TS-04-02", "PB-15", "Implement incident triage actions (Verify, Dismiss, Flag)", "Pham Tan Hao", 16, 0, "To Do"),
            ("TS-04-03", "PB-16", "Develop Threat Intelligence analytics dashboard", "Pham Tan Hao", 20, 0, "To Do"),
            ("TS-04-04", "PB-16", "Implement KPI metric cards (Total Scans, Fraud %, Latency)", "Pham Tan Hao", 14, 0, "To Do"),
            ("TS-04-05", "PB-17", "Build Whitelist/Blacklist management UI and CRUD API", "Nguyen Phan Duc Tuan", 18, 0, "To Do"),
            ("TS-04-06", "PB-17", "Add dynamic keyword lexicon management interface", "Nguyen Phan Duc Tuan", 12, 0, "To Do"),
            ("TS-04-07", "PB-18", "Implement PDF report export generator with forensic stamp", "Dao Thi My Nhung", 18, 0, "To Do"),
            ("TS-04-08", "PB-18", "Implement CSV incident data export for external audit", "Dao Thi My Nhung", 10, 0, "To Do")
        ]),
        ("Sprint 5", "Sprint 5 - Hardening & Final Defense", [
            ("TS-05-01", "PB-19", "Configure SlowAPI rate limiting (30 requests/min/IP)", "Pham Tan Hao", 14, 0, "To Do"),
            ("TS-05-02", "PB-19", "Implement OWASP security headers, CORS and input cleansing", "Pham Tan Hao", 18, 0, "To Do"),
            ("TS-05-03", "PB-20", "Execute comprehensive pytest suite across all AI engines", "Dao Thi My Nhung", 18, 0, "To Do"),
            ("TS-05-04", "PB-20", "Perform Locust load and stress testing under 50 concurrency", "Pham Tan Hao", 12, 0, "To Do"),
            ("TS-05-05", "PB-20", "Verify model calibration and zero extreme score artifacts", "Nguyen Phan Duc Tuan", 14, 0, "To Do"),
            ("TS-05-06", "PB-20", "Prepare final presentation slide deck & live demo scenario", "Tran Hoang Nhat Nam", 20, 0, "To Do")
        ])
    ]

    sp_headers = ["Task Id", "PB Ref", "Task Description", "Assignee", "Est. Hours", "Actual Hours", "Status"]

    for sp_name, sp_title, tasks in sprint_details:
        ws_sp = workbook.add_worksheet(sp_name)
        ws_sp.set_column('A:A', 3)
        ws_sp.set_column('B:B', 14)  # Task Id
        ws_sp.set_column('C:C', 12)  # PB Ref
        ws_sp.set_column('D:D', 44)  # Task Description
        ws_sp.set_column('E:E', 22)  # Assignee
        ws_sp.set_column('F:F', 14)  # Est. Hours
        ws_sp.set_column('G:G', 14)  # Actual Hours
        ws_sp.set_column('H:H', 16)  # Status

        ws_sp.write('B2', sp_title, title_fmt)
        ws_sp.write('B3', "SFDS Capstone Development Team C1SE.06", subtitle_fmt)

        for c_idx, h in enumerate(sp_headers, start=1):
            ws_sp.write(4, c_idx, h, header_fmt)

        for r_idx, task in enumerate(tasks, start=5):
            ws_sp.write(r_idx, 1, task[0], cell_bold_left)
            ws_sp.write(r_idx, 2, task[1], cell_center)
            ws_sp.write(r_idx, 3, task[2], cell_left)
            ws_sp.write(r_idx, 4, task[3], cell_left)
            ws_sp.write(r_idx, 5, task[4], cell_right)
            ws_sp.write(r_idx, 6, task[5], cell_right)

            st = task[6]
            if st == "Done":
                ws_sp.write(r_idx, 7, st, status_done)
            elif st == "In Progress":
                ws_sp.write(r_idx, 7, st, status_in_progress)
            else:
                ws_sp.write(r_idx, 7, st, status_todo)

        total_r = len(tasks) + 5
        ws_sp.write(total_r, 1, "Total", total_fmt)
        ws_sp.write(total_r, 2, "", total_fmt)
        ws_sp.write(total_r, 3, "", total_fmt)
        ws_sp.write(total_r, 4, "", total_fmt)
        ws_sp.write_formula(total_r, 5, f'=SUM(F6:F{total_r})', total_fmt)
        ws_sp.write_formula(total_r, 6, f'=SUM(G6:G{total_r})', total_fmt)
        ws_sp.write(total_r, 7, "", total_fmt)

    workbook.close()
    print(f"Successfully generated: {filename}")

if __name__ == "__main__":
    create_backlog()

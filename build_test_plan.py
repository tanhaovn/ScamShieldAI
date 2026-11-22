from pathlib import Path
from datetime import date
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

OUT = Path(r"D:/scam-detector/C1SE.06_TestPlan_SFDS_v1.0.docx")

NAVY = "17365D"
BLUE = "D9EAF7"
PALE = "F4F8FB"
GRAY = "D9D9D9"
WHITE = "FFFFFF"
BLACK = "000000"


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_borders(cell, color=GRAY, size="6"):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = borders.find(qn(f"w:{edge}"))
        if el is None:
            el = OxmlElement(f"w:{edge}")
            borders.append(el)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), size)
        el.set(qn("w:color"), color)


def set_cell_margins(cell, top=90, start=100, bottom=90, end=100):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, val in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")


def repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def prevent_row_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    tr_pr.append(cant_split)


def keep_with_next(paragraph):
    paragraph.paragraph_format.keep_with_next = True


def add_page_number(paragraph):
    run = paragraph.add_run("Page ")
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = "PAGE"
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_char1, instr_text, fld_char2])


def format_run(run, size=None, bold=None, color=BLACK, italic=None):
    run.font.name = "Times New Roman"
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Times New Roman")
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Times New Roman")
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Times New Roman")
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)


def add_table(doc, headers, rows, widths=None, font_size=9, header_fill=NAVY):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.style = "Table Grid"
    hdr = table.rows[0]
    repeat_table_header(hdr)
    prevent_row_split(hdr)
    for i, text in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = str(text)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_shading(cell, header_fill)
        set_cell_borders(cell)
        set_cell_margins(cell)
        if widths:
            cell.width = Inches(widths[i])
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            format_run(r, font_size, True, WHITE)
    for row_index, values in enumerate(rows):
        body_row = table.add_row()
        prevent_row_split(body_row)
        cells = body_row.cells
        for i, value in enumerate(values):
            cell = cells[i]
            cell.text = "" if value is None else str(value)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_borders(cell)
            set_cell_margins(cell)
            if widths:
                cell.width = Inches(widths[i])
            if row_index % 2 == 1:
                set_cell_shading(cell, PALE)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 0 or len(str(value)) < 18 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            for r in p.runs:
                format_run(r, font_size)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    format_run(r, 11)
    return p


def add_numbered(doc, text):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    format_run(r, 11)
    return p


def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    keep_with_next(p)
    return p


def add_body(doc, text, bold_lead=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    if bold_lead and text.startswith(bold_lead):
        r1 = p.add_run(bold_lead)
        format_run(r1, 11, True)
        r2 = p.add_run(text[len(bold_lead):])
        format_run(r2, 11)
    else:
        r = p.add_run(text)
        format_run(r, 11)
    return p


doc = Document()
doc.core_properties.title = "SFDS Test Plan"
doc.core_properties.subject = "Test Plan for Scam Fraud Detection System with Explanations"
doc.core_properties.author = "C1SE.06"
doc.core_properties.keywords = "SFDS, Test Plan, C1SE.06, CMU-SE 450"

for section in doc.sections:
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.72)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(0.8)
    section.header_distance = Inches(0.35)
    section.footer_distance = Inches(0.35)

styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Times New Roman"
normal._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
normal.font.size = Pt(11)
normal.font.color.rgb = RGBColor(0, 0, 0)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15

title_style = styles["Title"]
title_style.font.name = "Times New Roman"
title_style._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
title_style._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
title_style.font.size = Pt(24)
title_style.font.bold = True
title_style.font.color.rgb = RGBColor(0, 0, 0)
title_ppr = title_style.element.get_or_add_pPr()
title_border = title_ppr.find(qn("w:pBdr"))
if title_border is not None:
    title_ppr.remove(title_border)

for name, size in (("Heading 1", 15), ("Heading 2", 12), ("Heading 3", 11)):
    st = styles[name]
    st.font.name = "Times New Roman"
    st._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    st._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.color.rgb = RGBColor(0, 0, 0)
    st.paragraph_format.space_before = Pt(10 if name == "Heading 1" else 7)
    st.paragraph_format.space_after = Pt(5)
    st.paragraph_format.keep_with_next = True

for section in doc.sections:
    footer = section.footer
    p = footer.paragraphs[0]
    p.text = "C1SE.06  SFDS Test Plan  Version 1.0\t"
    p.paragraph_format.tab_stops.add_tab_stop(Inches(6.25), WD_TAB_ALIGNMENT.RIGHT)
    format_run(p.runs[0], 9)
    add_page_number(p)

# Cover
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(2)
r = p.add_run("DUY TAN UNIVERSITY")
format_run(r, 14, True)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(18)
r = p.add_run("SCHOOL OF COMPUTER SCIENCE  CMU-SE 450")
format_run(r, 12, True)

p = doc.add_paragraph(style="Title")
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(42)
p.paragraph_format.space_after = Pt(12)
p.add_run("Test Plan")

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(8)
r = p.add_run("Scam Fraud Detection System with Explanations")
format_run(r, 16, True)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(26)
r = p.add_run("SFDS  Project C1SE.06")
format_run(r, 13, True)

meta = add_table(doc, ["Document", "Value"], [
    ["Version", "1.0"],
    ["Document date", "20 Nov 2026"],
    ["Prepared by", "Dao Thi My Nhung  QA Lead"],
    ["Created by", "C1SE.06"],
    ["Approved by", "Eng. Ha Manh Toan  Project Mentor"],
    ["Status", "For review and approval"],
], widths=[1.7, 4.9], font_size=10)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(12)
r = p.add_run("Team members")
format_run(r, 11, True)
for name in ("Pham Tan Hao", "Dao Thi My Nhung", "Tran Hoang Nhat Nam", "Nguyen Phan Duc Tuan"):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(1)
    format_run(p.add_run(name), 10)

doc.add_page_break()

add_heading(doc, "Document control", 1)
add_heading(doc, "Project information", 2)
add_table(doc, ["Field", "Details"], [
    ["Project acronym", "SFDS"],
    ["Project title", "Scam Fraud Detection System with Explanations"],
    ["Project code", "CMU-SE 450  C1SE.06"],
    ["Academic year", "2024 to 2025  Capstone Period"],
    ["Lead institution", "Duy Tan University  School of Computer Science"],
    ["Project mentor", "Eng. Ha Manh Toan"],
    ["Project leader", "Pham Tan Hao"],
    ["QA lead", "Dao Thi My Nhung"],
    ["Delivery plan", "Five sprints across Week 1 to Week 15"],
], widths=[1.8, 4.8], font_size=9.5)

add_heading(doc, "Team and responsibilities", 2)
add_table(doc, ["Name", "Student ID", "Project role", "Primary test responsibility"], [
    ["Pham Tan Hao", "29219020823", "Project Leader and Full-stack Developer", "Test coordination, backend, security, performance"],
    ["Dao Thi My Nhung", "29209200048", "QA Lead and UI-UX Designer", "Test planning, UI, regression, defect reporting"],
    ["Tran Hoang Nhat Nam", "29219423638", "Frontend Developer and Technical Writer", "Frontend, usability, browser compatibility, evidence"],
    ["Nguyen Phan Duc Tuan", "29211151140", "AI Lead and Full-stack Developer", "Model, OCR, calibration, AI pipeline validation"],
], widths=[1.35, 1.05, 2.1, 2.25], font_size=8.5)

add_heading(doc, "Document approvals", 2)
add_table(doc, ["Reviewer or approver", "Role", "Signature", "Date"], [
    ["Pham Tan Hao", "Project Leader", "", ""],
    ["Dao Thi My Nhung", "QA Lead", "", ""],
    ["Eng. Ha Manh Toan", "Project Mentor", "", ""],
], widths=[1.7, 1.7, 1.8, 1.4], font_size=9)

add_heading(doc, "Revision history", 2)
add_table(doc, ["Version", "Date", "Change", "Author", "Approval"], [
    ["1.0", "20 Nov 2026", "Initial test plan for SFDS", "Dao Thi My Nhung", "Pending"],
], widths=[0.8, 1.2, 2.6, 1.5, 1.0], font_size=9)

doc.add_page_break()

add_heading(doc, "1 Introduction", 1)
add_heading(doc, "1.1 Purpose", 2)
add_body(doc, "This Test Plan defines how team C1SE.06 will verify and validate the Scam Fraud Detection System with Explanations. It converts the product backlog into a controlled testing scope covering the FastAPI and React platform, the multimodal AI pipeline, explainable risk results, administration functions, reporting, security, and performance.")
add_body(doc, "The plan gives the team one basis for test design, execution, defect handling, sprint closure, and final acceptance. Detailed test cases and sprint test reports are maintained separately and trace back to the product backlog identifiers PB-01 through PB-20.")

add_heading(doc, "1.2 Quality objectives", 2)
for item in [
    "Plan test coverage for all 20 product backlog items and execute every Priority 5 test at least once before release.",
    "Verify that risk scores, labels, evidence, and Vietnamese explanations remain consistent across URL, text, and image inputs.",
    "Confirm that trusted domains are not falsely flagged and known malicious domains receive immediate high-risk handling.",
    "Validate secure authentication, authorization, upload controls, input sanitization, rate limiting, and restricted CORS behavior.",
    "Achieve more than 85 percent automated test coverage for the unit and integration suite defined in PB-20.",
    "Demonstrate p95 response latency below 3.0 seconds under 50 concurrent users for the final load test defined in PB-20.",
    "Release with no unresolved Critical or High severity defect and with at least 90 percent of executed test cases passing.",
]:
    add_bullet(doc, item)

add_heading(doc, "1.3 Reference baseline", 2)
add_table(doc, ["Reference", "Use in this plan"], [
    ["C1SE.06 Product Backlog SFDS version 1.0", "Source of scope, acceptance criteria, ownership, sprint allocation, and estimates"],
    ["C1SE.20 Test Plan version 1.0", "Reference for the document structure, governance topics, and test management sections"],
    ["C1SE.20 Sprint 1 to Sprint 3 Test Cases", "Reference for test case fields, module grouping, and sprint report summaries"],
], widths=[2.45, 4.15], font_size=9)

add_heading(doc, "2 Test scope", 1)
add_heading(doc, "2.1 In-scope functions", 2)

sprint_scope = [
    ["Sprint 1", "PB-01 to PB-05", "Architecture, JWT authentication, PhishVN URL detection, domain gating, ResNet-18 brand impersonation"],
    ["Sprint 2", "PB-06 to PB-10", "ELA and EXIF forensics, Vietnamese OCR, fraud keywords and regex, multimodal reasoning, explanations"],
    ["Sprint 3", "PB-11 to PB-14", "Multimodal scan UI, risk visualization, local history, citizen feedback and false-result reporting"],
    ["Sprint 4", "PB-15 to PB-18", "Incident triage, threat metrics, whitelist and blacklist management, PDF and CSV exports"],
    ["Sprint 5", "PB-19 to PB-20", "Security hardening, rate limiting, regression, load testing, calibration, final acceptance"],
]
add_table(doc, ["Sprint", "Backlog", "Functional scope"], sprint_scope, widths=[0.9, 1.25, 4.45], font_size=9)

add_heading(doc, "2.2 User interface scope", 2)
for item in [
    "Public scan interface for URL, free-text, and image submissions with client-side validation and progress feedback.",
    "Result interface containing a risk gauge, evidence breakdown, radar visualization, explanations, and safety recommendations.",
    "Inspection history with search, filters, detail replay, and clear-history confirmation.",
    "Incident feedback workflow with optional contact information and validation feedback.",
    "Admin authentication, incident triage, metrics dashboard, dynamic protection lists, and report export controls.",
]:
    add_bullet(doc, item)

add_heading(doc, "2.3 Interfaces and data scope", 2)
for item in [
    "REST APIs between the React frontend and FastAPI backend.",
    "SQLAlchemy persistence using SQLite locally and MySQL where configured.",
    "Model artifacts for HistGradientBoosting and ResNet-18, Tesseract vie and eng language data, and rules or registries used by the reasoning pipeline.",
    "Supported uploads: JPEG, PNG, and WebP up to 10 MB, including metadata and malformed-file validation cases.",
    "Generated PDF investigation reports and CSV incident logs.",
]:
    add_bullet(doc, item)

add_heading(doc, "2.4 Out-of-scope items", 2)
for item in [
    "Production operation by banks, government agencies, or law-enforcement organizations.",
    "Real financial transfers, account recovery, or direct blocking of third-party accounts and domains.",
    "Retraining with new external datasets unless a backlog change explicitly adds that work.",
    "Native mobile applications and browsers or file formats not listed in the agreed compatibility matrix.",
]:
    add_bullet(doc, item)

add_heading(doc, "3 Test strategy", 1)
add_heading(doc, "3.1 Test levels", 2)
add_table(doc, ["Level", "Purpose", "Primary owner", "Evidence"], [
    ["Unit", "Verify feature extractors, validators, score calculations, API services, and UI components in isolation", "Developers", "pytest or Jest results and coverage"],
    ["Integration", "Verify model, OCR, rules, database, and frontend-backend contracts", "Developer and QA", "API results, logs, database records"],
    ["System", "Verify complete public and admin workflows using representative inputs", "QA Lead and team", "Executed cases, screenshots, exports"],
    ["Acceptance", "Confirm backlog acceptance criteria and release readiness", "Project Leader and Mentor", "Acceptance checklist and approval"],
], widths=[0.9, 3.0, 1.4, 1.4], font_size=8.5)

add_heading(doc, "3.2 Test types and approach", 2)
add_table(doc, ["Test type", "Approach", "Main coverage"], [
    ["Functional", "Black-box and API validation against acceptance criteria", "PB-02 to PB-18"],
    ["AI and model", "Golden datasets, boundary scores, calibration checks, false positive and false negative review", "PB-03, PB-05, PB-07 to PB-10, PB-20"],
    ["Forensic", "Controlled image edits, compression levels, EXIF variants, and missing metadata", "PB-06"],
    ["Security", "Authentication, authorization, injection, XSS, CORS, upload validation, rate limit, OWASP ZAP", "PB-02 and PB-19"],
    ["Performance", "Timing assertions, repeated scans, Locust load at 50 concurrent users, p95 measurement", "PB-03, PB-04, PB-20"],
    ["Usability", "Task completion, readability of Vietnamese explanations, responsive layout, validation clarity", "PB-10 to PB-14"],
    ["Compatibility", "Latest stable desktop Chrome and Edge; responsive browser checks at agreed viewport sizes", "PB-11 to PB-18"],
    ["Regression", "Risk-based rerun after defect fixes and at each sprint closure", "All implemented modules"],
], widths=[1.05, 3.35, 2.3], font_size=8.5)

add_heading(doc, "3.3 Test design techniques", 2)
for item in [
    "Equivalence partitioning for valid and invalid URLs, text, credentials, files, status values, and export filters.",
    "Boundary value analysis for score bands 0 to 39, 40 to 69, and 70 to 100; 10 MB uploads; token expiry; 30 requests per minute; history capacity of 50; and performance thresholds.",
    "Decision tables for whitelist versus blacklist precedence, authentication roles, incident actions, and multimodal consensus outcomes.",
    "State-transition testing for feedback status, incident triage status, authentication sessions, and history operations.",
    "Pairwise combinations of URL, text, and image evidence to verify consensus fusion and explanation consistency.",
    "Exploratory testing for Vietnamese scam wording, deceptive subdomains, unusual images, ambiguous evidence, and user workflow failures.",
]:
    add_bullet(doc, item)

add_heading(doc, "3.4 Test environment", 2)
add_table(doc, ["Layer", "Planned configuration"], [
    ["Frontend", "React 18, Vite, Tailwind CSS"],
    ["Backend", "FastAPI on Python 3.12, Uvicorn, SQLAlchemy"],
    ["AI and image", "PyTorch, Scikit-Learn, Tesseract OCR with vie and eng data, OpenCV"],
    ["Database", "SQLite for local tests and MySQL when the integrated environment is configured"],
    ["Browsers", "Latest stable Chrome and Edge; agreed responsive desktop and mobile-width viewports"],
    ["API and security", "Postman or equivalent API client, pytest, OWASP ZAP"],
    ["Performance", "Locust with 50 concurrent virtual users and server monitoring"],
    ["Test evidence", "Versioned test cases, execution log, defect log, screenshots, API responses, generated PDF and CSV files"],
], widths=[1.45, 5.15], font_size=9)

add_heading(doc, "3.5 Test data management", 2)
for item in [
    "Maintain labeled safe, suspicious, and malicious URLs, including Vietnamese banks, government domains, punycode, IP-address URLs, redirects, and deceptive subdomains.",
    "Maintain screenshots and messages representing safe content, impersonation, urgency, OTP solicitation, fake investment, fake transfer receipts, and edited images.",
    "Remove or mask personal data. Do not use real credentials, OTP values, bank balances, or citizen evidence without authorization.",
    "Version the golden dataset and expected verdicts so model or rule changes can be compared consistently.",
    "Keep destructive security payloads isolated from production services and third-party systems.",
]:
    add_bullet(doc, item)

add_heading(doc, "4 Test criteria", 1)
add_heading(doc, "4.1 Entry criteria", 2)
for item in [
    "The sprint backlog item and acceptance criteria are clear and approved for testing.",
    "The target build is deployed, version identified, and basic smoke testing has passed.",
    "Required model files, OCR language packs, database migrations, and test accounts are available.",
    "Test data and expected outcomes are reviewed, including privacy and safety constraints.",
    "Known blockers and environment limitations are recorded before execution begins.",
]:
    add_bullet(doc, item)

add_heading(doc, "4.2 Pass and fail rules", 2)
add_table(doc, ["Result", "Definition"], [
    ["Pass", "Observed result matches all expected results and no new defect is found."],
    ["Fail", "One or more expected results are not met, or an unacceptable defect occurs."],
    ["Blocked", "Execution cannot continue because of an environment, dependency, data, or build issue."],
    ["Not run", "The test has not been executed in the identified build."],
    ["Not applicable", "The case does not apply to the selected configuration and the reason is recorded."],
], widths=[1.25, 5.35], font_size=9)

add_heading(doc, "4.3 Exit and release criteria", 2)
for item in [
    "All planned Priority 5 cases are executed and all PB-01 through PB-20 items have traceable test evidence.",
    "Overall executed-case pass rate is at least 90 percent, excluding approved Not applicable cases.",
    "No unresolved Critical or High severity defect remains. Medium defects require an agreed workaround or documented acceptance.",
    "Automated coverage is above 85 percent for the suite defined in PB-20.",
    "The final load test demonstrates p95 latency below 3.0 seconds with 50 concurrent users.",
    "Calibration review finds no unexplained extreme-score jumps for ambiguous inputs.",
    "The Project Leader and Mentor review the final test report and acceptance evidence.",
]:
    add_bullet(doc, item)

add_heading(doc, "4.4 Suspension and resumption", 2)
add_body(doc, "Testing may be suspended when the build cannot start, the database is corrupted, required model artifacts are missing, more than 30 percent of smoke tests fail, or execution could expose sensitive data or an external system. Testing resumes after the blocking issue is fixed, a new build is identified, smoke tests pass, and affected cases are reset for re-execution.")

add_heading(doc, "4.5 Defect severity", 2)
add_table(doc, ["Severity", "Definition", "Example", "Release rule"], [
    ["Critical", "System unusable, security compromise, data exposure, or consistently unsafe verdict", "Authentication bypass or malicious evidence reported as safe without warning", "Must be fixed"],
    ["High", "Core function fails with no acceptable workaround", "Scan fails, admin action corrupts data, export omits required evidence", "Must be fixed"],
    ["Medium", "Function is impaired but a workaround exists", "One filter fails or explanation contains a material formatting error", "Fix or formally accept"],
    ["Low", "Minor cosmetic or wording issue with no material effect", "Alignment, spacing, or non-blocking label defect", "May be deferred"],
], widths=[0.8, 2.35, 2.6, 1.0], font_size=8)

add_heading(doc, "5 Test management", 1)
add_heading(doc, "5.1 Responsibilities", 2)
add_table(doc, ["Role", "Responsibilities"], [
    ["Project Leader", "Approve scope, prioritize defects, coordinate builds, confirm release decision"],
    ["QA Lead", "Maintain this plan, design and review cases, coordinate execution, report quality status, manage regression"],
    ["AI Lead", "Provide model artifacts and golden data, validate calibration and AI-specific results, investigate model defects"],
    ["Frontend Developer", "Support UI, accessibility, responsive, browser, history, and documentation tests"],
    ["All team members", "Perform peer review, execute assigned tests, reproduce defects, attach evidence, and verify fixes"],
    ["Project Mentor", "Review acceptance evidence and approve or reject final readiness"],
], widths=[1.55, 5.05], font_size=9)

add_heading(doc, "5.2 Tools", 2)
add_table(doc, ["Purpose", "Tool", "Output"], [
    ["Test case tracking", "Excel or Google Sheets", "Sprint test case files and test reports"],
    ["API and integration testing", "Postman and pytest", "Requests, assertions, logs, coverage"],
    ["Frontend testing", "Jest or Vitest and browser developer tools", "Component results and screenshots"],
    ["Security testing", "OWASP ZAP and manual validation", "Findings and evidence"],
    ["Load testing", "Locust", "Latency, throughput, and error-rate report"],
    ["Defect and task tracking", "Team project board", "Defect status, owner, severity, target sprint"],
    ["Communication", "Gmail, Zalo, or Discord", "Review coordination and blocker notification"],
], widths=[1.7, 2.45, 2.45], font_size=8.5)

add_heading(doc, "5.3 Test case standard", 2)
add_body(doc, "Each detailed test case should contain: Test Case ID, module or representation, related backlog ID, priority, prerequisites, test steps, test data, expected result, actual result, execution count, status, executor, build, execution date, and defect reference when failed. Use the identifier pattern TC_SFDS_S< sprint >_< module >_< sequence >, for example TC_SFDS_S2_OCR_001.")

add_heading(doc, "5.4 Defect workflow", 2)
for step in [
    "Record the defect with build, environment, severity, reproduction steps, expected result, actual result, and evidence.",
    "Triage the defect and assign an owner and target sprint.",
    "Fix and developer-check the defect in a clearly identified build.",
    "QA re-tests the failed case and performs risk-based regression around the change.",
    "Close the defect when verification passes; otherwise reopen it with updated evidence.",
]:
    add_numbered(doc, step)

add_heading(doc, "5.5 Test deliverables", 2)
for item in [
    "Approved Test Plan and backlog traceability matrix.",
    "Sprint test case workbooks and sprint test reports for Sprint 1 through Sprint 5.",
    "Automated unit and integration test results with coverage evidence.",
    "Defect log and verification evidence.",
    "Security scan and load test reports.",
    "Final test summary and acceptance sign-off.",
]:
    add_bullet(doc, item)

doc.add_page_break()
add_heading(doc, "6 Test schedule", 1)
add_table(doc, ["Phase", "Period", "Primary test work", "Exit evidence"], [
    ["Planning and baseline", "Before Sprint 1 testing", "Approve plan, prepare environments, data, case templates, and smoke suite", "Approved plan and ready environment"],
    ["Sprint 1", "Week 1 to Week 3", "Architecture smoke, authentication, URL model, domain gating, visual model", "Sprint 1 test report"],
    ["Sprint 2", "Week 4 to Week 6", "Forensics, OCR, keywords, multimodal consensus, explanation quality", "Sprint 2 test report"],
    ["Sprint 3", "Week 7 to Week 9", "Public UI, result visualization, history, feedback, responsive checks", "Sprint 3 test report"],
    ["Sprint 4", "Week 10 to Week 12", "Admin triage, intelligence metrics, dynamic lists, PDF and CSV export", "Sprint 4 test report"],
    ["Sprint 5", "Week 13 to Week 15", "Security, full regression, load, calibration, final acceptance", "Final test report and sign-off"],
], widths=[1.15, 1.15, 3.3, 1.35], font_size=8.5)

add_heading(doc, "7 Product backlog traceability", 1)
trace_rows = [
    ["PB-01", "Sprint 1", "Architecture and core scaffolding", "Smoke, configuration, CI", "QA and Project Leader", "5"],
    ["PB-02", "Sprint 1", "User and admin authentication", "API, security, role, session", "Project Leader", "5"],
    ["PB-03", "Sprint 1", "PhishVN lexical URL detection", "Feature, model, latency, boundary", "AI Lead", "5"],
    ["PB-04", "Sprint 1", "Domain gating and trusted registry", "Whitelist, blacklist, normalization, latency", "Project Leader", "5"],
    ["PB-05", "Sprint 1", "ResNet-18 brand impersonation", "Model, calibration, image variants", "AI Lead", "5"],
    ["PB-06", "Sprint 2", "ELA and EXIF forensics", "Image manipulation, metadata, robustness", "Project Leader", "4"],
    ["PB-07", "Sprint 2", "Vietnamese OCR", "Accuracy, preprocessing, language, noise", "AI Lead", "5"],
    ["PB-08", "Sprint 2", "Vietnamese risk keywords", "Keyword, regex, false positive, normalization", "QA Lead", "5"],
    ["PB-09", "Sprint 2", "Multimodal reasoning", "Decision table, fusion, pairwise, calibration", "AI Lead", "5"],
    ["PB-10", "Sprint 2", "Human-readable explanations", "Content, entity alignment, Vietnamese usability", "Frontend and QA", "4"],
    ["PB-11", "Sprint 3", "Multimodal scan interface", "UI, validation, upload, responsive, progress", "Frontend", "5"],
    ["PB-12", "Sprint 3", "Risk gauge and visual explanation", "Score bands, charts, advice, consistency", "Frontend and QA", "4"],
    ["PB-13", "Sprint 3", "Local history and offline cache", "Capacity, persistence, clear, detail replay", "Frontend", "3"],
    ["PB-14", "Sprint 3", "Incident feedback", "Validation, optional email, persistence, status", "QA Lead", "3"],
    ["PB-15", "Sprint 4", "Admin incident triage", "Authorization, filters, states, actions", "Project Leader", "4"],
    ["PB-16", "Sprint 4", "Threat intelligence metrics", "KPI accuracy, charts, timing, empty data", "Project Leader", "4"],
    ["PB-17", "Sprint 4", "Whitelist and blacklist manager", "CRUD, regex, keyword weight, cache invalidation", "AI Lead", "4"],
    ["PB-18", "Sprint 4", "Incident report export", "PDF, CSV, evidence, encoding, filters", "QA Lead", "3"],
    ["PB-19", "Sprint 5", "Security hardening", "Rate limit, upload security, CORS, injection, XSS", "Project Leader", "5"],
    ["PB-20", "Sprint 5", "E2E stress and calibration", "Regression, coverage, load, p95, score stability", "QA and AI Lead", "5"],
]
add_table(doc, ["PB ID", "Sprint", "Backlog item", "Planned test focus", "Owner", "Priority"], trace_rows, widths=[0.65, 0.75, 1.75, 2.45, 1.15, 0.55], font_size=7.7)

add_heading(doc, "8 Risks and assumptions", 1)
add_heading(doc, "8.1 Test risks", 2)
add_table(doc, ["Risk", "Probability", "Impact", "Mitigation"], [
    ["Vietnamese OCR varies with image quality and font", "High", "High", "Use diverse golden images, preprocessing variants, and confidence review"],
    ["Model or rules produce false positives or false negatives", "Medium", "High", "Use balanced datasets, threshold boundaries, manual review, and regression"],
    ["Malformed or hostile uploads affect stability or security", "Medium", "High", "Validate MIME and magic bytes, isolate files, run security tests"],
    ["Third-party model or OCR artifacts differ between environments", "Medium", "Medium", "Pin versions and checksums; verify setup before execution"],
    ["Sensitive evidence is exposed in logs or test artifacts", "Low", "High", "Use synthetic or masked data and restrict artifact access"],
    ["Insufficient time remains after development", "Medium", "High", "Test each sprint, automate critical checks, and prioritize by risk"],
    ["Load environment does not represent final deployment", "Medium", "Medium", "Record hardware and configuration; compare baseline and target runs"],
], widths=[2.25, 0.85, 0.75, 2.9], font_size=8.2)

add_heading(doc, "8.2 Assumptions", 2)
add_table(doc, ["Assumption", "Impact if incorrect", "Owner"], [
    ["Backlog acceptance criteria remain the approved baseline", "Coverage and expected results require revision", "Project Leader"],
    ["Versioned model artifacts and Vietnamese OCR data are available", "AI and OCR tests cannot start", "AI Lead"],
    ["Representative safe and scam test data can be prepared legally", "Accuracy and calibration evidence is incomplete", "QA Lead"],
    ["The integrated environment exposes required logs and metrics", "Defects and performance results are harder to diagnose", "Project Leader"],
    ["All team members execute and review assigned tests", "Sprint closure and traceability are delayed", "All members"],
], widths=[3.0, 2.6, 1.1], font_size=8.5)

add_heading(doc, "9 Approval", 1)
add_body(doc, "Approval confirms that the defined scope, approach, responsibilities, criteria, and schedule are suitable for testing SFDS. Any material change to backlog scope, release criteria, or test environment must be recorded in the revision history and reviewed by the Project Leader, QA Lead, and Project Mentor.")
add_table(doc, ["Name", "Role", "Decision", "Signature", "Date"], [
    ["Pham Tan Hao", "Project Leader", "Approve or reject", "", ""],
    ["Dao Thi My Nhung", "QA Lead", "Approve or reject", "", ""],
    ["Eng. Ha Manh Toan", "Project Mentor", "Approve or reject", "", ""],
], widths=[1.5, 1.45, 1.35, 1.35, 1.1], font_size=8.5)

# Prevent stray blank page where possible and normalize all remaining runs.
for paragraph in doc.paragraphs:
    for run in paragraph.runs:
        if run.font.name is None:
            format_run(run, 11)

doc.save(OUT)
print(OUT)

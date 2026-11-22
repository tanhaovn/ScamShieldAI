from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source.docx"
OUTPUT = ROOT / "C1SE.06_DatabaseDesign_SFDS_v1.1_corrected.docx"
ERD_IMAGE = ROOT / "erd-sfds-black-white.png"


TABLES = {
    "users": [
        ["Id", "Field", "Type", "Constraint", "Description"],
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique auto-generated identifier for the user."],
        ["2", "email", "VARCHAR(255)", "Required, Unique", "The user's login email address."],
        ["3", "password_hash", "VARCHAR(255)", "Required", "Password hash generated using PBKDF2-HMAC-SHA256 with a random salt and 100,000 iterations."],
        ["4", "full_name", "VARCHAR(255)", "Optional", "The full name of the user."],
        ["5", "role", "ENUM('user','admin')", "Default: 'user'", "Role-based access level governing system permissions."],
        ["6", "is_active", "BOOLEAN", "Required, Default: true", "Flag indicating whether the account is active."],
        ["7", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the account was created."],
        ["8", "updated_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP; updated on modification", "Timestamp of the last profile update."],
    ],
    "auth_identities": [
        ["Id", "Field", "Type", "Constraint", "Description"],
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique identifier for an external identity binding."],
        ["2", "user_id", "INT", "Required, Foreign Key", "References users(id) ON DELETE CASCADE."],
        ["3", "provider", "VARCHAR(50)", "Required, Composite Unique with provider_subject", "Name of the external identity provider, such as 'google'."],
        ["4", "provider_subject", "VARCHAR(255)", "Required, Composite Unique with provider", "Subject identifier issued by the external identity provider."],
        ["5", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the external identity was linked."],
    ],
    "scam_categories": [
        ["Id", "Field", "Type", "Constraint", "Description"],
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique category identifier."],
        ["2", "code", "VARCHAR(50)", "Required, Unique", "Unique category code, such as 'phishing' or 'fake_invoice'."],
        ["3", "display_name", "VARCHAR(150)", "Required", "Human-readable Vietnamese category name."],
        ["4", "description", "TEXT", "Optional", "Detailed description of the scam category."],
    ],
    "scan_history": [
        ["Id", "Field", "Type", "Constraint", "Description"],
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique scan record identifier."],
        ["2", "user_id", "INT", "Required, Foreign Key", "References users(id) ON DELETE CASCADE."],
        ["3", "image_url", "VARCHAR(1024)", "Required", "Storage URL or path of the scanned image."],
        ["4", "original_filename", "VARCHAR(512)", "Optional", "Original name of the uploaded file."],
        ["5", "extracted_text", "TEXT", "Optional", "Text extracted from the image by OCR."],
        ["6", "scam_category_id", "INT", "Optional, Foreign Key", "References scam_categories(id) ON DELETE SET NULL."],
        ["7", "risk_score", "INT", "Required", "Calculated risk score; the application represents it on a 0-100 scale."],
        ["8", "risk_level", "ENUM('an_toan','nghi_ngo','nguy_hiem')", "Required", "Categorical risk classification level."],
        ["9", "explanation", "TEXT", "Optional", "Plain-language explanation of the scan result."],
        ["10", "highlighted_regions", "JSON", "Optional", "Structured evidence, such as highlighted regions or flagged terms."],
        ["11", "suggested_action", "TEXT", "Optional", "Recommended safety actions for the user."],
        ["12", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the scan record was created."],
    ],
    "scan_feedback": [
        ["Id", "Field", "Type", "Constraint", "Description"],
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique feedback identifier."],
        ["2", "scan_id", "INT", "Optional, Foreign Key", "References scan_history(id) ON DELETE SET NULL."],
        ["3", "client_scan_id", "VARCHAR(100)", "Optional", "Client-generated identifier for feedback not linked to a stored scan."],
        ["4", "verdict", "ENUM('correct','false_alarm','missed_scam')", "Required", "User assessment of whether the scan result was correct."],
        ["5", "predicted_level", "VARCHAR(30)", "Required", "Risk level predicted when the scan was performed."],
        ["6", "risk_score", "INT", "Required", "Risk score associated with the submitted feedback."],
        ["7", "source_type", "VARCHAR(30)", "Required", "Type of analyzed input associated with the feedback."],
        ["8", "original_filename", "VARCHAR(512)", "Optional", "Original file name associated with the scan."],
        ["9", "note", "TEXT", "Optional", "Additional note supplied with the feedback."],
        ["10", "evidence_snapshot", "JSON", "Optional", "Snapshot of the evidence shown for the scan result."],
        ["11", "review_status", "VARCHAR(30)", "Required, Default: 'pending'", "Administrative review state of the feedback."],
        ["12", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the feedback was submitted."],
    ],
    "scam_keywords": [
        ["Id", "Field", "Type", "Constraint", "Description"],
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique keyword rule identifier."],
        ["2", "keyword", "VARCHAR(255)", "Required, Unique", "Vietnamese fraud keyword or regular-expression pattern."],
        ["3", "category", "VARCHAR(100)", "Required", "Fraud category associated with the keyword."],
        ["4", "weight", "INT", "Required, Default: 10", "Risk contribution weight accepted by the API from 1 to 50."],
        ["5", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the rule was registered."],
    ],
    "training_dataset": [
        ["Id", "Field", "Type", "Constraint", "Description"],
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique dataset sample identifier."],
        ["2", "image_url", "VARCHAR(1024)", "Required", "Storage path of the curated training image."],
        ["3", "scam_category_id", "INT", "Optional, Foreign Key", "References scam_categories(id) ON DELETE SET NULL."],
        ["4", "is_anonymized", "BOOLEAN", "Required, Default: false", "Flag indicating whether personally identifiable information has been removed."],
        ["5", "is_verified", "BOOLEAN", "Required, Default: false", "Flag indicating whether the ground-truth label has been verified."],
        ["6", "uploaded_by", "INT", "Required, Foreign Key", "References users(id) ON DELETE CASCADE."],
        ["7", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the sample was added."],
    ],
    "ai_models": [
        ["Id", "Field", "Type", "Constraint", "Description"],
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique AI model identifier."],
        ["2", "version_name", "VARCHAR(100)", "Required, Unique", "Unique registered model version name."],
        ["3", "description", "TEXT", "Optional", "Model architecture, configuration or dataset description."],
        ["4", "is_active", "BOOLEAN", "Required, Default: false", "Flag indicating whether the model is active."],
        ["5", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the model record was created."],
    ],
    "model_evaluations": [
        ["Id", "Field", "Type", "Constraint", "Description"],
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique evaluation identifier."],
        ["2", "ai_model_id", "INT", "Required, Foreign Key", "References ai_models(id) ON DELETE CASCADE."],
        ["3", "macro_f1", "DECIMAL(5,4)", "Optional", "Macro F1 score measured on the evaluation dataset."],
        ["4", "recall", "DECIMAL(5,4)", "Optional", "Recall measured on fraudulent samples."],
        ["5", "false_alarm_rate", "DECIMAL(5,4)", "Optional", "False-alarm rate measured on benign samples."],
        ["6", "explanation_usefulness", "DECIMAL(5,4)", "Optional", "Score assessing the usefulness of generated explanations."],
        ["7", "evaluated_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the evaluation was recorded."],
    ],
    "system_activity_logs": [
        ["Id", "Field", "Type", "Constraint", "Description"],
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique log entry identifier."],
        ["2", "admin_id", "INT", "Optional, Foreign Key", "References users(id) ON DELETE SET NULL."],
        ["3", "action_type", "VARCHAR(100)", "Required", "Type of administrative or automated system action."],
        ["4", "description", "TEXT", "Optional", "Detailed description of the recorded action."],
        ["5", "created_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the action was recorded."],
    ],
    "visitor_devices": [
        ["Id", "Field", "Type", "Constraint", "Description"],
        ["1", "id", "INT", "Primary Key, Auto-Increment", "Unique visitor-device record identifier."],
        ["2", "device_id", "VARCHAR(100)", "Required, Unique", "Client-generated identifier for the visitor device."],
        ["3", "device_name", "VARCHAR(160)", "Optional", "Human-readable device name when available."],
        ["4", "platform", "VARCHAR(120)", "Optional", "Operating system or device platform."],
        ["5", "browser", "VARCHAR(120)", "Optional", "Browser name and version when available."],
        ["6", "user_agent", "VARCHAR(1000)", "Optional", "Raw browser user-agent string."],
        ["7", "ip_address", "VARCHAR(64)", "Optional", "Recorded IP address of the visitor."],
        ["8", "latitude", "FLOAT", "Optional", "Approximate latitude when location permission is granted."],
        ["9", "longitude", "FLOAT", "Optional", "Approximate longitude when location permission is granted."],
        ["10", "location_accuracy", "FLOAT", "Optional", "Reported location accuracy in meters."],
        ["11", "location_permission", "VARCHAR(30)", "Required, Default: 'unknown'", "Current location-permission state reported by the client."],
        ["12", "visit_count", "INT", "Required, Default: 1", "Number of recorded visits from the device."],
        ["13", "first_seen_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP", "Timestamp when the device was first recorded."],
        ["14", "last_seen_at", "TIMESTAMP", "Default: CURRENT_TIMESTAMP; updated on modification", "Timestamp of the most recent recorded visit."],
    ],
}


def set_paragraph_text(paragraph, text):
    if not paragraph.runs:
        paragraph.add_run(text)
        return
    paragraph.runs[0].text = text
    for run in paragraph.runs[1:]:
        run.text = ""


def set_cell_text(cell, text):
    paragraph = cell.paragraphs[0]
    set_paragraph_text(paragraph, str(text))
    for extra in cell.paragraphs[1:]:
        set_paragraph_text(extra, "")


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = tr_pr.find(qn("w:tblHeader"))
    if tbl_header is None:
        tbl_header = OxmlElement("w:tblHeader")
        tr_pr.append(tbl_header)
    tbl_header.set(qn("w:val"), "true")


def prevent_row_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    if tr_pr.find(qn("w:cantSplit")) is None:
        tr_pr.append(OxmlElement("w:cantSplit"))


def resize_and_fill_table(table, rows):
    while len(table.rows) < len(rows):
        table._tbl.append(deepcopy(table.rows[-1]._tr))
    while len(table.rows) > len(rows):
        table._tbl.remove(table.rows[-1]._tr)
    for row_index, values in enumerate(rows):
        for col_index, value in enumerate(values):
            set_cell_text(table.rows[row_index].cells[col_index], value)
        prevent_row_split(table.rows[row_index])
    set_repeat_table_header(table.rows[0])


def find_paragraph(doc, exact_text):
    for paragraph in doc.paragraphs:
        if paragraph.text.strip() == exact_text:
            return paragraph
    raise ValueError(f"Paragraph not found: {exact_text}")


def insert_cloned_paragraph_before(anchor, source, text):
    element = deepcopy(source._p)
    anchor._p.addprevious(element)
    paragraph = anchor._parent.add_paragraph()._element
    paragraph.getparent().remove(paragraph)
    from docx.text.paragraph import Paragraph
    result = Paragraph(element, anchor._parent)
    set_paragraph_text(result, text)
    return result


doc = Document(SOURCE)

# Correct database-related headings and static descriptions.
set_paragraph_text(
    find_paragraph(doc, "1.3 Introduction about Relational Database Management System (MySQL & SQLite)"),
    "1.3 Introduction about Relational Database Management Systems (PostgreSQL and SQLite)",
)
for paragraph in doc.paragraphs:
    if "1.3 Introduction about Relational Database Management System (MySQL & SQLite)" in paragraph.text:
        set_paragraph_text(
            paragraph,
            paragraph.text.replace(
                "1.3 Introduction about Relational Database Management System (MySQL & SQLite)",
                "1.3 Introduction about Relational Database Management Systems (PostgreSQL and SQLite)",
            ),
        )

for paragraph in doc.paragraphs:
    if "depicting all 10 tables" in paragraph.text:
        set_paragraph_text(paragraph, paragraph.text.replace("all 10 tables", "all 11 tables"))

# Update table overview wording while retaining the existing 11-table structure.
overview = doc.tables[4]
overview_rows = [
    ["Collection / Table Name", "Short Description"],
    ["users", "Stores login accounts, password hashes and role-based permissions ('user', 'admin')."],
    ["auth_identities", "Links internal user accounts to identities supplied by an external authentication provider."],
    ["scam_categories", "Stores the standardized catalog of scam categories."],
    ["scan_history", "Stores persisted image-scan records, OCR text, risk results, explanations and suggested actions."],
    ["scan_feedback", "Stores user feedback about correct predictions, false alarms and missed scams for administrative review."],
    ["scam_keywords", "Stores unique Vietnamese fraud terms or patterns and their risk weights."],
    ["training_dataset", "Stores anonymized and verified image samples used for model training and evaluation."],
    ["ai_models", "Stores registered AI model versions, descriptions and activation status."],
    ["model_evaluations", "Stores evaluation metrics recorded for registered AI models."],
    ["system_activity_logs", "Stores administrative and automated activity log entries."],
    ["visitor_devices", "Stores privacy-conscious visitor-device, browser, permission, location and visit information."],
]
resize_and_fill_table(overview, overview_rows)

# Replace all Chapter 3 definitions using the current SQLAlchemy ORM model.
table_indices = {
    "users": 5,
    "auth_identities": 6,
    "scam_categories": 7,
    "scan_history": 8,
    "scan_feedback": 9,
    "scam_keywords": 10,
    "training_dataset": 11,
    "ai_models": 12,
    "model_evaluations": 13,
    "system_activity_logs": 14,
}
for table_name, index in table_indices.items():
    resize_and_fill_table(doc.tables[index], TABLES[table_name])

# The source contained an unimplemented incidents table; repurpose it as scan_feedback.
set_paragraph_text(find_paragraph(doc, "3.5 Table incidents"), "3.5 Table scan_feedback")
set_paragraph_text(find_paragraph(doc, "Table 6. Table incidents"), "Table 6. Table scan_feedback")
for paragraph in doc.paragraphs:
    if paragraph.text.strip().startswith("3.5 Table incidents"):
        set_paragraph_text(paragraph, paragraph.text.replace("3.5 Table incidents", "3.5 Table scan_feedback"))

# Add the missing visitor_devices definition immediately before Chapter 4.
section4 = find_paragraph(doc, "4. Hardware and software Requirements")
heading_template = find_paragraph(doc, "3.10 Table system_activity_logs")
caption_template = find_paragraph(doc, "Table 11. Table system_activity_logs")
insert_cloned_paragraph_before(section4, heading_template, "3.11 Table visitor_devices")
insert_cloned_paragraph_before(section4, caption_template, "Table 12. Table visitor_devices")

visitor_table_element = deepcopy(doc.tables[14]._tbl)
section4._p.addprevious(visitor_table_element)
from docx.table import Table
visitor_table = Table(visitor_table_element, section4._parent)
resize_and_fill_table(visitor_table, TABLES["visitor_devices"])

# Renumber the hardware table caption after inserting Table 12.
set_paragraph_text(find_paragraph(doc, "Table 12. Attributes of Scam Fraud Detection Application"), "Table 13. Attributes of Scam Fraud Detection Application")

# Correct the database platform summary in Chapter 4 without changing unrelated requirements.
hardware_table = doc.tables[-1]
for row in hardware_table.rows:
    if row.cells[0].text.strip() == "Database":
        set_cell_text(
            row.cells[1],
            "PostgreSQL 18 (Production)\nSQLite (Local Development and Testing)\nSQLAlchemy 2.0 ORM",
        )

# Replace the outdated ERD image with the current 11-table black-and-white diagram.
figure_caption = find_paragraph(doc, "Figure 1. Table Relationship Diagram (ERD)")
body_elements = list(doc._body._body)
caption_pos = body_elements.index(figure_caption._p)
image_paragraph = None
for element in reversed(body_elements[:caption_pos]):
    if element.tag == qn("w:p") and element.xpath(".//w:drawing"):
        from docx.text.paragraph import Paragraph
        image_paragraph = Paragraph(element, doc._body)
        break
if image_paragraph is not None:
    for run in list(image_paragraph.runs):
        image_paragraph._p.remove(run._r)
    image_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    image_paragraph.add_run().add_picture(str(ERD_IMAGE), width=Inches(6.45))

# Add a TOC entry for the new table. Word will refresh page numbers when opened.
toc_anchor = None
for paragraph in doc.paragraphs:
    if paragraph.text.strip().startswith("3.10 Table system_activity_logs") and paragraph.style.name.lower().startswith("toc"):
        toc_anchor = paragraph
        break
if toc_anchor is not None:
    next_element = toc_anchor._p.getnext()
    clone = deepcopy(toc_anchor._p)
    toc_anchor._p.addnext(clone)
    from docx.text.paragraph import Paragraph
    toc_new = Paragraph(clone, toc_anchor._parent)
    set_paragraph_text(toc_new, "3.11 Table visitor_devices")

# Ask Microsoft Word to update TOC and other fields on open.
settings = doc.settings._element
update_fields = settings.find(qn("w:updateFields"))
if update_fields is None:
    update_fields = OxmlElement("w:updateFields")
    settings.append(update_fields)
update_fields.set(qn("w:val"), "true")

doc.save(OUTPUT)
print(OUTPUT)

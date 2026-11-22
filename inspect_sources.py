from pathlib import Path
from openpyxl import load_workbook
from docx import Document
import json

FILES = [
    Path(r"D:/TAILIEU_CAPSTONE_C1SE06_SFDS/3. PRODUCT BACKLOG & USER STORY/C1SE.06_ProductBacklog_SFDS_v1.0.xlsx"),
    Path(r"D:/TAILIEU_CAPSTONE_C1SE20_ver02/7. TEST PLAN/C1SE.20_TestCase Sprint1_ver2.0.xlsx"),
    Path(r"D:/TAILIEU_CAPSTONE_C1SE20_ver02/7. TEST PLAN/C1SE.20_TestCase Sprint2_ver1.0 .xlsx"),
    Path(r"D:/TAILIEU_CAPSTONE_C1SE20_ver02/7. TEST PLAN/C1SE.20_TestCase Sprint3_ver1.0.xlsx"),
    Path(r"D:/TAILIEU_CAPSTONE_C1SE20_ver02/7. TEST PLAN/C1SE.20_TestCase Sprint1_ver1.0.xlsx"),
]
DOCX = Path(r"D:/TAILIEU_CAPSTONE_C1SE20_ver02/7. TEST PLAN/C1SE.20_TestPlan_ver1.0.docx")

def clean(v):
    if v is None:
        return None
    return str(v).strip().replace("\r", " ").replace("\n", " | ")

def workbook_summary(path):
    wb = load_workbook(path, data_only=False, read_only=True)
    result = {"path": str(path), "sheets": []}
    for ws in wb.worksheets:
        rows = []
        for row in ws.iter_rows():
            vals = [clean(c.value) for c in row]
            if any(v not in (None, "") for v in vals):
                while vals and vals[-1] in (None, ""):
                    vals.pop()
                rows.append(vals)
        result["sheets"].append({"title": ws.title, "max_row": ws.max_row, "max_column": ws.max_column, "rows": rows})
    return result

def doc_summary(path):
    doc = Document(path)
    return {
        "path": str(path),
        "paragraphs": [clean(p.text) for p in doc.paragraphs if clean(p.text)],
        "tables": [
            [[clean(c.text) for c in row.cells] for row in table.rows]
            for table in doc.tables
        ],
        "sections": len(doc.sections),
    }

out = {"workbooks": [workbook_summary(p) for p in FILES], "docx": doc_summary(DOCX)}
Path("source_inventory.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({
    "files": [{"path": str(p), "exists": p.exists(), "size": p.stat().st_size if p.exists() else None} for p in FILES + [DOCX]],
    "sheet_counts": {p.name: len(load_workbook(p, read_only=True).sheetnames) for p in FILES},
    "doc_paragraphs": len(out["docx"]["paragraphs"]),
    "doc_tables": len(out["docx"]["tables"]),
}, ensure_ascii=False, indent=2))

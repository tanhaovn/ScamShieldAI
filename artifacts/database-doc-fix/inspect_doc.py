from pathlib import Path
import sys

from docx import Document


doc_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("source.docx")
doc = Document(doc_path)

print(f"paragraphs={len(doc.paragraphs)} tables={len(doc.tables)} sections={len(doc.sections)}")
for idx, paragraph in enumerate(doc.paragraphs):
    text = " ".join(paragraph.text.split())
    if text:
        print(f"P{idx:03d} [{paragraph.style.name}] {text[:220]}")

print("\nTABLE INVENTORY")
for idx, table in enumerate(doc.tables):
    rows = []
    for row in table.rows[:3]:
        rows.append(" | ".join(" ".join(cell.text.split()) for cell in row.cells))
    print(f"T{idx:02d} rows={len(table.rows)} cols={len(table.columns)} style={table.style.name if table.style else '-'}")
    for row in rows:
        print(f"  {row[:500]}")

print("\nFULL DATABASE TABLES")
for idx, table in enumerate(doc.tables[4:15], start=4):
    print(f"\nT{idx:02d}")
    for row in table.rows:
        print(" | ".join(" ".join(cell.text.split()) for cell in row.cells))

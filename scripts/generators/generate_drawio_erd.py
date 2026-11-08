# -*- coding: utf-8 -*-
"""
Generate Draw.io XML file for SFDS Database ERD using ElementTree
Ensures 100% valid XML structure with proper escaping.
"""

import xml.etree.ElementTree as ET

def generate_drawio():
    filename = "SFDS_Database_ERD.drawio"

    tables = {
        "users": {
            "x": 60, "y": 340, "w": 300, "h": 260,
            "title": "users",
            "cols": [
                ("[PK] id", "INT AUTO_INCREMENT"),
                ("email", "VARCHAR(255) UNIQUE"),
                ("password_hash", "VARCHAR(255)"),
                ("full_name", "VARCHAR(255)"),
                ("role", "ENUM('user','admin')"),
                ("is_active", "BOOLEAN"),
                ("created_at", "TIMESTAMP"),
                ("updated_at", "TIMESTAMP")
            ]
        },
        "auth_identities": {
            "x": 60, "y": 90, "w": 300, "h": 170,
            "title": "auth_identities",
            "cols": [
                ("[PK] id", "INT AUTO_INCREMENT"),
                ("[FK] user_id", "INT (FK)"),
                ("provider", "VARCHAR(50)"),
                ("provider_subject", "VARCHAR(255)"),
                ("created_at", "TIMESTAMP")
            ]
        },
        "system_activity_logs": {
            "x": 60, "y": 680, "w": 300, "h": 170,
            "title": "system_activity_logs",
            "cols": [
                ("[PK] id", "INT AUTO_INCREMENT"),
                ("[FK] admin_id", "INT (FK)"),
                ("action_type", "VARCHAR(100)"),
                ("description", "TEXT"),
                ("created_at", "TIMESTAMP")
            ]
        },
        "scam_keywords": {
            "x": 60, "y": 910, "w": 300, "h": 170,
            "title": "scam_keywords",
            "cols": [
                ("[PK] id", "INT AUTO_INCREMENT"),
                ("keyword", "VARCHAR(255)"),
                ("category", "VARCHAR(100)"),
                ("weight", "INT"),
                ("created_at", "TIMESTAMP")
            ]
        },
        "scam_categories": {
            "x": 460, "y": 90, "w": 320, "h": 150,
            "title": "scam_categories",
            "cols": [
                ("[PK] id", "INT AUTO_INCREMENT"),
                ("code", "VARCHAR(50) UNIQUE"),
                ("display_name", "VARCHAR(150)"),
                ("description", "TEXT")
            ]
        },
        "scan_history": {
            "x": 460, "y": 310, "w": 340, "h": 360,
            "title": "scan_history",
            "cols": [
                ("[PK] id", "INT AUTO_INCREMENT"),
                ("[FK] user_id", "INT (FK)"),
                ("image_url", "VARCHAR(1024)"),
                ("original_filename", "VARCHAR(512)"),
                ("extracted_text", "LONGTEXT"),
                ("[FK] scam_category_id", "INT (FK)"),
                ("risk_score", "INT (0-100)"),
                ("risk_level", "ENUM(...)"),
                ("explanation", "TEXT"),
                ("highlighted_terms", "JSON / TEXT"),
                ("suggested_action", "TEXT"),
                ("created_at", "TIMESTAMP")
            ]
        },
        "incidents": {
            "x": 460, "y": 740, "w": 320, "h": 220,
            "title": "incidents",
            "cols": [
                ("[PK] id", "INT AUTO_INCREMENT"),
                ("[FK] sme_user_id", "INT (FK)"),
                ("[FK] scan_history_id", "INT (FK)"),
                ("status", "ENUM(...)"),
                ("assigned_to", "VARCHAR(255)"),
                ("notes", "TEXT"),
                ("created_at", "TIMESTAMP")
            ]
        },
        "ai_models": {
            "x": 900, "y": 90, "w": 320, "h": 160,
            "title": "ai_models",
            "cols": [
                ("[PK] id", "INT AUTO_INCREMENT"),
                ("version_name", "VARCHAR(100) UNIQUE"),
                ("description", "TEXT"),
                ("is_active", "BOOLEAN"),
                ("created_at", "TIMESTAMP")
            ]
        },
        "model_evaluations": {
            "x": 900, "y": 320, "w": 320, "h": 210,
            "title": "model_evaluations",
            "cols": [
                ("[PK] id", "INT AUTO_INCREMENT"),
                ("[FK] ai_model_id", "INT (FK)"),
                ("macro_f1", "DECIMAL(5,4)"),
                ("recall", "DECIMAL(5,4)"),
                ("false_alarm_rate", "DECIMAL(5,4)"),
                ("explanation_usefulness", "DECIMAL(5,4)"),
                ("evaluated_at", "TIMESTAMP")
            ]
        },
        "training_dataset": {
            "x": 900, "y": 600, "w": 320, "h": 220,
            "title": "training_dataset",
            "cols": [
                ("[PK] id", "INT AUTO_INCREMENT"),
                ("image_url", "VARCHAR(1024)"),
                ("[FK] scam_category_id", "INT (FK)"),
                ("is_anonymized", "BOOLEAN"),
                ("is_verified", "BOOLEAN"),
                ("[FK] uploaded_by", "INT (FK)"),
                ("created_at", "TIMESTAMP")
            ]
        }
    }

    edges = [
        ("edge_u_auth", "users", "auth_identities", "1 : N", "0.5", "0.0", "0.5", "1.0"),
        ("edge_u_scan", "users", "scan_history", "1 : N", "1.0", "0.4", "0.0", "0.4"),
        ("edge_cat_scan", "scam_categories", "scan_history", "1 : N", "0.5", "1.0", "0.5", "0.0"),
        ("edge_scan_inc", "scan_history", "incidents", "1 : 1", "0.5", "1.0", "0.5", "0.0"),
        ("edge_u_inc", "users", "incidents", "1 : N", "0.7", "1.0", "0.0", "0.5"),
        ("edge_u_log", "users", "system_activity_logs", "1 : N", "0.5", "1.0", "0.5", "0.0"),
        ("edge_ai_eval", "ai_models", "model_evaluations", "1 : N", "0.5", "1.0", "0.5", "0.0"),
        ("edge_cat_train", "scam_categories", "training_dataset", "1 : N", "1.0", "0.5", "0.0", "0.2"),
        ("edge_u_train", "users", "training_dataset", "1 : N", "1.0", "0.8", "0.0", "0.6")
    ]

    # Create XML Structure
    mxfile = ET.Element("mxfile", host="app.diagrams.net", version="24.0.0")
    diagram = ET.SubElement(mxfile, "diagram", id="sfds-database-erd", name="SFDS Database ERD")
    model = ET.SubElement(diagram, "mxGraphModel", dx="1422", dy="800", grid="1", gridSize="10",
                          guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1",
                          pageScale="1", pageWidth="1400", pageHeight="1150", math="0", shadow="0")
    root = ET.SubElement(model, "root")

    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    # Add table nodes
    for tbl_id, tbl in tables.items():
        rows = [
            '<table style="width:100%; border-collapse:collapse; font-family:\'Times New Roman\', serif;">',
            f'<tr style="background-color:#D9D9D9; text-align:center; font-weight:bold; font-size:13px;">'
            f'<td colspan="2" style="padding:6px; border-bottom:1.5px solid #000000; color:#000000;">{tbl["title"]}</td></tr>'
        ]
        for col, dtype in tbl["cols"]:
            is_pk = "[PK]" in col
            is_fk = "[FK]" in col
            font_weight = "bold" if (is_pk or is_fk) else "normal"
            text_color = "#000000" if is_pk else ("#1A1A1A" if is_fk else "#000000")
            rows.append(
                f'<tr style="font-size:11px;">'
                f'<td style="padding:3px 6px; font-weight:{font_weight}; color:{text_color}; border-bottom:1px solid #EEEEEE; text-align:left;">{col}</td>'
                f'<td style="padding:3px 6px; text-align:right; font-style:italic; color:#555555; border-bottom:1px solid #EEEEEE;">{dtype}</td>'
                f'</tr>'
            )
        rows.append('</table>')
        html_val = "".join(rows)

        style = "html=1;whiteSpace=wrap;rounded=1;arcSize=4;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;shadow=0;overflow=hidden;"
        cell = ET.SubElement(root, "mxCell", id=tbl_id, value=html_val, style=style, vertex="1", parent="1")
        ET.SubElement(cell, "mxGeometry", x=str(tbl["x"]), y=str(tbl["y"]), width=str(tbl["w"]), height=str(tbl["h"]), **{"as": "geometry"})

    # Add edge nodes
    for edge_id, src, tgt, label, ex, ey, enx, eny in edges:
        style = (f"edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
                 f"entryX={enx};entryY={eny};exitX={ex};exitY={ey};strokeColor=#000000;strokeWidth=1.5;"
                 f"endArrow=classic;endFill=1;labelBackgroundColor=#FFFFFF;fontFamily=Times New Roman;"
                 f"fontStyle=1;fontSize=10;")
        edge_cell = ET.SubElement(root, "mxCell", id=edge_id, value=label, style=style, edge="1", parent="1", source=src, target=tgt)
        geo = ET.SubElement(edge_cell, "mxGeometry", relative="1", **{"as": "geometry"})
        ET.SubElement(geo, "mxPoint", **{"as": "offset"})

    tree = ET.ElementTree(mxfile)
    ET.indent(tree, space="  ", level=0)
    tree.write(filename, encoding="utf-8", xml_declaration=True)
    print(f"Successfully generated 100% valid Drawio XML: {filename}")

if __name__ == "__main__":
    generate_drawio()

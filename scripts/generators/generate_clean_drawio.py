# -*- coding: utf-8 -*-
"""
Generate Draw.io XML with Clean, Non-Crossing Orthogonal Arrows
Every connector routes through dedicated corridors with zero overlap.
Output: SFDS_Database_ERD.drawio
"""

import xml.etree.ElementTree as ET

def generate_clean_drawio():
    filename = "SFDS_Database_ERD.drawio"

    # Precise non-overlapping layout
    # Col 1: X = 80
    # Col 2: X = 480
    # Col 3: X = 900
    tables = {
        # --- COLUMN 1 (User Management & Auditing) ---
        "auth_identities": {
            "x": 80, "y": 80, "w": 300,
            "title": "auth_identities",
            "cols": [
                ("<b>[PK] id</b>", "INT AUTO_INCREMENT"),
                ("<b>[FK] user_id</b>", "INT (FK)"),
                ("provider", "VARCHAR(50)"),
                ("provider_subject", "VARCHAR(255)"),
                ("created_at", "TIMESTAMP")
            ]
        },
        "users": {
            "x": 80, "y": 300, "w": 300,
            "title": "users",
            "cols": [
                ("<b>[PK] id</b>", "INT AUTO_INCREMENT"),
                ("email", "VARCHAR(255) UNIQUE"),
                ("password_hash", "VARCHAR(255)"),
                ("full_name", "VARCHAR(255)"),
                ("role", "ENUM('user','admin')"),
                ("is_active", "BOOLEAN"),
                ("created_at", "TIMESTAMP"),
                ("updated_at", "TIMESTAMP")
            ]
        },
        "system_activity_logs": {
            "x": 80, "y": 600, "w": 300,
            "title": "system_activity_logs",
            "cols": [
                ("<b>[PK] id</b>", "INT AUTO_INCREMENT"),
                ("<b>[FK] admin_id</b>", "INT (FK)"),
                ("action_type", "VARCHAR(100)"),
                ("description", "TEXT"),
                ("created_at", "TIMESTAMP")
            ]
        },
        "scam_keywords": {
            "x": 80, "y": 820, "w": 300,
            "title": "scam_keywords",
            "cols": [
                ("<b>[PK] id</b>", "INT AUTO_INCREMENT"),
                ("keyword", "VARCHAR(255)"),
                ("category", "VARCHAR(100)"),
                ("weight", "INT"),
                ("created_at", "TIMESTAMP")
            ]
        },

        # --- COLUMN 2 (Core Fraud Detection & Incidents) ---
        "scam_categories": {
            "x": 480, "y": 80, "w": 320,
            "title": "scam_categories",
            "cols": [
                ("<b>[PK] id</b>", "INT AUTO_INCREMENT"),
                ("code", "VARCHAR(50) UNIQUE"),
                ("display_name", "VARCHAR(150)"),
                ("description", "TEXT")
            ]
        },
        "scan_history": {
            "x": 480, "y": 280, "w": 320,
            "title": "scan_history",
            "cols": [
                ("<b>[PK] id</b>", "INT AUTO_INCREMENT"),
                ("<b>[FK] user_id</b>", "INT (FK)"),
                ("image_url", "VARCHAR(1024)"),
                ("original_filename", "VARCHAR(512)"),
                ("extracted_text", "LONGTEXT"),
                ("<b>[FK] scam_category_id</b>", "INT (FK)"),
                ("risk_score", "INT (0-100)"),
                ("risk_level", "ENUM(...)"),
                ("explanation", "TEXT"),
                ("highlighted_terms", "JSON / TEXT"),
                ("suggested_action", "TEXT"),
                ("created_at", "TIMESTAMP")
            ]
        },
        "incidents": {
            "x": 480, "y": 700, "w": 320,
            "title": "incidents",
            "cols": [
                ("<b>[PK] id</b>", "INT AUTO_INCREMENT"),
                ("<b>[FK] sme_user_id</b>", "INT (FK)"),
                ("<b>[FK] scan_history_id</b>", "INT (FK)"),
                ("status", "ENUM(...)"),
                ("assigned_to", "VARCHAR(255)"),
                ("notes", "TEXT"),
                ("created_at", "TIMESTAMP")
            ]
        },

        # --- COLUMN 3 (AI Datasets & Model Governance) ---
        "training_dataset": {
            "x": 900, "y": 80, "w": 320,
            "title": "training_dataset",
            "cols": [
                ("<b>[PK] id</b>", "INT AUTO_INCREMENT"),
                ("image_url", "VARCHAR(1024)"),
                ("<b>[FK] scam_category_id</b>", "INT (FK)"),
                ("is_anonymized", "BOOLEAN"),
                ("is_verified", "BOOLEAN"),
                ("<b>[FK] uploaded_by</b>", "INT (FK)"),
                ("created_at", "TIMESTAMP")
            ]
        },
        "ai_models": {
            "x": 900, "y": 380, "w": 320,
            "title": "ai_models",
            "cols": [
                ("<b>[PK] id</b>", "INT AUTO_INCREMENT"),
                ("version_name", "VARCHAR(100) UNIQUE"),
                ("description", "TEXT"),
                ("is_active", "BOOLEAN"),
                ("created_at", "TIMESTAMP")
            ]
        },
        "model_evaluations": {
            "x": 900, "y": 620, "w": 320,
            "title": "model_evaluations",
            "cols": [
                ("<b>[PK] id</b>", "INT AUTO_INCREMENT"),
                ("<b>[FK] ai_model_id</b>", "INT (FK)"),
                ("macro_f1", "DECIMAL(5,4)"),
                ("recall", "DECIMAL(5,4)"),
                ("false_alarm_rate", "DECIMAL(5,4)"),
                ("explanation_usefulness", "DECIMAL(5,4)"),
                ("evaluated_at", "TIMESTAMP")
            ]
        }
    }

    # Edges with explicit dedicated routing waypoints to eliminate crossing
    # Each entry: (id, src, tgt, label, exitX, exitY, entryX, entryY, [waypoints])
    edge_routes = [
        # 1. users -> auth_identities (Straight UP)
        ("edge_u_auth", "users", "auth_identities", "1 : N", "0.5", "0.0", "0.5", "1.0", []),
        
        # 2. users -> scan_history (Straight RIGHT)
        ("edge_u_scan", "users", "scan_history", "1 : N", "1.0", "0.25", "0.0", "0.25", []),
        
        # 3. users -> system_activity_logs (Straight DOWN)
        ("edge_u_log", "users", "system_activity_logs", "1 : N", "0.5", "1.0", "0.5", "0.0", []),
        
        # 4. users -> incidents (Corridor turn between Col 1 and Col 2)
        ("edge_u_inc", "users", "incidents", "1 : N", "1.0", "0.85", "0.0", "0.4", [
            ("430", "500"), ("430", "780")
        ]),
        
        # 5. scam_categories -> scan_history (Straight DOWN)
        ("edge_cat_scan", "scam_categories", "scan_history", "1 : N", "0.5", "1.0", "0.5", "0.0", []),
        
        # 6. scan_history -> incidents (Straight DOWN)
        ("edge_scan_inc", "scan_history", "incidents", "1 : 1", "0.5", "1.0", "0.5", "0.0", []),
        
        # 7. scam_categories -> training_dataset (Straight RIGHT)
        ("edge_cat_train", "scam_categories", "training_dataset", "1 : N", "1.0", "0.5", "0.0", "0.5", []),
        
        # 8. users -> training_dataset (Clean Top Corridor: Y = 40)
        ("edge_u_train", "users", "training_dataset", "1 : N", "0.0", "0.15", "0.5", "0.0", [
            ("40", "335"), ("40", "40"), ("1060", "40")
        ]),
        
        # 9. ai_models -> model_evaluations (Straight DOWN)
        ("edge_ai_eval", "ai_models", "model_evaluations", "1 : N", "0.5", "1.0", "0.5", "0.0", [])
    ]

    mxfile = ET.Element("mxfile", host="app.diagrams.net", version="24.0.0")
    diagram = ET.SubElement(mxfile, "diagram", id="sfds-database-erd", name="SFDS Database ERD")
    model = ET.SubElement(diagram, "mxGraphModel", dx="1422", dy="800", grid="1", gridSize="10",
                          guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1",
                          pageScale="1", pageWidth="1400", pageHeight="1150", math="0", shadow="0")
    root = ET.SubElement(model, "root")

    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    row_h = 26
    hdr_h = 26

    # Draw table nodes using native draw.io List
    for tbl_id, tbl in tables.items():
        total_h = hdr_h + len(tbl["cols"]) * row_h
        
        swimlane_style = (
            "swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;"
            "horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;"
            "resizeLast=0;collapsible=1;marginBottom=0;whiteSpace=wrap;html=1;"
            "fontFamily=Times New Roman;fontSize=13;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"
        )
        container = ET.SubElement(root, "mxCell", id=tbl_id, value=tbl["title"], style=swimlane_style, vertex="1", parent="1")
        ET.SubElement(container, "mxGeometry", x=str(tbl["x"]), y=str(tbl["y"]), width=str(tbl["w"]), height=str(total_h), **{"as": "geometry"})

        for idx, (col_name, col_type) in enumerate(tbl["cols"]):
            item_id = f"{tbl_id}_item_{idx+1}"
            val = f"{col_name} : {col_type}"
            item_style = (
                "text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;"
                "spacingLeft=8;spacingRight=8;overflow=hidden;rotatable=0;"
                "points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;"
                "fontFamily=Times New Roman;fontSize=11;"
            )
            item_cell = ET.SubElement(root, "mxCell", id=item_id, value=val, style=item_style, vertex="1", parent=tbl_id)
            ET.SubElement(item_cell, "mxGeometry", y=str(hdr_h + idx * row_h), width=str(tbl["w"]), height=str(row_h), **{"as": "geometry"})

    # Draw edges with clean orthogonal routing
    for edge_id, src, tgt, label, ex, ey, enx, eny, waypoints in edge_routes:
        edge_style = (
            f"edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
            f"entryX={enx};entryY={eny};exitX={ex};exitY={ey};strokeColor=#000000;strokeWidth=1.5;"
            f"endArrow=classic;endFill=1;labelBackgroundColor=#FFFFFF;fontFamily=Times New Roman;"
            f"fontStyle=1;fontSize=10;"
        )
        edge_cell = ET.SubElement(root, "mxCell", id=edge_id, value=label, style=edge_style, edge="1", parent="1", source=src, target=tgt)
        geo = ET.SubElement(edge_cell, "mxGeometry", relative="1", **{"as": "geometry"})
        ET.SubElement(geo, "mxPoint", **{"as": "offset"})
        
        # Add explicit waypoints to force clean corridor pathing
        if waypoints:
            arr = ET.SubElement(geo, "Array", **{"as": "points"})
            for wx, wy in waypoints:
                ET.SubElement(arr, "mxPoint", x=wx, y=wy)

    tree = ET.ElementTree(mxfile)
    ET.indent(tree, space="  ", level=0)
    tree.write(filename, encoding="utf-8", xml_declaration=True)
    print(f"Successfully generated pristine clean Draw.io ERD: {filename}")

if __name__ == "__main__":
    generate_clean_drawio()

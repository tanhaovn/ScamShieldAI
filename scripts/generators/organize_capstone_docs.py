# -*- coding: utf-8 -*-
"""
Script to organize all Capstone C1SE.06 documents into standard numbered folders
Matching the structure of D:\TAILIEU_CAPSTONE_C1SE20_ver02.
Target: D:\TAILIEU_CAPSTONE_C1SE06_SFDS and D:\scam-detector\TAILIEU_CAPSTONE_C1SE06_SFDS
"""

import os
import shutil

target_dirs = [
    r"D:\scam-detector\TAILIEU_CAPSTONE_C1SE06_SFDS"
]

folders = [
    "1. PROPOSAL",
    "2. PROJECT PLAN",
    "3. PRODUCT BACKLOG & USER STORY",
    "4. ARCHITECTURE DESIGN",
    "5. DATABASE DESIGN",
    "6. USER INTERFACE DESIGN",
    "7. TEST PLAN",
    "8. SPRINT BACKLOG",
    "9. CODE STANDARD",
    "10. REFLECTION",
    "11. MEETING MINUTES"
]

def organize():
    for base in target_dirs:
        os.makedirs(base, exist_ok=True)
        for f in folders:
            os.makedirs(os.path.join(base, f), exist_ok=True)

        # 1. PROPOSAL
        prop_files = [
            "C1SE.06-Proposal_SFDS_v2.1.docx",
            "C1SE.06-Proposal_SFDS_v2.0.docx",
        ]
        for pf in prop_files:
            if os.path.exists(pf):
                shutil.copy2(pf, os.path.join(base, "1. PROPOSAL", pf))

        # 2. PROJECT PLAN
        plan_files = [
            "C1SE.06_ProjectPlan_SFDS_v1.2.docx",
            "C1SE.06_ProjectPlan_SFDS_v1.1.docx",
            "C1SE.06_ProjectPlan_SFDS_v1.0.docx"
        ]
        for pf in plan_files:
            if os.path.exists(pf):
                shutil.copy2(pf, os.path.join(base, "2. PROJECT PLAN", pf))

        # 3. PRODUCT BACKLOG & USER STORY
        bl_file = "C1SE.06_ProductBacklog_SFDS_v1.0.xlsx"
        if os.path.exists(bl_file):
            shutil.copy2(bl_file, os.path.join(base, "3. PRODUCT BACKLOG & USER STORY", bl_file))
            # also copy to 8. SPRINT BACKLOG
            shutil.copy2(bl_file, os.path.join(base, "8. SPRINT BACKLOG", bl_file))

        # 4. ARCHITECTURE DESIGN
        arch_file = "C1SE.06_ArchitectureDesign_SFDS_v1.0.docx"
        if os.path.exists(arch_file):
            shutil.copy2(arch_file, os.path.join(base, "4. ARCHITECTURE DESIGN", arch_file))
        # copy diagrams
        if os.path.exists("arch_diagrams"):
            diag_dest = os.path.join(base, "4. ARCHITECTURE DESIGN", "diagrams")
            os.makedirs(diag_dest, exist_ok=True)
            for f in os.listdir("arch_diagrams"):
                if f.startswith("fig") and not f.startswith("fig_sfds_erd"):
                    shutil.copy2(os.path.join("arch_diagrams", f), os.path.join(diag_dest, f))

        # 5. DATABASE DESIGN
        db_files = [
            "C1SE.06_DatabaseDesign_SFDS_v1.0.docx",
            "C1SE.06_DatabaseDesign_SFDS_v1.1.docx",
            "SFDS_Database_ERD.drawio",
            "schema.sql"
        ]
        for dbf in db_files:
            if os.path.exists(dbf):
                shutil.copy2(dbf, os.path.join(base, "5. DATABASE DESIGN", dbf))
        
        # copy ERD png
        erd_png = os.path.join("arch_diagrams", "fig_sfds_erd.png")
        if os.path.exists(erd_png):
            shutil.copy2(erd_png, os.path.join(base, "5. DATABASE DESIGN", "SFDS_Database_ERD.png"))

        # Root summary spreadsheet
        if os.path.exists(bl_file):
            shutil.copy2(bl_file, os.path.join(base, bl_file))

        # Readme / Guide in root of folder
        readme_content = """# THƯ MỤC QUẢN LÝ TÀI LIỆU CAPSTONE 1 - C1SE.06
Dự án: SFDS (Scam Fraud Detection System with Explanations)
Lớp: CMU-SE 450 - Đại học Duy Tân

DANH MỤC THƯ MỤC:
1. PROPOSAL: Đề xuất dự án (Project Proposal v2.1)
2. PROJECT PLAN: Kế hoạch triển khai dự án (Project Plan v1.2)
3. PRODUCT BACKLOG & USER STORY: Bảng tính Product Backlog 20 items & Sprint tracking (.xlsx)
4. ARCHITECTURE DESIGN: Thiết kế kiến trúc hệ thống (Architecture Design v1.0 & Sơ đồ C&C, Module, Allocation)
5. DATABASE DESIGN: Thiết kế cơ sở dữ liệu (Database Design v1.0, Sơ đồ Draw.io, ERD Image, schema.sql)
6. USER INTERFACE DESIGN: Thiết kế giao diện (UI/UX)
7. TEST PLAN: Kế hoạch kiểm thử hệ thống
8. SPRINT BACKLOG: Nhật ký theo dõi từng Sprint
9. CODE STANDARD: Tiêu chuẩn lập trình nhóm
10. REFLECTION: Báo cáo đánh giá tổng kết Sprint
11. MEETING MINUTES: Biên bản họp nhóm định kỳ
"""
        with open(os.path.join(base, "README.txt"), "w", encoding="utf-8") as rf:
            rf.write(readme_content)

        print(f"Successfully organized folder: {base}")

if __name__ == "__main__":
    organize()

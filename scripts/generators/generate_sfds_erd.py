# -*- coding: utf-8 -*-
"""
Generate Clean PNG ERD diagram matching the pristine Draw.io layout
Output: arch_diagrams/fig_sfds_erd.png
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs("arch_diagrams", exist_ok=True)

fig, ax = plt.subplots(figsize=(18, 12), dpi=300)
ax.set_xlim(0, 18)
ax.set_ylim(0, 12)
ax.axis('off')

def draw_table(ax, x, y, w, h, title, cols, pk_indices=[0], fk_indices=[]):
    hdr_h = 0.55
    hdr_rect = patches.FancyBboxPatch((x, y + h - hdr_h), w, hdr_h,
                                     boxstyle="square,pad=0",
                                     linewidth=1.2, edgecolor="#000000", facecolor="#D9D9D9")
    ax.add_patch(hdr_rect)
    ax.text(x + w/2, y + h - hdr_h/2, title,
            ha='center', va='center', fontsize=11, fontweight='bold', fontfamily='serif', color='#000000')

    body_h = h - hdr_h
    body_rect = patches.FancyBboxPatch((x, y), w, body_h,
                                      boxstyle="square,pad=0",
                                      linewidth=1.2, edgecolor="#000000", facecolor="#FFFFFF")
    ax.add_patch(body_rect)

    line_h = body_h / max(len(cols), 1)
    for i, col in enumerate(cols):
        cur_y = y + body_h - (i + 0.5) * line_h
        prefix = ""
        weight = 'normal'
        if i in pk_indices:
            prefix = "[PK] "
            weight = 'bold'
        elif i in fk_indices:
            prefix = "[FK] "
            weight = 'bold'
        
        ax.text(x + 0.15, cur_y, prefix + col[0],
                ha='left', va='center', fontsize=8.5, fontweight=weight, fontfamily='serif', color='#000000')
        ax.text(x + w - 0.15, cur_y, col[1],
                ha='right', va='center', fontsize=8.0, fontstyle='italic', fontfamily='serif', color='#444444')
        if i < len(cols) - 1:
            ax.plot([x, x + w], [cur_y - line_h/2, cur_y - line_h/2], color='#E0E0E0', linewidth=0.6)

# COLUMN 1 (Left: X = 0.8)
# auth_identities (Top)
draw_table(ax, 0.8, 9.2, 4.0, 2.3, "auth_identities", [
    ("id", "INT AUTO_INCREMENT"),
    ("user_id", "INT (FK)"),
    ("provider", "VARCHAR(50)"),
    ("provider_subject", "VARCHAR(255)"),
    ("created_at", "TIMESTAMP")
], pk_indices=[0], fk_indices=[1])

# users (Center)
draw_table(ax, 0.8, 4.8, 4.0, 3.8, "users", [
    ("id", "INT AUTO_INCREMENT"),
    ("email", "VARCHAR(255) UNIQUE"),
    ("password_hash", "VARCHAR(255)"),
    ("full_name", "VARCHAR(255)"),
    ("role", "ENUM('user','admin')"),
    ("is_active", "BOOLEAN"),
    ("created_at", "TIMESTAMP"),
    ("updated_at", "TIMESTAMP")
], pk_indices=[0])

# system_activity_logs (Bottom)
draw_table(ax, 0.8, 2.2, 4.0, 2.0, "system_activity_logs", [
    ("id", "INT AUTO_INCREMENT"),
    ("admin_id", "INT (FK)"),
    ("action_type", "VARCHAR(100)"),
    ("description", "TEXT"),
    ("created_at", "TIMESTAMP")
], pk_indices=[0], fk_indices=[1])

# scam_keywords (Far Bottom)
draw_table(ax, 0.8, 0.4, 4.0, 1.4, "scam_keywords", [
    ("id", "INT AUTO_INCREMENT"),
    ("keyword", "VARCHAR(255)"),
    ("category", "VARCHAR(100)"),
    ("weight", "INT"),
    ("created_at", "TIMESTAMP")
], pk_indices=[0])

# COLUMN 2 (Center: X = 6.8)
# scam_categories (Top)
draw_table(ax, 6.8, 9.4, 4.4, 2.1, "scam_categories", [
    ("id", "INT AUTO_INCREMENT"),
    ("code", "VARCHAR(50) UNIQUE"),
    ("display_name", "VARCHAR(150)"),
    ("description", "TEXT")
], pk_indices=[0])

# scan_history (Center)
draw_table(ax, 6.8, 3.7, 4.4, 4.9, "scan_history", [
    ("id", "INT AUTO_INCREMENT"),
    ("user_id", "INT (FK)"),
    ("image_url", "VARCHAR(1024)"),
    ("original_filename", "VARCHAR(512)"),
    ("extracted_text", "LONGTEXT"),
    ("scam_category_id", "INT (FK)"),
    ("risk_score", "INT (0-100)"),
    ("risk_level", "ENUM(...)"),
    ("explanation", "TEXT"),
    ("highlighted_terms", "JSON"),
    ("suggested_action", "TEXT"),
    ("created_at", "TIMESTAMP")
], pk_indices=[0], fk_indices=[1, 5])

# incidents (Bottom)
draw_table(ax, 6.8, 0.4, 4.4, 2.7, "incidents", [
    ("id", "INT AUTO_INCREMENT"),
    ("sme_user_id", "INT (FK)"),
    ("scan_history_id", "INT (FK)"),
    ("status", "ENUM(...)"),
    ("assigned_to", "VARCHAR(255)"),
    ("notes", "TEXT"),
    ("created_at", "TIMESTAMP")
], pk_indices=[0], fk_indices=[1, 2])

# COLUMN 3 (Right: X = 12.8)
# training_dataset (Top)
draw_table(ax, 12.8, 8.8, 4.4, 2.7, "training_dataset", [
    ("id", "INT AUTO_INCREMENT"),
    ("image_url", "VARCHAR(1024)"),
    ("scam_category_id", "INT (FK)"),
    ("is_anonymized", "BOOLEAN"),
    ("is_verified", "BOOLEAN"),
    ("uploaded_by", "INT (FK)"),
    ("created_at", "TIMESTAMP")
], pk_indices=[0], fk_indices=[2, 5])

# ai_models (Middle)
draw_table(ax, 12.8, 5.2, 4.4, 2.2, "ai_models", [
    ("id", "INT AUTO_INCREMENT"),
    ("version_name", "VARCHAR(100) UNIQUE"),
    ("description", "TEXT"),
    ("is_active", "BOOLEAN"),
    ("created_at", "TIMESTAMP")
], pk_indices=[0])

# model_evaluations (Bottom)
draw_table(ax, 12.8, 1.8, 4.4, 2.6, "model_evaluations", [
    ("id", "INT AUTO_INCREMENT"),
    ("ai_model_id", "INT (FK)"),
    ("macro_f1", "DECIMAL(5,4)"),
    ("recall", "DECIMAL(5,4)"),
    ("false_alarm_rate", "DECIMAL(5,4)"),
    ("explanation_usefulness", "DECIMAL(5,4)"),
    ("evaluated_at", "TIMESTAMP")
], pk_indices=[0], fk_indices=[1])

# Clean straight / L-shaped arrows
def draw_arrow(ax, p1, p2, label="1 : N"):
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle="-|>", color="#000000", lw=1.4, mutation_scale=12))
    mid_x = (p1[0] + p2[0]) / 2
    mid_y = (p1[1] + p2[1]) / 2
    ax.text(mid_x, mid_y, label, fontsize=8, ha='center', va='center',
            fontfamily='serif', fontweight='bold',
            bbox=dict(boxstyle="square,pad=0.2", fc="#FFFFFF", ec="#000000", lw=0.6))

# 1. users -> auth_identities (Straight UP)
draw_arrow(ax, (2.8, 8.6), (2.8, 9.2), "1 : N")

# 2. users -> scan_history (Straight RIGHT)
draw_arrow(ax, (4.8, 6.7), (6.8, 6.7), "1 : N")

# 3. users -> system_activity_logs (Straight DOWN)
draw_arrow(ax, (2.8, 4.8), (2.8, 4.2), "1 : N")

# 4. scam_categories -> scan_history (Straight DOWN)
draw_arrow(ax, (9.0, 9.4), (9.0, 8.6), "1 : N")

# 5. scan_history -> incidents (Straight DOWN)
draw_arrow(ax, (9.0, 3.7), (9.0, 3.1), "1 : 1")

# 6. scam_categories -> training_dataset (Straight RIGHT)
draw_arrow(ax, (11.2, 10.4), (12.8, 10.4), "1 : N")

# 7. ai_models -> model_evaluations (Straight DOWN)
draw_arrow(ax, (15.0, 5.2), (15.0, 4.4), "1 : N")

# 8. users -> incidents (Corridor route)
ax.annotate("", xy=(6.8, 1.8), xytext=(4.8, 5.3),
            arrowprops=dict(arrowstyle="-|>", color="#000000", lw=1.3,
                            connectionstyle="angle,angleA=0,angleB=90,rad=0", mutation_scale=12))
ax.text(5.8, 1.8, "1 : N", fontsize=8, ha='center', va='center', fontfamily='serif', fontweight='bold',
        bbox=dict(boxstyle="square,pad=0.2", fc="#FFFFFF", ec="#000000", lw=0.6))

# 9. users -> training_dataset (Top corridor route)
ax.annotate("", xy=(15.0, 11.5), xytext=(2.8, 11.5),
            arrowprops=dict(arrowstyle="-|>", color="#000000", lw=1.3,
                            connectionstyle="angle,angleA=90,angleB=0,rad=0", mutation_scale=12))
ax.text(8.9, 11.6, "1 : N", fontsize=8, ha='center', va='center', fontfamily='serif', fontweight='bold',
        bbox=dict(boxstyle="square,pad=0.2", fc="#FFFFFF", ec="#000000", lw=0.6))

plt.tight_layout()
plt.savefig("arch_diagrams/fig_sfds_erd.png", dpi=300, bbox_inches='tight')
plt.close()
print("Successfully generated pristine clean ERD PNG!")

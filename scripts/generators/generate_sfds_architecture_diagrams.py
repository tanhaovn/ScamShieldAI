# -*- coding: utf-8 -*-
"""Generate clean academic architectural diagrams for SFDS Architecture Design document."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs("arch_diagrams", exist_ok=True)

plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

def draw_system_context():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Central System
    circle = patches.Ellipse((50, 50), 30, 22, facecolor='#F2F2F2', edgecolor='#000000', linewidth=2)
    ax.add_patch(circle)
    ax.text(50, 51, "SFDS Core System\n(FastAPI Gateway & AI Core)", ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')

    # External Actors
    # Top Left: Guest User
    rect_user = patches.Rectangle((5, 75), 24, 16, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(rect_user)
    ax.text(17, 83, "End User / Guest\n(Web Browser)", ha='center', va='center', fontsize=10, fontweight='bold')

    # Top Right: Admin
    rect_admin = patches.Rectangle((71, 75), 24, 16, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(rect_admin)
    ax.text(83, 83, "System Administrator\n(Admin Portal)", ha='center', va='center', fontsize=10, fontweight='bold')

    # Bottom Left: OCR & Forensics Engine
    rect_ocr = patches.Rectangle((5, 10), 26, 16, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(rect_ocr)
    ax.text(18, 18, "Tesseract OCR & Forensics\n(OpenCV ELA / EXIF)", ha='center', va='center', fontsize=10, fontweight='bold')

    # Bottom Right: AI Models & PhishVN
    rect_ai = patches.Rectangle((69, 10), 26, 16, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(rect_ai)
    ax.text(82, 18, "AI Inference Pipeline\n(ResNet-18 & PhishVN URL)", ha='center', va='center', fontsize=10, fontweight='bold')

    # Arrows with labels
    # User -> System
    ax.annotate("", xy=(37, 58), xytext=(24, 75), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(26, 68, "Upload Image / Text / PDF", fontsize=8.5, rotation=35, ha='center')

    # System -> User
    ax.annotate("", xy=(22, 75), xytext=(35, 54), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(22, 60, "Risk Score & Decomposed XAI", fontsize=8.5, rotation=35, ha='center')

    # Admin <-> System
    ax.annotate("", xy=(63, 58), xytext=(76, 75), arrowprops=dict(arrowstyle="<-", lw=1.5, color="black"))
    ax.text(74, 68, "Manage Datasets & Models", fontsize=8.5, rotation=-35, ha='center')
    ax.annotate("", xy=(78, 75), xytext=(65, 54), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(78, 60, "Audit Logs & Benchmarks", fontsize=8.5, rotation=-35, ha='center')

    # System <-> OCR
    ax.annotate("", xy=(20, 26), xytext=(38, 42), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(24, 36, "Send Image for OCR/ELA", fontsize=8.5, rotation=40, ha='center')
    ax.annotate("", xy=(41, 40), xytext=(24, 26), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(35, 30, "Extracted Text & QR", fontsize=8.5, rotation=40, ha='center')

    # System <-> AI
    ax.annotate("", xy=(79, 26), xytext=(62, 42), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(74, 36, "Features & Text Tensors", fontsize=8.5, rotation=-40, ha='center')
    ax.annotate("", xy=(59, 40), xytext=(76, 26), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(64, 30, "PhishVN & ResNet Labels", fontsize=8.5, rotation=-40, ha='center')

    plt.tight_layout()
    plt.savefig("arch_diagrams/fig1_system_context.png", bbox_inches='tight')
    plt.close()

def draw_cc_client():
    fig, ax = plt.subplots(figsize=(9, 8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Outer Client Container
    client_box = patches.Rectangle((20, 15), 75, 75, facecolor='#FAFAFA', edgecolor='#000000', linewidth=2)
    ax.add_patch(client_box)
    ax.text(57, 87, "CLIENT APPLICATION [React SPA - Vite]", ha='center', fontsize=12, fontweight='bold')

    # User Actor
    ax.text(8, 75, "User /\nGuest", ha='center', va='center', fontsize=10, fontweight='bold')
    circle_head = patches.Circle((8, 83), 4, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(circle_head)

    # Components inside Client
    # Page Container
    p_box = patches.Rectangle((25, 55), 32, 26, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(p_box)
    ax.text(41, 71, "Page Containers\n(ScanPage, AdminPage,\nHistoryPage, AuthPage)", ha='center', va='center', fontsize=9.5, fontweight='bold')

    # UI Components
    comp_box = patches.Rectangle((62, 55), 30, 26, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(comp_box)
    ax.text(77, 71, "UI Components\n(UploadBox, CanvasHighlight,\nSafetyAssistant, Breakdown)", ha='center', va='center', fontsize=9.5, fontweight='bold')

    # Service Layer
    svc_box = patches.Rectangle((25, 22), 67, 24, facecolor='#F2F2F2', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(svc_box)
    ax.text(58, 38, "API & Client State Services\n(useAppController, localStorage History Manager, Axios HTTP Client)", ha='center', va='center', fontsize=10, fontweight='bold')

    # Server outside
    srv_box = patches.Rectangle((25, 1), 67, 10, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(srv_box)
    ax.text(58, 6, "BACKEND APPLICATION SERVER [FastAPI / Python]", ha='center', va='center', fontsize=11, fontweight='bold')

    # Connectors
    # User <-> Page Container
    ax.annotate("", xy=(25, 70), xytext=(14, 70), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(19, 72, "Input", fontsize=8.5, ha='center')
    ax.annotate("", xy=(14, 66), xytext=(25, 66), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(19, 63, "View", fontsize=8.5, ha='center')

    # UI Components -> Page Container
    ax.annotate("", xy=(57, 68), xytext=(62, 68), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(59.5, 70, "Compose", fontsize=8.5, ha='center')

    # Page Container -> Service
    ax.annotate("", xy=(41, 46), xytext=(41, 55), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(46, 50, "Call Action", fontsize=8.5, ha='left')

    # Service -> Server
    ax.annotate("", xy=(50, 11), xytext=(50, 22), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(45, 16, "HTTP Multipart / JSON", fontsize=8.5, ha='right')
    ax.annotate("", xy=(66, 22), xytext=(66, 11), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(71, 16, "JSON Response", fontsize=8.5, ha='left')

    plt.tight_layout()
    plt.savefig("arch_diagrams/fig2_cc_client.png", bbox_inches='tight')
    plt.close()

def draw_cc_server():
    fig, ax = plt.subplots(figsize=(10.5, 7.5), dpi=300)
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Server Outer Box
    server_box = patches.Rectangle((20, 12), 80, 80, facecolor='#FAFAFA', edgecolor='#000000', linewidth=2)
    ax.add_patch(server_box)
    ax.text(60, 88, "BACKEND APPLICATION SERVER [FastAPI / Uvicorn]", ha='center', fontsize=12, fontweight='bold')

    # Client on left
    client_box = patches.Rectangle((2, 60), 14, 25, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(client_box)
    ax.text(9, 72, "Client\n[React SPA]", ha='center', va='center', fontsize=9.5, fontweight='bold')

    # Inside Server:
    # 1. API Gateway / Request Handler
    gw_box = patches.Rectangle((24, 55), 25, 26, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(gw_box)
    ax.text(36.5, 71, "API Request Router\n& Middleware\n(MagicByte Check, JWT Auth,\nCORS, Rate Limiter)", ha='center', va='center', fontsize=9, fontweight='bold')

    # 2. Multimodal CoT Reasoning Engine
    cot_box = patches.Rectangle((54, 55), 22, 26, facecolor='#F2F2F2', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(cot_box)
    ax.text(65, 71, "Multimodal CoT\nReasoning Engine\n(Domain Gating &\nSoft Consensus)", ha='center', va='center', fontsize=9, fontweight='bold')

    # 3. AI Inference Subsystems
    ai_box = patches.Rectangle((80, 55), 18, 26, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(ai_box)
    ax.text(89, 71, "AI Pipelines\n- ResNet-18\n- PhishVN URL\n- Tesseract OCR\n- ELA Forensics", ha='center', va='center', fontsize=8.5, fontweight='bold')

    # 4. Service Layer & Safety Assistant
    svc_box = patches.Rectangle((24, 20), 45, 26, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(svc_box)
    ax.text(46.5, 36, "Application Services\n(ExplanationBuilder, SafetyAssistant,\nAuditLogger, DatasetService)", ha='center', va='center', fontsize=9.5, fontweight='bold')

    # 5. Database (SQLite / MySQL)
    db_box = patches.Rectangle((75, 20), 22, 26, facecolor='#E6E6E6', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(db_box)
    ax.text(86, 36, "Database Engine\n[SQLAlchemy ORM]\nSQLite (Dev) /\nMySQL (Prod)", ha='center', va='center', fontsize=9.5, fontweight='bold')

    # Connectors
    # Client <-> API Router
    ax.annotate("", xy=(24, 73), xytext=(16, 73), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(20, 75, "POST", fontsize=8.5, ha='center')
    ax.annotate("", xy=(16, 67), xytext=(24, 67), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(20, 64, "JSON", fontsize=8.5, ha='center')

    # Router -> CoT
    ax.annotate("", xy=(54, 68), xytext=(49, 68), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    # CoT <-> AI Pipelines
    ax.annotate("", xy=(80, 71), xytext=(76, 71), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.annotate("", xy=(76, 65), xytext=(80, 65), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))

    # CoT -> Application Services
    ax.annotate("", xy=(46, 46), xytext=(60, 55), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(56, 48, "Features", fontsize=8, ha='left')

    # Services -> DB
    ax.annotate("", xy=(75, 33), xytext=(69, 33), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(72, 35, "Persist", fontsize=8, ha='center')

    plt.tight_layout()
    plt.savefig("arch_diagrams/fig3_cc_server.png", bbox_inches='tight')
    plt.close()

def draw_module_views():
    # Module View Client
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Layer 1: Presentation Pages
    p_box = patches.Rectangle((5, 65), 90, 28, facecolor='#FAFAFA', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(p_box)
    ax.text(50, 88, "Page View Modules (React Views)", ha='center', fontsize=11, fontweight='bold')
    pages = ["ScanPage\n(Multi-source Scanner)", "HistoryPage\n(LocalStorage Viewer)", "AdminPage\n(Dataset & Logs)", "AuthPage\n(Admin Sign-in)", "OverviewPage\n(System Metrics)"]
    for i, p in enumerate(pages):
        b = patches.Rectangle((7 + i*18, 68), 16, 17, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1)
        ax.add_patch(b)
        ax.text(15 + i*18, 76.5, p, ha='center', va='center', fontsize=8, fontweight='bold')

    # Layer 2: UI Components
    c_box = patches.Rectangle((5, 35), 90, 24, facecolor='#FAFAFA', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(c_box)
    ax.text(50, 54, "Reusable Component Modules", ha='center', fontsize=11, fontweight='bold')
    comps = ["UploadDropzone", "CanvasBoundingBox", "ScoreMeterBar", "SafetyAssistantWidget", "TechnicalBreakdown"]
    for i, c in enumerate(comps):
        b = patches.Rectangle((7 + i*18, 38), 16, 13, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1)
        ax.add_patch(b)
        ax.text(15 + i*18, 44.5, c, ha='center', va='center', fontsize=8)

    # Layer 3: Services & State
    s_box = patches.Rectangle((5, 5), 90, 24, facecolor='#F2F2F2', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(s_box)
    ax.text(50, 24, "State Management & HTTP Services", ha='center', fontsize=11, fontweight='bold')
    services = ["useAppController", "localStorageManager", "apiClient (Axios)", "notificationService"]
    for i, s in enumerate(services):
        b = patches.Rectangle((12 + i*20, 8), 18, 13, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1)
        ax.add_patch(b)
        ax.text(21 + i*20, 14.5, s, ha='center', va='center', fontsize=8)

    # Arrows between layers
    ax.annotate("", xy=(50, 59), xytext=(50, 65), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(52, 62, "Imports & Renders", fontsize=8.5)
    ax.annotate("", xy=(50, 29), xytext=(50, 35), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(52, 32, "Executes Actions & API Calls", fontsize=8.5)

    plt.tight_layout()
    plt.savefig("arch_diagrams/fig4_module_client.png", bbox_inches='tight')
    plt.close()

    # Module View Server
    fig, ax = plt.subplots(figsize=(10.5, 7), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    layers = [
        ("API Routing & Middleware Layer", ["main.py (FastAPI App)", "Auth Middleware (JWT)", "MagicByteValidator", "CORS & ExceptionHandlers"], 76, 18),
        ("Analytical & Machine Learning Layer", ["ocr_service (Tesseract)", "phishvn_url_model", "phishing_model (ResNet-18)", "visual_forensics (ELA/EXIF)"], 51, 18),
        ("Reasoning & Business Logic Layer", ["reasoning_engine (CoT)", "risk_engine (Rule-based)", "explanation_builder", "safety_assistant"], 26, 18),
        ("Data Persistence & Storage Layer", ["database.py (Engine)", "models.py (SQLAlchemy)", "schema.sql (MySQL Table DDL)", "LocalStorage Sync"], 1, 18)
    ]

    for title, mods, y, h in layers:
        box = patches.Rectangle((5, y), 90, h, facecolor='#FAFAFA' if y > 20 else '#F2F2F2', edgecolor='#000000', linewidth=1.5)
        ax.add_patch(box)
        ax.text(50, y + h - 4, title, ha='center', fontsize=10.5, fontweight='bold')
        for i, m in enumerate(mods):
            b = patches.Rectangle((7 + i*22, y + 2), 20, 9, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1)
            ax.add_patch(b)
            ax.text(17 + i*22, y + 6.5, m, ha='center', va='center', fontsize=7.5)

    # Vertical connectors
    ax.annotate("", xy=(50, 69), xytext=(50, 76), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.annotate("", xy=(50, 44), xytext=(50, 51), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.annotate("", xy=(50, 19), xytext=(50, 26), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))

    plt.tight_layout()
    plt.savefig("arch_diagrams/fig5_module_server.png", bbox_inches='tight')
    plt.close()

def draw_allocation_view():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # 1. Client Machine (User Browser)
    box_client = patches.Rectangle((5, 50), 30, 42, facecolor='#FAFAFA', edgecolor='#000000', linewidth=2)
    ax.add_patch(box_client)
    ax.text(20, 88, "<<Client Device>>\nUser Workstation / Mobile", ha='center', fontsize=9.5, fontweight='bold')
    
    node_b = patches.Rectangle((7, 54), 26, 26, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1)
    ax.add_patch(node_b)
    ax.text(20, 67, "Web Browser Runtime\n(Chrome / Safari / Edge)\n- React 18 SPA\n- Canvas Rendering\n- HTML5 localStorage (50)", ha='center', va='center', fontsize=8.5)

    # 2. Application Server Node (Docker / Linux VM)
    box_server = patches.Rectangle((45, 10), 50, 82, facecolor='#FAFAFA', edgecolor='#000000', linewidth=2)
    ax.add_patch(box_server)
    ax.text(70, 88, "<<Server Host Node>>\nDocker Container / Linux Server", ha='center', fontsize=10, fontweight='bold')

    # Inside Server:
    # FastAPI Container
    c_api = patches.Rectangle((48, 54), 44, 26, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1)
    ax.add_patch(c_api)
    ax.text(70, 67, "<<Execution Environment>>\nPython 3.12 + FastAPI / Uvicorn\n- REST API Endpoints (/check-image)\n- PyTorch ResNet-18 Worker\n- PhishVN Scikit-Learn Engine\n- Pytesseract OCR C-Binding", ha='center', va='center', fontsize=8.5)

    # Local Disk / Uploads Sandbox
    c_fs = patches.Rectangle((48, 33), 20, 16, facecolor='#FFFFFF', edgecolor='#000000', linewidth=1)
    ax.add_patch(c_fs)
    ax.text(58, 41, "<<File System>>\nuploads/ sandbox\ntessdata/ traineddata\nmodels/ checkpoints", ha='center', va='center', fontsize=8)

    # Database Container
    c_db = patches.Rectangle((72, 33), 20, 16, facecolor='#E6E6E6', edgecolor='#000000', linewidth=1)
    ax.add_patch(c_db)
    ax.text(82, 41, "<<Database>>\nSQLite (Dev Engine)\nMySQL 8.0 (Prod)\nTCP Port 3306", ha='center', va='center', fontsize=8)

    # Connectors
    ax.annotate("", xy=(48, 67), xytext=(33, 67), arrowprops=dict(arrowstyle="<->", lw=1.5, color="black"))
    ax.text(40.5, 71, "HTTPS / REST\nJSON / Multipart", fontsize=8.5, ha='center')

    ax.annotate("", xy=(58, 49), xytext=(58, 54), arrowprops=dict(arrowstyle="<->", lw=1.2, color="black"))
    ax.annotate("", xy=(82, 49), xytext=(82, 54), arrowprops=dict(arrowstyle="<->", lw=1.2, color="black"))
    ax.text(85, 51.5, "SQLAlchemy", fontsize=8, ha='left')

    plt.tight_layout()
    plt.savefig("arch_diagrams/fig6_allocation_view.png", bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    draw_system_context()
    draw_cc_client()
    draw_cc_server()
    draw_module_views()
    draw_allocation_view()
    print("All architecture diagrams generated successfully!")

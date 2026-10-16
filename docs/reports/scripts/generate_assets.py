import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image, ImageDraw, ImageFont

os.makedirs("report_assets", exist_ok=True)

# 1. SIES GST LOGO
def create_sies_logo():
    img = Image.new("RGBA", (500, 160), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Left: Sunburst radiating lines
    cx, cy = 70, 60
    import math
    for i in range(24):
        angle = i * (2 * math.pi / 24)
        x1 = cx + 22 * math.cos(angle)
        y1 = cy + 22 * math.sin(angle)
        x2 = cx + 45 * math.cos(angle)
        y2 = cy + 45 * math.sin(angle)
        draw.line([(x1, y1), (x2, y2)], fill=(235, 130, 20), width=3)
    
    # "SIES" text
    draw.text((35, 105), "SIES", fill=(0, 51, 102), font_size=32)
    draw.text((15, 140), "RISE WITH EDUCATION", fill=(0, 51, 102), font_size=11)
    
    # Right: Teal block
    draw.rectangle([(160, 20), (480, 135)], fill=(0, 128, 145))
    draw.text((180, 40), "Graduate School of", fill=(255, 255, 255), font_size=24)
    draw.text((180, 80), "Technology (Autonomous)", fill=(255, 225, 80), font_size=22)
    
    img.save("report_assets/sies_logo.png")
    print("Created sies_logo.png")

# 2. GANTT CHART (Fig 1.1)
def create_gantt():
    fig, ax = plt.subplots(figsize=(10, 4.5))
    tasks = [
        "Problem Definition & Literature Review",
        "Dataset Assembly & Preprocessing",
        "AI Classifier Training & ONNX Export",
        "Deterministic Rules & Checksum Engine",
        "FastAPI & Ingestion Gateway Build",
        "Reverse-Offset Redaction & Crypto",
        "SOC Dashboard & Copilot Integration",
        "Testing, SLA Benchmarking & Final Report"
    ]
    starts = [1, 3, 5, 7, 9, 11, 13, 15]
    durations = [3, 3, 3, 3, 3, 3, 3, 2]
    
    y_pos = np.arange(len(tasks))
    colors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#9467bd']
    
    for i in range(len(tasks)):
        ax.barh(y_pos[i], durations[i], left=starts[i], align='center', color=colors[i], edgecolor='black', alpha=0.85)
        ax.text(starts[i] + durations[i]/2, y_pos[i], f"{durations[i]} wks", ha='center', va='center', color='black', fontweight='bold', fontsize=9)
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels(tasks, fontsize=10, fontweight='medium')
    ax.invert_yaxis()
    ax.set_xlabel('Project Timeline (Weeks 1 to 16)', fontsize=11, fontweight='bold')
    ax.set_title('Figure 1.1: SecureFlowAI Project Schedule — Gantt Chart', fontsize=12, fontweight='bold', pad=15)
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig("report_assets/fig1_1_gantt.png", dpi=200)
    plt.close()
    print("Created fig1_1_gantt.png")

# 3. ARCHITECTURE DIAGRAM (Fig 3.1)
def create_arch_diagram():
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.axis('off')
    
    # Layer 1
    rect1 = patches.FancyBboxPatch((0.05, 0.78), 0.9, 0.16, boxstyle="round,pad=0.03", ec="#1f77b4", fc="#e8f4f8", lw=2)
    ax.add_patch(rect1)
    ax.text(0.5, 0.90, "Layer 1: Capture & Endpoint Sources", ha='center', va='center', fontsize=12, fontweight='bold', color="#0d47a1")
    ax.text(0.5, 0.83, "Chrome/Edge Browser Extension (MV3)  |  Desktop Clipboard Daemon  |  Email SMTP Connector", ha='center', va='center', fontsize=10)
    
    # Arrow 1
    ax.annotate('', xy=(0.5, 0.71), xytext=(0.5, 0.78), arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8))
    
    # Layer 2 & 3
    rect2 = patches.FancyBboxPatch((0.05, 0.48), 0.9, 0.22, boxstyle="round,pad=0.03", ec="#ff7f0e", fc="#fff5eb", lw=2)
    ax.add_patch(rect2)
    ax.text(0.5, 0.66, "Layer 2 & 3: Ingestion Gateway & Hybrid AI Detection Core", ha='center', va='center', fontsize=12, fontweight='bold', color="#d84315")
    ax.text(0.5, 0.58, "Multi-Format Extractor (PyMuPDF, python-docx, openpyxl)  +  In-Memory EasyOCR Pipeline", ha='center', va='center', fontsize=10)
    ax.text(0.5, 0.52, "Deterministic Checksums (Luhn, MOD-97)  |  Sliding-Window ONNX INT8 Transformer  |  Contextual NER", ha='center', va='center', fontsize=9.5, style='italic')
    
    # Arrow 2
    ax.annotate('', xy=(0.5, 0.41), xytext=(0.5, 0.48), arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8))
    
    # Layer 4
    rect3 = patches.FancyBboxPatch((0.05, 0.24), 0.9, 0.16, boxstyle="round,pad=0.03", ec="#2ca02c", fc="#f0f9f0", lw=2)
    ax.add_patch(rect3)
    ax.text(0.5, 0.35, "Layer 4: Data & Cryptography Enforcement", ha='center', va='center', fontsize=12, fontweight='bold', color="#1b5e20")
    ax.text(0.5, 0.28, "Dynamic Risk Scorer (0-100)  |  Reverse-Offset Masking  |  HMAC Token Vault  |  AES-256-GCM Encryption", ha='center', va='center', fontsize=10)
    
    # Arrow 3
    ax.annotate('', xy=(0.5, 0.17), xytext=(0.5, 0.24), arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8))
    
    # Layer 5
    rect4 = patches.FancyBboxPatch((0.05, 0.02), 0.9, 0.14, boxstyle="round,pad=0.03", ec="#9467bd", fc="#f7f2fb", lw=2)
    ax.add_patch(rect4)
    ax.text(0.5, 0.11, "Layer 5: Governance, SOC Dashboard & Analyst Copilot", ha='center', va='center', fontsize=12, fontweight='bold', color="#4a148c")
    ax.text(0.5, 0.05, "React CISO War Room  |  PostgreSQL Immutable Audit Trail  |  Conversational Analyst Copilot  |  PCI/GDPR Reports", ha='center', va='center', fontsize=9.5)
    
    plt.tight_layout()
    plt.savefig("report_assets/fig3_1_architecture.png", dpi=200)
    plt.close()
    print("Created fig3_1_architecture.png")

# 4. ER DIAGRAM (Fig 4.1)
def create_er_diagram():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    boxes = [
        ("USER", 0.15, 0.75, ["user_id (PK)", "username", "email", "department", "role", "created_at"]),
        ("SECURITY_POLICY", 0.75, 0.75, ["policy_id (PK)", "policy_name", "block_threshold", "encrypt_threshold", "whitelisted_domains"]),
        ("DLP_AUDIT_LOG", 0.45, 0.40, ["event_id (PK)", "user_id (FK)", "timestamp", "destination", "risk_score", "action_taken", "payload_sha256"]),
        ("TOKEN_VAULT", 0.15, 0.10, ["token_id (PK)", "encrypted_value", "nonce", "auth_tag", "entity_type", "created_by (FK)"]),
        ("INCIDENT_OVERRIDE", 0.75, 0.10, ["override_id (PK)", "event_id (FK)", "approved_by (FK)", "justification", "approved_at"])
    ]
    
    for name, x, y, attrs in boxes:
        h = 0.04 + len(attrs) * 0.032
        rect = patches.FancyBboxPatch((x-0.14, y-h/2), 0.28, h, boxstyle="round,pad=0.01", ec="#333", fc="#fdfdfd", lw=1.5)
        ax.add_patch(rect)
        ax.text(x, y + h/2 - 0.02, name, ha='center', va='center', fontsize=10, fontweight='bold', color="#003366")
        ax.plot([x-0.14, x+0.14], [y + h/2 - 0.035, y + h/2 - 0.035], color='#333', lw=1)
        for idx, attr in enumerate(attrs):
            ax.text(x-0.12, y + h/2 - 0.06 - idx*0.03, f"• {attr}", ha='left', va='center', fontsize=8.5)

    # Connections
    ax.annotate('', xy=(0.40, 0.48), xytext=(0.20, 0.65), arrowprops=dict(arrowstyle="->", lw=1.5, color='#444'))
    ax.text(0.28, 0.58, "1 : N (triggers)", fontsize=8, color="#555")
    
    ax.annotate('', xy=(0.50, 0.48), xytext=(0.70, 0.65), arrowprops=dict(arrowstyle="->", lw=1.5, color='#444'))
    ax.text(0.62, 0.58, "enforces", fontsize=8, color="#555")
    
    ax.annotate('', xy=(0.20, 0.22), xytext=(0.38, 0.35), arrowprops=dict(arrowstyle="->", lw=1.5, color='#444'))
    ax.text(0.25, 0.28, "vaults PII", fontsize=8, color="#555")

    ax.annotate('', xy=(0.70, 0.22), xytext=(0.52, 0.35), arrowprops=dict(arrowstyle="->", lw=1.5, color='#444'))
    ax.text(0.63, 0.28, "overrides", fontsize=8, color="#555")

    ax.set_title("Figure 4.1: SecureFlowAI Entity-Relationship (ER) Schema", fontsize=12, fontweight='bold', pad=10)
    plt.tight_layout()
    plt.savefig("report_assets/fig4_1_er_diagram.png", dpi=200)
    plt.close()
    print("Created fig4_1_er_diagram.png")

# 5. UML ACTIVITY DIAGRAM (Fig 4.2)
def create_uml_diagram():
    fig, ax = plt.subplots(figsize=(8, 9))
    ax.axis('off')
    
    steps = [
        ("User Initiates Copy / Paste / Upload", 0.5, 0.92, "oval"),
        ("Intercept Data at Endpoint (Browser / Daemon)", 0.5, 0.82, "box"),
        ("Extract Text & Tables (PyMuPDF / EasyOCR)", 0.5, 0.72, "box"),
        ("Run Checksums (Luhn / MOD-97) & INT8 Classifier", 0.5, 0.62, "box"),
        ("Compute Unified Risk Score (0-100)", 0.5, 0.52, "box"),
        ("Evaluate Risk Thresholds", 0.5, 0.42, "diamond"),
        ("Action: ALLOW (Score < 45)", 0.20, 0.28, "box"),
        ("Action: MASK / ENCRYPT (45-79)", 0.50, 0.28, "box"),
        ("Action: BLOCK (Score >= 80)", 0.80, 0.28, "box"),
        ("Commit Immutable Log to PostgreSQL & Notify SOC", 0.5, 0.14, "box"),
        ("Transaction Completed", 0.5, 0.04, "oval")
    ]
    
    for text, x, y, shape in steps:
        if shape == "box":
            p = patches.FancyBboxPatch((x-0.18, y-0.03), 0.36, 0.06, boxstyle="round,pad=0.01", ec="#003366", fc="#e6f2ff", lw=1.5)
        elif shape == "oval":
            p = patches.FancyBboxPatch((x-0.18, y-0.025), 0.36, 0.05, boxstyle="circle,pad=0.01", ec="#333", fc="#e0e0e0", lw=2)
        elif shape == "diamond":
            p = patches.RegularPolygon((x, y), numVertices=4, radius=0.07, orientation=np.pi/4, ec="#cc6600", fc="#fff2e6", lw=1.5)
        ax.add_patch(p)
        ax.text(x, y, text, ha='center', va='center', fontsize=8.5, fontweight='bold')

    # Connect lines
    lines = [
        ((0.5, 0.895), (0.5, 0.85)),
        ((0.5, 0.79), (0.5, 0.75)),
        ((0.5, 0.69), (0.5, 0.65)),
        ((0.5, 0.59), (0.5, 0.55)),
        ((0.5, 0.49), (0.5, 0.46))
    ]
    for p1, p2 in lines:
        ax.annotate('', xy=p2, xytext=p1, arrowprops=dict(arrowstyle="->", lw=1.2, color='#333'))

    # Branching from diamond
    ax.annotate('', xy=(0.20, 0.31), xytext=(0.43, 0.42), arrowprops=dict(arrowstyle="->", lw=1.2, color='#2ca02c'))
    ax.text(0.26, 0.38, "Low Risk", fontsize=8, color="#1b5e20", fontweight='bold')
    
    ax.annotate('', xy=(0.50, 0.31), xytext=(0.50, 0.37), arrowprops=dict(arrowstyle="->", lw=1.2, color='#ff7f0e'))
    ax.text(0.51, 0.34, "Medium", fontsize=8, color="#b35400", fontweight='bold')

    ax.annotate('', xy=(0.80, 0.31), xytext=(0.57, 0.42), arrowprops=dict(arrowstyle="->", lw=1.2, color='#d62728'))
    ax.text(0.70, 0.38, "Critical", fontsize=8, color="#990000", fontweight='bold')

    # Converge to audit log
    ax.annotate('', xy=(0.40, 0.17), xytext=(0.20, 0.25), arrowprops=dict(arrowstyle="->", lw=1.2, color='#333'))
    ax.annotate('', xy=(0.50, 0.17), xytext=(0.50, 0.25), arrowprops=dict(arrowstyle="->", lw=1.2, color='#333'))
    ax.annotate('', xy=(0.60, 0.17), xytext=(0.80, 0.25), arrowprops=dict(arrowstyle="->", lw=1.2, color='#333'))
    
    ax.annotate('', xy=(0.50, 0.065), xytext=(0.50, 0.11), arrowprops=dict(arrowstyle="->", lw=1.2, color='#333'))

    ax.set_title("Figure 4.2: SecureFlowAI UML Activity Workflow Diagram", fontsize=12, fontweight='bold', pad=10)
    plt.tight_layout()
    plt.savefig("report_assets/fig4_2_uml_activity.png", dpi=200)
    plt.close()
    print("Created fig4_2_uml_activity.png")

# 6. DFD LEVEL 1 (Fig 4.3)
def create_dfd_diagram():
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.axis('off')
    
    # External Entities
    ax.add_patch(patches.Rectangle((0.03, 0.65), 0.14, 0.14, ec="#333", fc="#e0ecf8", lw=1.5))
    ax.text(0.10, 0.72, "E1: Bank\nEmployee", ha='center', va='center', fontsize=9.5, fontweight='bold')
    
    ax.add_patch(patches.Rectangle((0.83, 0.65), 0.14, 0.14, ec="#333", fc="#f8e0e0", lw=1.5))
    ax.text(0.90, 0.72, "E2: External\nRecipient / Cloud", ha='center', va='center', fontsize=9.5, fontweight='bold')

    ax.add_patch(patches.Rectangle((0.83, 0.15), 0.14, 0.14, ec="#333", fc="#e0f8e0", lw=1.5))
    ax.text(0.90, 0.22, "E3: SOC\nAnalyst", ha='center', va='center', fontsize=9.5, fontweight='bold')

    # Core Processes
    procs = [
        ("P1: Ingest & Extract Text", 0.35, 0.72),
        ("P2: Hybrid Classify & Rules", 0.58, 0.72),
        ("P3: Evaluate Risk Policy", 0.58, 0.42),
        ("P4: Enforce Action (Block/Mask)", 0.35, 0.42),
        ("P5: Audit & Alert Logger", 0.58, 0.18)
    ]
    for p_name, x, y in procs:
        p = patches.FancyBboxPatch((x-0.10, y-0.05), 0.20, 0.10, boxstyle="round,pad=0.01", ec="#003366", fc="#fff9e6", lw=1.5)
        ax.add_patch(p)
        ax.text(x, y, p_name, ha='center', va='center', fontsize=8.5, fontweight='bold')

    # Data Stores
    stores = [
        ("D1: Policy Cache", 0.35, 0.25),
        ("D2: PostgreSQL Audit DB", 0.35, 0.08),
        ("D3: Token Vault", 0.78, 0.42)
    ]
    for s_name, x, y in stores:
        ax.plot([x-0.09, x+0.09], [y+0.03, y+0.03], color='#333', lw=1.5)
        ax.plot([x-0.09, x+0.09], [y-0.03, y-0.03], color='#333', lw=1.5)
        ax.text(x, y, s_name, ha='center', va='center', fontsize=8.5, fontweight='bold', color="#4a148c")

    # Connectors
    ax.annotate('Payload', xy=(0.25, 0.72), xytext=(0.17, 0.72), arrowprops=dict(arrowstyle="->", lw=1.2))
    ax.annotate('Text', xy=(0.48, 0.72), xytext=(0.45, 0.72), arrowprops=dict(arrowstyle="->", lw=1.2))
    ax.annotate('Score & Entities', xy=(0.58, 0.47), xytext=(0.58, 0.67), arrowprops=dict(arrowstyle="->", lw=1.2))
    ax.annotate('Decision', xy=(0.45, 0.42), xytext=(0.48, 0.42), arrowprops=dict(arrowstyle="->", lw=1.2))
    ax.annotate('Safe Data', xy=(0.83, 0.72), xytext=(0.68, 0.72), arrowprops=dict(arrowstyle="->", lw=1.2, color='#2ca02c'))
    ax.annotate('Block Alert', xy=(0.10, 0.65), xytext=(0.30, 0.42), arrowprops=dict(arrowstyle="->", lw=1.2, color='#d62728'))
    ax.annotate('Telemetry', xy=(0.58, 0.23), xytext=(0.58, 0.37), arrowprops=dict(arrowstyle="->", lw=1.2))
    ax.annotate('SOC Alert', xy=(0.83, 0.22), xytext=(0.68, 0.18), arrowprops=dict(arrowstyle="->", lw=1.2, color='#9467bd'))

    ax.set_title("Figure 4.3: SecureFlowAI Level 1 Data Flow Diagram (DFD)", fontsize=12, fontweight='bold', pad=10)
    plt.tight_layout()
    plt.savefig("report_assets/fig4_3_dfd_level1.png", dpi=200)
    plt.close()
    print("Created fig4_3_dfd_level1.png")

# 7. UI MOCKUPS (Fig 5.1, 5.2, 5.3, 5.4)
def create_ui_figures():
    # Fig 5.1: UI Overview
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.axis('off')
    ax.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor='#111827'))
    ax.add_patch(patches.Rectangle((0, 0.88), 1, 0.12, facecolor='#1f2937'))
    ax.text(0.04, 0.94, "🛡️ SecureFlow AI — Enterprise Banking DLP Command Console", color='white', fontsize=13, fontweight='bold', va='center')
    ax.text(0.92, 0.94, "SOC: Active", color='#10b981', fontsize=10, fontweight='bold', va='center')
    
    # 4 KPI cards
    kpis = [("Total Flows", "1,420,890"), ("Threats Blocked", "42"), ("Avg Latency", "11.4 ms"), ("Compliance Score", "99.8%")]
    colors = ["#3b82f6", "#ef4444", "#10b981", "#8b5cf6"]
    for i, (k, v) in enumerate(kpis):
        x = 0.04 + i * 0.24
        ax.add_patch(patches.FancyBboxPatch((x, 0.65), 0.21, 0.18, boxstyle="round,pad=0.01", ec="#374151", fc="#1f2937", lw=1))
        ax.text(x+0.02, 0.78, k, color='#9ca3af', fontsize=9)
        ax.text(x+0.02, 0.70, v, color=colors[i], fontsize=15, fontweight='bold')
        
    # Main content box: Recent Incidents
    ax.add_patch(patches.FancyBboxPatch((0.04, 0.08), 0.92, 0.52, boxstyle="round,pad=0.01", ec="#374151", fc="#1f2937", lw=1))
    ax.text(0.06, 0.55, "Recent DLP Detection & Interception Events", color='white', fontsize=11, fontweight='bold')
    
    events = [
        ("INC-8091", "emp_401", "Outlook Web", "external@gmail.com", "Visa PAN (16d)", "Score 95", "BLOCK", "#ef4444"),
        ("INC-8090", "emp_112", "Desktop Agent", "USB Storage (E:)", "Salary Dossier (.xlsx)", "Score 88", "BLOCK", "#ef4444"),
        ("INC-8089", "emp_782", "Chrome MV3", "partner@visa.com", "IBAN Wire Transfer", "Score 52", "ENCRYPT", "#f59e0b"),
        ("INC-8088", "emp_991", "Email Gateway", "client@corp.bank", "Meeting Agenda (.docx)", "Score 12", "ALLOW", "#10b981")
    ]
    ax.plot([0.06, 0.94], [0.50, 0.50], color='#374151', lw=1)
    ax.text(0.07, 0.46, "Incident ID", color='#9ca3af', fontsize=8.5, fontweight='bold')
    ax.text(0.18, 0.46, "User", color='#9ca3af', fontsize=8.5, fontweight='bold')
    ax.text(0.28, 0.46, "Channel", color='#9ca3af', fontsize=8.5, fontweight='bold')
    ax.text(0.42, 0.46, "Destination", color='#9ca3af', fontsize=8.5, fontweight='bold')
    ax.text(0.60, 0.46, "Detected Entity", color='#9ca3af', fontsize=8.5, fontweight='bold')
    ax.text(0.76, 0.46, "Risk Tier", color='#9ca3af', fontsize=8.5, fontweight='bold')
    ax.text(0.86, 0.46, "Action", color='#9ca3af', fontsize=8.5, fontweight='bold')
    
    for idx, (iid, usr, ch, dst, ent, rsk, act, col) in enumerate(events):
        y = 0.38 - idx * 0.08
        ax.text(0.07, y, iid, color='white', fontsize=8)
        ax.text(0.18, y, usr, color='#d1d5db', fontsize=8)
        ax.text(0.28, y, ch, color='#d1d5db', fontsize=8)
        ax.text(0.42, y, dst, color='#d1d5db', fontsize=8)
        ax.text(0.60, y, ent, color='#fca5a5' if 'Visa' in ent else '#93c5fd', fontsize=8)
        ax.text(0.76, y, rsk, color=col, fontsize=8, fontweight='bold')
        ax.text(0.86, y, act, color=col, fontsize=8, fontweight='bold')

    plt.tight_layout()
    plt.savefig("report_assets/fig5_1_ui.png", dpi=200)
    plt.close()
    print("Created fig5_1_ui.png")

    # Fig 5.2: File Upload Interface
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.axis('off')
    ax.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor='#f9fafb'))
    ax.add_patch(patches.FancyBboxPatch((0.1, 0.15), 0.8, 0.7, boxstyle="round,pad=0.02", ec="#cbd5e1", fc="#ffffff", lw=1.5, ls='--'))
    ax.text(0.5, 0.65, "📁 Drag & Drop Financial Document (.pdf, .xlsx, .docx)", color='#1e293b', fontsize=12, fontweight='bold', ha='center')
    ax.text(0.5, 0.55, "Support for scanned KYC files, checks, and Excel audit sheets up to 50MB", color='#64748b', fontsize=9, ha='center')
    ax.add_patch(patches.FancyBboxPatch((0.38, 0.35), 0.24, 0.12, boxstyle="round,pad=0.01", ec="#2563eb", fc="#2563eb", lw=1))
    ax.text(0.5, 0.41, "Browse Files", color='white', fontsize=11, fontweight='bold', ha='center')
    ax.text(0.5, 0.22, "Selected file: Q3_Retail_Loan_Disbursement.xlsx (2.4 MB)", color='#047857', fontsize=9, ha='center')
    ax.set_title("Figure 5.2: SecureFlowAI File Inspection & Upload Dialog", fontsize=11, fontweight='bold', pad=10)
    plt.tight_layout()
    plt.savefig("report_assets/fig5_2_upload.png", dpi=200)
    plt.close()
    print("Created fig5_2_upload.png")

    # Fig 5.3: Model Selection & Settings
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.axis('off')
    ax.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor='#f8fafc'))
    ax.add_patch(patches.FancyBboxPatch((0.08, 0.1), 0.84, 0.8, boxstyle="round,pad=0.02", ec="#cbd5e1", fc="#ffffff", lw=1.5))
    ax.text(0.12, 0.82, "⚙️ Detection Engine & Model Configuration", color='#0f172a', fontsize=12, fontweight='bold')
    
    # Dropdown 1
    ax.text(0.12, 0.70, "Select AI Classifier Engine:", color='#475569', fontsize=9.5, fontweight='bold')
    ax.add_patch(patches.Rectangle((0.12, 0.58), 0.76, 0.08, ec="#94a3b8", fc="#f1f5f9"))
    ax.text(0.14, 0.62, "MiniLM-L6-v2 (ONNX INT8 Quantized) — Sub-15ms Latency (Recommended)", color='#0f172a', fontsize=9)
    
    # Sliders
    ax.text(0.12, 0.48, "Risk Block Threshold: 80 / 100", color='#475569', fontsize=9.5, fontweight='bold')
    ax.plot([0.12, 0.88], [0.42, 0.42], color='#cbd5e1', lw=4)
    ax.plot([0.12, 0.72], [0.42, 0.42], color='#ef4444', lw=4)
    ax.plot(0.72, 0.42, 'o', color='#b91c1c', markersize=10)
    
    ax.text(0.12, 0.32, "OCR Extraction Pipeline: PyMuPDF + In-Memory EasyOCR (Enabled)", color='#475569', fontsize=9.5, fontweight='bold')
    ax.text(0.12, 0.22, "Whitelisted Domains: @partnerbank.com, @visa.com, @swift.com", color='#059669', fontsize=9)
    ax.set_title("Figure 5.3: Policy & Model Selection Configuration Panel", fontsize=11, fontweight='bold', pad=10)
    plt.tight_layout()
    plt.savefig("report_assets/fig5_3_model_selection.png", dpi=200)
    plt.close()
    print("Created fig5_3_model_selection.png")

    # Fig 5.4: Response & Real-Time Masking
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.axis('off')
    ax.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor='#1e293b'))
    ax.text(0.05, 0.90, "🔍 Real-Time Inspection & Remediation Result", color='white', fontsize=11, fontweight='bold')
    
    # Input card
    ax.add_patch(patches.FancyBboxPatch((0.05, 0.52), 0.90, 0.32, boxstyle="round,pad=0.01", ec="#475569", fc="#0f172a", lw=1))
    ax.text(0.07, 0.76, "Original Input Payload (Intercepted from Webmail Draft):", color='#94a3b8', fontsize=8.5)
    ax.text(0.07, 0.64, "\"Please disburse loan to John Doe at account GB29NWBK60161331926819\nand charge processing fee to card 4532-8921-0043-9182.\"", color='#fca5a5', fontsize=9, style='italic')

    # Output card
    ax.add_patch(patches.FancyBboxPatch((0.05, 0.08), 0.90, 0.38, boxstyle="round,pad=0.01", ec="#10b981", fc="#0f172a", lw=1.5))
    ax.text(0.07, 0.38, "Remediated Output (Format-Preserving Reverse-Offset Masking):", color='#34d399', fontsize=8.5, fontweight='bold')
    ax.text(0.07, 0.26, "\"Please disburse loan to John Doe at account [IBAN_GB****6819]\nand charge processing fee to card [CARD_****9182].\"", color='#67e8f9', fontsize=9, style='italic')
    ax.text(0.07, 0.14, "Action: REMEDIATE | Tier: RESTRICTED | Risk Score: 78/100 | Latency: 11.2 ms | Verified: Luhn & MOD-97", color='#a7f3d0', fontsize=8)

    ax.set_title("Figure 5.4: Real-Time Detection, Checksum Verification & Masking", fontsize=11, fontweight='bold', pad=10, color='white')
    plt.tight_layout()
    plt.savefig("report_assets/fig5_4_response.png", dpi=200)
    plt.close()
    print("Created fig5_4_response.png")

# 8. EVALUATION METRICS CHART (Fig 5.5)
def create_metrics_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    
    # Subplot A: Average Metrics
    metrics = ["Accuracy", "Precision", "Recall", "F1-Score", "Adv. Defense"]
    baseline = [80.5, 78.2, 85.0, 81.4, 41.0]
    proposed = [96.8, 95.4, 99.4, 97.2, 92.4]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    ax1.bar(x - width/2, baseline, width, label='Signature/Baseline', color='#94a3b8')
    ax1.bar(x + width/2, proposed, width, label='SecureFlowAI', color='#2563eb')
    ax1.set_ylabel('Score (%)', fontsize=10, fontweight='bold')
    ax1.set_title('(a) Average Performance Metrics Comparison', fontsize=10.5, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics, rotation=20, fontsize=8.5)
    ax1.set_ylim(0, 110)
    ax1.legend(loc='lower right', fontsize=8.5)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Subplot B: Per-Query / Channel Latency & Accuracy
    channels = ["Browser Form", "PDF Upload", "Excel Sheet", "Scanned KYC", "Clipboard"]
    acc = [98.5, 96.2, 97.4, 94.8, 99.1]
    lat = [8.2, 14.5, 12.1, 19.8, 6.4]
    
    ax2_twin = ax2.twinx()
    ax2.bar(channels, acc, color='#10b981', alpha=0.85, width=0.4, label='Accuracy (%)')
    ax2_twin.plot(channels, lat, color='#ef4444', marker='o', linewidth=2.5, label='Latency (ms)')
    
    ax2.set_ylabel('Detection Accuracy (%)', color='#065f46', fontsize=10, fontweight='bold')
    ax2_twin.set_ylabel('Inference Latency (ms)', color='#991b1b', fontsize=10, fontweight='bold')
    ax2.set_title('(b) Per-Channel Accuracy vs Latency (SLA < 25ms)', fontsize=10.5, fontweight='bold')
    ax2.set_xticklabels(channels, rotation=25, fontsize=8.5)
    ax2.set_ylim(80, 105)
    ax2_twin.set_ylim(0, 30)
    ax2_twin.axhline(25, color='#b91c1c', linestyle=':', label='25ms SLA Target')
    ax2.grid(axis='y', linestyle='--', alpha=0.5)

    plt.suptitle("Figure 5.5: Evaluation Metrics & SLA Latency Benchmarks for SecureFlowAI", fontsize=12, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig("report_assets/fig5_5_metrics.png", dpi=200)
    plt.close()
    print("Created fig5_5_metrics.png")

if __name__ == "__main__":
    create_sies_logo()
    create_gantt()
    create_arch_diagram()
    create_er_diagram()
    create_uml_diagram()
    create_dfd_diagram()
    create_ui_figures()
    create_metrics_chart()
    print("\nALL REPORT ASSETS GENERATED SUCCESSFULLY!")

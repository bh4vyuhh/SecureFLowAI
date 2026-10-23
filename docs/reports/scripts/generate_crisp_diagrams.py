import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon
import numpy as np

os.makedirs("report_assets", exist_ok=True)
os.makedirs("docs/reports/assets", exist_ok=True)

# Clean, professional typography
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#334155'
plt.rcParams['axes.linewidth'] = 1.4

def save_fig(fig, filename):
    for target in [f"report_assets/{filename}", f"docs/reports/assets/{filename}"]:
        fig.savefig(target, dpi=300, bbox_inches='tight', pad_inches=0.1)
    print(f"Saved ultra-crisp {filename}")

# ==============================================================================
# 1. GANTT CHART (Fig 1.1)
# ==============================================================================
def create_crisp_gantt():
    fig, ax = plt.subplots(figsize=(8.0, 4.6), dpi=300)
    
    tasks = [
        "1. Problem Definition & Survey",
        "2. Banking Dataset Assembly",
        "3. Hybrid Model & Quantization",
        "4. Luhn & MOD-97 Verification",
        "5. Ingestion Gateway & OCR",
        "6. Masking & AES-256 Vault",
        "7. SOC Console & Copilot",
        "8. SLA Testing & Viva Report"
    ]
    
    start_weeks = [1, 3, 5, 7, 9, 11, 13, 15]
    durations   = [3, 3, 3, 3, 3, 3, 3, 2]
    
    y_pos = np.arange(len(tasks))
    bar_colors = [
        '#1E3A8A', '#2563EB', '#0D9488', '#059669',
        '#D97706', '#EA580C', '#7C3AED', '#475569'
    ]
    
    for i in range(len(tasks)):
        ax.barh(y_pos[i], durations[i], left=start_weeks[i], height=0.62,
                color=bar_colors[i], edgecolor='#0F172A', linewidth=1.5, zorder=3)
        ax.text(start_weeks[i] + durations[i] / 2, y_pos[i], f"{durations[i]} Wks",
                ha='center', va='center', color='white', fontweight='bold', fontsize=10.5, zorder=4)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(tasks, fontsize=11.0, fontweight='bold', color='#0F172A')
    ax.invert_yaxis()
    
    ax.set_xlim(0.5, 17.5)
    ax.set_xticks(range(1, 18))
    ax.set_xticklabels([f"W{w}" for w in range(1, 18)], fontsize=9.5, fontweight='bold', color='#1E293B')
    ax.set_xlabel("Academic Project Schedule (Weeks 1 to 16)", fontsize=11.0, fontweight='bold', labelpad=8, color='#0F172A')
    
    ax.grid(axis='x', linestyle='--', alpha=0.6, color='#94A3B8', zorder=1)
    ax.set_axisbelow(True)
    
    ax.axvspan(1, 4.5, color='#F8FAFC', alpha=0.9, zorder=0)
    ax.axvspan(4.5, 10.5, color='#F1F5F9', alpha=0.9, zorder=0)
    ax.axvspan(10.5, 17, color='#F8FAFC', alpha=0.9, zorder=0)
    
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_color('#CBD5E1')
        ax.spines[spine].set_linewidth(1.3)
        
    ax.set_title("Figure 1.1: SecureFlowAI Project Milestone Gantt Chart",
                 fontsize=12.0, fontweight='bold', color='#0F172A', pad=12)
    save_fig(fig, "fig1_1_gantt.png")
    plt.close()

# ==============================================================================
# 2. SYSTEM ARCHITECTURE DIAGRAM (Fig 3.1)
# ==============================================================================
def create_crisp_architecture():
    fig, ax = plt.subplots(figsize=(8.0, 8.4), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    
    # Outer Card
    bg = FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=0.8", ec="#94A3B8", fc="#FFFFFF", lw=1.6)
    ax.add_patch(bg)
    
    # Title Banner
    title_box = FancyBboxPatch((3, 92), 94, 6.2, boxstyle="round,pad=0.4", ec="#1E3A8A", fc="#1E3A8A", lw=1)
    ax.add_patch(title_box)
    ax.text(50, 95.1, "SECUREFLOWAI: MULTI-TIER BANKING DLP ARCHITECTURE",
            ha='center', va='center', color='white', fontsize=12.0, fontweight='bold')

    def draw_layer(y, h, title, subtitle, items, border_c, header_c, bg_c):
        card = FancyBboxPatch((3, y), 94, h, boxstyle="round,pad=0.4", ec=border_c, fc=bg_c, lw=1.6)
        ax.add_patch(card)
        # Header strip
        strip = FancyBboxPatch((3, y + h - 4.4), 94, 4.4, boxstyle="round,pad=0.1", ec=border_c, fc=header_c, lw=1)
        ax.add_patch(strip)
        ax.text(50, y + h - 2.2, title, ha='center', va='center', color='white', fontsize=10.5, fontweight='bold')
        ax.text(5, y + h - 6.0, subtitle, ha='left', va='center', color='#1E293B', fontsize=8.8, fontstyle='italic', fontweight='bold')
        
        n = len(items)
        sub_w = (94 - (n + 1) * 2) / n
        sub_h = h - 8.8
        for i, (b_title, b_desc) in enumerate(items):
            bx = 3 + 2 + i * (sub_w + 2)
            by = y + 1.8
            sub_card = FancyBboxPatch((bx, by), sub_w, sub_h, boxstyle="round,pad=0.2", ec="#94A3B8", fc="#FFFFFF", lw=1.3)
            ax.add_patch(sub_card)
            ax.text(bx + sub_w/2, by + sub_h - 2.2, b_title, ha='center', va='center', color='#0F172A', fontsize=9.5, fontweight='bold')
            ax.text(bx + sub_w/2, by + sub_h/2 - 1.2, b_desc, ha='center', va='center', color='#1E293B', fontsize=8.4, linespacing=1.28)

    # Layer 1
    draw_layer(
        72.5, 17,
        "LAYER 1: ENDPOINT & SENSOR INGESTION TIER",
        "Interception layer capturing outbound egress events at user workstations",
        [
            ("Browser Extension", "Chrome/Edge MV3\nDOM paste & HTTP uploads\nZero external egress"),
            ("Desktop OS Daemon", "Low-level clipboard hook\nMonitors buffer changes\nIntercepts file copies"),
            ("Enterprise Mail Gateway", "Milter/SMTP proxy hook\nScans body & attachments\n(PDF, XLSX, DOCX)")
        ],
        "#2563EB", "#2563EB", "#EFF6FF"
    )

    # Arrow 1
    ax.annotate('', xy=(50, 68.5), xytext=(50, 72.5),
                arrowprops=dict(facecolor='#1E3A8A', edgecolor='#1E3A8A', width=2.2, headwidth=7, headlength=7))
    ax.text(51.5, 70.5, "Encrypted Local JSON / Binary Stream via mTLS", color='#1E3A8A', fontsize=8.8, fontweight='bold')

    # Layer 2
    draw_layer(
        50.5, 17,
        "LAYER 2: INGESTION GATEWAY & DOCUMENT EXTRACTION CORE",
        "FastAPI asynchronous pipeline with multi-format streaming parsers & OCR",
        [
            ("FastAPI Gateway", "Non-blocking event loop\nmTLS authentication\nCircuit breaker fail-open"),
            ("Document Parsers", "PyMuPDF (PDF text/tables)\npython-docx (Office DOCX)\nopenpyxl (Financial Sheets)"),
            ("EasyOCR Image Engine", "In-memory OCR pipeline\nScanned checks, PAN cards\nNational ID KYC images")
        ],
        "#0D9488", "#0D9488", "#F0FDFA"
    )

    # Arrow 2
    ax.annotate('', xy=(50, 46.5), xytext=(50, 50.5),
                arrowprops=dict(facecolor='#0D9488', edgecolor='#0D9488', width=2.2, headwidth=7, headlength=7))
    ax.text(51.5, 48.5, "Normalized Text Streams & Extracted Image Tokens", color='#0D9488', fontsize=8.8, fontweight='bold')

    # Layer 3
    draw_layer(
        28.5, 17,
        "LAYER 3: HYBRID AI CLASSIFIER & VERIFICATION ENGINE",
        "Two-stage pipeline: mathematical checksum verification + quantized neural model",
        [
            ("Algorithmic Checksums", "Luhn (Credit Card PAN)\nMOD-97 (IBAN accounts)\nRegex Routing & SWIFT"),
            ("ONNX INT8 Transformer", "Sliding-window MiniLM\n11.4ms local CPU inference\nZero cloud dependencies"),
            ("Contextual NER & Rules", "spaCy named entity engine\nDisambiguates false alarms\n(Phone vs. Card numbers)")
        ],
        "#D97706", "#D97706", "#FFFBEB"
    )

    # Arrow 3
    ax.annotate('', xy=(50, 24.5), xytext=(50, 28.5),
                arrowprops=dict(facecolor='#D97706', edgecolor='#D97706', width=2.2, headwidth=7, headlength=7))
    ax.text(51.5, 26.5, "Entity Spans, Offsets & Computed Risk Score (0 - 100)", color='#D97706', fontsize=8.8, fontweight='bold')

    # Layer 4 & 5
    card_bot = FancyBboxPatch((3, 3), 94, 20.5, boxstyle="round,pad=0.4", ec="#7C3AED", fc="#FAF5FF", lw=1.6)
    ax.add_patch(card_bot)
    strip_bot = FancyBboxPatch((3, 19.3), 94, 4.2, boxstyle="round,pad=0.1", ec="#7C3AED", fc="#7C3AED", lw=1)
    ax.add_patch(strip_bot)
    ax.text(50, 21.4, "LAYER 4 & 5: ENFORCEMENT, CRYPTOGRAPHY & SOC GOVERNANCE",
            ha='center', va='center', color='white', fontsize=10.5, fontweight='bold')

    bot_items = [
        ("Reverse Masking", "Preserves sentence\nReplaces sensitive spans\nwith HMAC tokens"),
        ("AES-256 Vault", "Envelope encryption\nZero-knowledge keys\nDetokenization audit"),
        ("Audit Trail", "SQLite & PostgreSQL\nSHA-256 payload digest\nPCI-DSS / GDPR proof"),
        ("SOC Console", "React 19 dashboard\nWebSocket real-time push\nAnalyst AI Copilot")
    ]
    b_w = (94 - 5 * 2) / 4
    b_h = 13.5
    for i, (b_title, b_desc) in enumerate(bot_items):
        bx = 3 + 2 + i * (b_w + 2)
        by = 4.8
        sub_card = FancyBboxPatch((bx, by), b_w, b_h, boxstyle="round,pad=0.2", ec="#94A3B8", fc="#FFFFFF", lw=1.3)
        ax.add_patch(sub_card)
        ax.text(bx + b_w/2, by + b_h - 2.2, b_title, ha='center', va='center', color='#0F172A', fontsize=9.2, fontweight='bold')
        ax.text(bx + b_w/2, by + b_h/2 - 1.2, b_desc, ha='center', va='center', color='#1E293B', fontsize=8.0, linespacing=1.28)

    save_fig(fig, "fig3_1_architecture.png")
    plt.close()

# ==============================================================================
# 3. ENTITY RELATIONSHIP (ER) DIAGRAM (Fig 4.1)
# ==============================================================================
def create_crisp_er():
    fig, ax = plt.subplots(figsize=(8.0, 7.0), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    
    bg = FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=0.8", ec="#CBD5E1", fc="#F8FAFC", lw=1.4)
    ax.add_patch(bg)
    
    def draw_entity(x, y, w, h, title, fields, color="#1E3A8A"):
        hdr = FancyBboxPatch((x, y + h - 5.5), w, 5.5, boxstyle="round,pad=0.1", ec=color, fc=color, lw=1.6)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - 2.7, title, ha='center', va='center', color='white', fontsize=10.5, fontweight='bold')
        
        body = FancyBboxPatch((x, y), w, h - 5.5, boxstyle="round,pad=0.1", ec=color, fc='#FFFFFF', lw=1.6)
        ax.add_patch(body)
        
        for idx, (f_name, f_type, is_pk, is_fk) in enumerate(fields):
            fy = y + h - 8.4 - idx * 3.1
            prefix = "[PK] " if is_pk else ("[FK] " if is_fk else " •  ")
            f_col = "#DC2626" if is_pk else ("#D97706" if is_fk else "#0F172A")
            ax.text(x + 2, fy, f"{prefix}{f_name}", ha='left', va='center', color=f_col,
                    fontsize=9.2, fontweight='bold' if (is_pk or is_fk) else 'bold')
            ax.text(x + w - 2, fy, f_type, ha='right', va='center', color="#475569", fontsize=8.6, fontfamily='monospace', fontweight='semibold')

    # Top Row: BANK_USER (Left) and SECURITY_POLICY (Right)
    draw_entity(5, 68, 42, 27, "BANK_USER", [
        ("user_id", "UUID", True, False),
        ("employee_email", "VARCHAR(128)", False, False),
        ("department_name", "VARCHAR(64)", False, False),
        ("assigned_role", "VARCHAR(32)", False, False),
        ("risk_tier", "INTEGER", False, False),
        ("created_at", "TIMESTAMP", False, False)
    ], "#1E3A8A")

    draw_entity(53, 68, 42, 27, "SECURITY_POLICY", [
        ("policy_id", "UUID", True, False),
        ("policy_code", "VARCHAR(64)", False, False),
        ("mask_threshold", "INTEGER", False, False),
        ("block_threshold", "INTEGER", False, False),
        ("whitelisted_domains", "JSONB", False, False),
        ("fail_mode", "VARCHAR(16)", False, False)
    ], "#0D9488")

    # Center: DLP_AUDIT_LOG
    draw_entity(24, 27, 52, 36, "DLP_AUDIT_LOG", [
        ("incident_id", "UUID", True, False),
        ("user_id", "UUID", False, True),
        ("policy_id", "UUID", False, True),
        ("timestamp", "TIMESTAMP", False, False),
        ("source_action", "VARCHAR(32)", False, False),
        ("destination", "VARCHAR(255)", False, False),
        ("classification", "VARCHAR(32)", False, False),
        ("risk_score", "INTEGER", False, False),
        ("enforcement", "VARCHAR(16)", False, False),
        ("payload_sha256", "CHAR(64)", False, False)
    ], "#B45309")

    # Bottom Row: TOKEN_VAULT (Left) and INCIDENT_OVERRIDE (Right)
    draw_entity(5, 3, 42, 20, "TOKEN_VAULT", [
        ("token_id", "VARCHAR(64)", True, False),
        ("incident_id", "UUID", False, True),
        ("encrypted_pii", "BYTEA", False, False),
        ("iv_nonce", "BYTEA", False, False),
        ("auth_tag", "BYTEA", False, False)
    ], "#6D28D9")

    draw_entity(53, 3, 42, 20, "INCIDENT_OVERRIDE", [
        ("override_id", "UUID", True, False),
        ("incident_id", "UUID", False, True),
        ("analyst_id", "UUID", False, True),
        ("justification", "TEXT", False, False),
        ("authorized_at", "TIMESTAMP", False, False)
    ], "#475569")

    # Connectors
    ax.annotate('', xy=(35, 63), xytext=(26, 68),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#1E3A8A', connectionstyle="angle,angleA=-90,angleB=180,rad=3"))
    ax.text(25, 64.5, "1 : N (Triggers)", color='#1E3A8A', fontsize=9.2, fontweight='bold')

    ax.annotate('', xy=(65, 63), xytext=(74, 68),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#0D9488', connectionstyle="angle,angleA=-90,angleB=0,rad=3"))
    ax.text(68, 64.5, "1 : N (Governs)", color='#0D9488', fontsize=9.2, fontweight='bold')

    ax.annotate('', xy=(26, 23), xytext=(35, 27),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#6D28D9', connectionstyle="angle,angleA=-90,angleB=180,rad=3"))
    ax.text(23, 24.8, "1 : N (Vaults)", color='#6D28D9', fontsize=9.2, fontweight='bold')

    ax.annotate('', xy=(74, 23), xytext=(65, 27),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#475569', connectionstyle="angle,angleA=-90,angleB=0,rad=3"))
    ax.text(68, 24.8, "1 : 1 (Overrides)", color='#475569', fontsize=9.2, fontweight='bold')

    ax.set_title("Figure 4.1: SecureFlowAI Relational Schema & Entity-Relationship Model",
                 fontsize=12.0, fontweight='bold', color='#0F172A', pad=10)
    save_fig(fig, "fig4_1_er_diagram.png")
    plt.close()

# ==============================================================================
# 4. UML ACTIVITY WORKFLOW DIAGRAM (Fig 4.2)
# ==============================================================================
def create_crisp_uml():
    fig, ax = plt.subplots(figsize=(7.2, 9.4), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    bg = FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=0.8", ec="#CBD5E1", fc="#FFFFFF", lw=1.4)
    ax.add_patch(bg)

    # Start Node
    start_c = Circle((50, 94.5), 2.2, color='#0F172A', ec='#0F172A', lw=1.6)
    ax.add_patch(start_c)
    ax.text(50, 97.6, "User Initiates Egress (Copy / Paste / Upload)", ha='center', va='center',
            fontsize=9.8, fontweight='bold', color='#0F172A')

    def draw_activity_step(y, title, desc, w=74, h=6.5, fill='#F8FAFC', stroke='#2563EB'):
        card = FancyBboxPatch((50 - w/2, y), w, h, boxstyle="round,pad=0.3", ec=stroke, fc=fill, lw=1.6)
        ax.add_patch(card)
        ax.text(50, y + h - 2.2, title, ha='center', va='center', fontsize=9.8, fontweight='bold', color='#0F172A')
        ax.text(50, y + 2.0, desc, ha='center', va='center', fontsize=8.6, color='#1E293B', fontweight='semibold')

    def draw_down_arrow(y_start, y_end):
        ax.annotate('', xy=(50, y_end), xytext=(50, y_start),
                    arrowprops=dict(arrowstyle="->", lw=1.8, color='#0F172A'))

    # Steps
    draw_down_arrow(92.3, 87)
    draw_activity_step(80.5, "1. Intercept Egress Traffic", "Endpoint Sensors capture clipboard text or multi-format document buffer", fill='#EFF6FF', stroke='#2563EB')

    draw_down_arrow(80.5, 75)
    draw_activity_step(68.5, "2. Parse Payload & Ingest Text", "PyMuPDF/docx/openpyxl extract plain text; EasyOCR runs on image buffers", fill='#F0FDFA', stroke='#0D9488')

    draw_down_arrow(68.5, 63)
    draw_activity_step(56.5, "3. Run Checksums & INT8 Classifier", "Luhn & MOD-97 verify card/IBAN numbers; Quantized ONNX classifies tier", fill='#FFFBEB', stroke='#D97706')

    draw_down_arrow(56.5, 51)
    draw_activity_step(44.5, "4. Compute Unified Risk Score (0 - 100)", "Aggregates entity sensitivity, domain whitelists, and user risk clearance tier", fill='#FAF5FF', stroke='#7C3AED')

    # Decision Diamond
    draw_down_arrow(44.5, 39)
    diamond = Polygon([(50, 39), (64, 34), (50, 29), (36, 34)], closed=True, ec='#B45309', fc='#FEF3C7', lw=2.0)
    ax.add_patch(diamond)
    ax.text(50, 34, "Evaluate Risk\nThreshold", ha='center', va='center', fontsize=9.2, fontweight='bold', color='#92400E')

    # 3 Branches
    # Left: ALLOW
    ax.annotate('', xy=(20, 23.5), xytext=(36, 34),
                arrowprops=dict(arrowstyle="->", lw=1.6, color='#16A34A', connectionstyle="angle,angleA=180,angleB=90,rad=3"))
    ax.text(23, 35.8, "[Score < 45]\nLow Risk", ha='center', va='center', fontsize=8.6, fontweight='bold', color='#16A34A')
    
    card_allow = FancyBboxPatch((7, 17.5), 26, 6, boxstyle="round,pad=0.2", ec='#16A34A', fc='#F0FDF4', lw=1.6)
    ax.add_patch(card_allow)
    ax.text(20, 21.0, "ALLOW TRANSFER", ha='center', va='center', fontsize=9.0, fontweight='bold', color='#166534')
    ax.text(20, 19.0, "Transmit Unmodified", ha='center', va='center', fontsize=8.0, color='#1E293B')

    # Center: MASK
    ax.annotate('', xy=(50, 23.5), xytext=(50, 29),
                arrowprops=dict(arrowstyle="->", lw=1.6, color='#D97706'))
    ax.text(51.5, 26.5, "[45 <= Score < 80]", ha='left', va='center', fontsize=8.6, fontweight='bold', color='#D97706')
    
    card_mask = FancyBboxPatch((37, 17.5), 26, 6, boxstyle="round,pad=0.2", ec='#D97706', fc='#FFFBEB', lw=1.6)
    ax.add_patch(card_mask)
    ax.text(50, 21.0, "MASK & TOKENIZE", ha='center', va='center', fontsize=9.0, fontweight='bold', color='#B45309')
    ax.text(50, 19.0, "HMAC Reverse-Offset", ha='center', va='center', fontsize=8.0, color='#1E293B')

    # Right: BLOCK
    ax.annotate('', xy=(80, 23.5), xytext=(64, 34),
                arrowprops=dict(arrowstyle="->", lw=1.6, color='#DC2626', connectionstyle="angle,angleA=0,angleB=90,rad=3"))
    ax.text(77, 35.8, "[Score >= 80]\nCritical Risk", ha='center', va='center', fontsize=8.6, fontweight='bold', color='#DC2626')
    
    card_block = FancyBboxPatch((67, 17.5), 26, 6, boxstyle="round,pad=0.2", ec='#DC2626', fc='#FEF2F2', lw=1.6)
    ax.add_patch(card_block)
    ax.text(80, 21.0, "BLOCK EXFILTRATION", ha='center', va='center', fontsize=9.0, fontweight='bold', color='#991B1B')
    ax.text(80, 19.0, "Drop & Alert SOC", ha='center', va='center', fontsize=8.0, color='#1E293B')

    # Converge to Step 5
    ax.annotate('', xy=(35, 12), xytext=(20, 17.5), arrowprops=dict(arrowstyle="->", lw=1.5, color='#334155', connectionstyle="angle,angleA=-90,angleB=180,rad=3"))
    ax.annotate('', xy=(50, 12), xytext=(50, 17.5), arrowprops=dict(arrowstyle="->", lw=1.5, color='#334155'))
    ax.annotate('', xy=(65, 12), xytext=(80, 17.5), arrowprops=dict(arrowstyle="->", lw=1.5, color='#334155', connectionstyle="angle,angleA=-90,angleB=0,rad=3"))

    draw_activity_step(5.5, "5. Commit Audit Trail & Publish Telemetry",
                       "Write immutable SHA-256 event to SQLite/PostgreSQL; push WebSocket alert to SOC Console",
                       w=76, h=6.5, fill='#F1F5F9', stroke='#475569')

    # End Node
    draw_down_arrow(5.5, 2.8)
    outer_c = Circle((50, 1.8), 1.2, color='#FFFFFF', ec='#0F172A', lw=1.6)
    inner_c = Circle((50, 1.8), 0.6, color='#0F172A', ec='#0F172A', lw=1.2)
    ax.add_patch(outer_c)
    ax.add_patch(inner_c)

    ax.set_title("Figure 4.2: SecureFlowAI UML Activity Workflow Diagram",
                 fontsize=12.0, fontweight='bold', color='#0F172A', pad=10)
    save_fig(fig, "fig4_2_uml_activity.png")
    plt.close()

# ==============================================================================
# 5. DFD LEVEL 1 (Fig 4.3)
# ==============================================================================
def create_crisp_dfd():
    fig, ax = plt.subplots(figsize=(8.0, 6.4), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    bg = FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=0.8", ec="#CBD5E1", fc="#F8FAFC", lw=1.4)
    ax.add_patch(bg)

    def draw_entity_dfd(x, y, w, h, id_str, name_str, col="#1E3A8A", bg_col="#EFF6FF"):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2", ec=col, fc=bg_col, lw=1.6)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 2.8, id_str, ha='center', va='center', fontsize=8.6, fontweight='bold', color=col)
        ax.text(x + w/2, y + h/2 - 1.0, name_str, ha='center', va='center', fontsize=9.2, fontweight='bold', color='#0F172A')

    def draw_process(x, y, w, h, p_num, p_title, p_sub, col="#0D9488", bg_col="#F0FDFA"):
        p_box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2", ec=col, fc=bg_col, lw=1.6)
        ax.add_patch(p_box)
        strip = FancyBboxPatch((x, y + h - 3.4), w, 3.4, boxstyle="round,pad=0.1", ec=col, fc=col, lw=1)
        ax.add_patch(strip)
        ax.text(x + w/2, y + h - 1.7, f"Process {p_num}", ha='center', va='center', fontsize=8.8, fontweight='bold', color='white')
        ax.text(x + w/2, y + h/2 + 0.3, p_title, ha='center', va='center', fontsize=9.2, fontweight='bold', color='#0F172A')
        ax.text(x + w/2, y + 2.3, p_sub, ha='center', va='center', fontsize=8.0, color='#1E293B', fontweight='semibold')

    def draw_datastore(x, y, w, h, ds_id, ds_name):
        ax.plot([x, x + w], [y + h, y + h], color='#6D28D9', lw=2.2)
        ax.plot([x, x + w], [y, y], color='#6D28D9', lw=2.2)
        ax.fill_between([x, x + w], [y, y], [y + h, y + h], color='#F5F3FF', alpha=0.95)
        ax.text(x + 2.5, y + h/2, ds_id, ha='left', va='center', fontsize=9.0, fontweight='bold', color='#6D28D9')
        ax.text(x + w/2 + 2, y + h/2, ds_name, ha='center', va='center', fontsize=8.8, fontweight='bold', color='#0F172A')

    # Row 1 (y=70): Ingestion & Inspection
    draw_entity_dfd(4, 70, 18, 16, "ENTITY E1", "Bank User /\nWorkstation", col="#1E3A8A", bg_col="#EFF6FF")
    draw_process(28, 70, 20, 16, "1.0", "Ingest & Extract", "Multi-format parsing/OCR", col="#0D9488", bg_col="#F0FDFA")
    draw_process(54, 70, 20, 16, "2.0", "Hybrid Inspect", "Checksums & INT8", col="#D97706", bg_col="#FFFBEB")
    draw_entity_dfd(80, 70, 17, 16, "ENTITY E2", "External Target /\nCloud / Web", col="#DC2626", bg_col="#FEF2F2")

    # Row 2 (y=40): Policy & Enforcement
    draw_datastore(4, 42, 18, 12, "D1", "Security Policies\n(Rule Limits)")
    draw_process(28, 40, 20, 16, "3.0", "Risk Score", "Threshold evaluation", col="#B45309", bg_col="#FEF3C7")
    draw_process(54, 40, 20, 16, "4.0", "Enforce & Mask", "Reverse-offset token", col="#2563EB", bg_col="#EFF6FF")
    draw_datastore(80, 42, 17, 12, "D2", "Token Vault\n(AES-GCM Keys)")

    # Row 3 (y=12): Audit & Forensics
    draw_datastore(28, 14, 20, 12, "D3", "Forensic Audit DB\n(SHA-256 Logs)")
    draw_process(54, 12, 20, 16, "5.0", "Audit & Alert", "SQLite & WebSocket", col="#475569", bg_col="#F1F5F9")
    draw_entity_dfd(80, 12, 17, 16, "ENTITY E3", "SOC Analyst /\nAuditor", col="#7C3AED", bg_col="#FAF5FF")

    # Row 1 Connectors
    ax.annotate('', xy=(28, 78), xytext=(22, 78), arrowprops=dict(arrowstyle="->", lw=1.6, color='#0F172A'))
    ax.text(25, 80.2, "Raw Data", ha='center', va='center', fontsize=8.2, fontweight='bold', color='#0F172A')

    ax.annotate('', xy=(54, 78), xytext=(48, 78), arrowprops=dict(arrowstyle="->", lw=1.6, color='#0F172A'))
    ax.text(51, 80.2, "Tokens", ha='center', va='center', fontsize=8.2, fontweight='bold', color='#0F172A')

    # P2.0 -> P3.0
    ax.annotate('', xy=(38, 56), xytext=(54, 70),
                arrowprops=dict(arrowstyle="->", lw=1.6, color='#0F172A', connectionstyle="arc3,rad=-0.1"))
    ax.text(49, 64, "PII Findings", ha='center', va='center', fontsize=8.6, fontweight='bold', color='#0F172A')

    # Row 2 Connectors
    ax.annotate('', xy=(28, 48), xytext=(22, 48), arrowprops=dict(arrowstyle="->", lw=1.5, color='#6D28D9', linestyle='--'))
    ax.text(25, 50.2, "Rules", ha='center', va='center', fontsize=8.2, color='#6D28D9', fontweight='bold')

    ax.annotate('', xy=(54, 48), xytext=(48, 48), arrowprops=dict(arrowstyle="->", lw=1.6, color='#0F172A'))
    ax.text(51, 50.2, "Verdict", ha='center', va='center', fontsize=8.2, fontweight='bold', color='#0F172A')

    ax.annotate('', xy=(80, 48), xytext=(74, 48), arrowprops=dict(arrowstyle="<->", lw=1.6, color='#6D28D9', linestyle='--'))
    ax.text(77, 50.2, "HMAC Keys", ha='center', va='center', fontsize=8.2, color='#6D28D9', fontweight='bold')

    # P4.0 -> E2
    ax.annotate('', xy=(80, 78), xytext=(64, 56),
                arrowprops=dict(arrowstyle="->", lw=1.6, color='#16A34A', connectionstyle="arc3,rad=0.15"))
    ax.text(73, 67, "Allowed / Masked", ha='center', va='center', fontsize=8.6, fontweight='bold', color='#16A34A')

    # P4.0 -> P5.0
    ax.annotate('', xy=(64, 28), xytext=(64, 40), arrowprops=dict(arrowstyle="->", lw=1.6, color='#0F172A'))
    ax.text(65.5, 34, "Audit Event", ha='left', va='center', fontsize=8.2, fontweight='bold', color='#0F172A')

    # Row 3 Connectors
    ax.annotate('', xy=(48, 20), xytext=(54, 20), arrowprops=dict(arrowstyle="->", lw=1.5, color='#475569', linestyle='--'))
    ax.text(51, 22.2, "Commit", ha='center', va='center', fontsize=8.2, color='#475569', fontweight='bold')

    ax.annotate('', xy=(80, 20), xytext=(74, 20), arrowprops=dict(arrowstyle="->", lw=1.6, color='#7C3AED'))
    ax.text(77, 22.2, "Live Alert", ha='center', va='center', fontsize=8.2, fontweight='bold', color='#7C3AED')

    ax.set_title("Figure 4.3: SecureFlowAI Level 1 Data Flow Diagram (DFD)",
                 fontsize=12.0, fontweight='bold', color='#0F172A', pad=10)
    save_fig(fig, "fig4_3_dfd_level1.png")
    plt.close()

# ==============================================================================
# 6. MODEL METRICS & BENCHMARKS (Fig 5.5)
# ==============================================================================
def create_crisp_metrics():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.0, 4.0), dpi=300)
    
    # Subplot 1: Latency Comparison
    models = ['PyTorch FP32\n(Baseline)', 'ONNX FP32\n(Standard)', 'SecureFlowAI\n(ONNX INT8)']
    latencies = [142.6, 48.2, 11.4]
    colors = ['#94A3B8', '#38BDF8', '#10B981']
    
    bars = ax1.bar(models, latencies, color=colors, edgecolor='#0F172A', linewidth=1.4, width=0.55)
    ax1.set_ylabel("Latency (ms) - Lower is Better", fontsize=9.5, fontweight='bold', color='#0F172A')
    ax1.set_title("A: CPU Inference Latency", fontsize=10.5, fontweight='bold', color='#0F172A', pad=8)
    ax1.grid(axis='y', linestyle='--', alpha=0.5, color='#CBD5E1')
    ax1.set_axisbelow(True)
    ax1.set_ylim(0, 165)
    ax1.tick_params(axis='x', labelsize=8.8)
    ax1.tick_params(axis='y', labelsize=9.0)
    
    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., h + 3, f"{h:.1f} ms",
                 ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#0F172A')
    
    ax1.text(2, 32, "12.5x Speedup", ha='center', va='bottom',
             fontsize=8.8, fontweight='bold', color='#065F46',
             bbox=dict(boxstyle="round,pad=0.25", fc="#D1FAE5", ec="#10B981", lw=1.2))

    # Subplot 2: Classification Precision, Recall, F1
    entities = ['Cards', 'IBAN', 'SWIFT', 'Tax ID', 'Overall']
    precision = [0.992, 0.985, 0.978, 0.981, 0.984]
    recall    = [0.988, 0.972, 0.965, 0.976, 0.975]
    f1        = [0.990, 0.978, 0.971, 0.978, 0.979]
    
    x = np.arange(len(entities))
    w = 0.25
    
    ax2.bar(x - w, precision, w, label='Precision', color='#1E3A8A', edgecolor='#0F172A', lw=1.2)
    ax2.bar(x, recall, w, label='Recall', color='#0D9488', edgecolor='#0F172A', lw=1.2)
    ax2.bar(x + w, f1, w, label='F1-Score', color='#F59E0B', edgecolor='#0F172A', lw=1.2)
    
    ax2.set_xticks(x)
    ax2.set_xticklabels(entities, fontsize=8.8, fontweight='bold', color='#1E293B')
    ax2.set_ylabel("Score (0.0 to 1.0)", fontsize=9.5, fontweight='bold', color='#0F172A')
    ax2.set_title("B: Entity Accuracy Scores", fontsize=10.5, fontweight='bold', color='#0F172A', pad=8)
    ax2.set_ylim(0.85, 1.02)
    ax2.grid(axis='y', linestyle='--', alpha=0.5, color='#CBD5E1')
    ax2.set_axisbelow(True)
    ax2.legend(loc='lower left', framealpha=0.9, fontsize=8.2)
    ax2.tick_params(axis='y', labelsize=9.0)

    save_fig(fig, "fig5_5_metrics.png")
    plt.close()

if __name__ == "__main__":
    create_crisp_gantt()
    create_crisp_architecture()
    create_crisp_er()
    create_crisp_uml()
    create_crisp_dfd()
    create_crisp_metrics()
    print("ALL CRISP DIAGRAMS SUCCESSFULLY GENERATED!")

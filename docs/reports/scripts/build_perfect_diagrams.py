import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon
import numpy as np

# Output directories
os.makedirs("Report_Images_Ready_To_Insert", exist_ok=True)
os.makedirs("report_assets", exist_ok=True)
os.makedirs("docs/reports/assets", exist_ok=True)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

def save_all_targets(fig, base_name, descriptive_name):
    targets = [
        f"Report_Images_Ready_To_Insert/{descriptive_name}",
        f"report_assets/{base_name}",
        f"docs/reports/assets/{base_name}"
    ]
    for t in targets:
        fig.savefig(t, dpi=300, bbox_inches='tight', pad_inches=0.15)
    print(f"Generated: {descriptive_name}")

# ==============================================================================
# 1. GANTT CHART (Figure 1.1)
# ==============================================================================
def generate_perfect_gantt():
    fig, ax = plt.subplots(figsize=(9.2, 5.0), dpi=300)
    
    tasks = [
        "Phase 1: Problem Definition & Survey",
        "Phase 2: Banking DLP Dataset Assembly",
        "Phase 3: Hybrid AI Model & Quantization",
        "Phase 4: Algorithmic Checksum Verification",
        "Phase 5: Ingestion Gateway & Multi-OCR",
        "Phase 6: Reverse Masking & AES-256 Vault",
        "Phase 7: SOC Console & Copilot Dashboard",
        "Phase 8: SLA Testing & Final Viva Report"
    ]
    
    start_weeks = [1, 3, 5, 7, 9, 11, 13, 15]
    durations   = [3, 3, 3, 3, 3, 3, 3, 2]
    
    y_pos = np.arange(len(tasks))
    bar_colors = [
        '#1E3A8A', '#2563EB', '#0D9488', '#059669',
        '#D97706', '#EA580C', '#7C3AED', '#334155'
    ]
    
    for i in range(len(tasks)):
        ax.barh(y_pos[i], durations[i], left=start_weeks[i], height=0.58,
                color=bar_colors[i], edgecolor='#0F172A', linewidth=1.4, zorder=3)
        ax.text(start_weeks[i] + durations[i] / 2, y_pos[i], f"{durations[i]} Weeks",
                ha='center', va='center', color='white', fontweight='bold', fontsize=10.0, zorder=4)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(tasks, fontsize=10.5, fontweight='bold', color='#0F172A')
    ax.invert_yaxis()
    
    ax.set_xlim(0.5, 17.5)
    ax.set_xticks(range(1, 18))
    ax.set_xticklabels([f"W{w}" for w in range(1, 18)], fontsize=9.5, fontweight='bold', color='#1E293B')
    ax.set_xlabel("Academic Project Schedule (Weeks 1 to 16)", fontsize=11.0, fontweight='bold', labelpad=10, color='#0F172A')
    
    ax.grid(axis='x', linestyle='--', alpha=0.6, color='#94A3B8', zorder=1)
    ax.set_axisbelow(True)
    
    ax.axvspan(1, 4.5, color='#F8FAFC', alpha=0.9, zorder=0)
    ax.axvspan(4.5, 10.5, color='#F1F5F9', alpha=0.9, zorder=0)
    ax.axvspan(10.5, 17, color='#F8FAFC', alpha=0.9, zorder=0)
    
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_color('#CBD5E1')
        ax.spines[spine].set_linewidth(1.3)
        
    ax.set_title("Figure 1.1: SecureFlowAI Project Milestone Gantt Chart",
                 fontsize=12.5, fontweight='bold', color='#0F172A', pad=14)
    save_all_targets(fig, "fig1_1_gantt.png", "Figure_1.1_Project_Gantt_Chart.png")
    plt.close()

# ==============================================================================
# 2. SYSTEM ARCHITECTURE (Figure 3.1)
# ==============================================================================
def generate_perfect_architecture():
    fig, ax = plt.subplots(figsize=(9.2, 11.2), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 112)
    
    # Outer Card
    bg = FancyBboxPatch((1, 1), 98, 110, boxstyle="round,pad=0.8", ec="#94A3B8", fc="#FFFFFF", lw=1.6)
    ax.add_patch(bg)
    
    # Title Banner
    title_box = FancyBboxPatch((3, 104), 94, 5.8, boxstyle="round,pad=0.4", ec="#1E3A8A", fc="#1E3A8A", lw=1)
    ax.add_patch(title_box)
    ax.text(50, 106.9, "SECUREFLOWAI: MULTI-TIER BANKING DLP ARCHITECTURE",
            ha='center', va='center', color='white', fontsize=12.0, fontweight='bold')

    def draw_layer_card(y, h, title, subtitle, items, border_c, header_c, bg_c):
        card = FancyBboxPatch((3, y), 94, h, boxstyle="round,pad=0.4", ec=border_c, fc=bg_c, lw=1.6)
        ax.add_patch(card)
        
        # Header strip
        strip = FancyBboxPatch((3, y + h - 4.5), 94, 4.5, boxstyle="round,pad=0.1", ec=border_c, fc=header_c, lw=1)
        ax.add_patch(strip)
        ax.text(50, y + h - 2.2, title, ha='center', va='center', color='white', fontsize=10.5, fontweight='bold')
        ax.text(5, y + h - 6.4, subtitle, ha='left', va='center', color='#1E293B', fontsize=8.8, fontstyle='italic', fontweight='bold')
        
        n = len(items)
        sub_w = (94 - (n + 1) * 2) / n
        sub_h = h - 9.6
        for i, (b_title, b_desc) in enumerate(items):
            bx = 3 + 2 + i * (sub_w + 2)
            by = y + 2.0
            sub_card = FancyBboxPatch((bx, by), sub_w, sub_h, boxstyle="round,pad=0.2", ec="#94A3B8", fc="#FFFFFF", lw=1.3)
            ax.add_patch(sub_card)
            # Title header box inside subcard
            t_box = FancyBboxPatch((bx, by + sub_h - 3.2), sub_w, 3.2, boxstyle="round,pad=0.1", ec=border_c, fc=bg_c, lw=1)
            ax.add_patch(t_box)
            ax.text(bx + sub_w/2, by + sub_h - 1.6, b_title, ha='center', va='center', color='#0F172A', fontsize=9.2, fontweight='bold')
            # Description text cleanly below title box
            ax.text(bx + sub_w/2, by + (sub_h - 3.2)/2, b_desc, ha='center', va='center', color='#334155', fontsize=8.2, linespacing=1.3)

    # Layer 1 (y: 81 to 102, h: 21)
    draw_layer_card(
        81, 21,
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
    ax.annotate('', xy=(50, 76.5), xytext=(50, 81),
                arrowprops=dict(facecolor='#1E3A8A', edgecolor='#1E3A8A', width=2.2, headwidth=7, headlength=7))
    ax.text(51.5, 78.8, "Encrypted Local JSON / Binary Stream via mTLS", color='#1E3A8A', fontsize=8.8, fontweight='bold')

    # Layer 2 (y: 54.5 to 75.5, h: 21)
    draw_layer_card(
        54.5, 21,
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
    ax.annotate('', xy=(50, 50), xytext=(50, 54.5),
                arrowprops=dict(facecolor='#0D9488', edgecolor='#0D9488', width=2.2, headwidth=7, headlength=7))
    ax.text(51.5, 52.3, "Normalized Text Streams & Extracted Image Tokens", color='#0D9488', fontsize=8.8, fontweight='bold')

    # Layer 3 (y: 28 to 49, h: 21)
    draw_layer_card(
        28, 21,
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
    ax.annotate('', xy=(50, 23.5), xytext=(50, 28),
                arrowprops=dict(facecolor='#D97706', edgecolor='#D97706', width=2.2, headwidth=7, headlength=7))
    ax.text(51.5, 25.8, "Entity Spans, Offsets & Computed Risk Score (0 - 100)", color='#D97706', fontsize=8.8, fontweight='bold')

    # Layer 4 & 5 (y: 2.5 to 22.5, h: 20)
    card_bot = FancyBboxPatch((3, 2.5), 94, 20.0, boxstyle="round,pad=0.4", ec="#7C3AED", fc="#FAF5FF", lw=1.6)
    ax.add_patch(card_bot)
    strip_bot = FancyBboxPatch((3, 18.0), 94, 4.5, boxstyle="round,pad=0.1", ec="#7C3AED", fc="#7C3AED", lw=1)
    ax.add_patch(strip_bot)
    ax.text(50, 20.2, "LAYER 4 & 5: ENFORCEMENT, CRYPTOGRAPHY & SOC GOVERNANCE",
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
        by = 3.5
        sub_card = FancyBboxPatch((bx, by), b_w, b_h, boxstyle="round,pad=0.2", ec="#94A3B8", fc="#FFFFFF", lw=1.3)
        ax.add_patch(sub_card)
        t_box = FancyBboxPatch((bx, by + b_h - 3.2), b_w, 3.2, boxstyle="round,pad=0.1", ec="#7C3AED", fc="#FAF5FF", lw=1)
        ax.add_patch(t_box)
        ax.text(bx + b_w/2, by + b_h - 1.6, b_title, ha='center', va='center', color='#0F172A', fontsize=9.0, fontweight='bold')
        ax.text(bx + b_w/2, by + (b_h - 3.2)/2, b_desc, ha='center', va='center', color='#334155', fontsize=8.0, linespacing=1.3)

    save_all_targets(fig, "fig3_1_architecture.png", "Figure_3.1_System_Architecture_Diagram.png")
    plt.close()

# ==============================================================================
# 3. ENTITY RELATIONSHIP DIAGRAM (Figure 4.1)
# ==============================================================================
def generate_perfect_er():
    fig, ax = plt.subplots(figsize=(9.2, 8.4), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    
    bg = FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=0.8", ec="#CBD5E1", fc="#F8FAFC", lw=1.4)
    ax.add_patch(bg)

    def draw_table_card(x, y, w, h, title, fields, color="#1E3A8A"):
        hdr = FancyBboxPatch((x, y + h - 5.0), w, 5.0, boxstyle="round,pad=0.1", ec=color, fc=color, lw=1.6)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - 2.5, title, ha='center', va='center', color='white', fontsize=10.5, fontweight='bold')
        
        body = FancyBboxPatch((x, y), w, h - 5.0, boxstyle="round,pad=0.1", ec=color, fc='#FFFFFF', lw=1.6)
        ax.add_patch(body)
        
        for idx, (f_name, f_type, is_pk, is_fk) in enumerate(fields):
            fy = y + h - 7.8 - idx * 2.8
            prefix = "[PK] " if is_pk else ("[FK] " if is_fk else " •  ")
            f_col = "#DC2626" if is_pk else ("#D97706" if is_fk else "#0F172A")
            ax.text(x + 2, fy, f"{prefix}{f_name}", ha='left', va='center', color=f_col,
                    fontsize=9.0, fontweight='bold' if (is_pk or is_fk) else 'bold')
            ax.text(x + w - 2, fy, f_type, ha='right', va='center', color="#475569", fontsize=8.2, fontfamily='monospace', fontweight='semibold')

    # Top Row: BANK_USER (Left) and SECURITY_POLICY (Right) - y: 70 to 94, h: 24
    draw_table_card(5, 70, 42, 24, "BANK_USER", [
        ("user_id", "UUID", True, False),
        ("employee_email", "VARCHAR(128)", False, False),
        ("department_name", "VARCHAR(64)", False, False),
        ("assigned_role", "VARCHAR(32)", False, False),
        ("risk_tier", "INTEGER", False, False),
        ("created_at", "TIMESTAMP", False, False)
    ], "#1E3A8A")

    draw_table_card(53, 70, 42, 24, "SECURITY_POLICY", [
        ("policy_id", "UUID", True, False),
        ("policy_code", "VARCHAR(64)", False, False),
        ("mask_threshold", "INTEGER", False, False),
        ("block_threshold", "INTEGER", False, False),
        ("whitelisted_domains", "JSONB", False, False),
        ("fail_mode", "VARCHAR(16)", False, False)
    ], "#0D9488")

    # Middle Row: DLP_AUDIT_LOG (Center, 2 COLUMNS OF FIELDS) - y: 35 to 58, h: 23
    dlp_x, dlp_y, dlp_w, dlp_h = 10, 35, 80, 23
    dlp_hdr = FancyBboxPatch((dlp_x, dlp_y + dlp_h - 4.8), dlp_w, 4.8, boxstyle="round,pad=0.1", ec="#B45309", fc="#B45309", lw=1.6)
    ax.add_patch(dlp_hdr)
    ax.text(dlp_x + dlp_w/2, dlp_y + dlp_h - 2.4, "DLP_AUDIT_LOG (Central Forensic Record)", ha='center', va='center', color='white', fontsize=10.5, fontweight='bold')
    
    dlp_body = FancyBboxPatch((dlp_x, dlp_y), dlp_w, dlp_h - 4.8, boxstyle="round,pad=0.1", ec="#B45309", fc='#FFFFFF', lw=1.6)
    ax.add_patch(dlp_body)

    col1_fields = [
        ("incident_id", "UUID", True, False),
        ("user_id", "UUID", False, True),
        ("policy_id", "UUID", False, True),
        ("timestamp", "TIMESTAMP", False, False),
        ("source_action", "VARCHAR(32)", False, False)
    ]
    col2_fields = [
        ("destination", "VARCHAR(255)", False, False),
        ("classification", "VARCHAR(32)", False, False),
        ("risk_score", "INTEGER", False, False),
        ("enforcement", "VARCHAR(16)", False, False),
        ("payload_sha256", "CHAR(64)", False, False)
    ]
    for idx, (f_name, f_type, is_pk, is_fk) in enumerate(col1_fields):
        fy = dlp_y + dlp_h - 7.8 - idx * 2.8
        prefix = "[PK] " if is_pk else ("[FK] " if is_fk else " •  ")
        f_col = "#DC2626" if is_pk else ("#D97706" if is_fk else "#0F172A")
        ax.text(dlp_x + 3, fy, f"{prefix}{f_name}", ha='left', va='center', color=f_col, fontsize=9.0, fontweight='bold')
        ax.text(dlp_x + 38, fy, f_type, ha='right', va='center', color="#475569", fontsize=8.2, fontfamily='monospace', fontweight='semibold')

    # Divider line
    ax.plot([dlp_x + 40, dlp_x + 40], [dlp_y + 1, dlp_y + dlp_h - 5], color='#E2E8F0', lw=1.2)

    for idx, (f_name, f_type, is_pk, is_fk) in enumerate(col2_fields):
        fy = dlp_y + dlp_h - 7.8 - idx * 2.8
        prefix = " •  "
        ax.text(dlp_x + 43, fy, f"{prefix}{f_name}", ha='left', va='center', color="#0F172A", fontsize=9.0, fontweight='bold')
        ax.text(dlp_x + dlp_w - 3, fy, f_type, ha='right', va='center', color="#475569", fontsize=8.2, fontfamily='monospace', fontweight='semibold')

    # Bottom Row: TOKEN_VAULT (Left) and INCIDENT_OVERRIDE (Right) - y: 4 to 25, h: 21
    draw_table_card(5, 4, 42, 21, "TOKEN_VAULT", [
        ("token_id", "VARCHAR(64)", True, False),
        ("incident_id", "UUID", False, True),
        ("encrypted_pii", "BYTEA", False, False),
        ("iv_nonce", "BYTEA", False, False),
        ("auth_tag", "BYTEA", False, False)
    ], "#6D28D9")

    draw_table_card(53, 4, 42, 21, "INCIDENT_OVERRIDE", [
        ("override_id", "UUID", True, False),
        ("incident_id", "UUID", False, True),
        ("analyst_id", "UUID", False, True),
        ("justification", "TEXT", False, False),
        ("authorized_at", "TIMESTAMP", False, False)
    ], "#475569")

    # Connectors with generous breathing room
    # BANK_USER -> DLP_AUDIT_LOG
    ax.annotate('', xy=(30, 58), xytext=(26, 70),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#1E3A8A'))
    ax.text(22, 64, "1 : N (Triggers)", color='#1E3A8A', fontsize=9.2, fontweight='bold')

    # SECURITY_POLICY -> DLP_AUDIT_LOG
    ax.annotate('', xy=(70, 58), xytext=(74, 70),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#0D9488'))
    ax.text(75, 64, "1 : N (Governs)", color='#0D9488', fontsize=9.2, fontweight='bold')

    # DLP_AUDIT_LOG -> TOKEN_VAULT
    ax.annotate('', xy=(26, 25), xytext=(30, 35),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#6D28D9'))
    ax.text(18, 30, "1 : N (Vaults)", color='#6D28D9', fontsize=9.2, fontweight='bold')

    # DLP_AUDIT_LOG -> INCIDENT_OVERRIDE
    ax.annotate('', xy=(74, 25), xytext=(70, 35),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#475569'))
    ax.text(73, 30, "1 : 1 (Overrides)", color='#475569', fontsize=9.2, fontweight='bold')

    ax.set_title("Figure 4.1: SecureFlowAI Relational Schema & Entity-Relationship Model",
                 fontsize=12.5, fontweight='bold', color='#0F172A', pad=12)
    save_all_targets(fig, "fig4_1_er_diagram.png", "Figure_4.1_Entity_Relationship_ER_Diagram.png")
    plt.close()

# ==============================================================================
# 4. UML ACTIVITY DIAGRAM (Figure 4.2)
# ==============================================================================
def generate_perfect_uml():
    fig, ax = plt.subplots(figsize=(8.2, 11.2), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 114)

    bg = FancyBboxPatch((1, 1), 98, 112, boxstyle="round,pad=0.8", ec="#CBD5E1", fc="#FFFFFF", lw=1.4)
    ax.add_patch(bg)

    # Start Node
    start_c = Circle((50, 107), 2.0, color='#0F172A', ec='#0F172A', lw=1.6)
    ax.add_patch(start_c)
    ax.text(50, 110.2, "User Initiates Egress (Copy / Paste / Upload)", ha='center', va='center',
            fontsize=10.0, fontweight='bold', color='#0F172A')

    def draw_step_card(y, title, desc, w=76, h=8.5, fill='#F8FAFC', stroke='#2563EB'):
        card = FancyBboxPatch((50 - w/2, y), w, h, boxstyle="round,pad=0.3", ec=stroke, fc=fill, lw=1.6)
        ax.add_patch(card)
        ax.text(50, y + h - 2.6, title, ha='center', va='center', fontsize=10.2, fontweight='bold', color='#0F172A')
        ax.text(50, y + 3.0, desc, ha='center', va='center', fontsize=8.6, color='#1E293B')

    def draw_arrow(y_start, y_end):
        ax.annotate('', xy=(50, y_end), xytext=(50, y_start),
                    arrowprops=dict(arrowstyle="->", lw=1.8, color='#0F172A'))

    # Step 1 (y: 92 to 100.5, h: 8.5)
    draw_arrow(105, 100.5)
    draw_step_card(92, "1. Intercept Egress Traffic", "Endpoint Sensors capture clipboard text or multi-format document buffer", fill='#EFF6FF', stroke='#2563EB')

    # Step 2 (y: 77 to 85.5, h: 8.5)
    draw_arrow(92, 85.5)
    draw_step_card(77, "2. Parse Payload & Ingest Text", "PyMuPDF/docx/openpyxl extract plain text; EasyOCR runs on image buffers", fill='#F0FDFA', stroke='#0D9488')

    # Step 3 (y: 62 to 70.5, h: 8.5)
    draw_arrow(77, 70.5)
    draw_step_card(62, "3. Run Checksums & INT8 Classifier", "Luhn & MOD-97 verify card/IBAN numbers; Quantized ONNX classifies tier", fill='#FFFBEB', stroke='#D97706')

    # Step 4 (y: 47 to 55.5, h: 8.5)
    draw_arrow(62, 55.5)
    draw_step_card(47, "4. Compute Unified Risk Score (0 - 100)", "Aggregates entity sensitivity, domain whitelists, and user risk clearance tier", fill='#FAF5FF', stroke='#7C3AED')

    # Decision Diamond (y: 33 to 42)
    draw_arrow(47, 42)
    diamond = Polygon([(50, 42), (65, 37.5), (50, 33), (35, 37.5)], closed=True, ec='#B45309', fc='#FEF3C7', lw=2.0)
    ax.add_patch(diamond)
    ax.text(50, 37.5, "Evaluate Risk\nThreshold", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#92400E')

    # 3 Branches
    # Left: ALLOW (y: 19 to 26.5, h: 7.5)
    ax.annotate('', xy=(20, 26.5), xytext=(35, 37.5),
                arrowprops=dict(arrowstyle="->", lw=1.6, color='#16A34A', connectionstyle="angle,angleA=180,angleB=90,rad=3"))
    ax.text(23, 39.5, "[Score < 45]\nLow Risk", ha='center', va='center', fontsize=8.6, fontweight='bold', color='#16A34A')
    
    card_allow = FancyBboxPatch((7, 19), 26, 7.5, boxstyle="round,pad=0.2", ec='#16A34A', fc='#F0FDF4', lw=1.6)
    ax.add_patch(card_allow)
    ax.text(20, 23.5, "ALLOW TRANSFER", ha='center', va='center', fontsize=9.2, fontweight='bold', color='#166534')
    ax.text(20, 21.0, "Transmit Unmodified", ha='center', va='center', fontsize=8.2, color='#1E293B')

    # Center: MASK
    ax.annotate('', xy=(50, 26.5), xytext=(50, 33),
                arrowprops=dict(arrowstyle="->", lw=1.6, color='#D97706'))
    ax.text(51.5, 29.8, "[45 <= Score < 80]", ha='left', va='center', fontsize=8.6, fontweight='bold', color='#D97706')
    
    card_mask = FancyBboxPatch((37, 19), 26, 7.5, boxstyle="round,pad=0.2", ec='#D97706', fc='#FFFBEB', lw=1.6)
    ax.add_patch(card_mask)
    ax.text(50, 23.5, "MASK & TOKENIZE", ha='center', va='center', fontsize=9.2, fontweight='bold', color='#B45309')
    ax.text(50, 21.0, "HMAC Reverse-Offset", ha='center', va='center', fontsize=8.2, color='#1E293B')

    # Right: BLOCK
    ax.annotate('', xy=(80, 26.5), xytext=(65, 37.5),
                arrowprops=dict(arrowstyle="->", lw=1.6, color='#DC2626', connectionstyle="angle,angleA=0,angleB=90,rad=3"))
    ax.text(77, 39.5, "[Score >= 80]\nCritical Risk", ha='center', va='center', fontsize=8.6, fontweight='bold', color='#DC2626')
    
    card_block = FancyBboxPatch((67, 19), 26, 7.5, boxstyle="round,pad=0.2", ec='#DC2626', fc='#FEF2F2', lw=1.6)
    ax.add_patch(card_block)
    ax.text(80, 23.5, "BLOCK EXFILTRATION", ha='center', va='center', fontsize=9.2, fontweight='bold', color='#991B1B')
    ax.text(80, 21.0, "Drop & Alert SOC", ha='center', va='center', fontsize=8.2, color='#1E293B')

    # Converge to Step 5 (y: 6.5 to 16.0, h: 9.5)
    ax.annotate('', xy=(35, 16.0), xytext=(20, 19), arrowprops=dict(arrowstyle="->", lw=1.5, color='#334155', connectionstyle="angle,angleA=-90,angleB=180,rad=3"))
    ax.annotate('', xy=(50, 16.0), xytext=(50, 19), arrowprops=dict(arrowstyle="->", lw=1.5, color='#334155'))
    ax.annotate('', xy=(65, 16.0), xytext=(80, 19), arrowprops=dict(arrowstyle="->", lw=1.5, color='#334155', connectionstyle="angle,angleA=-90,angleB=0,rad=3"))

    card_s5 = FancyBboxPatch((50 - 42, 6.5), 84, 9.5, boxstyle="round,pad=0.3", ec='#475569', fc='#F1F5F9', lw=1.6)
    ax.add_patch(card_s5)
    ax.text(50, 6.5 + 9.5 - 2.8, "5. Commit Audit Trail & Publish Telemetry", ha='center', va='center', fontsize=10.2, fontweight='bold', color='#0F172A')
    ax.text(50, 6.5 + 4.0, "Write immutable SHA-256 event to SQLite/PostgreSQL;\npush WebSocket alert to SOC Console", ha='center', va='center', fontsize=8.6, color='#1E293B', linespacing=1.25)

    # End Node
    draw_arrow(6.5, 3.2)
    outer_c = Circle((50, 2.0), 1.2, color='#FFFFFF', ec='#0F172A', lw=1.6)
    inner_c = Circle((50, 2.0), 0.6, color='#0F172A', ec='#0F172A', lw=1.2)
    ax.add_patch(outer_c)
    ax.add_patch(inner_c)

    ax.set_title("Figure 4.2: SecureFlowAI UML Activity Workflow Diagram",
                 fontsize=12.5, fontweight='bold', color='#0F172A', pad=12)
    save_all_targets(fig, "fig4_2_uml_activity.png", "Figure_4.2_UML_Activity_Workflow_Diagram.png")
    plt.close()

# ==============================================================================
# 5. DFD LEVEL 1 (Figure 4.3)
# ==============================================================================
def generate_perfect_dfd():
    fig, ax = plt.subplots(figsize=(9.8, 7.2), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 106)
    ax.set_ylim(0, 100)

    bg = FancyBboxPatch((1, 1), 104, 98, boxstyle="round,pad=0.8", ec="#CBD5E1", fc="#F8FAFC", lw=1.4)
    ax.add_patch(bg)

    def draw_entity(x, y, w, h, id_str, name_str, col="#1E3A8A", bg_col="#EFF6FF"):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2", ec=col, fc=bg_col, lw=1.6)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 2.8, id_str, ha='center', va='center', fontsize=8.8, fontweight='bold', color=col)
        ax.text(x + w/2, y + h/2 - 1.0, name_str, ha='center', va='center', fontsize=9.2, fontweight='bold', color='#0F172A')

    def draw_proc(x, y, w, h, p_num, p_title, p_sub, col="#0D9488", bg_col="#F0FDFA"):
        p_box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2", ec=col, fc=bg_col, lw=1.6)
        ax.add_patch(p_box)
        strip = FancyBboxPatch((x, y + h - 3.6), w, 3.6, boxstyle="round,pad=0.1", ec=col, fc=col, lw=1)
        ax.add_patch(strip)
        ax.text(x + w/2, y + h - 1.8, f"Process {p_num}", ha='center', va='center', fontsize=8.8, fontweight='bold', color='white')
        ax.text(x + w/2, y + h/2 + 0.5, p_title, ha='center', va='center', fontsize=9.2, fontweight='bold', color='#0F172A')
        ax.text(x + w/2, y + 2.5, p_sub, ha='center', va='center', fontsize=8.0, color='#1E293B')

    def draw_store(x, y, w, h, ds_id, ds_name):
        ax.plot([x, x + w], [y + h, y + h], color='#6D28D9', lw=2.2)
        ax.plot([x, x + w], [y, y], color='#6D28D9', lw=2.2)
        ax.fill_between([x, x + w], [y, y], [y + h, y + h], color='#F5F3FF', alpha=0.95)
        ax.text(x + w/2, y + h - 3.2, f"[{ds_id}]", ha='center', va='center', fontsize=9.2, fontweight='bold', color='#6D28D9')
        ax.text(x + w/2, y + 3.8, ds_name, ha='center', va='center', fontsize=8.4, fontweight='bold', color='#0F172A')

    # Row 1 (y: 70 to 86)
    # E1 (x: 4 to 22, w=18)
    # Gap (x: 22 to 32, w=10)
    # P1.0 (x: 32 to 52, w=20)
    # Gap (x: 52 to 62, w=10)
    # P2.0 (x: 62 to 82, w=20)
    # Gap (x: 82 to 88, w=6)
    # E2 (x: 88 to 104, w=16)
    draw_entity(4, 70, 18, 16, "ENTITY E1", "Bank User /\nWorkstation", col="#1E3A8A", bg_col="#EFF6FF")
    draw_proc(32, 70, 20, 16, "1.0", "Ingest & Extract", "Multi-format/OCR", col="#0D9488", bg_col="#F0FDFA")
    draw_proc(62, 70, 20, 16, "2.0", "Hybrid Inspect", "Checksums & INT8", col="#D97706", bg_col="#FFFBEB")
    draw_entity(88, 70, 16, 16, "ENTITY E2", "External Target /\nCloud / Web", col="#DC2626", bg_col="#FEF2F2")

    # Connectors Row 1 (Clean spacing, label strictly above arrow)
    ax.annotate('', xy=(32, 78), xytext=(22, 78), arrowprops=dict(arrowstyle="->", lw=1.6, color='#0F172A'))
    ax.text(27, 80.5, "Raw Data", ha='center', va='bottom', fontsize=8.2, fontweight='bold', color='#0F172A')

    ax.annotate('', xy=(62, 78), xytext=(52, 78), arrowprops=dict(arrowstyle="->", lw=1.6, color='#0F172A'))
    ax.text(57, 80.5, "Tokens", ha='center', va='bottom', fontsize=8.2, fontweight='bold', color='#0F172A')

    # Row 2 (y: 40 to 56)
    # D1 (x: 4 to 22, w=18)
    # P3.0 (x: 32 to 52, w=20)
    # P4.0 (x: 62 to 82, w=20)
    # D2 (x: 88 to 104, w=16)
    draw_store(4, 42, 18, 12, "D1", "Security Rules\n(Policy Limits)")
    draw_proc(32, 40, 20, 16, "3.0", "Risk Score", "Threshold match", col="#B45309", bg_col="#FEF3C7")
    draw_proc(62, 40, 20, 16, "4.0", "Enforce & Mask", "Reverse-offset", col="#2563EB", bg_col="#EFF6FF")
    draw_store(88, 42, 16, 12, "D2", "Token Vault\n(AES-GCM Keys)")

    # P2.0 -> P3.0 (Diagonal downward)
    ax.annotate('', xy=(42, 56), xytext=(62, 70),
                arrowprops=dict(arrowstyle="->", lw=1.6, color='#0F172A', connectionstyle="arc3,rad=-0.1"))
    ax.text(55, 63.5, "PII Findings", ha='center', va='center', fontsize=8.6, fontweight='bold', color='#0F172A')

    # D1 -> P3.0
    ax.annotate('', xy=(32, 48), xytext=(22, 48), arrowprops=dict(arrowstyle="->", lw=1.5, color='#6D28D9', linestyle='--'))
    ax.text(27, 50.5, "Rules", ha='center', va='bottom', fontsize=8.2, color='#6D28D9', fontweight='bold')

    # P3.0 -> P4.0
    ax.annotate('', xy=(62, 48), xytext=(52, 48), arrowprops=dict(arrowstyle="->", lw=1.6, color='#0F172A'))
    ax.text(57, 50.5, "Verdict", ha='center', va='bottom', fontsize=8.2, fontweight='bold', color='#0F172A')

    # P4.0 <-> D2
    ax.annotate('', xy=(88, 48), xytext=(82, 48), arrowprops=dict(arrowstyle="<->", lw=1.6, color='#6D28D9', linestyle='--'))
    ax.text(85, 50.5, "Keys", ha='center', va='bottom', fontsize=8.0, color='#6D28D9', fontweight='bold')

    # P4.0 -> E2
    ax.annotate('', xy=(88, 76), xytext=(78, 56),
                arrowprops=dict(arrowstyle="->", lw=1.6, color='#16A34A', connectionstyle="arc3,rad=0.15"))
    ax.text(87, 65, "Allowed / Masked", ha='center', va='center', fontsize=8.6, fontweight='bold', color='#16A34A')

    # Row 3 (y: 12 to 28)
    # D3 (x: 32 to 52, w=20)
    # P5.0 (x: 62 to 82, w=20)
    # E3 (x: 88 to 104, w=16)
    draw_store(32, 14, 20, 12, "D3", "Forensic Audit DB\n(SHA-256 Logs)")
    draw_proc(62, 12, 20, 16, "5.0", "Audit & Alert", "SQLite & WebSocket", col="#475569", bg_col="#F1F5F9")
    draw_entity(88, 12, 16, 16, "ENTITY E3", "SOC Analyst /\nAuditor", col="#7C3AED", bg_col="#FAF5FF")

    # P4.0 -> P5.0 (Vertical downward)
    ax.annotate('', xy=(72, 28), xytext=(72, 40), arrowprops=dict(arrowstyle="->", lw=1.6, color='#0F172A'))
    ax.text(73.5, 34, "Audit Event", ha='left', va='center', fontsize=8.2, fontweight='bold', color='#0F172A')

    # P5.0 -> D3
    ax.annotate('', xy=(52, 20), xytext=(62, 20), arrowprops=dict(arrowstyle="->", lw=1.5, color='#475569', linestyle='--'))
    ax.text(57, 22.5, "Commit", ha='center', va='bottom', fontsize=8.2, color='#475569', fontweight='bold')

    # P5.0 -> E3
    ax.annotate('', xy=(88, 20), xytext=(82, 20), arrowprops=dict(arrowstyle="->", lw=1.6, color='#7C3AED'))
    ax.text(85, 22.5, "Alert", ha='center', va='bottom', fontsize=8.2, fontweight='bold', color='#7C3AED')

    ax.set_title("Figure 4.3: SecureFlowAI Level 1 Data Flow Diagram (DFD)",
                 fontsize=12.5, fontweight='bold', color='#0F172A', pad=12)
    save_all_targets(fig, "fig4_3_dfd_level1.png", "Figure_4.3_Data_Flow_Diagram_DFD_Level_1.png")
    plt.close()

# ==============================================================================
# 6. METRICS & BENCHMARKS (Figure 5.5)
# ==============================================================================
def generate_perfect_metrics():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 4.8), dpi=300)
    fig.subplots_adjust(wspace=0.36, left=0.10, right=0.96, top=0.88, bottom=0.18)
    
    # Subplot 1: Latency Comparison
    models = ['PyTorch FP32\n(Baseline)', 'ONNX FP32\n(Standard)', 'SecureFlowAI\n(ONNX INT8)']
    latencies = [142.6, 48.2, 11.4]
    colors = ['#94A3B8', '#38BDF8', '#10B981']
    
    bars = ax1.bar(models, latencies, color=colors, edgecolor='#0F172A', linewidth=1.4, width=0.55)
    ax1.set_ylabel("Inference Latency (Milliseconds - Lower is Better)", fontsize=9.8, fontweight='bold', color='#0F172A', labelpad=8)
    ax1.set_title("A: Local CPU Inference Latency", fontsize=11.0, fontweight='bold', color='#0F172A', pad=10)
    ax1.grid(axis='y', linestyle='--', alpha=0.5, color='#CBD5E1')
    ax1.set_axisbelow(True)
    ax1.set_ylim(0, 168)
    ax1.tick_params(axis='x', labelsize=9.0)
    ax1.tick_params(axis='y', labelsize=9.2)
    
    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., h + 3, f"{h:.1f} ms",
                 ha='center', va='bottom', fontsize=9.8, fontweight='bold', color='#0F172A')
    
    # Speedup badge placed cleanly
    ax1.text(2.0, 42, "12.5x Speedup\n(Zero Cloud Egress)", ha='center', va='bottom',
             fontsize=8.8, fontweight='bold', color='#065F46',
             bbox=dict(boxstyle="round,pad=0.35", fc="#D1FAE5", ec="#10B981", lw=1.3))

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
    ax2.set_xticklabels(entities, fontsize=9.2, fontweight='bold', color='#1E293B')
    ax2.set_ylabel("Classification Performance Ratio (0.0 to 1.0)", fontsize=9.8, fontweight='bold', color='#0F172A', labelpad=10)
    ax2.set_title("B: Entity Accuracy & SLA Benchmark", fontsize=11.0, fontweight='bold', color='#0F172A', pad=10)
    ax2.set_ylim(0.85, 1.025)
    ax2.grid(axis='y', linestyle='--', alpha=0.5, color='#CBD5E1')
    ax2.set_axisbelow(True)
    ax2.legend(loc='lower left', framealpha=0.92, fontsize=8.6)
    ax2.tick_params(axis='y', labelsize=9.2)

    save_all_targets(fig, "fig5_5_metrics.png", "Figure_5.5_Quantitative_Performance_Metrics.png")
    plt.close()

# ==============================================================================
# COPY & INTUITIVELY RENAME UI SCREENSHOTS AND OTHER REPORT ASSETS
# ==============================================================================
def organize_all_report_images():
    import shutil
    asset_renames = [
        ("report_assets/fig5_1_ui.png", "Figure_5.1_SOC_Command_Console_UI.png"),
        ("report_assets/fig5_5_audit.png", "Figure_5.1b_SOC_Incident_Audit_Log_UI.png"),
        ("report_assets/fig5_6_copilot.png", "Figure_5.1c_SOC_Analyst_Copilot_UI.png"),
        ("report_assets/fig5_2_upload.png", "Figure_5.2_File_Upload_Scanner_UI.png"),
        ("report_assets/fig5_3_model_selection.png", "Figure_5.3_Model_Selection_Controls_UI.png"),
        ("report_assets/fig5_4_response.png", "Figure_5.4_Real_Time_Masking_Response_UI.png"),
        ("report_assets/fig_plagiarism.png", "Plagiarism_Report_DrillBit.png"),
        ("report_assets/fig_certificates.png", "Certificates_Presentation_and_Competition.png"),
        ("report_assets/sies_logo.png", "SIES_College_Logo.png"),
    ]
    for src, dst_name in asset_renames:
        if os.path.exists(src):
            shutil.copy2(src, f"Report_Images_Ready_To_Insert/{dst_name}")
            print(f"Copied: {dst_name}")

if __name__ == "__main__":
    generate_perfect_gantt()
    generate_perfect_architecture()
    generate_perfect_er()
    generate_perfect_uml()
    generate_perfect_dfd()
    generate_perfect_metrics()
    organize_all_report_images()
    print("ALL IMAGES GENERATED & ORGANIZED IN Report_Images_Ready_To_Insert/")

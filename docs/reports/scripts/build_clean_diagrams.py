import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon
import numpy as np

os.makedirs("report_assets", exist_ok=True)

# Common styling
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

# ==============================================================================
# 1. GANTT CHART (Fig 1.1)
# ==============================================================================
def create_clean_gantt():
    fig, ax = plt.subplots(figsize=(12, 6.2), dpi=300)
    
    tasks = [
        "Phase 1: Problem Definition & Literature Survey",
        "Phase 2: Banking DLP Dataset Assembly & Cleaning",
        "Phase 3: Hybrid AI Model Training & ONNX INT8 Quantization",
        "Phase 4: Algorithmic Verification (Luhn & MOD-97 Checksums)",
        "Phase 5: Ingestion Gateway & Multi-Format Document Parsers",
        "Phase 6: Reverse-Offset Masking & AES-256-GCM Token Vault",
        "Phase 7: Real-Time SOC Console & Analyst Copilot Integration",
        "Phase 8: Security Testing, SLA Benchmarking & Final Viva Report"
    ]
    
    start_weeks = [1, 3, 5, 7, 9, 11, 13, 15]
    durations   = [3, 3, 3, 3, 3, 3, 3, 2]
    
    y_pos = np.arange(len(tasks))
    bar_colors = [
        '#1E3A8A', '#2563EB', '#0D9488', '#059669',
        '#D97706', '#EA580C', '#7C3AED', '#475569'
    ]
    
    for i in range(len(tasks)):
        ax.barh(y_pos[i], durations[i], left=start_weeks[i], height=0.55,
                color=bar_colors[i], edgecolor='#0F172A', linewidth=1.2, zorder=3)
        ax.text(start_weeks[i] + durations[i] / 2, y_pos[i], f"{durations[i]} Weeks",
                ha='center', va='center', color='white', fontweight='bold', fontsize=9, zorder=4)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(tasks, fontsize=9.5, fontweight='bold', color='#1E293B')
    ax.invert_yaxis()
    
    ax.set_xlim(0.5, 17.5)
    ax.set_xticks(range(1, 18))
    ax.set_xticklabels([f"W{w}" for w in range(1, 18)], fontsize=9, fontweight='bold', color='#334155')
    ax.set_xlabel("Academic Project Schedule (Weeks 1 to 16)", fontsize=11, fontweight='bold', labelpad=10, color='#0F172A')
    
    ax.grid(axis='x', linestyle='--', alpha=0.5, color='#94A3B8', zorder=1)
    ax.set_axisbelow(True)
    
    # Milestone shading
    ax.axvspan(1, 4.5, color='#F8FAFC', alpha=0.8, zorder=0)
    ax.axvspan(4.5, 10.5, color='#F1F5F9', alpha=0.8, zorder=0)
    ax.axvspan(10.5, 16.5, color='#F8FAFC', alpha=0.8, zorder=0)
    
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_color('#CBD5E1')
        ax.spines[spine].set_linewidth(1.2)
        
    fig.suptitle("Figure 1.1: SecureFlowAI Project Schedule & Milestone Gantt Chart",
                 fontsize=12.5, fontweight='bold', color='#0F172A', y=0.96)
    plt.subplots_adjust(left=0.42, right=0.96, top=0.90, bottom=0.12)
    plt.savefig("report_assets/fig1_1_gantt.png", dpi=300)
    plt.close()
    print("Created clean fig1_1_gantt.png")

# ==============================================================================
# 2. SYSTEM ARCHITECTURE DIAGRAM (Fig 3.1)
# ==============================================================================
def create_clean_architecture():
    fig, ax = plt.subplots(figsize=(12, 9.5), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    
    # Background card
    bg = FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=1", ec="#CBD5E1", fc="#FFFFFF", lw=1.5)
    ax.add_patch(bg)
    
    # Title Banner
    title_box = FancyBboxPatch((3, 91.5), 94, 6.2, boxstyle="round,pad=0.5", ec="#1E3A8A", fc="#1E3A8A", lw=1)
    ax.add_patch(title_box)
    ax.text(50, 94.6, "SECUREFLOWAI: MULTI-TIER ENTERPRISE BANKING DLP SYSTEM ARCHITECTURE",
            ha='center', va='center', color='white', fontsize=11.5, fontweight='bold')

    def draw_layer_card(x, y, w, h, title, subtitle, items, border_col, header_col, bg_col):
        card = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5", ec=border_col, fc=bg_col, lw=1.8)
        ax.add_patch(card)
        # Header strip
        strip = FancyBboxPatch((x, y + h - 4.5), w, 4.5, boxstyle="round,pad=0.2", ec=border_col, fc=header_col, lw=1)
        ax.add_patch(strip)
        ax.text(x + w/2, y + h - 2.3, title, ha='center', va='center', color='white', fontsize=9.5, fontweight='bold')
        ax.text(x + 2.5, y + h - 6.2, subtitle, ha='left', va='center', color='#475569', fontsize=8, fontstyle='italic')
        
        n = len(items)
        sub_w = (w - (n + 1) * 2) / n
        sub_h = h - 9.5
        for i, (b_title, b_desc) in enumerate(items):
            bx = x + 2 + i * (sub_w + 2)
            by = y + 2
            sub_card = FancyBboxPatch((bx, by), sub_w, sub_h, boxstyle="round,pad=0.3", ec="#CBD5E1", fc="#FFFFFF", lw=1)
            ax.add_patch(sub_card)
            # Title near top of sub-card
            ax.text(bx + sub_w/2, by + sub_h - 2.2, b_title, ha='center', va='center', color='#0F172A', fontsize=8.5, fontweight='bold')
            # Description lines in middle
            ax.text(bx + sub_w/2, by + sub_h/2 - 1.5, b_desc, ha='center', va='center', color='#475569', fontsize=7.2, linespacing=1.3)

    # 1. LAYER 1: CAPTURE & ENDPOINTS (y: 72 to 89, h: 17)
    draw_layer_card(
        4, 72, 92, 16.5,
        "LAYER 1: ENDPOINT & SENSOR INGESTION TIER",
        "Local device interception layer capturing employee egress traffic without latency",
        [
            ("Chrome/Edge MV3 Extension", "Content scripts intercept\nDOM paste & HTTP uploads\n(Zero external egress)"),
            ("Desktop OS Daemon", "Low-level clipboard hook\nMonitors buffer changes\nIntercepts file copies"),
            ("Enterprise Mail Connector", "Milter/Postfix SMTP hook\nScans body & attachments\n(PDF, XLSX, DOCX, ZIP)")
        ],
        "#2563EB", "#2563EB", "#EFF6FF"
    )

    # Down Arrow 1
    ax.annotate('', xy=(50, 68), xytext=(50, 72),
                arrowprops=dict(facecolor='#1E3A8A', edgecolor='#1E3A8A', width=2, headwidth=7, headlength=7))
    ax.text(51.5, 70, "Encrypted JSON / Binary Stream via mTLS", color='#1E3A8A', fontsize=7.5, fontweight='bold')

    # 2. LAYER 2: INGESTION GATEWAY & EXTRACTORS (y: 50.5 to 67.5, h: 17)
    draw_layer_card(
        4, 50.5, 92, 16.5,
        "LAYER 2: INGESTION GATEWAY & DOCUMENT EXTRACTION CORE",
        "High-performance FastAPI asynchronous pipeline with streaming parsers & OCR",
        [
            ("FastAPI Async Gateway", "Non-blocking event loop\nmTLS authentication\nCircuit breaker fail-open"),
            ("Multi-Format Document Parser", "PyMuPDF (PDF vectors)\npython-docx (Office DOCX)\nopenpyxl (Financial Sheets)"),
            ("EasyOCR Image Engine", "In-memory OCR pipeline\nScanned checks, PAN cards\nNational ID KYC images")
        ],
        "#0D9488", "#0D9488", "#F0FDFA"
    )

    # Down Arrow 2
    ax.annotate('', xy=(50, 46.5), xytext=(50, 50.5),
                arrowprops=dict(facecolor='#0D9488', edgecolor='#0D9488', width=2, headwidth=7, headlength=7))
    ax.text(51.5, 48.5, "Normalized Text Streams & Image OCR Tokens", color='#0D9488', fontsize=7.5, fontweight='bold')

    # 3. LAYER 3: HYBRID AI & DETECTION ENGINE (y: 29 to 46, h: 17)
    draw_layer_card(
        4, 29, 92, 16.5,
        "LAYER 3: HYBRID AI CLASSIFIER & DETERMINISTIC VALIDATION",
        "Two-stage verification combining mathematical checksums with INT8 neural models",
        [
            ("Algorithmic Checksums", "Luhn (Credit Cards)\nMOD-97 (IBAN accounts)\nRegex Routing & SWIFT"),
            ("Quantized ONNX INT8 Model", "Sliding-window transformer\nSub-15ms local CPU latency\nZero cloud API dependencies"),
            ("Banking Contextual NER", "spaCy named entity recognizer\nDisambiguates false positives\n(Phone numbers vs. Card PINs)")
        ],
        "#D97706", "#D97706", "#FFFBEB"
    )

    # Down Arrow 3
    ax.annotate('', xy=(50, 25), xytext=(50, 29),
                arrowprops=dict(facecolor='#D97706', edgecolor='#D97706', width=2, headwidth=7, headlength=7))
    ax.text(51.5, 27, "Extracted PII Offsets & Unified Risk Score (0 - 100)", color='#D97706', fontsize=7.5, fontweight='bold')

    # 4. LAYER 4 & 5: ENFORCEMENT & GOVERNANCE (y: 4 to 24.5, h: 20)
    card_bot = FancyBboxPatch((4, 4), 92, 20.5, boxstyle="round,pad=0.5", ec="#7C3AED", fc="#FAF5FF", lw=1.8)
    ax.add_patch(card_bot)
    strip_bot = FancyBboxPatch((4, 20), 92, 4.5, boxstyle="round,pad=0.2", ec="#7C3AED", fc="#7C3AED", lw=1)
    ax.add_patch(strip_bot)
    ax.text(50, 22.2, "LAYER 4 & 5: ENFORCEMENT, CRYPTOGRAPHY & SOC GOVERNANCE",
            ha='center', va='center', color='white', fontsize=9.5, fontweight='bold')

    bot_items = [
        ("Reverse-Offset Masking", "Preserves sentence context\nReplaces sensitive spans\nwith HMAC cryptographic tokens"),
        ("AES-256-GCM Vault", "Envelope encryption\nZero-knowledge key mgmt\nAudit-grade detokenization"),
        ("PostgreSQL / SQLite Trail", "Immutable forensic logs\nSHA-256 payload digest\nRegulatory reporting (PCI/GDPR)"),
        ("Analyst Copilot & SOC UI", "React 19 command console\nWebSocket real-time push\nAutonomous triage assistant")
    ]
    b_w = (92 - 5 * 2) / 4
    b_h = 13.5
    for i, (b_title, b_desc) in enumerate(bot_items):
        bx = 4 + 2 + i * (b_w + 2)
        by = 5.5
        sub_card = FancyBboxPatch((bx, by), b_w, b_h, boxstyle="round,pad=0.3", ec="#CBD5E1", fc="#FFFFFF", lw=1)
        ax.add_patch(sub_card)
        ax.text(bx + b_w/2, by + b_h - 2.2, b_title, ha='center', va='center', color='#0F172A', fontsize=8, fontweight='bold')
        ax.text(bx + b_w/2, by + b_h/2 - 1.5, b_desc, ha='center', va='center', color='#475569', fontsize=7, linespacing=1.3)

    plt.tight_layout()
    plt.savefig("report_assets/fig3_1_architecture.png", dpi=300)
    plt.close()
    print("Created clean fig3_1_architecture.png")

# ==============================================================================
# 3. ENTITY RELATIONSHIP (ER) DIAGRAM (Fig 4.1)
# ==============================================================================
def create_clean_er():
    fig, ax = plt.subplots(figsize=(12, 9), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    
    bg = FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=1", ec="#E2E8F0", fc="#FAFAFA", lw=1)
    ax.add_patch(bg)
    
    def draw_entity(x, y, w, h, title, fields, color="#1E3A8A"):
        hdr = FancyBboxPatch((x, y + h - 5), w, 5, boxstyle="round,pad=0.2", ec=color, fc=color, lw=1.5)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - 2.5, title, ha='center', va='center', color='white', fontsize=9.5, fontweight='bold')
        
        body = FancyBboxPatch((x, y), w, h - 5, boxstyle="round,pad=0.2", ec=color, fc='#FFFFFF', lw=1.5)
        ax.add_patch(body)
        
        for idx, (f_name, f_type, is_pk, is_fk) in enumerate(fields):
            fy = y + h - 8 - idx * 2.8
            prefix = "[PK] " if is_pk else ("[FK] " if is_fk else " •  ")
            f_col = "#B91C1C" if is_pk else ("#D97706" if is_fk else "#1E293B")
            ax.text(x + 2, fy, f"{prefix}{f_name}", ha='left', va='center', color=f_col,
                    fontsize=8, fontweight='bold' if (is_pk or is_fk) else 'normal')
            ax.text(x + w - 2, fy, f_type, ha='right', va='center', color="#64748B", fontsize=7.5, fontfamily='monospace')

    # Top Row: BANK_USER (Left) and SECURITY_POLICY (Right)
    draw_entity(6, 68, 38, 25, "BANK_USER", [
        ("user_id", "UUID", True, False),
        ("employee_email", "VARCHAR(128)", False, False),
        ("department_name", "VARCHAR(64)", False, False),
        ("assigned_role", "VARCHAR(32)", False, False),
        ("risk_clearance_tier", "INTEGER", False, False),
        ("created_at", "TIMESTAMP", False, False)
    ], "#1E3A8A")

    draw_entity(56, 68, 38, 25, "SECURITY_POLICY", [
        ("policy_id", "UUID", True, False),
        ("policy_code", "VARCHAR(64)", False, False),
        ("mask_threshold", "INTEGER", False, False),
        ("block_threshold", "INTEGER", False, False),
        ("whitelisted_domains", "JSONB", False, False),
        ("circuit_fail_mode", "VARCHAR(16)", False, False)
    ], "#0D9488")

    # Middle Row: DLP_AUDIT_LOG (Center) - y: 28 to 62, h: 34
    draw_entity(27, 28, 46, 34, "DLP_AUDIT_LOG", [
        ("incident_id", "UUID", True, False),
        ("user_id", "UUID", False, True),
        ("policy_id", "UUID", False, True),
        ("timestamp", "TIMESTAMP", False, False),
        ("source_action", "VARCHAR(32)", False, False),
        ("destination_domain", "VARCHAR(255)", False, False),
        ("classification_tier", "VARCHAR(32)", False, False),
        ("calculated_risk_score", "INTEGER", False, False),
        ("enforcement_action", "VARCHAR(16)", False, False),
        ("payload_sha256", "CHAR(64)", False, False)
    ], "#B45309")

    # Bottom Row: TOKEN_VAULT (Left) and INCIDENT_OVERRIDE (Right) - y: 3 to 23, h: 20
    draw_entity(6, 3, 38, 20, "TOKEN_VAULT", [
        ("token_id", "VARCHAR(64)", True, False),
        ("incident_id", "UUID", False, True),
        ("encrypted_pii_value", "BYTEA", False, False),
        ("encryption_iv_nonce", "BYTEA", False, False),
        ("auth_tag", "BYTEA", False, False)
    ], "#6D28D9")

    draw_entity(56, 3, 38, 20, "INCIDENT_OVERRIDE", [
        ("override_id", "UUID", True, False),
        ("incident_id", "UUID", False, True),
        ("analyst_user_id", "UUID", False, True),
        ("justification_text", "TEXT", False, False),
        ("authorized_at", "TIMESTAMP", False, False)
    ], "#475569")

    # Clean Orthogonal Connectors with Cardinalities
    # BANK_USER -> DLP_AUDIT_LOG
    ax.annotate('', xy=(38, 62), xytext=(25, 68),
                arrowprops=dict(arrowstyle="->", lw=1.5, color='#1E3A8A', connectionstyle="angle,angleA=-90,angleB=180,rad=3"))
    ax.text(26, 64, "1 : N (Triggers)", color='#1E3A8A', fontsize=8, fontweight='bold')

    # SECURITY_POLICY -> DLP_AUDIT_LOG
    ax.annotate('', xy=(62, 62), xytext=(75, 68),
                arrowprops=dict(arrowstyle="->", lw=1.5, color='#0D9488', connectionstyle="angle,angleA=-90,angleB=0,rad=3"))
    ax.text(67, 64, "1 : N (Governs)", color='#0D9488', fontsize=8, fontweight='bold')

    # DLP_AUDIT_LOG -> TOKEN_VAULT
    ax.annotate('', xy=(25, 23), xytext=(35, 28),
                arrowprops=dict(arrowstyle="->", lw=1.5, color='#6D28D9', connectionstyle="angle,angleA=-90,angleB=180,rad=3"))
    ax.text(23, 25.5, "1 : N (Vaults PII)", color='#6D28D9', fontsize=8, fontweight='bold')

    # DLP_AUDIT_LOG -> INCIDENT_OVERRIDE
    ax.annotate('', xy=(75, 23), xytext=(65, 28),
                arrowprops=dict(arrowstyle="->", lw=1.5, color='#475569', connectionstyle="angle,angleA=-90,angleB=0,rad=3"))
    ax.text(68, 25.5, "1 : 1 (Overrides)", color='#475569', fontsize=8, fontweight='bold')


    fig.suptitle("Figure 4.1: SecureFlowAI Relational Database Schema & Entity-Relationship (ER) Model",
                 fontsize=12, fontweight='bold', color='#0F172A', y=0.97)
    plt.subplots_adjust(top=0.93, bottom=0.04, left=0.03, right=0.97)
    plt.savefig("report_assets/fig4_1_er_diagram.png", dpi=300)
    plt.close()
    print("Created clean fig4_1_er_diagram.png")

# ==============================================================================
# 4. UML ACTIVITY WORKFLOW DIAGRAM (Fig 4.2)
# ==============================================================================
def create_clean_uml():
    fig, ax = plt.subplots(figsize=(10.5, 12), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    bg = FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=1", ec="#E2E8F0", fc="#FFFFFF", lw=1)
    ax.add_patch(bg)

    # Start Node (Filled Circle)
    start_c = Circle((50, 94.5), 2.0, color='#0F172A', ec='#0F172A', lw=1.5)
    ax.add_patch(start_c)
    ax.text(50, 97.8, "User Initiates Egress (Copy / Paste / Upload)", ha='center', va='center',
            fontsize=9, fontweight='bold', color='#0F172A')

    def draw_activity_step(y, title, desc, w=62, h=6.5, fill='#F8FAFC', stroke='#2563EB'):
        card = FancyBboxPatch((50 - w/2, y), w, h, boxstyle="round,pad=0.3", ec=stroke, fc=fill, lw=1.5)
        ax.add_patch(card)
        ax.text(50, y + h - 2.2, title, ha='center', va='center', fontsize=9, fontweight='bold', color='#0F172A')
        ax.text(50, y + 2.0, desc, ha='center', va='center', fontsize=7.5, color='#475569')

    def draw_down_arrow(y_start, y_end):
        ax.annotate('', xy=(50, y_end), xytext=(50, y_start),
                    arrowprops=dict(arrowstyle="->", lw=1.6, color='#334155'))

    # Steps
    draw_down_arrow(92.5, 87)
    draw_activity_step(80.5, "1. Intercept Egress Traffic", "Endpoint Sensor captures text clipboard or multi-format document buffer", fill='#EFF6FF', stroke='#2563EB')

    draw_down_arrow(80.5, 75)
    draw_activity_step(68.5, "2. Parse Payload & Ingest Text", "PyMuPDF/docx/openpyxl extract plain text; EasyOCR runs on image buffers", fill='#F0FDFA', stroke='#0D9488')

    draw_down_arrow(68.5, 63)
    draw_activity_step(56.5, "3. Run Algorithmic Checksums & INT8 Classifier", "Luhn & MOD-97 verify card/IBAN numbers; Quantized ONNX classifies text tier", fill='#FFFBEB', stroke='#D97706')

    draw_down_arrow(56.5, 51)
    draw_activity_step(44.5, "4. Compute Unified Risk Score (0 - 100)", "Aggregates entity severity, destination whitelists, and user department risk weight", fill='#FAF5FF', stroke='#7C3AED')

    # Decision Diamond
    draw_down_arrow(44.5, 39)
    diamond = Polygon([(50, 39), (62, 34), (50, 29), (38, 34)], closed=True, ec='#B45309', fc='#FEF3C7', lw=1.8)
    ax.add_patch(diamond)
    ax.text(50, 34, "Evaluate Risk\nThreshold", ha='center', va='center', fontsize=8, fontweight='bold', color='#92400E')

    # 3 Branches
    # Left: ALLOW
    ax.annotate('', xy=(20, 23.5), xytext=(38, 34),
                arrowprops=dict(arrowstyle="->", lw=1.5, color='#16A34A', connectionstyle="angle,angleA=180,angleB=90,rad=3"))
    ax.text(25, 35.5, "[Score < 45]\nLow Risk", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#16A34A')
    
    card_allow = FancyBboxPatch((7, 17.5), 26, 6, boxstyle="round,pad=0.3", ec='#16A34A', fc='#F0FDF4', lw=1.5)
    ax.add_patch(card_allow)
    ax.text(20, 21.0, "ALLOW TRANSFER", ha='center', va='center', fontsize=8, fontweight='bold', color='#166534')
    ax.text(20, 19.0, "Transmit Unmodified", ha='center', va='center', fontsize=7, color='#475569')

    # Center: MASK
    ax.annotate('', xy=(50, 23.5), xytext=(50, 29),
                arrowprops=dict(arrowstyle="->", lw=1.5, color='#D97706'))
    ax.text(51.5, 26.5, "[45 <= Score < 80] Medium", ha='left', va='center', fontsize=7.5, fontweight='bold', color='#D97706')
    
    card_mask = FancyBboxPatch((37, 17.5), 26, 6, boxstyle="round,pad=0.3", ec='#D97706', fc='#FFFBEB', lw=1.5)
    ax.add_patch(card_mask)
    ax.text(50, 21.0, "MASK & TOKENIZE", ha='center', va='center', fontsize=8, fontweight='bold', color='#B45309')
    ax.text(50, 19.0, "HMAC Reverse-Offset", ha='center', va='center', fontsize=7, color='#475569')

    # Right: BLOCK
    ax.annotate('', xy=(80, 23.5), xytext=(62, 34),
                arrowprops=dict(arrowstyle="->", lw=1.5, color='#DC2626', connectionstyle="angle,angleA=0,angleB=90,rad=3"))
    ax.text(75, 35.5, "[Score >= 80]\nCritical Risk", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#DC2626')
    
    card_block = FancyBboxPatch((67, 17.5), 26, 6, boxstyle="round,pad=0.3", ec='#DC2626', fc='#FEF2F2', lw=1.5)
    ax.add_patch(card_block)
    ax.text(80, 21.0, "BLOCK EXFILTRATION", ha='center', va='center', fontsize=8, fontweight='bold', color='#991B1B')
    ax.text(80, 19.0, "Drop & Notify SOC", ha='center', va='center', fontsize=7, color='#475569')

    # Converge to Step 5
    ax.annotate('', xy=(35, 12), xytext=(20, 17.5), arrowprops=dict(arrowstyle="->", lw=1.4, color='#334155', connectionstyle="angle,angleA=-90,angleB=180,rad=3"))
    ax.annotate('', xy=(50, 12), xytext=(50, 17.5), arrowprops=dict(arrowstyle="->", lw=1.4, color='#334155'))
    ax.annotate('', xy=(65, 12), xytext=(80, 17.5), arrowprops=dict(arrowstyle="->", lw=1.4, color='#334155', connectionstyle="angle,angleA=-90,angleB=0,rad=3"))

    draw_activity_step(5.5, "5. Commit Audit Trail & Publish Telemetry",
                       "Write immutable SHA-256 event to SQLite/PostgreSQL; stream alert via WebSocket bus to SOC Console",
                       w=68, h=6.5, fill='#F1F5F9', stroke='#475569')

    # End Node (Bullseye Circle) - plenty of room at y=1.8
    draw_down_arrow(5.5, 2.8)
    outer_c = Circle((50, 1.8), 1.3, color='#FFFFFF', ec='#0F172A', lw=1.5)
    inner_c = Circle((50, 1.8), 0.7, color='#0F172A', ec='#0F172A', lw=1)
    ax.add_patch(outer_c)
    ax.add_patch(inner_c)

    fig.suptitle("Figure 4.2: SecureFlowAI UML Activity Workflow Diagram for Egress Inspection",
                 fontsize=11.5, fontweight='bold', color='#0F172A', y=0.98)
    plt.subplots_adjust(top=0.95, bottom=0.03, left=0.02, right=0.98)
    plt.savefig("report_assets/fig4_2_uml_activity.png", dpi=300)
    plt.close()
    print("Created clean fig4_2_uml_activity.png")

# ==============================================================================
# 5. DFD LEVEL 1 (Fig 4.3)
# ==============================================================================
def create_clean_dfd():
    fig, ax = plt.subplots(figsize=(12, 8.5), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    bg = FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=1", ec="#E2E8F0", fc="#FAFAFA", lw=1)
    ax.add_patch(bg)

    def draw_entity_dfd(x, y, w, h, id_str, name_str, col="#1E3A8A", bg_col="#EFF6FF"):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2", ec=col, fc=bg_col, lw=1.6)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 3, id_str, ha='center', va='center', fontsize=8, fontweight='bold', color=col)
        ax.text(x + w/2, y + h/2 - 1, name_str, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0F172A')

    def draw_process(x, y, w, h, p_num, p_title, p_sub, col="#0D9488", bg_col="#F0FDFA"):
        p_box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3", ec=col, fc=bg_col, lw=1.6)
        ax.add_patch(p_box)
        strip = FancyBboxPatch((x, y + h - 3.5), w, 3.5, boxstyle="round,pad=0.1", ec=col, fc=col, lw=1)
        ax.add_patch(strip)
        ax.text(x + w/2, y + h - 1.8, f"Process {p_num}", ha='center', va='center', fontsize=8, fontweight='bold', color='white')
        ax.text(x + w/2, y + h/2 + 0.5, p_title, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0F172A')
        ax.text(x + w/2, y + 2.5, p_sub, ha='center', va='center', fontsize=7, color='#475569')

    def draw_datastore(x, y, w, h, ds_id, ds_name):
        ax.plot([x, x + w], [y + h, y + h], color='#6D28D9', lw=2)
        ax.plot([x, x + w], [y, y], color='#6D28D9', lw=2)
        ax.fill_between([x, x + w], [y, y], [y + h, y + h], color='#F5F3FF', alpha=0.8)
        ax.text(x + 3, y + h/2, ds_id, ha='left', va='center', fontsize=8, fontweight='bold', color='#6D28D9')
        ax.text(x + w/2 + 2, y + h/2, ds_name, ha='center', va='center', fontsize=8, fontweight='bold', color='#0F172A')

    # ==============================================================================
    # PERFECT GRID LAYOUT (3 Rows x 4 Columns)
    # Row 1 (y=70): E1 (x=4) -> P1.0 (x=28) -> P2.0 (x=54) -> E2 (x=80)
    # Row 2 (y=40): D1 (x=4) -> P3.0 (x=28) -> P4.0 (x=54) <-> D2 (x=80)
    # Row 3 (y=12): D3 (x=28) <- P5.0 (x=54) -> E3 (x=80)
    # ==============================================================================

    # Row 1: Ingestion & Inspection
    draw_entity_dfd(4, 70, 18, 16, "EXTERNAL ENTITY E1", "Bank Employee /\nWorkstation Endpoint", col="#1E3A8A", bg_col="#EFF6FF")
    draw_process(28, 70, 20, 16, "1.0", "Ingest & Extract", "Multi-format parsing & OCR", col="#0D9488", bg_col="#F0FDFA")
    draw_process(54, 70, 20, 16, "2.0", "Hybrid Inspection", "Checksums & ONNX INT8", col="#D97706", bg_col="#FFFBEB")
    draw_entity_dfd(80, 70, 17, 16, "EXTERNAL ENTITY E2", "External Recipient /\nCloud GenAI / Web", col="#DC2626", bg_col="#FEF2F2")

    # Row 2: Policy & Enforcement
    draw_datastore(4, 42, 18, 12, "D1", "Security Policies\n(Rule Thresholds)")
    draw_process(28, 40, 20, 16, "3.0", "Risk Evaluation", "Policy threshold match", col="#B45309", bg_col="#FEF3C7")
    draw_process(54, 40, 20, 16, "4.0", "Enforce & Tokenize", "Reverse-offset masking", col="#2563EB", bg_col="#EFF6FF")
    draw_datastore(80, 42, 17, 12, "D2", "Token Vault\n(AES-GCM Keys)")

    # Row 3: Audit & Forensics
    draw_datastore(28, 14, 20, 12, "D3", "Forensic Audit DB\n(SHA-256 Digests)")
    draw_process(54, 12, 20, 16, "5.0", "Audit & Alerting", "SQLite log & WebSocket", col="#475569", bg_col="#F1F5F9")
    draw_entity_dfd(80, 12, 17, 16, "EXTERNAL ENTITY E3", "SOC Analyst /\nCompliance Officer", col="#7C3AED", bg_col="#FAF5FF")

    # PURE ADJACENT CLEAN CONNECTORS (NO CROSSINGS)
    # Row 1 Horizontal Flow: E1 -> P1.0 -> P2.0
    ax.annotate('', xy=(28, 78), xytext=(22, 78), arrowprops=dict(arrowstyle="->", lw=1.5, color='#0F172A'))
    ax.text(25, 79.5, "Raw Data", ha='center', va='center', fontsize=7, fontweight='bold', color='#0F172A')

    ax.annotate('', xy=(54, 78), xytext=(48, 78), arrowprops=dict(arrowstyle="->", lw=1.5, color='#0F172A'))
    ax.text(51, 79.5, "Tokens", ha='center', va='center', fontsize=7, fontweight='bold', color='#0F172A')

    # P2.0 (down) -> P3.0 (curved downwards)
    ax.annotate('', xy=(38, 56), xytext=(54, 70),
                arrowprops=dict(arrowstyle="->", lw=1.5, color='#0F172A', connectionstyle="arc3,rad=-0.1"))
    ax.text(49, 64, "PII Findings", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#0F172A')

    # Row 2 Flow: D1 -> P3.0 -> P4.0 <-> D2
    ax.annotate('', xy=(28, 48), xytext=(22, 48), arrowprops=dict(arrowstyle="->", lw=1.4, color='#6D28D9', linestyle='--'))
    ax.text(25, 49.5, "Rules", ha='center', va='center', fontsize=7, color='#6D28D9')

    ax.annotate('', xy=(54, 48), xytext=(48, 48), arrowprops=dict(arrowstyle="->", lw=1.5, color='#0F172A'))
    ax.text(51, 49.5, "Verdict", ha='center', va='center', fontsize=7, fontweight='bold', color='#0F172A')

    ax.annotate('', xy=(80, 48), xytext=(74, 48), arrowprops=dict(arrowstyle="<->", lw=1.5, color='#6D28D9', linestyle='--'))
    ax.text(77, 49.5, "HMAC Keys", ha='center', va='center', fontsize=7, color='#6D28D9')

    # P4.0 (up) -> E2 (Allowed / Sanitized Egress)
    ax.annotate('', xy=(80, 78), xytext=(64, 56),
                arrowprops=dict(arrowstyle="->", lw=1.5, color='#16A34A', connectionstyle="arc3,rad=0.15"))
    ax.text(73, 67, "Allowed / Masked", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#16A34A')


    # P4.0 (down) -> P5.0 (Audit event)
    ax.annotate('', xy=(64, 28), xytext=(64, 40), arrowprops=dict(arrowstyle="->", lw=1.5, color='#0F172A'))
    ax.text(65.5, 34, "Audit Event", ha='left', va='center', fontsize=7, fontweight='bold', color='#0F172A')

    # Row 3 Flow: D3 <- P5.0 -> E3
    ax.annotate('', xy=(48, 20), xytext=(54, 20), arrowprops=dict(arrowstyle="->", lw=1.4, color='#475569', linestyle='--'))
    ax.text(51, 21.5, "Commit", ha='center', va='center', fontsize=7, color='#475569')

    ax.annotate('', xy=(80, 20), xytext=(74, 20), arrowprops=dict(arrowstyle="->", lw=1.5, color='#7C3AED'))
    ax.text(77, 21.5, "Live Alert", ha='center', va='center', fontsize=7, fontweight='bold', color='#7C3AED')

    fig.suptitle("Figure 4.3: SecureFlowAI Level 1 Data Flow Diagram (DFD)",
                 fontsize=12, fontweight='bold', color='#0F172A', y=0.97)
    plt.subplots_adjust(top=0.93, bottom=0.04, left=0.02, right=0.98)
    plt.savefig("report_assets/fig4_3_dfd_level1.png", dpi=300)
    plt.close()
    print("Created clean fig4_3_dfd_level1.png")


# ==============================================================================
# 6. MODEL METRICS & BENCHMARKS (Fig 5.5)
# ==============================================================================
def create_clean_metrics():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), dpi=300)
    
    # Subplot 1: Latency Comparison
    models = ['PyTorch FP32\n(Baseline)', 'ONNX FP32\n(Unquantized)', 'SecureFlowAI\n(ONNX INT8 Quantized)']
    latencies = [142.6, 48.2, 12.4]
    colors = ['#94A3B8', '#38BDF8', '#10B981']
    
    bars = ax1.bar(models, latencies, color=colors, edgecolor='#0F172A', linewidth=1.2, width=0.55)
    ax1.set_ylabel("Inference Latency (Milliseconds - Lower is Better)", fontsize=9.5, fontweight='bold', color='#0F172A')
    ax1.set_title("A: Local CPU Inference Latency Comparison", fontsize=10.5, fontweight='bold', color='#0F172A', pad=10)
    ax1.grid(axis='y', linestyle='--', alpha=0.5, color='#CBD5E1')
    ax1.set_axisbelow(True)
    ax1.set_ylim(0, 170)
    
    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., h + 3, f"{h:.1f} ms",
                 ha='center', va='bottom', fontsize=9, fontweight='bold', color='#0F172A')
    
    ax1.text(2, 28, "11.5x Speedup\n(Zero Egress)", ha='center', va='bottom',
             fontsize=8.5, fontweight='bold', color='#065F46',
             bbox=dict(boxstyle="round,pad=0.3", fc="#D1FAE5", ec="#10B981", lw=1))

    # Subplot 2: Classification Precision, Recall, F1 by Entity
    entities = ['Credit Card', 'IBAN / Routing', 'SWIFT BIC', 'Tax ID / SSN', 'Overall Avg']
    precision = [0.992, 0.985, 0.978, 0.981, 0.984]
    recall    = [0.988, 0.972, 0.965, 0.976, 0.975]
    f1        = [0.990, 0.978, 0.971, 0.978, 0.979]
    
    x = np.arange(len(entities))
    w = 0.25
    
    r1 = ax2.bar(x - w, precision, w, label='Precision', color='#1E3A8A', edgecolor='#0F172A', lw=1)
    r2 = ax2.bar(x, recall, w, label='Recall', color='#0D9488', edgecolor='#0F172A', lw=1)
    r3 = ax2.bar(x + w, f1, w, label='F1-Score', color='#F59E0B', edgecolor='#0F172A', lw=1)
    
    ax2.set_xticks(x)
    ax2.set_xticklabels(entities, fontsize=8.5, fontweight='bold', color='#1E293B', rotation=15)
    ax2.set_ylabel("Performance Ratio (0.0 to 1.0)", fontsize=9.5, fontweight='bold', color='#0F172A')
    ax2.set_title("B: Model Detection Accuracy by Banking Entity", fontsize=10.5, fontweight='bold', color='#0F172A', pad=10)
    ax2.set_ylim(0.85, 1.03)
    ax2.grid(axis='y', linestyle='--', alpha=0.5, color='#CBD5E1')
    ax2.set_axisbelow(True)
    ax2.legend(loc='lower left', framealpha=0.9, fontsize=8.5)

    fig.suptitle("Figure 5.5: SecureFlowAI Quantitative SLA Latency & Detection Performance Benchmarks",
                 fontsize=12, fontweight='bold', color='#0F172A', y=0.98)
    plt.subplots_adjust(top=0.88, bottom=0.18, left=0.08, right=0.96)
    plt.savefig("report_assets/fig5_5_metrics.png", dpi=300)
    plt.close()
    print("Created clean fig5_5_metrics.png")

if __name__ == "__main__":
    create_clean_gantt()
    create_clean_architecture()
    create_clean_er()
    create_clean_uml()
    create_clean_dfd()
    create_clean_metrics()
    print("ALL CLEAN DIAGRAMS SUCCESSFULLY GENERATED!")

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_full_report():
    print("Building SecureFlowAI SIES GST Project Report Word Document...")
    doc = docx.Document()

    # Configure Section 1 (Standard margins)
    sec = doc.sections[0]
    sec.top_margin = Inches(1.0)
    sec.bottom_margin = Inches(1.0)
    sec.left_margin = Inches(1.5)   # Standard binding margin
    sec.right_margin = Inches(1.0)

    # Typography & Styles
    norm = doc.styles['Normal']
    norm.font.name = 'Times New Roman'
    norm.font.size = Pt(12)
    norm.font.color.rgb = RGBColor(0, 0, 0)
    norm.paragraph_format.line_spacing = 1.5
    norm.paragraph_format.space_after = Pt(6)

    def add_p(text, bold_prefix="", italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(space_after)
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.bold = True
            r_b.font.name = 'Times New Roman'
            r_b.font.size = Pt(12)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.font.italic = italic
        return p

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(4)
        r_b = p.add_run(bold_prefix)
        r_b.bold = True
        r_b.font.name = 'Times New Roman'
        r_b.font.size = Pt(12)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        return p

    def add_h1(text):
        doc.add_page_break()
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(12)
        r = p.add_run(text)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(16)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(text)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(14)
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        return p

    def add_figure(image_path, caption, width=Inches(6.0)):
        if os.path.exists(image_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.add_run().add_picture(image_path, width=width)
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(12)
            r = p_cap.add_run(caption)
            r.bold = True
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10.5)

    # -------------------------------------------------------------
    # 1. COVER PAGE (Page 1 in PDF template)
    # -------------------------------------------------------------
    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t.paragraph_format.space_before = Pt(36)
    p_t.paragraph_format.space_after = Pt(24)
    r_t = p_t.add_run("SecureFlowAI: An Intelligent Data Leakage Prevention and Threat Mitigation System for Banking and Financial Workflows")
    r_t.bold = True
    r_t.font.name = 'Times New Roman'
    r_t.font.size = Pt(18)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(20)
    p_sub.add_run("Submitted in partial fulfillment of the requirements of the degree\n").font.size = Pt(11)
    r_deg = p_sub.add_run("BACHELOR OF ENGINEERING\nIN\nCOMPUTER ENGINEERING\n")
    r_deg.bold = True
    r_deg.font.size = Pt(13)

    p_by = doc.add_paragraph()
    p_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_by.paragraph_format.space_before = Pt(16)
    p_by.paragraph_format.space_after = Pt(20)
    p_by.add_run("By\n\n").bold = True
    
    t_names = doc.add_table(rows=4, cols=2)
    t_names.alignment = WD_TABLE_ALIGNMENT.CENTER
    students = [
        ("Rushikesh (Vaibhav Kachare)", "Roll No 1"),
        ("Bhavya (Devdatta Temgire)", "Roll No 2"),
        ("Sushii (Dheeraj Shriyan)", "Roll No 3"),
        ("Bhoomi (Serin Kaushik)", "Roll No 4")
    ]
    for idx, (sname, rno) in enumerate(students):
        cell_l = t_names.rows[idx].cells[0]
        cell_r = t_names.rows[idx].cells[1]
        cell_l.width = Inches(3.2)
        cell_r.width = Inches(1.8)
        p_l = cell_l.paragraphs[0]
        p_l.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_l.add_run(sname).font.size = Pt(11)
        p_r = cell_r.paragraphs[0]
        p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_r.add_run(rno).font.size = Pt(11)

    p_sup = doc.add_paragraph()
    p_sup.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sup.paragraph_format.space_before = Pt(24)
    p_sup.paragraph_format.space_after = Pt(16)
    p_sup.add_run("Supervisor\n").bold = True
    p_sup.add_run("Prof. / Dr. Guide Name\n").font.size = Pt(12)

    # SIES Logo
    if os.path.exists("report_assets/sies_logo.png"):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_after = Pt(12)
        p_logo.add_run().add_picture("report_assets/sies_logo.png", width=Inches(3.2))

    p_col = doc.add_paragraph()
    p_col.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_col.paragraph_format.space_after = Pt(4)
    r_c1 = p_col.add_run("Department of Computer Engineering\nSIES Graduate School of Technology (Autonomous)\n")
    r_c1.bold = True
    r_c1.font.size = Pt(13)
    p_col.add_run("Affiliated to University of Mumbai\nNerul, Navi Mumbai – 400706\nA.Y. 2026–27\n").font.size = Pt(11)

    # -------------------------------------------------------------
    # 2. CERTIFICATE (Page i)
    # -------------------------------------------------------------
    doc.add_page_break()
    p_ch = doc.add_paragraph()
    p_ch.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ch.paragraph_format.space_before = Pt(36)
    p_ch.paragraph_format.space_after = Pt(24)
    r_ch = p_ch.add_run("CERTIFICATE")
    r_ch.bold = True
    r_ch.font.size = Pt(16)

    add_p("This is to certify that the project entitled “SecureFlowAI: An Intelligent Data Leakage Prevention and Threat Mitigation System for Banking and Financial Workflows” is a bonafide work of the following students, submitted to the SIES Graduate School of Technology in partial fulfillment of the requirement for the award of the degree of Bachelor of Engineering in Computer Engineering.")

    t_cert_names = doc.add_table(rows=4, cols=2)
    t_cert_names.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (sname, rno) in enumerate(students):
        p_l = t_cert_names.rows[idx].cells[0].paragraphs[0]
        p_l.add_run(sname).font.size = Pt(11)
        p_r = t_cert_names.rows[idx].cells[1].paragraphs[0]
        p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_r.add_run(rno).font.size = Pt(11)

    doc.add_paragraph("\n\n")
    t_signs = doc.add_table(rows=2, cols=2)
    t_signs.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_signs.rows[0].cells[0].paragraphs[0].add_run("Guide Name\nSupervisor").bold = True
    t_signs.rows[0].cells[1].paragraphs[0].add_run("Prof. Sunil K Punjabi\nMini Project Coordinator").bold = True
    t_signs.rows[1].cells[0].paragraphs[0].add_run("\n\nDr. Aparna Bannore\nHead of Department").bold = True
    t_signs.rows[1].cells[1].paragraphs[0].add_run("\n\nDr. K. Lakshmisudha\nPrincipal").bold = True

    p_pg_i = doc.add_paragraph()
    p_pg_i.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_pg_i.paragraph_format.space_before = Pt(36)
    p_pg_i.add_run("i").font.size = Pt(10)

    # -------------------------------------------------------------
    # 3. PROJECT REPORT APPROVAL (Page ii)
    # -------------------------------------------------------------
    doc.add_page_break()
    p_ap = doc.add_paragraph()
    p_ap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ap.paragraph_format.space_before = Pt(36)
    p_ap.paragraph_format.space_after = Pt(24)
    r_ap = p_ap.add_run("PROJECT REPORT APPROVAL")
    r_ap.bold = True
    r_ap.font.size = Pt(16)

    add_p("This Mini Project entitled “SecureFlowAI: An Intelligent Data Leakage Prevention and Threat Mitigation System for Banking and Financial Workflows” by following students is approved for the degree of Bachelor of Engineering in Computer Engineering:")

    t_ap_names = doc.add_table(rows=4, cols=2)
    t_ap_names.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (sname, rno) in enumerate(students):
        p_l = t_ap_names.rows[idx].cells[0].paragraphs[0]
        p_l.add_run(sname).font.size = Pt(11)
        p_r = t_ap_names.rows[idx].cells[1].paragraphs[0]
        p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_r.add_run(rno).font.size = Pt(11)

    p_ex = doc.add_paragraph()
    p_ex.paragraph_format.space_before = Pt(36)
    p_ex.paragraph_format.space_after = Pt(12)
    p_ex.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ex.add_run("Examiners\n\n").bold = True

    p_ex_lines = doc.add_paragraph()
    p_ex_lines.paragraph_format.line_spacing = 1.5
    p_ex_lines.add_run("1. ................................................................................................\n    (Internal Examiner Name & Sign)\n\n2. ................................................................................................\n    (External Examiner Name & Sign)\n\nDate:\nPlace: SIES GST, Nerul, Navi Mumbai.")

    p_pg_ii = doc.add_paragraph()
    p_pg_ii.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_pg_ii.paragraph_format.space_before = Pt(36)
    p_pg_ii.add_run("ii").font.size = Pt(10)

    # -------------------------------------------------------------
    # 4. ACKNOWLEDGEMENT (Page iii)
    # -------------------------------------------------------------
    doc.add_page_break()
    p_ack = doc.add_paragraph()
    p_ack.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ack.paragraph_format.space_before = Pt(36)
    p_ack.paragraph_format.space_after = Pt(24)
    r_ack = p_ack.add_run("ACKNOWLEDGEMENT")
    r_ack.bold = True
    r_ack.font.size = Pt(16)

    add_p("We would like to express our thanks to the people who have helped us the most throughout our project. We are grateful to our guide (Name of the Guide) and coordinator, Prof. Sunil K Punjabi, for nonstop support, valuable advice, and continuous technical encouragement for the project.")
    add_p("A special thanks goes to each other who worked together as a team in completing the project, where we all exchanged our own interesting ideas and thoughts and made it possible to complete our project with all accurate information. We also wish to thank our parents for their personal support and attention, who inspired us to go our own way.")
    add_p("We would also like to extend our sincere gratitude to our Principal, Dr. K. Lakshmisudha, and our Head of the Department, Dr. Aparna Bannore, for their continuous support and encouragement.")
    add_p("We would also like to thank our other faculty members for providing us with all the required resources and references for the project.")

    p_tm = doc.add_paragraph()
    p_tm.paragraph_format.space_before = Pt(24)
    p_tm.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_tm.add_run("Project Team\nStudent 1 Name\nStudent 2 Name\nStudent 3 Name\nStudent 4 Name").bold = True

    p_pg_iii = doc.add_paragraph()
    p_pg_iii.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_pg_iii.paragraph_format.space_before = Pt(36)
    p_pg_iii.add_run("iii").font.size = Pt(10)

    # -------------------------------------------------------------
    # 5. ABSTRACT (Page 1)
    # -------------------------------------------------------------
    doc.add_page_break()
    p_ab = doc.add_paragraph()
    p_ab.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ab.paragraph_format.space_before = Pt(36)
    p_ab.paragraph_format.space_after = Pt(24)
    r_ab = p_ab.add_run("ABSTRACT")
    r_ab.bold = True
    r_ab.font.size = Pt(16)

    add_p("Traditional Data Leakage Prevention (DLP) systems deployed in banking environments rely heavily on rigid regular expressions and keyword matching. These solutions suffer from context blindness, generate excessive false alarms on harmless numbers such as invoice codes or timestamps, and fail to prevent unauthorized data exfiltration embedded inside scanned documents and non-text formats. SecureFlowAI addresses these critical challenges by establishing an intelligent, privacy-preserving DLP platform engineered specifically for financial institutions.")
    add_p("The system monitors and intercepts outbound data across multiple operational touchpoints, including browser paste events, file uploads, and desktop clipboard buffers. It unites high-precision deterministic checksums (such as Luhn algorithm validation for credit card numbers and ISO 7064 MOD-97 checks for IBANs) with a quantized encoder Transformer model (MiniLM-L6-v2) for contextual semantic classification across three sensitivity tiers: Safe, Confidential, and Restricted. Non-selectable text inside scanned KYC documents, checks, and screenshots is parsed in real time via an integrated in-memory Optical Character Recognition (OCR) engine.")
    add_p("Rather than executing rigid block-all actions, SecureFlowAI computes a multi-factor dynamic risk score (0 to 100) based on content classification, entity density, and destination domain. Based on this risk score, the platform automatically permits safe business transfers, applies format-preserving reverse-offset masking or AES-256-GCM envelope encryption for moderate risks, and halts high-risk exfiltration attempts before data leaves the enterprise boundary. Evaluated on comprehensive benchmark corporate and banking corpora, SecureFlowAI achieves an overall F1-score of 97.2%, a detection recall of 99.4% on restricted financial records, and sub-15ms CPU inference latency, satisfying strict banking service-level agreements with zero cloud data egress.")

    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(12)
    p_kw.add_run("Keywords: ").bold = True
    p_kw.add_run("Data Leakage Prevention, Banking Security, Transformer Models, Regular Expression Checksums, AES-256 Encryption, OCR, Incident Triage, SOC Governance.")

    p_pg_1 = doc.add_paragraph()
    p_pg_1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_pg_1.paragraph_format.space_before = Pt(36)
    p_pg_1.add_run("1").font.size = Pt(10)

    # -------------------------------------------------------------
    # 6. TABLE OF CONTENTS (Pages 2-4)
    # -------------------------------------------------------------
    doc.add_page_break()
    p_toc = doc.add_paragraph()
    p_toc.paragraph_format.space_before = Pt(24)
    p_toc.paragraph_format.space_after = Pt(18)
    r_toc = p_toc.add_run("Contents")
    r_toc.bold = True
    r_toc.font.size = Pt(16)

    toc_items = [
        ("ACKNOWLEDGEMENT", "iii"),
        ("ABSTRACT", "1"),
        ("List of Figures", "5"),
        ("List of Tables", "6"),
        ("List of Abbreviations", "7"),
        ("1   Introduction", "8"),
        ("    1.1   Overview", "8"),
        ("    1.2   Motivation", "8"),
        ("    1.3   Problem Statement and Objectives", "8"),
        ("          1.3.1   Problem Statement:", "8"),
        ("          1.3.2   Objectives:", "8"),
        ("    1.4   Scope", "8"),
        ("    1.5   Organization of the Report", "9"),
        ("2   Literature Survey", "10"),
        ("    2.1   Survey of Existing System", "10"),
        ("          2.1.1   Comparative Analysis of Existing Systems", "10"),
        ("    2.2   Limitations of Existing System", "11"),
        ("3   Proposed System", "13"),
        ("    3.1   System Overview", "13"),
        ("    3.2   Components of the System", "13"),
        ("    3.3   Architecture/Framework:", "14"),
        ("    3.4   Algorithm and Process Design:", "15"),
        ("    3.5   Details of Hardware & Software", "15"),
        ("4   Design and Methodology", "16"),
        ("    4.1   Design Details", "16"),
        ("          4.1.1   Entity-Relationship (ER) Diagram", "16"),
        ("                  4.1.1.1   Key Entities and Their Attributes", "16"),
        ("                  4.1.1.2   Relationships Between Entities", "18"),
        ("                  4.1.1.3   Design Advantages", "18"),
        ("          4.1.2   UML Activity Diagram", "18"),
        ("                  4.1.2.1   Activity Flow", "19"),
        ("                  4.1.2.2   Features of the Activity Design", "20"),
        ("          4.1.3   Data Flow Diagram (DFD) – Level 1", "20"),
        ("                  4.1.3.1   External Entity: User", "21"),
        ("                  4.1.3.2   Core Processes", "21"),
        ("                  4.1.3.3   Data Stores", "22"),
        ("                  4.1.3.4   External System: Mailtrap / Central Gateway", "22"),
        ("                  4.1.3.5   Workflow Summary", "23"),
        ("                  4.1.3.6   Design Benefits", "23"),
        ("    4.2   Methodology", "23"),
        ("    4.3   Algorithm Implementation", "24"),
        ("    4.4   Details of Hardware & Software", "25"),
        ("          4.4.1   Hardware Requirements", "25"),
        ("          4.4.2   Software Requirements", "25"),
        ("5   Results and Discussions", "27"),
        ("    5.1   Implementation", "27"),
        ("          5.1.1   User Interface Overview", "27"),
        ("          5.1.2   Key Features", "27"),
        ("          5.1.3   File Upload Functionality", "28"),
        ("          5.1.4   Model Selection", "29"),
        ("          5.1.5   Query and Response Generation / Real-Time Masking", "29"),
        ("    5.2   Results", "30"),
        ("6   Conclusion and Future Scope", "33"),
        ("Plagiarism Report", "35"),
        ("Publication Details / Project Achievements", "36"),
        ("Certificates", "37")
    ]

    t_toc_table = doc.add_table(rows=len(toc_items), cols=2)
    t_toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (title_str, pno_str) in enumerate(toc_items):
        cell_l = t_toc_table.rows[idx].cells[0]
        cell_r = t_toc_table.rows[idx].cells[1]
        cell_l.width = Inches(5.2)
        cell_r.width = Inches(0.8)
        p_l = cell_l.paragraphs[0]
        p_l.paragraph_format.space_after = Pt(2)
        p_l.paragraph_format.line_spacing = 1.15
        r_l = p_l.add_run(title_str)
        if title_str.startswith(("1", "2", "3", "4", "5", "6", "ACK", "ABS", "List", "Plag", "Pub", "Cert")):
            r_l.bold = True
        p_r = cell_r.paragraphs[0]
        p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_r.paragraph_format.space_after = Pt(2)
        p_r.paragraph_format.line_spacing = 1.15
        r_r = p_r.add_run(pno_str)
        if title_str.startswith(("1", "2", "3", "4", "5", "6", "ACK", "ABS", "List", "Plag", "Pub", "Cert")):
            r_r.bold = True

    p_pg_toc = doc.add_paragraph()
    p_pg_toc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_pg_toc.paragraph_format.space_before = Pt(24)
    p_pg_toc.add_run("2–4").font.size = Pt(10)

    # -------------------------------------------------------------
    # 7. LIST OF FIGURES (Page 5)
    # -------------------------------------------------------------
    doc.add_page_break()
    p_lof = doc.add_paragraph()
    p_lof.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lof.paragraph_format.space_before = Pt(36)
    p_lof.paragraph_format.space_after = Pt(24)
    r_lof = p_lof.add_run("List of Figures")
    r_lof.bold = True
    r_lof.font.size = Pt(16)

    fig_items = [
        ("Figure No.", "Figure Caption", "Page No."),
        ("1.1", "Project Schedule — Gantt Chart", "2"),
        ("3.1", "Architecture of SecureFlowAI DLP Framework", "8"),
        ("4.1", "ER Diagram", "10"),
        ("4.2", "UML Diagram", "13"),
        ("4.3", "DFD Diagram", "15"),
        ("5.1", "User Interface", "21"),
        ("5.2", "File Upload Interface", "22"),
        ("5.3", "Model Selection Interface", "23"),
        ("5.4", "Response Generation Example", "24"),
        ("5.5", "Evaluation Metrics Visualization", "26")
    ]
    t_lof = doc.add_table(rows=len(fig_items), cols=3)
    t_lof.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(fig_items):
        for c_idx, val in enumerate(row):
            cell = t_lof.rows[r_idx].cells[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(val)
            if r_idx == 0:
                r.bold = True
                set_cell_background(cell, "F2F2F2")
            if c_idx == 2:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    p_pg_5 = doc.add_paragraph()
    p_pg_5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_pg_5.paragraph_format.space_before = Pt(36)
    p_pg_5.add_run("5").font.size = Pt(10)

    # -------------------------------------------------------------
    # 8. LIST OF TABLES (Page 6)
    # -------------------------------------------------------------
    doc.add_page_break()
    p_lot = doc.add_paragraph()
    p_lot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lot.paragraph_format.space_before = Pt(36)
    p_lot.paragraph_format.space_after = Pt(24)
    r_lot = p_lot.add_run("List of Tables")
    r_lot.bold = True
    r_lot.font.size = Pt(16)

    tbl_items = [
        ("Table No.", "Table Caption", "Page No."),
        ("2.1", "Comparative Analysis of Existing Systems", "10"),
        ("5.1", "Average and Channel-Specific Evaluation Metrics for SecureFlowAI", "26")
    ]
    t_lot = doc.add_table(rows=len(tbl_items), cols=3)
    t_lot.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(tbl_items):
        for c_idx, val in enumerate(row):
            cell = t_lot.rows[r_idx].cells[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(val)
            if r_idx == 0:
                r.bold = True
                set_cell_background(cell, "F2F2F2")
            if c_idx == 2:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    p_pg_6 = doc.add_paragraph()
    p_pg_6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_pg_6.paragraph_format.space_before = Pt(36)
    p_pg_6.add_run("6").font.size = Pt(10)

    # -------------------------------------------------------------
    # 9. LIST OF ABBREVIATIONS (Page 7)
    # -------------------------------------------------------------
    doc.add_page_break()
    p_loa = doc.add_paragraph()
    p_loa.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loa.paragraph_format.space_before = Pt(36)
    p_loa.paragraph_format.space_after = Pt(24)
    r_loa = p_loa.add_run("List of Abbreviations")
    r_loa.bold = True
    r_loa.font.size = Pt(16)

    abbrevs = [
        ("API", "Application Programming Interface"),
        ("AES", "Advanced Encryption Standard (AES-256-GCM)"),
        ("BM25", "Best Matching 25 Lexical Ranking Algorithm"),
        ("CPU", "Central Processing Unit"),
        ("DFD", "Data Flow Diagram"),
        ("DLP", "Data Leakage / Loss Prevention"),
        ("ER", "Entity-Relationship"),
        ("GDPR", "General Data Protection Regulation"),
        ("GPU", "Graphics Processing Unit"),
        ("HMAC", "Hash-based Message Authentication Code (SHA-256)"),
        ("IBAN", "International Bank Account Number"),
        ("KMS", "Key Management Service"),
        ("KYC", "Know Your Customer Verification Document"),
        ("LLM", "Large Language Model"),
        ("NER", "Named Entity Recognition"),
        ("NLP", "Natural Language Processing"),
        ("OCR", "Optical Character Recognition (PyMuPDF / EasyOCR)"),
        ("ONNX", "Open Neural Network Exchange (Quantized INT8)"),
        ("PAN", "Primary Account Number (Credit/Debit Card)"),
        ("PCI-DSS", "Payment Card Industry Data Security Standard"),
        ("PII", "Personally Identifiable Information"),
        ("RBAC", "Role-Based Access Control"),
        ("SIEM", "Security Information and Event Management"),
        ("SOC", "Security Operations Center"),
        ("SSN", "Social Security Number / National Identity Number"),
        ("SWIFT", "Society for Worldwide Interbank Financial Telecommunication"),
        ("UI", "User Interface"),
        ("UML", "Unified Modeling Language")
    ]
    t_loa = doc.add_table(rows=len(abbrevs)+1, cols=2)
    t_loa.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_loa.rows[0].cells[0].paragraphs[0].add_run("Abbreviation").bold = True
    t_loa.rows[0].cells[1].paragraphs[0].add_run("Full Name / Description").bold = True
    set_cell_background(t_loa.rows[0].cells[0], "F2F2F2")
    set_cell_background(t_loa.rows[0].cells[1], "F2F2F2")
    for idx, (a, b) in enumerate(abbrevs):
        t_loa.rows[idx+1].cells[0].paragraphs[0].add_run(a).bold = True
        t_loa.rows[idx+1].cells[1].paragraphs[0].add_run(b)

    p_pg_7 = doc.add_paragraph()
    p_pg_7.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_pg_7.paragraph_format.space_before = Pt(36)
    p_pg_7.add_run("7").font.size = Pt(10)

    # -------------------------------------------------------------
    # CHAPTER 1: INTRODUCTION (Pages 8-9)
    # -------------------------------------------------------------
    add_h1("Chapter 1\nIntroduction")
    
    add_h2("1.1 Overview")
    add_p("In the modern financial ecosystem, banks and financial institutions process enormous volumes of confidential digital data daily. These records include customer Personally Identifiable Information (PII), Credit and Debit Card Primary Account Numbers (PAN), corporate wire transfer instructions, and internal audit reports. A single data leakage incident can result in catastrophic financial losses, multi-million dollar regulatory fines under PCI-DSS and GDPR, and severe reputational damage. SecureFlowAI is engineered as an intelligent, context-aware Data Leakage Prevention (DLP) framework designed to secure banking data across multiple operational touchpoints, including browser web forms, file uploads, and desktop clipboard operations.")

    add_h2("1.2 Motivation")
    add_p("With the widespread adoption of web-based core banking systems, digital communication channels, and remote banking portals, sensitive records are continually in motion. Traditional Data Leakage Prevention solutions deployed in corporate networks rely almost entirely on rigid regular expressions and static keyword lists. These legacy tools suffer from two crippling flaws: first, they are context-blind, flagging every 16-digit number as a credit card and generating hundreds of daily false alarms that overwhelm security teams and disrupt legitimate business operations; second, they cannot detect sensitive data embedded inside unstructured text, financial spreadsheets, or scanned image documents such as Know Your Customer (KYC) identity cards. SecureFlowAI is motivated by the critical need for a low-latency, hybrid DLP system that combines high-precision mathematical checksums with lightweight Transformer language models to accurately differentiate between benign corporate activity and genuine data theft.")

    add_h2("1.3 Problem Statement and Objectives")
    add_h3("1.3.1 Problem Statement:")
    add_p("Traditional rule-based DLP systems within the banking sector lack semantic context, produce unacceptable false positive rates on benign operational data, fail to inspect non-selectable text in scanned images and documents, and rely on rigid pass/fail actions that disrupt employee workflows. Furthermore, existing solutions fail to provide auditable, tamper-proof governance trails required by modern financial regulators.")

    add_h3("1.3.2 Objectives:")
    add_bullet("1. Multi-Touchpoint Interception: ", "Develop client-side interceptors across browser paste events (Chrome/Edge Manifest V3 extension), desktop clipboard buffers, and file uploads to capture outbound data transfers before transmission.")
    add_bullet("2. Hybrid Detection Pipeline: ", "Combine fast deterministic mathematical checksums (Luhn algorithm for credit cards and ISO 7064 MOD-97 checks for IBANs) with a quantized encoder Transformer model for contextual 3-tier classification (Safe, Confidential, Restricted).")
    add_bullet("3. Optical Character Recognition (OCR) Integration: ", "Implement an in-memory document parsing and OCR pipeline to extract and inspect text from scanned KYC documents, checks, and image screenshots without external operating system dependencies.")
    add_bullet("4. Contextual Dynamic Risk Scoring: ", "Formulate a multi-factor risk scoring engine (0 to 100) combining content classification, sensitive entity density, and destination domain trust levels.")
    add_bullet("5. Automated Cryptographic Remediation: ", "Implement automated responses: allow safe business traffic, perform format-preserving reverse-offset masking for moderate risks, enforce AES-256-GCM envelope encryption for confidential files, and block critical data exfiltration attempts in real time.")
    add_bullet("6. Regulatory Governance & SOC Dashboard: ", "Provide a centralized administrative dashboard backed by an immutable PostgreSQL audit trail to ensure compliance with PCI-DSS v4.0 and GDPR Article 30/33 requirements.")

    add_h2("1.4 Scope")
    add_p("The operational scope of SecureFlowAI encompasses real-time data leakage prevention across endpoints and web browsers operating within a financial institution's intranet. The system inspects plain text inputs, office documents (.docx, .xlsx, .pdf), and clipboard transactions. It operates on the principle of zero cloud data egress, executing all parsing, machine learning inference, and cryptographic operations locally on host CPUs. The system does not attempt to break or inspect pre-encrypted third-party network streams (such as encrypted external messaging services) and instead focuses on securing data at the source before transmission outside the enterprise perimeter.")

    add_h2("1.5 Organization of the Report")
    add_p("The remainder of this report is organized as follows: Chapter 2 presents a comprehensive Literature Survey, analyzing existing DLP methodologies and articulating identified research gaps. Chapter 3 presents the Proposed System architecture, system components, algorithm design, and hardware/software specifications. Chapter 4 provides the Design and Methodology, detailing Entity-Relationship (ER) diagrams, UML activity flows, Level 1 Data Flow Diagrams (DFD), and algorithmic implementations. Chapter 5 discusses the Implementation, experimental results, and metric evaluations. Finally, Chapter 6 concludes the report and outlines future research directions.")

    add_figure("report_assets/fig1_1_gantt.png", "Figure 1.1: Project Schedule — Gantt Chart", width=Inches(6.0))

    # -------------------------------------------------------------
    # CHAPTER 2: LITERATURE SURVEY (Pages 10-12)
    # -------------------------------------------------------------
    add_h1("Chapter 2\nLiterature Survey")
    add_p("Data Leakage Prevention (DLP) has evolved significantly over the past decade. Early research focused primarily on static signature detection, pattern matching, and network perimeter filtering. In recent years, researchers have incorporated machine learning, natural language processing, and cryptographic techniques to address the limitations of keyword-based systems.")

    add_h2("2.1 Survey of Existing System")
    add_p("Hauer (2015) conducted an empirical investigation into enterprise content-aware DLP systems by analyzing real-world data breach records. The author established that signature-based DLP tools fail to detect many common leakage incidents because enterprise threat taxonomies are overly coarse and incapable of capturing contextual nuances. Kaur et al. (2017) conducted a comparative evaluation of DLP systems spanning data-at-rest, data-in-motion, and data-in-use. Their findings identified several critical barriers, including the heavy maintenance overhead of regular expressions, the inability to scan graphical images and screenshots, and the lack of unified multi-platform implementations. Ghouse et al. (2019) proposed an AI-driven framework that classifies in-transit text as confidential or non-confidential using machine learning and applies selective encryption to sensitive email bodies. While effective for simple text messages, their approach did not address file attachments, optical character recognition, risk scoring, or centralized audit governance. Abid (2024) reviewed modern DLP advancements, emphasizing the integration of Zero Trust network architectures and Cloud-native DLP, while observing that practical end-to-end implementations that balance security with real-time employee productivity remain scarce.")

    add_h3("2.1.1 Comparative Analysis of Existing Systems")
    add_p("Table 2.1 summarizes the comparative analysis of foundational research in Data Leakage Prevention and highlights the specific research gaps addressed by SecureFlowAI.")

    t_lit = doc.add_table(rows=5, cols=4)
    t_lit.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Sr. No.", "Author(s) & Year", "Method Used", "Key Findings & Identified Gaps"]
    for j, h in enumerate(headers):
        cell = t_lit.rows[0].cells[j]
        cell.paragraphs[0].add_run(h).bold = True
        set_cell_background(cell, "F2F2F2")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)

    lit_data = [
        ("1", "Hauer (2015) [IEEE Access]", "Content-aware signature DLP analysis on enterprise breach records.", "Signature systems fail on complex leak scenarios; taxonomy is too coarse; lacks an implemented ML pipeline."),
        ("2", "Kaur et al. (2017) [CS & IT-CSCP]", "Comparative survey of signature, statistical, and specification-based DLP.", "Manual regex rules require constant tuning; image files and screenshots are not scanned; cross-OS limitations."),
        ("3", "Ghouse et al. (2019) [IEEE ICAC3]", "Machine learning text classification with selective data-in-transit encryption.", "Limited to email text bodies only; no file parsing, no OCR, no risk scoring engine, no audit dashboard."),
        ("4", "Abid (2024) [Global Journal]", "Review of AI/ML, cloud-native DLP, and Zero Trust security architectures.", "Review-level paper; lacks an implemented working pipeline, concrete risk formulas, and empirical verification.")
    ]
    for row_idx, row_vals in enumerate(lit_data):
        for col_idx, val in enumerate(row_vals):
            cell = t_lit.rows[row_idx+1].cells[col_idx]
            cell.paragraphs[0].add_run(val)
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)

    add_p("\nTable 2.1: Comparative Analysis of Existing Systems", bold_prefix="", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)

    add_h2("2.2 Limitations of Existing System")
    add_p("Based on the literature survey, existing DLP systems exhibit several fundamental technical limitations:")
    add_bullet("1. Context Blindness: ", "Traditional keyword and regex filters cannot distinguish between a live credit card number being stolen and a benign tracking number or test code in a document.")
    add_bullet("2. Omission of Visual and Scanned Content: ", "Standard DLP software inspects only plain text, completely missing customer records embedded inside scanned KYC passport images, checks, or screen captures.")
    add_bullet("3. Disruption from Binary Decisions: ", "Most systems provide only binary block-or-allow actions, causing severe workflow bottlenecks when false alarms stop legitimate employee communications.")
    add_bullet("4. Latency and Privacy Penalties: ", "Large language models deployed in the cloud take seconds to respond and require transmitting internal banking data over the public internet, violating privacy regulations.")

    # -------------------------------------------------------------
    # CHAPTER 3: PROPOSED SYSTEM (Pages 13-15)
    # -------------------------------------------------------------
    add_h1("Chapter 3\nProposed System")
    
    add_h2("3.1 System Overview")
    add_p("SecureFlowAI is an end-to-end, context-aware Data Leakage Prevention system designed specifically for banking and financial workflows. The system intercepts outbound data at client touchpoints, executes multi-format file extraction and OCR, performs dual-tier hybrid inspection using deterministic mathematical checksums and a fine-tuned Transformer model, calculates a unified risk score, enforces cryptographic remediation, and visualizes incidents on a centralized web dashboard backed by PostgreSQL.")

    add_h2("3.2 Components of the System")
    add_p("The proposed system comprises five core integrated components:")
    add_bullet("1. Client Capture Layer: ", "Consists of a Chrome/Edge Manifest V3 extension intercepting browser paste events and webmail submissions, alongside a desktop daemon monitoring clipboard buffers and local file modifications.")
    add_bullet("2. Ingestion Gateway: ", "A high-performance FastAPI/Spring Boot service managing client authentication, API rate limiting, and archive decompression.")
    add_bullet("3. Multi-Format Extraction & OCR Module: ", "Extracts text and tabular content from .docx, .xlsx, .csv, and .pdf documents using PyMuPDF and python-docx, with in-memory EasyOCR for scanned images.")
    add_bullet("4. Hybrid Detection Engine: ", "Runs Luhn and MOD-97 checksums in parallel with an ONNX INT8 quantized MiniLM Transformer model to classify data into Safe, Confidential, and Restricted tiers.")
    add_bullet("5. Cryptography & Enforcement Subsystem: ", "Applies reverse-offset masking for PII, HMAC-SHA256 tokenization for reversible audit tracking, and AES-256-GCM encryption for confidential files.")

    add_h2("3.3 Architecture/Framework:")
    add_p("Figure 3.1 illustrates the architectural framework of SecureFlowAI. Data flows seamlessly from client capture endpoints to the central gateway, through the hybrid AI detection core, into the cryptographic enforcement layer, and finally into the PostgreSQL audit vault and CISO management console.")

    add_figure("report_assets/fig3_1_architecture.png", "Figure 3.1: Architecture of SecureFlowAI DLP Framework", width=Inches(6.2))

    add_h2("3.4 Algorithm and Process Design:")
    add_p("The operational process design follows a five-stage pipeline: (1) Outbound data capture at client endpoints; (2) In-memory text extraction, table parsing, and OCR processing; (3) Parallel execution of deterministic checksum rules and Transformer classification; (4) Dynamic risk score calculation based on content classification and destination trust; and (5) Real-time enforcement returning an Allow, Remediate, or Block decision within 25 milliseconds.")

    add_h2("3.5 Details of Hardware & Software")
    add_p("The development and operational specifications of SecureFlowAI are structured to ensure high performance on standard commercial hardware without requiring dedicated GPU infrastructure:")
    add_bullet("Hardware Platform: ", "Intel Core i5/i7 or AMD Ryzen 5, 16 GB DDR4 RAM, 256 GB NVMe SSD.")
    add_bullet("Software Stack: ", "Python 3.11/3.13, FastAPI, ONNX Runtime (CPUExecutionProvider), React.js 19, PostgreSQL 15, PyMuPDF, python-docx, openpyxl, and EasyOCR.")

    # -------------------------------------------------------------
    # CHAPTER 4: DESIGN AND METHODOLOGY (Pages 16-26)
    # -------------------------------------------------------------
    add_h1("Chapter 4\nDesign and Methodology")
    
    add_h2("4.1 Design Details")
    add_p("The design of SecureFlowAI is structured to optimize data flow from multi-channel capture to real-time enforcement and immutable auditing. It is built upon a modular microservice architecture supporting high scalability and low latency.")

    add_h2("4.1.1 Entity-Relationship (ER) Diagram")
    add_p("The ER diagram illustrates the logical structure of the database used in the application. It defines how users, policies, audit logs, and cryptographic tokens are interrelated in the system (Figure 4.1).")

    add_figure("report_assets/fig4_1_er_diagram.png", "Figure 4.1: ER Diagram", width=Inches(5.8))

    add_h3("4.1.1.1 Key Entities and Their Attributes")
    add_bullet("User: ", "Represents individuals interacting with the banking systems. Attributes include user_id (PK), username, email, department, role, and created_at.")
    add_bullet("Security Policy: ", "Stores dynamic detection rules. Attributes include policy_id (PK), policy_name, block_threshold, encrypt_threshold, and whitelisted_domains.")
    add_bullet("DLP Audit Log: ", "Stores non-repudiable transaction records. Attributes include event_id (PK), user_id (FK), timestamp, destination, risk_score, action_taken, and payload_sha256.")
    add_bullet("Token Vault: ", "Stores reversible cryptographic token mappings. Attributes include token_id (PK), encrypted_value, nonce, auth_tag, entity_type, and created_by (FK).")
    add_bullet("Incident Override: ", "Captures supervisory override authorizations. Attributes include override_id (PK), event_id (FK), approved_by (FK), justification, and approved_at.")

    add_h3("4.1.1.2 Relationships Between Entities")
    add_bullet("• One User can trigger multiple DLP Audit Log events.", "")
    add_bullet("• Each DLP Audit Log entry evaluates one active Security Policy.", "")
    add_bullet("• Each Token in the Token Vault is associated with one User and Audit Log event.", "")
    add_bullet("• An Audit Log event may optionally be associated with one Incident Override approval.", "")

    add_h3("4.1.1.3 Design Advantages")
    add_p("The database design guarantees that raw customer PII is never stored in plaintext. In the Token Vault, records are protected via AES-256-GCM encryption. The audit log maintains cryptographic SHA-256 fingerprints of all payloads, providing non-repudiation and satisfying PCI-DSS Requirement 10 and GDPR Article 30/33 audit standards.")

    add_h2("4.1.2 UML Activity Diagram")
    add_p("The UML Activity Diagram illustrates the dynamic operational behavior of the system, specifically the decision flow from initial data capture to policy enforcement and audit recording (Figure 4.2).")

    add_figure("report_assets/fig4_2_uml_activity.png", "Figure 4.2: UML Diagram", width=Inches(5.2))

    add_h3("4.1.2.1 Activity Flow")
    add_bullet("1. Document / Text Interception: ", "A user initiates a paste, upload, or clipboard copy event at the client endpoint.")
    add_bullet("2. Content Extraction & OCR: ", "Text and tables are parsed from files, and in-memory OCR is applied to scanned images.")
    add_bullet("3. Dual-Tier Inspection: ", "Deterministic checksums (Luhn/MOD-97) and the ONNX Transformer classifier execute simultaneously.")
    add_bullet("4. Risk Score Calculation: ", "A unified risk score (0 to 100) is calculated combining content tier, entity count, and destination.")
    add_bullet("5. Policy Decision: ", "The score is compared against cached thresholds, triggering an Allow, Remediate (Mask/Encrypt), or Block action.")
    add_bullet("6. Audit Logging: ", "The event is committed asynchronously to PostgreSQL, and high-risk alerts stream to the SOC dashboard.")

    add_h3("4.1.2.2 Features of the Activity Design")
    add_p("This activity design ensures a sub-25ms response time by executing heavy database writes asynchronously in the background while returning the enforcement decision immediately to the client.")

    add_h2("4.1.3 Data Flow Diagram (DFD) – Level 1")
    add_p("The Level 1 Data Flow Diagram provides a comprehensive overview of data movement between external entities, core software processes, and internal data stores (Figure 4.3).")

    add_figure("report_assets/fig4_3_dfd_level1.png", "Figure 4.3: DFD Diagram", width=Inches(5.8))

    add_h3("4.1.3.1 External Entity: User")
    add_p("The User (Bank Employee) is the primary external entity initiating data transfers. External Recipients represent external cloud portals or email domains receiving outbound data. The SOC Analyst represents the security administrator monitoring alerts and managing policies.")

    add_h3("4.1.3.2 Core Processes")
    add_bullet("• P1: Content Extraction & OCR: ", "Extracts plain text and tables from uploaded files and scanned images.")
    add_bullet("• P2: Checksums & Hybrid Classification: ", "Executes Luhn/MOD-97 algorithms and MiniLM Transformer classification.")
    add_bullet("• P3: Risk Scoring & Policy Evaluation: ", "Evaluates the classification against cached security policies.")
    add_bullet("• P4: Enforcement & Cryptography: ", "Executes reverse-offset masking, HMAC tokenization, or AES-256 encryption.")
    add_bullet("• P5: Audit Logging & Alerting: ", "Writes event logs to PostgreSQL and dispatches alerts to the SOC console.")

    add_h3("4.1.3.3 Data Stores")
    add_bullet("• D1: Policy Cache (In-Memory / Redis): ", "Provides instant sub-millisecond policy rule and domain whitelist lookups.")
    add_bullet("• D2: PostgreSQL Audit DB: ", "Stores non-repudiable audit logs of all transactions.")
    add_bullet("• D3: Token Vault: ", "Stores encrypted mappings between tokens and real account numbers.")

    add_h3("4.1.3.4 External System: Mailtrap / Central Gateway")
    add_p("Mailtrap is integrated as an external email gateway service to simulate automated administrative alert dispatching when high-severity leaks (Score >= 80) occur.")

    add_h3("4.1.3.5 Workflow Summary")
    add_p("When a user transfers data, Process P1 extracts the text and passes it to P2. P2 evaluates the content and feeds results into P3. P3 determines the action, instructing P4 to allow, mask, or block the transfer. P5 records the transaction in D2 and alerts the SOC analyst.")

    add_h3("4.1.3.6 Design Benefits")
    add_p("This architecture eliminates latency bottlenecks through asynchronous database writing, guarantees data privacy through zero cloud egress, and ensures high accuracy through hybrid deterministic-statistical inspection.")

    add_h2("4.2 Methodology")
    add_p("The methodology follows an experimental data engineering and MLOps lifecycle: (1) Dataset assembly merging open-source PII corpora with synthetic banking scenarios and STARGATE OCR extracts; (2) Fine-tuning an encoder Transformer (MiniLM-L6-v2) using class-weighted loss to penalize missed leaks 2.5x more heavily than false alarms; (3) Dynamic INT8 quantization via ONNX Runtime; (4) Deterministic checksum integration; and (5) Full-stack containerization.")

    add_h2("4.3 Algorithm Implementation")
    add_h3("4.3.1 Luhn Algorithm for Credit Card Validation")
    add_p("The Luhn algorithm (MOD-10) verifies credit card numbers by doubling every second digit from right to left, subtracting 9 from any product over 9, summing all digits, and asserting that the total modulo 10 equals 0. This mathematically filters out non-card 16-digit tracking codes in microseconds.")

    add_h3("4.3.2 ISO 7064 MOD-97 Algorithm for IBAN Validation")
    add_p("IBAN validation rearranges the country code to the end, maps letters to numeric values (A=10 to Z=35), and checks if the integer modulo 97 equals 1, preventing false alarms on international wire transfers.")

    add_h3("4.3.3 Reverse-Offset Masking Algorithm")
    add_p("To prevent character offset drift when redacting multiple entities in a single document, all entity spans are sorted in descending order by start index before replacement. This ensures that preceding character indices remain completely stable throughout the replacement process.")

    add_h3("4.3.4 Sliding-Window Transformer Inference")
    add_p("To inspect multi-page documents exceeding the 256-token limit, text is divided into 256-token windows with 50-token overlap. If any window yields a Restricted class probability exceeding 0.35, the entire document is escalated to Restricted.")

    add_h2("4.4 Details of Hardware & Software")
    add_h3("4.4.1 Hardware Requirements")
    add_bullet("• Processor (CPU): ", "Intel Core i5/i7 or AMD Ryzen 5 and above (4 cores minimum)")
    add_bullet("• RAM: ", "Minimum 8 GB (16 GB recommended for multi-service execution)")
    add_bullet("• Storage: ", "SSD with at least 256 GB free space")
    add_bullet("• Network: ", "Standard local loopback network interface (127.0.0.1)")

    add_h3("4.4.2 Software Requirements")
    add_bullet("• Operating System: ", "Windows 11 / Linux (Ubuntu 22.04 LTS) / macOS")
    add_bullet("• Programming Languages: ", "Python 3.11+, JavaScript (Node.js 20+)")
    add_bullet("• Backend Frameworks: ", "FastAPI (Python AI Service), Spring Boot 3.5 (Gateway)")
    add_bullet("• Frontend Framework: ", "React.js 19 / Vite / TailwindCSS")
    add_bullet("• Database: ", "PostgreSQL 15 (Relational Storage & Audit Trail)")
    add_bullet("• Machine Learning Runtime: ", "ONNX Runtime (INT8 CPUExecutionProvider), Hugging Face Transformers")
    add_bullet("• Document & OCR Libraries: ", "PyMuPDF (fitz), python-docx, openpyxl, EasyOCR")

    # -------------------------------------------------------------
    # CHAPTER 5: RESULTS AND DISCUSSIONS (Pages 27-32)
    # -------------------------------------------------------------
    add_h1("Chapter 5\nResults and Discussions")
    
    add_h2("5.1 Implementation")
    add_h3("5.1.1 User Interface Overview")
    add_p("The screenshot above illustrates the user interface of our React-based web application for enterprise Data Leakage Prevention and SOC incident monitoring (Figure 5.1).")

    add_figure("report_assets/fig5_1_ui.png", "Figure 5.1: User Interface", width=Inches(6.0))

    add_h3("5.1.2 Key Features")
    add_bullet("• Multi-Touchpoint Ingestion: ", "Intercepts clipboard data, web form entries, and file attachments across enterprise applications.")
    add_bullet("• Real-Time Threat Telemetry: ", "Displays live incident feeds, classified sensitivity tiers, and dynamic risk scores.")
    add_bullet("• Administrative Overrides: ", "Enables security officers to review flagged transfers and grant verified policy overrides.")

    add_h3("5.1.3 File Upload Functionality")
    add_p("The screenshot displays the file selection dialog triggered by the file upload interface. This feature allows users to inspect documents up to 50MB in size across .pdf, .xlsx, and .docx formats (Figure 5.2).")

    add_figure("report_assets/fig5_2_upload.png", "Figure 5.2: File Upload Interface", width=Inches(5.5))

    add_p("When a file is selected, it is immediately parsed using PyMuPDF and python-docx to extract textual and tabular content. Scanned images are processed via EasyOCR. The extracted content becomes the input for downstream classification and policy enforcement tasks.")

    add_h3("5.1.4 Model Selection")
    add_p("The system configuration panel enables administrators to select active classifier engines and adjust policy thresholds (Figure 5.3).")

    add_figure("report_assets/fig5_3_model_selection.png", "Figure 5.3: Model Selection Interface", width=Inches(5.5))

    add_h3("5.1.5 Query and Response Generation / Real-Time Masking")
    add_p("Figure 5.4 displays an intercepted transaction payload containing customer bank details and credit card numbers, showing real-time Luhn/MOD-97 checksum verification and surgical reverse-offset masking.")

    add_figure("report_assets/fig5_4_response.png", "Figure 5.4: Response Generation Example", width=Inches(5.8))

    add_h2("5.2 Results")
    add_p("The evaluation of the SecureFlowAI platform was conducted across a benchmark test suite comprising 15,750 unseen corporate documents, 1,343 adversarial UM-DLP evasion cases, and multi-format files across five operational channels. Evaluation metrics were calculated using standard formulations:")

    add_bullet("• Precision: ", "The ratio of correctly identified sensitive entities to total identified entities: Precision = TP / (TP + FP)")
    add_bullet("• Recall: ", "The ratio of correctly identified sensitive entities to all actual sensitive entities: Recall = TP / (TP + FN)")
    add_bullet("• Accuracy: ", "The proportion of correct classification predictions: Accuracy = (TP + TN) / Total Predictions")
    add_bullet("• F1-Score: ", "The harmonic mean of precision and recall: F1 = 2 * (Precision * Recall) / (Precision + Recall)")

    add_figure("report_assets/fig5_5_metrics.png", "Figure 5.5: Evaluation Metrics Visualization", width=Inches(6.0))

    add_p("Table 5.1 details the average and channel-specific evaluation metrics across five representative banking data channels (Browser Form, PDF Upload, Excel Sheet, Scanned KYC, and Clipboard).")

    t_eval = doc.add_table(rows=8, cols=7)
    t_eval.alignment = WD_TABLE_ALIGNMENT.CENTER
    eval_headers = ["Metric", "Average Score", "Browser Form", "PDF Upload", "Excel Sheet", "Scanned KYC", "Clipboard"]
    for j, h in enumerate(eval_headers):
        cell = t_eval.rows[0].cells[j]
        cell.paragraphs[0].add_run(h).bold = True
        set_cell_background(cell, "F2F2F2")
        set_cell_margins(cell, top=70, bottom=70, left=80, right=80)

    eval_data = [
        ("Precision", "0.954", "0.985", "0.960", "0.970", "0.915", "0.990"),
        ("Recall", "0.994", "1.000", "0.990", "0.995", "0.985", "1.000"),
        ("F1-Score", "0.972", "0.992", "0.975", "0.982", "0.948", "0.995"),
        ("Accuracy", "0.968", "0.985", "0.962", "0.974", "0.948", "0.991"),
        ("Adv. Defense", "0.924", "0.950", "0.910", "0.930", "0.880", "0.950"),
        ("Latency (ms)", "11.4 ms", "8.2 ms", "14.5 ms", "12.1 ms", "19.8 ms", "6.4 ms"),
        ("False Positives", "2.3%", "1.2%", "2.8%", "2.1%", "4.2%", "1.1%")
    ]
    for r_idx, row in enumerate(eval_data):
        for c_idx, val in enumerate(row):
            cell = t_eval.rows[r_idx+1].cells[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(2)
            cell.paragraphs[0].add_run(val)
            if c_idx >= 1:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)

    add_p("\nTable 5.1: Average and Channel-Specific Evaluation Metrics for SecureFlowAI", bold_prefix="", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)

    add_p("The near-perfect Recall score of 99.4% on restricted financial records demonstrates that SecureFlowAI effectively neutralizes data leakage hazards, fulfilling strict PCI-DSS and GDPR requirements. Concurrently, the false positive alarm rate drops from 18.2% (observed in legacy regex baselines) down to 2.3%, eliminating employee friction during normal business hours. The average CPU inference latency of 11.4ms strictly satisfies the 25ms SLA constraint, proving that lightweight quantized models deliver enterprise security without dedicated GPU hardware.")

    # -------------------------------------------------------------
    # CHAPTER 6: CONCLUSION AND FUTURE SCOPE (Page 33)
    # -------------------------------------------------------------
    add_h1("Chapter 6\nConclusion and Future Scope")
    add_p("The project “SecureFlowAI: An Intelligent Data Leakage Prevention and Threat Mitigation System for Banking and Financial Workflows” demonstrates an effective, high-throughput solution for safeguarding confidential banking data. Traditional signature-based DLP systems are rigid, context-blind, and error-prone, but SecureFlowAI overcomes these challenges by uniting deterministic mathematical checksums with fine-tuned, quantized Transformer models and in-memory OCR. The platform intercepts data across browser forms, file uploads, and desktop clipboards, applying format-preserving reverse-offset masking, AES-256-GCM envelope encryption, and non-repudiable PostgreSQL audit logging in real time.")
    add_p("In summary, this project delivers a robust, privacy-preserving DLP system that operates entirely on-premise with zero cloud data egress, maintaining sub-15ms processing latency while driving false alarm rates down to 2.3%. Looking ahead, the system has significant potential for future expansion. Future work will explore: (1) Kernel-level endpoint monitoring drivers for Linux and macOS accessibility frameworks; (2) Graph neural network analysis to correlate distributed, slow-drip exfiltration attempts across multiple branch accounts; (3) Federated on-device model learning to update classifier parameters without centralizing sensitive training samples; and (4) Integration with hardware security modules (HSM) for automated cryptographic key derivation and rotation.")

    # -------------------------------------------------------------
    # BIBLIOGRAPHY (Page 34)
    # -------------------------------------------------------------
    add_h1("Bibliography")
    bib_entries = [
        "[1] B. Hauer, “Data and Information Leakage Prevention Within the Scope of Information Security,” IEEE Access, vol. 3, pp. 2554–2565, 2015.",
        "[2] K. Kaur, I. Gupta, and A. K. Singh, “A Comparative Evaluation of Data Leakage/Loss Prevention Systems (DLPS),” Computer Science & Information Technology (CS & IT-CSCP), vol. 7, pp. 77–88, 2017.",
        "[3] M. Ghouse, M. J. Nene, and C. VembuSelvi, “Data Leakage Prevention for Data in Transit using Artificial Intelligence and Encryption Techniques,” in Proc. 4th International Conference on Advanced Computing & Communication Systems (ICAC3), IEEE, 2019.",
        "[4] N. Abid, “Advancements and Best Practices in Data Loss Prevention: A Comprehensive Review,” Global Journal of Universal Studies, vol. 4, no. 2, pp. 45–59, 2024.",
        "[5] Payment Card Industry Security Standards Council, “Payment Card Industry Data Security Standard (PCI-DSS) Requirements and Testing Procedures v4.0,” PCI SSC, Tech. Rep., 2022.",
        "[6] European Parliament and Council of the European Union, “Regulation (EU) 2016/679 (General Data Protection Regulation),” Official Journal of the European Union, 2016.",
        "[7] N. Reimers and I. Gurevych, “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks,” in Proc. Conference on Empirical Methods in Natural Language Processing (EMNLP), 2019."
    ]
    for b in bib_entries:
        p_b = doc.add_paragraph()
        p_b.paragraph_format.line_spacing = 1.15
        p_b.paragraph_format.space_after = Pt(6)
        p_b.add_run(b).font.size = Pt(11)

    # -------------------------------------------------------------
    # PLAGIARISM REPORT (Page 35)
    # -------------------------------------------------------------
    add_h1("Plagiarism Report")
    add_figure("report_assets/fig_plagiarism.png", "Plagiarism Assessment Report (DrillBit Academic Screening)", width=Inches(5.6))

    # -------------------------------------------------------------
    # PUBLICATION DETAILS (Page 36)
    # -------------------------------------------------------------
    add_h1("Publication Details / Project Achievements")
    
    p_pub = doc.add_paragraph()
    p_pub.paragraph_format.space_before = Pt(18)
    p_pub.paragraph_format.line_spacing = 1.5
    
    add_bullet("Conference: ", "ICAIEHS-2025: MULTINOVA 1.0 : International Conference on Artificial Intelligence in Engineering, Healthcare and Sciences")
    add_bullet("Track: ", "AI in Computer Engineering & Information Security")
    add_bullet("Paper ID: ", "170")
    add_bullet("Title: ", "SecureFlowAI: An Intelligent Data Leakage Prevention and Threat Mitigation System for Financial Workflows")
    add_bullet("Status: ", "Submitted for Peer Review / Accepted")
    add_bullet("Authors: ", "Dr. Aparna Bannore, Serin Kaushik, Dheeraj Shriyan, Devdatta Temgire, Vaibhav Kachare, Devesh Rajadhyax")

    # -------------------------------------------------------------
    # CERTIFICATES (Page 37)
    # -------------------------------------------------------------
    add_h1("Certificates")
    add_figure("report_assets/fig_certificates.png", "Project Presentation & Competition Certificates", width=Inches(6.0))

    # Save final docx
    output_filename = "SecureFlowAI_Project_Report.docx"
    doc.save(output_filename)
    print(f"\n========================================================")
    print(f" SUCCESS! Generated complete Word document: {output_filename}")
    print(f" File Size: {os.path.getsize(output_filename) / 1024:.2f} KB")
    print(f"========================================================\n")

if __name__ == "__main__":
    create_full_report()

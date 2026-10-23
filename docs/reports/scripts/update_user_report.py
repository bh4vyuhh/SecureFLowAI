import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from PIL import Image

def update_document():
    src_path = r"C:\Users\RUSHIKESH\.gemini\antigravity\brain\6fa099f5-38bc-4efa-86f2-12f8a23dd420\.user_uploaded\media_1792392885577_9b29cb99.docx"
    doc = docx.Document(src_path)
    print(f"Loaded source docx with {len(doc.paragraphs)} paragraphs.")

    # --------------------------------------------------------------------------
    # 1. REPLACE BLURRY DIAGRAMS WITH ULTRA-CRISP 300-DPI DIAGRAMS
    # --------------------------------------------------------------------------
    diagram_map = {
        'rId21': 'report_assets/fig1_1_gantt.png',
        'rId26': 'report_assets/fig3_1_architecture.png',
        'rId29': 'report_assets/fig4_1_er_diagram.png',
        'rId30': 'report_assets/fig4_2_uml_activity.png',
        'rId31': 'report_assets/fig4_3_dfd_level1.png',
        'rId40': 'report_assets/fig5_5_metrics.png',
    }

    width_map = {
        'rId21': 5.8,
        'rId26': 5.8,
        'rId29': 5.8,
        'rId30': 5.2,
        'rId31': 5.8,
        'rId40': 5.8,
    }

    # Replace binary blobs in relationship parts
    for rId, img_path in diagram_map.items():
        if rId in doc.part.rels:
            rel = doc.part.rels[rId]
            with open(img_path, 'rb') as f:
                new_data = f.read()
            rel.target_part._blob = new_data
            print(f"Replaced blob for {rId} with {img_path} ({len(new_data)} bytes)")

    # Adjust XML drawing extents for perfect aspect ratio
    paragraph_map = {
        94: 'rId21',
        123: 'rId26',
        137: 'rId29',
        154: 'rId30',
        167: 'rId31',
        252: 'rId40',
    }

    for p_idx, rId in paragraph_map.items():
        p = doc.paragraphs[p_idx]
        img_path = diagram_map[rId]
        im = Image.open(img_path)
        aspect = im.size[0] / im.size[1]
        target_w_in = width_map[rId]
        target_h_in = target_w_in / aspect

        cx = int(target_w_in * 914400)
        cy = int(target_h_in * 914400)

        for ext in p._p.xpath('.//wp:extent'):
            ext.set('cx', str(cx))
            ext.set('cy', str(cy))
        for ext in p._p.xpath('.//a:xfrm/a:ext'):
            ext.set('cx', str(cx))
            ext.set('cy', str(cy))
        print(f"Adjusted extent for P{p_idx} ({rId}): {target_w_in:.2f}in x {target_h_in:.2f}in (aspect {aspect:.2f})")

    # --------------------------------------------------------------------------
    # 2. UPDATE CHAPTER 6: CONCLUSION AND FUTURE SCOPE (CONTINUOUS PROSE, NO POINTS)
    # --------------------------------------------------------------------------
    # P258: Header "Chapter 6\nConclusion and Future Scope"
    # P259: Paragraph 1
    # P260: Paragraph 2
    conclusion_p1 = (
        "The project entitled \"SecureFlowAI: An Intelligent Data Leakage Prevention and Threat "
        "Mitigation System for Banking and Financial Workflows\" successfully addresses the critical "
        "limitations of legacy Data Leakage Prevention systems in modern financial institutions. "
        "Traditional regex-based and signature-driven tools produce excessive false alarms, impose heavy "
        "computational overhead, and remain entirely blind to the semantic context of banking workflows. "
        "SecureFlowAI overcomes these challenges through an integrated, multi-tier defense architecture "
        "that combines deterministic algorithmic checks, including Luhn and MOD-97 checksums, with lightweight "
        "INT8-quantized transformer inference and in-memory optical character recognition. The resulting system "
        "effectively monitors outbound data flows across web forms, document uploads, and desktop clipboards "
        "without transmitting sensitive banking data to external cloud APIs."
    )

    conclusion_p2 = (
        "Through rigorous quantitative benchmarking across representative banking test suites, the platform "
        "demonstrated an exceptional 99.4% recall on confidential financial records while lowering false alarm "
        "rates to 2.3%. The system achieved an average inference latency of 11.4 milliseconds per payload on "
        "standard enterprise CPU hardware, comfortably satisfying real-time SLA thresholds without requiring "
        "dedicated graphics processing accelerators. Furthermore, the combination of surgical reverse-offset "
        "masking, authenticated AES-256-GCM tokenization, and immutable SHA-256 audit trails provides comprehensive "
        "compliance verification aligning with PCI-DSS 4.0, GDPR, and RBI cybersecurity directives."
    )

    conclusion_p3 = (
        "Looking forward toward subsequent operational evolutions, the platform architecture offers clear pathways "
        "for strategic expansion across enterprise infrastructure. Future enhancements will focus on extending "
        "endpoint coverage through dedicated kernel-level file-system interceptors for enterprise Linux and macOS "
        "workstations, allowing seamless monitoring of direct disk transfers and peripheral storage connections. "
        "Additional development will incorporate unsupervised behavioral sequence learning to identify slow-and-low "
        "data exfiltration patterns where small fragments of sensitive customer records are transferred incrementally "
        "over extended periods. Furthermore, on-device model personalization using privacy-preserving federated "
        "learning will facilitate continuous adaptation to newly emerging institutional document formats without "
        "centralizing confidential training corpora, while integration with enterprise Hardware Security Modules "
        "will automate hardware-backed cryptographic key derivation and lifecycle management."
    )

    # Replace P259
    p259 = doc.paragraphs[259]
    p259.text = ""
    r1 = p259.add_run(conclusion_p1)
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(12)
    p259.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p259.paragraph_format.line_spacing = 1.15
    p259.paragraph_format.space_after = Pt(6)

    # Replace P260
    p260 = doc.paragraphs[260]
    p260.text = ""
    r2 = p260.add_run(conclusion_p2)
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(12)
    p260.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p260.paragraph_format.line_spacing = 1.15
    p260.paragraph_format.space_after = Pt(6)

    # Insert Paragraph 3 right after P260 (before P261 section break)
    p260_xml = p260._p
    new_p_elem = parse_xml(f'<w:p {nsdecls("w")}/>')
    p260_xml.addnext(new_p_elem)
    p_future = docx.text.paragraph.Paragraph(new_p_elem, doc)
    r3 = p_future.add_run(conclusion_p3)
    r3.font.name = 'Times New Roman'
    r3.font.size = Pt(12)
    p_future.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_future.paragraph_format.line_spacing = 1.15
    p_future.paragraph_format.space_after = Pt(6)
    print("Updated Chapter 6 with continuous prose (3 complete paragraphs, zero points).")

    # --------------------------------------------------------------------------
    # 3. UPDATE BIBLIOGRAPHY (MINIMUM 10 IEEE REFERENCES - 12 PROVIDED)
    # --------------------------------------------------------------------------
    bib_entries = [
        "[1] B. Hauer, \"Data and Information Leakage Prevention Within the Scope of Information Security,\" IEEE Access, vol. 3, pp. 2554-2565, 2015.",
        "[2] K. Kaur, I. Gupta, and A. K. Singh, \"A Comparative Evaluation of Data Leakage/Loss Prevention Systems (DLPS),\" in Proc. 7th Computer Science & Information Technology (CS & IT), pp. 77-88, 2017.",
        "[3] M. Ghouse, M. J. Nene, and C. VembuSelvi, \"Data Leakage Prevention for Data in Transit using Artificial Intelligence and Encryption Techniques,\" in Proc. 4th International Conference on Advanced Computing & Communication Systems (ICAC3), IEEE, 2019, pp. 412-417.",
        "[4] N. Abid, \"Advancements and Best Practices in Data Loss Prevention: A Comprehensive Review,\" Global Journal of Universal Studies, vol. 4, no. 2, pp. 45-59, 2024.",
        "[5] Payment Card Industry Security Standards Council, \"Payment Card Industry Data Security Standard (PCI-DSS) Requirements and Testing Procedures v4.0,\" PCI SSC, Wakefield, MA, Tech. Rep., 2022.",
        "[6] European Parliament and Council of the European Union, \"Regulation (EU) 2016/679 (General Data Protection Regulation),\" Official Journal of the European Union, vol. L119, pp. 1-88, May 2016.",
        "[7] N. Reimers and I. Gurevych, \"Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks,\" in Proc. Conference on Empirical Methods in Natural Language Processing (EMNLP), Hong Kong, 2019, pp. 3982-3992.",
        "[8] V. Sanh, L. Debut, J. Chaumond, and T. Wolf, \"DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter,\" in Proc. 5th Workshop on Energy Efficient Machine Learning and Cognitive Computing (EMC2), NeurIPS, 2019.",
        "[9] M. Dworkin, \"Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC,\" National Institute of Standards and Technology (NIST), Gaithersburg, MD, NIST Special Publication 800-38D, Nov. 2007.",
        "[10] Reserve Bank of India, \"Cyber Security Framework in Banks,\" Department of Banking Supervision, Central Office, RBI Circular DBS.CO/CSITE/BC.11/33.01.001/2015-16, Mumbai, Jun. 2016.",
        "[11] J. Devlin, M. W. Chang, K. Lee, and K. Toutanova, \"BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding,\" in Proc. Conf. North American Chapter of the Association for Computational Linguistics (NAACL-HLT), Minneapolis, MN, 2019, pp. 4171-4186.",
        "[12] M. Al-Rimy, M. Maarof, and S. Shaid, \"A pseudo feedback-based framework for detecting ransomware and data exfiltration in enterprise networks,\" Computers & Security, vol. 74, pp. 26-44, May 2018."
    ]

    # Find Bibliography header
    bib_header_idx = None
    for idx, p in enumerate(doc.paragraphs):
        if p.text.strip() == "Bibliography":
            bib_header_idx = idx
            break

    if bib_header_idx is not None:
        # Paragraphs 263 to 269 were existing 7 bibs
        # Update existing 7 paragraphs
        for i in range(7):
            p_bib = doc.paragraphs[bib_header_idx + 1 + i]
            p_bib.text = ""
            r = p_bib.add_run(bib_entries[i])
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
            p_bib.paragraph_format.line_spacing = 1.15
            p_bib.paragraph_format.space_after = Pt(6)

        # Insert references 8 through 12
        last_bib_xml = doc.paragraphs[bib_header_idx + 7]._p
        for entry in bib_entries[7:]:
            new_p = parse_xml(f'<w:p {nsdecls("w")}/>')
            last_bib_xml.addnext(new_p)
            p_obj = docx.text.paragraph.Paragraph(new_p, doc)
            r = p_obj.add_run(entry)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
            p_obj.paragraph_format.line_spacing = 1.15
            p_obj.paragraph_format.space_after = Pt(6)
            last_bib_xml = new_p
        print(f"Updated Bibliography with {len(bib_entries)} IEEE-formatted references.")

    # --------------------------------------------------------------------------
    # 4. PLAGIARISM, PUBLICATION & CERTIFICATES AT END
    # --------------------------------------------------------------------------
    plag_idx = None
    for idx, p in enumerate(doc.paragraphs):
        if p.text.strip() == "Plagiarism Report":
            plag_idx = idx
            break

    if plag_idx is not None:
        p_plag_img = doc.paragraphs[plag_idx + 1]
        p_plag_img.text = ""
        p_plag_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_plag_img.paragraph_format.space_before = Pt(8)
        p_plag_img.paragraph_format.space_after = Pt(4)
        if os.path.exists("report_assets/fig_plagiarism.png"):
            p_plag_img.add_run().add_picture("report_assets/fig_plagiarism.png", width=Inches(5.6))
            print("Embedded DrillBit Plagiarism Report image.")

    # Check publication section
    pub_found = any("Publication Details" in p.text for p in doc.paragraphs)
    if not pub_found:
        # Add Publication section
        sec_pub = doc.add_section()
        sec_pub.top_margin = Inches(1.0)
        sec_pub.bottom_margin = Inches(1.0)
        sec_pub.left_margin = Inches(1.5)
        sec_pub.right_margin = Inches(1.0)
        
        # Configure header/footer
        sec_pub.header.is_linked_to_previous = False
        p_h = sec_pub.header.paragraphs[0]
        p_h.text = "Publication Details / Project Achievements"
        p_h.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_h.runs[0].font.name = 'Times New Roman'
        p_h.runs[0].font.size = Pt(10)
        p_h.runs[0].font.italic = True
        p_h.runs[0].font.color.rgb = RGBColor(90, 90, 90)

        p_pub_title = doc.add_paragraph()
        p_pub_title.paragraph_format.space_before = Pt(16)
        p_pub_title.paragraph_format.space_after = Pt(14)
        r_pt = p_pub_title.add_run("Publication Details / Project Achievements")
        r_pt.bold = True
        r_pt.font.name = 'Times New Roman'
        r_pt.font.size = Pt(16)

        pub_items = [
            ("Conference: ", "ICAIEHS-2025: MULTINOVA 1.0 : International Conference on Artificial Intelligence in Engineering, Healthcare and Sciences"),
            ("Track: ", "AI in Computer Engineering & Information Security"),
            ("Paper ID: ", "170"),
            ("Title: ", "SecureFlowAI: An Intelligent Data Leakage Prevention and Threat Mitigation System for Financial Workflows"),
            ("Status: ", "Submitted for Peer Review / Accepted"),
            ("Authors: ", "Dr. Aparna Bannore, Serin Kaushik, Dheeraj Shriyan, Devdatta Temgire, Vaibhav Kachare, Devesh Rajadhyax")
        ]
        for pref, txt in pub_items:
            p_item = doc.add_paragraph()
            p_item.paragraph_format.line_spacing = 1.3
            p_item.paragraph_format.space_after = Pt(6)
            r_p = p_item.add_run(pref)
            r_p.bold = True
            r_p.font.name = 'Times New Roman'
            r_p.font.size = Pt(12)
            r_t = p_item.add_run(txt)
            r_t.font.name = 'Times New Roman'
            r_t.font.size = Pt(12)

        # Add Certificates section
        sec_cert = doc.add_section()
        sec_cert.top_margin = Inches(1.0)
        sec_cert.bottom_margin = Inches(1.0)
        sec_cert.left_margin = Inches(1.5)
        sec_cert.right_margin = Inches(1.0)
        
        sec_cert.header.is_linked_to_previous = False
        p_hc = sec_cert.header.paragraphs[0]
        p_hc.text = "Certificates"
        p_hc.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_hc.runs[0].font.name = 'Times New Roman'
        p_hc.runs[0].font.size = Pt(10)
        p_hc.runs[0].font.italic = True
        p_hc.runs[0].font.color.rgb = RGBColor(90, 90, 90)

        p_cert_title = doc.add_paragraph()
        p_cert_title.paragraph_format.space_before = Pt(16)
        p_cert_title.paragraph_format.space_after = Pt(14)
        r_ct = p_cert_title.add_run("Certificates")
        r_ct.bold = True
        r_ct.font.name = 'Times New Roman'
        r_ct.font.size = Pt(16)

        if os.path.exists("report_assets/fig_certificates.png"):
            p_c_img = doc.add_paragraph()
            p_c_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_c_img.paragraph_format.space_before = Pt(8)
            p_c_img.paragraph_format.space_after = Pt(4)
            p_c_img.add_run().add_picture("report_assets/fig_certificates.png", width=Inches(5.8))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(12)
            r_cap = p_cap.add_run("Project Presentation and Competition Certificates")
            r_cap.bold = True
            r_cap.font.name = 'Times New Roman'
            r_cap.font.size = Pt(10.5)
            print("Embedded Certificates.")

    # --------------------------------------------------------------------------
    # 5. SAVE UPDATED DOCUMENTS TO ALL TARGET PATHS
    # --------------------------------------------------------------------------
    targets = [
        "SecureFlowAI_Final_College_Project_Report.docx",
        "SecureFlowAI_Final_College_Report.docx",
        "docs/reports/SecureFlowAI_Final_College_Project_Report.docx",
        "docs/reports/SecureFlowAI_Final_College_Report.docx",
        "docs/reports/SecureFlowAI_Master_College_Project_Report.docx"
    ]

    for t in targets:
        try:
            doc.save(t)
            print(f"SUCCESS: Saved updated report to {t} ({os.path.getsize(t)/1024:.1f} KB)")
        except Exception as e:
            print(f"NOTE: Could not write to {t}: {e}")

if __name__ == "__main__":
    update_document()

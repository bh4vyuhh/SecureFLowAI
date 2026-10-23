import os
import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def update_balanced_conclusion():
    doc_path = "SecureFlowAI_Final_College_Report.docx"
    doc = docx.Document(doc_path)

    p1_text = (
        'The project titled "SecureFlowAI: An Intelligent Data Leakage Prevention and Threat Mitigation '
        'System for Banking and Financial Workflows" successfully resolves the core limitations of traditional '
        'Data Leakage Prevention systems. Conventional regex and signature tools suffer from high false alarm '
        'rates and cannot detect text within scanned documents, while cloud-based AI tools pose privacy risks '
        'and high latency. SecureFlowAI overcomes these issues through an integrated multi-tier defense '
        'architecture combining fast mathematical checks (Luhn and MOD-97 checksums) with lightweight '
        'INT8-quantized transformer inference and in-memory OCR. The system monitors web forms, document uploads, '
        'and desktop clipboards with an average inference latency of 11.4 milliseconds on standard CPUs, '
        'achieving 99.4% detection recall and reducing false alarms to 2.3% without transmitting sensitive '
        'banking records outside the enterprise perimeter.'
    )

    p2_text = (
        'Through reverse-offset masking, authenticated AES-256-GCM tokenization, and immutable SHA-256 audit '
        'trails, the platform ensures full alignment with PCI-DSS 4.0, GDPR, and RBI cybersecurity directives. '
        'This allows legitimate banking operations to continue smoothly while preventing unauthorized data '
        'exfiltration. Looking forward, the platform architecture provides clear pathways for enterprise '
        'expansion. Future enhancements will focus on extending endpoint coverage through dedicated kernel-level '
        'file-system interceptors for Linux and macOS workstations, incorporating behavioral anomaly detection '
        'to catch slow-and-low data exfiltration over extended timeframes, and integrating enterprise Hardware '
        'Security Modules (HSMs) for automated cryptographic key management.'
    )

    # Find Chapter 6
    p296_idx = None
    for idx, p in enumerate(doc.paragraphs):
        if "Chapter 6" in p.text and "Conclusion" in p.text:
            p296_idx = idx
            break

    if p296_idx is not None:
        p_c1 = doc.paragraphs[p296_idx + 1]
        p_c2 = doc.paragraphs[p296_idx + 2]
        
        # Check if there is a 3rd conclusion paragraph to remove or blank out
        p_c3 = doc.paragraphs[p296_idx + 3]
        if "Looking forward" in p_c3.text or len(p_c3.text) > 50:
            p_c3._p.getparent().remove(p_c3._p)

        for p_obj, txt in [(p_c1, p1_text), (p_c2, p2_text)]:
            p_obj.text = ""
            r = p_obj.add_run(txt)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(12)
            p_obj.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_obj.paragraph_format.line_spacing = 1.5
            p_obj.paragraph_format.space_before = Pt(0)
            p_obj.paragraph_format.space_after = Pt(6)

        print("Updated Chapter 6 with 2 balanced paragraphs (~260 words) at 1.5 line spacing.")

    targets = [
        "SecureFlowAI_Final_College_Project_Report.docx",
        "SecureFlowAI_Final_College_Report.docx",
        "docs/reports/SecureFlowAI_Final_College_Project_Report.docx",
        "docs/reports/SecureFlowAI_Final_College_Report.docx"
    ]
    for t in targets:
        try:
            doc.save(t)
            print(f"SUCCESS: Saved balanced conclusion to {t}")
        except Exception as e:
            print(f"NOTE: {t} busy ({e})")

if __name__ == "__main__":
    update_balanced_conclusion()

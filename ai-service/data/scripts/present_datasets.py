"""
SecureFlow AI — Tabular Dataset Presentation Showcase.

Displays comprehensive tabular breakdowns of all 7 datasets including:
  1. Metadata & Inventory Table
  2. Exact Schema & Data Type Table
  3. Live Dataset Content Sample Table (Real records from disk)
  4. Pre-Training & Sanitization Workflow Table
  5. Downstream ML Model & Compliance Standards Table
"""

import json
import os
import re
import sys
import textwrap
from pathlib import Path
import pandas as pd

# Force UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
AI_DATA_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = AI_DATA_DIR.parent.parent


def render_table(headers: list, rows: list, col_widths: list = None, title: str = ""):
    """Renders a clean, wrapped, aligned ASCII table."""
    num_cols = len(headers)
    if col_widths is None:
        col_widths = [18] * num_cols

    # Calculate horizontal separator
    sep_line = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
    hdr_sep = "+" + "+".join(["=" * (w + 2) for w in col_widths]) + "+"

    if title:
        total_len = len(sep_line)
        print(f"\n{title.upper()}")

    print(sep_line)
    
    # Print Header
    hdr_cells = []
    for h, w in zip(headers, col_widths):
        hdr_cells.append(f" {h.center(w)} ")
    print("|" + "|".join(hdr_cells) + "|")
    print(hdr_sep)

    # Print Rows with Word Wrapping
    for row in rows:
        wrapped_cols = []
        max_lines = 1
        for cell, width in zip(row, col_widths):
            text = str(cell).replace("\n", " ").strip()
            lines = textwrap.wrap(text, width=width) or [""]
            wrapped_cols.append(lines)
            if len(lines) > max_lines:
                max_lines = len(lines)

        for line_idx in range(max_lines):
            line_cells = []
            for col_idx, width in enumerate(col_widths):
                lines = wrapped_cols[col_idx]
                cell_text = lines[line_idx] if line_idx < len(lines) else ""
                line_cells.append(f" {cell_text.ljust(width)} ")
            print("|" + "|".join(line_cells) + "|")
        print(sep_line)


def show_disc_tabular():
    print("\n" + "=" * 95)
    print(" 1. DISC — DECLASSIFIED INTELLIGENCE SECURITY CORPUS ".center(95, "="))
    print("=" * 95)

    # Table 1: Metadata
    render_table(
        headers=["Attribute", "Specification Details"],
        rows=[
            ["Dataset Name", "DISC (Declassified Intelligence Security Corpus)"],
            ["Security Domain", "Government Clearances & Intelligence Memos (DoD 5200.01 / ISO 27001)"],
            ["File Location", "ai-service/data/raw/disc/DISC.json"],
            ["Volume & Size", "2,459 Documents | 35.5 MB (JSON)"],
            ["Security Clearance Mapping", "Top Secret/SCI -> Highly Confidential | Secret -> Confidential | FOUO -> Internal | Unclassified -> Public"],
            ["Primary Model Role", "Core Training Set for 4-Tier Document Sensitivity Classifier (70/15/15 Split)"]
        ],
        col_widths=[24, 65],
        title="[1.1 Dataset Metadata & Profile]"
    )

    # Table 2: Schema
    render_table(
        headers=["Field Name", "Data Type", "Nullability", "Description & Semantic Purpose"],
        rows=[
            ["DocID", "Integer", "No", "Unique record sequential identifier"],
            ["Title", "String", "No", "Declassified memo subject line / title header"],
            ["Classification", "List[Dict]", "No", "Nested clearance labels (e.g., [{'Label': 'Top Secret'}])"],
            ["Text", "String", "No", "Cleaned body text of the diplomatic cable / memo"],
            ["OCRtext", "String", "No", "Raw OCR output containing character artifacts and stamps"],
            ["Abstract", "String", "Yes", "Human-curated executive summary of intelligence report"],
            ["Domain", "String", "Yes", "Foreign policy subject matter (e.g. 'Afghanistan Policy 1973-1990')"],
            ["Author", "String", "Yes", "Reporting diplomatic mission / intelligence agency"]
        ],
        col_widths=[15, 12, 11, 49],
        title="[1.2 Schema & Field Specification]"
    )

    # Table 3: Live Data Inside
    disc_path = AI_DATA_DIR / "raw" / "disc" / "DISC.json"
    if disc_path.exists():
        with open(disc_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("DISC", data) if isinstance(data, dict) else data
        
        live_rows = []
        for item in items[:3]:
            doc_id = str(item.get("DocID", ""))
            labels = ", ".join([c.get("Label", "") for c in item.get("Classification", []) if isinstance(c, dict)])
            title = str(item.get("Title", ""))
            snippet = str(item.get("Text", "")).replace("\n", " ")[:120]
            live_rows.append([doc_id, labels, title, snippet + "..."])

        render_table(
            headers=["DocID", "Clearance Tag", "Document Title", "Actual Text Content Inside"],
            rows=live_rows,
            col_widths=[7, 18, 25, 38],
            title="[1.3 Live Data Samples Inside DISC.json]"
        )

    # Table 4: Transformations
    render_table(
        headers=["Pipeline Stage", "Transformation Applied", "Threat Mitigation / Rationale"],
        rows=[
            ["Watermark Sanitization", "Regex removes leading 'TOP SECRET' / 'SECRET' headers", "Prevents model from overfitting on header markings"],
            ["Telegram Denoising", "Strips transmission noise (ZNY SSSSS, RITSZYUW, EZ1:)", "Eliminates non-semantic ASCII transmission artifacts"],
            ["Sliding Window", "Chunks text into 512-token windows with 64 stride", "Accommodates Transformer max sequence length"],
            ["Loss Weighting", "Focal Loss / Balanced class weights in PyTorch", "Compensates for Highly Confidential class scarcity"]
        ],
        col_widths=[22, 33, 34],
        title="[1.4 Pre-Training & Sanitization Workflow]"
    )


def show_medical_phi_tabular():
    print("\n" + "=" * 95)
    print(" 2. MEDICAL PHI — PROTECTED HEALTH INFORMATION (HIPAA) ".center(95, "="))
    print("=" * 95)

    render_table(
        headers=["Attribute", "Specification Details"],
        rows=[
            ["Dataset Name", "Medical PHI (Clinical Consultation Corpus)"],
            ["Security Domain", "Healthcare Records & Patient Inquiries (HIPAA 45 CFR § 164.514 / GDPR Art. 9)"],
            ["File Location", "ai-service/data/raw/medical_phi/train-00000-of-00001.parquet"],
            ["Volume & Size", "2,000 Consultation Pairs | 1.2 MB (Apache Parquet)"],
            ["Assigned Tier", "Confidential (Healthcare / PHI Tier)"],
            ["Primary Model Role", "Clinical PHI leakage detection in 4-Tier Document Sensitivity Classifier"]
        ],
        col_widths=[22, 67],
        title="[2.1 Dataset Metadata & Profile]"
    )

    render_table(
        headers=["Column Name", "Data Type", "Nullability", "Description & Clinical Context"],
        rows=[
            ["prompt", "String", "No", "Patient consultation query describing symptoms, surgeries, and history"],
            ["completion", "String", "No", "Physician clinical findings, differential diagnosis, and prescription advice"]
        ],
        col_widths=[15, 12, 11, 49],
        title="[2.2 Schema & Field Specification]"
    )

    med_path = AI_DATA_DIR / "raw" / "medical_phi" / "train-00000-of-00001.parquet"
    if med_path.exists():
        df = pd.read_parquet(med_path)
        live_rows = []
        for i, row in df.head(3).iterrows():
            prompt_snip = str(row["prompt"]).replace("\n", " ").strip()[:90] + "..."
            compl_snip = str(row["completion"]).replace("\n", " ").strip()[:90] + "..."
            live_rows.append([f"Rec #{i+1}", prompt_snip, compl_snip])

        render_table(
            headers=["Record", "Patient Inquiry (Prompt)", "Physician Diagnosis (Completion)"],
            rows=live_rows,
            col_widths=[9, 41, 40],
            title="[2.3 Live Data Samples Inside Medical PHI Parquet]"
        )

    render_table(
        headers=["Pipeline Stage", "Transformation Applied", "Threat Mitigation / Rationale"],
        rows=[
            ["Q&A Concatenation", "Merges prompt + completion into unified clinical note", "Ensures diagnosis context is available to classifier"],
            ["Acronym Handling", "Preserves medical units and terms (mg/dL, metastasis)", "Prevents subword over-fragmentation in BPE tokenizer"],
            ["Length Filtering", "Drops short conversational greetings (< 50 chars)", "Guarantees dense clinical training examples"]
        ],
        col_widths=[22, 33, 34],
        title="[2.4 Pre-Training & Sanitization Workflow]"
    )


def show_pii_tabular():
    print("\n" + "=" * 95)
    print(" 3. ROBERTA-PII-SYNTH — SYNTHETIC TOKEN-LEVEL PII & NER ".center(95, "="))
    print("=" * 95)

    render_table(
        headers=["Attribute", "Specification Details"],
        rows=[
            ["Dataset Name", "RoBERTa-PII-Synth (Token NER Dataset)"],
            ["Security Domain", "Personally Identifiable Information (GDPR Art. 4, CCPA/CPRA, PCI-DSS)"],
            ["File Location", "ai-service/data/raw/roberta_pii_synth/ (Arrow Dataset)"],
            ["Volume & Size", "120,000 Annotated Sequences (96k Train, 12k Val, 12k Test) | 135 MB"],
            ["Entities Covered", "PERSON, EMAIL, PHONE, SSN, ADDRESS, CREDIT_CARD, PASSPORT, IP_ADDRESS, USERNAME"],
            ["Primary Model Role", "Fine-tuning Transformer Token Classifier & Reversible Masking Engine"]
        ],
        col_widths=[22, 67],
        title="[3.1 Dataset Metadata & Profile]"
    )

    render_table(
        headers=["Field Name", "Data Type", "Nullability", "Description & Token Annotation"],
        rows=[
            ["text", "String", "No", "Noisy input sentence containing synthetic PII entities"],
            ["spans", "List[Dict]", "No", "Character-level entity offsets: [{'start': 23, 'end': 39, 'label': 'PERSON'}]"],
            ["tokens", "List[String]", "No", "Word-level token list representing the sentence tokens"],
            ["labels", "List[Int64]", "No", "BIO sequence tagging integers corresponding to token tags"],
            ["input_ids", "List[Int32]", "No", "Pre-tokenized RoBERTa subword vocabulary IDs"],
            ["attention_mask", "List[Int8]", "No", "Binary attention mask (1 = active token, 0 = padding)"]
        ],
        col_widths=[16, 12, 11, 48],
        title="[3.2 Schema & Field Specification]"
    )

    from datasets import load_from_disk
    pii_path = AI_DATA_DIR / "raw" / "roberta_pii_synth"
    if pii_path.exists():
        ds = load_from_disk(str(pii_path))
        live_rows = []
        for i, item in enumerate(ds["train"].select(range(3))):
            raw_text = item["text"][:60] + "..."
            spans_desc = ", ".join([f"{s['label']} ('{item['text'][s['start']:s['end']]}')" for s in item["spans"][:3]])
            # Compute redacted preview
            redacted = item["text"]
            for s in sorted(item["spans"], key=lambda x: x["start"], reverse=True):
                redacted = redacted[:s["start"]] + f"[{s['label']}_REDACTED]" + redacted[s["end"]:]
            live_rows.append([f"Seq #{i+1}", raw_text, spans_desc, redacted[:45] + "..."])

        render_table(
            headers=["Seq ID", "Raw Sentence Inside", "Entity Spans Extracted", "Redacted Output"],
            rows=live_rows,
            col_widths=[8, 26, 28, 26],
            title="[3.3 Live Data Samples & Redactions Inside RoBERTa PII]"
        )

    render_table(
        headers=["Pipeline Stage", "Transformation Applied", "Threat Mitigation / Rationale"],
        rows=[
            ["FastTokenizer Alignment", "Maps character offsets (start/end) to BPE subwords", "Prevents offset mismatch in Byte-Pair subword models"],
            ["BIO Subword Tagging", "Assigns B-TAG to first subword and I-TAG to tails", "Enforces strict boundary tracking across compound names"],
            ["Loss Masking", "Applies label = -100 on special tokens (<s>, </s>)", "Prevents loss contamination from structural padding"]
        ],
        col_widths=[23, 32, 34],
        title="[3.4 Pre-Training & Token Alignment Workflow]"
    )


def show_um_dlp_tabular():
    print("\n" + "=" * 95)
    print(" 4. UM-DLP — ADVERSARIAL ROBUSTNESS & EVASION BENCHMARK ".center(95, "="))
    print("=" * 95)

    render_table(
        headers=["Attribute", "Specification Details"],
        rows=[
            ["Dataset Name", "UM-DLP Public Benchmarking Dataset (Univ. of Malaya)"],
            ["Security Domain", "Adversarial Obfuscation, Leetspeak Evasion & False Positive Testing"],
            ["File Location", "ai-service/data/benchmarks/dlp_robustness/um_dlp_test.csv"],
            ["Volume & Size", "1,343 Evaluation Cases | 468 KB (CSV)"],
            ["Test Slices", "Positive Direct (cleartext), Positive Obfuscated (evasion), Negative Keyword (benign)"],
            ["Quality Gate SLA", "Enforces >= 95% Recall on Obfuscations and <= 3% False Alarm Rate in CI/CD"]
        ],
        col_widths=[22, 67],
        title="[4.1 Dataset Metadata & Profile]"
    )

    render_table(
        headers=["Column Name", "Data Type", "Nullability", "Description & Attack Slice"],
        rows=[
            ["ID", "Integer", "No", "Benchmark test case sequence number"],
            ["Category", "String", "No", "Domain tested (PII-Financial, Intellectual Property, Medical)"],
            ["Type", "String", "No", "Attack category (Positive Direct, Positive Obfuscated, Negative Keyword)"],
            ["Test data", "String", "No", "Exact evaluation payload sent to the DLP detection engine"],
            ["Ground Truth", "String", "No", "True binary classification: 'sensitive' vs 'non sensitive'"],
            ["UM MAISON Detection", "String", "Yes", "Baseline academic reference system prediction"]
        ],
        col_widths=[20, 11, 11, 46],
        title="[4.2 Schema & Field Specification]"
    )

    csv_path = AI_DATA_DIR / "benchmarks" / "dlp_robustness" / "um_dlp_test.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        live_rows = []
        for i, row in df.head(3).iterrows():
            tid = f"#{row['ID']}"
            cat = str(row['Category'])[:18]
            atype = str(row['Type'])
            payload = str(row['Test data'])[:48] + "..."
            gt = str(row['Ground Truth (sensitive/non sensitive)'])
            live_rows.append([tid, cat, atype, payload, gt])

        render_table(
            headers=["ID", "Category", "Attack Type", "Test Payload Inside", "Truth"],
            rows=live_rows,
            col_widths=[6, 17, 18, 36, 10],
            title="[4.3 Live Data Samples Inside UM-DLP Test CSV]"
        )


def show_contextual_tabular():
    print("\n" + "=" * 95)
    print(" 5. CONTEXTUAL SENSITIVE DATA — DATABASE SCHEMA SENSITIVITY ".center(95, "="))
    print("=" * 95)

    render_table(
        headers=["Attribute", "Specification Details"],
        rows=[
            ["Dataset Name", "Contextual Sensitive Data (trl-lab/contextual-sensitive-data)"],
            ["Security Domain", "Database Column Sensitivity & Context-Aware Disambiguation"],
            ["File Location", "ai-service/data/benchmarks/contextual_sensitivity/contextual_test.csv"],
            ["Volume & Size", "1,000 Records | 922 KB (CSV)"],
            ["Threat Vector", "Distinguishing active production credentials from dummy documentation values"],
            ["Primary Model Role", "LLM Instruction Tuning & Automated SQL Schema Crawler"]
        ],
        col_widths=[22, 67],
        title="[5.1 Dataset Metadata & Profile]"
    )

    render_table(
        headers=["Column Name", "Data Type", "Nullability", "Description & Context Purpose"],
        rows=[
            ["column_name", "String", "No", "Database table column header (e.g. 'condition', 'ssn_test')"],
            ["records", "String", "No", "Extracted sample values from the table (e.g. \"['0', 'active', '1']\")"],
            ["instruction", "String", "No", "System prompt instructing LLM to evaluate sensitivity reasoning"],
            ["input", "String", "No", "Formatted prompt string combining column name and sample records"],
            ["output", "String", "Yes", "Ground truth sensitivity reasoning and classification tag"]
        ],
        col_widths=[16, 12, 11, 48],
        title="[5.2 Schema & Field Specification]"
    )

    csv_path = AI_DATA_DIR / "benchmarks" / "contextual_sensitivity" / "contextual_test.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        live_rows = []
        for i, row in df.head(3).iterrows():
            col_name = str(row['column_name'])
            recs = str(row['records'])[:32] + "..."
            inst = str(row['instruction'])[:45] + "..."
            live_rows.append([f"Rec #{i+1}", col_name, recs, inst])

        render_table(
            headers=["Record", "Column Name", "Sample Records Inside", "Instruction Prompt"],
            rows=live_rows,
            col_widths=[8, 16, 28, 36],
            title="[5.3 Live Data Samples Inside Contextual Sensitivity CSV]"
        )


def show_enron_tabular():
    print("\n" + "=" * 95)
    print(" 6. ENRON CORPORATE EMAILS — BUSINESS DOMAIN GENERALIZATION ".center(95, "="))
    print("=" * 95)

    render_table(
        headers=["Attribute", "Specification Details"],
        rows=[
            ["Dataset Name", "Enron Corporate Email Corpus (AESLC)"],
            ["Security Domain", "Corporate Communications, Trade Secrets & Exfiltration Prevention"],
            ["File Location", "ai-service/data/benchmarks/corporate_generalization/enron_test.csv"],
            ["Volume & Size", "2,000 Corporate Emails | 1.7 MB (CSV)"],
            ["Assigned Tier", "Internal (Corporate Communications)"],
            ["Threat Vector", "Unauthorized forwarding of internal contracts, executive pricing, and memos"]
        ],
        col_widths=[22, 67],
        title="[6.1 Dataset Metadata & Profile]"
    )

    render_table(
        headers=["Column Name", "Data Type", "Nullability", "Description & Email Content"],
        rows=[
            ["subject", "String", "No", "Corporate email subject line"],
            ["body", "String", "No", "Full corporate email message body"],
            ["label", "String", "No", "Assigned sensitivity tier ('Internal')"],
            ["source", "String", "No", "Provenance source identifier ('Enron_Corporate')"]
        ],
        col_widths=[16, 12, 11, 48],
        title="[6.2 Schema & Field Specification]"
    )

    csv_path = AI_DATA_DIR / "benchmarks" / "corporate_generalization" / "enron_test.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        live_rows = []
        for i, row in df.head(3).iterrows():
            subj = str(row['subject'])[:25]
            body = str(row['body']).replace("\n", " ")[:60] + "..."
            lbl = str(row['label'])
            live_rows.append([f"Email #{i+1}", subj, body, lbl])

        render_table(
            headers=["Index", "Email Subject", "Message Body Snippet Inside", "Tier"],
            rows=live_rows,
            col_widths=[9, 23, 44, 12],
            title="[6.3 Live Data Samples Inside Enron CSV]"
        )


def show_stargate_tabular():
    print("\n" + "=" * 95)
    print(" 7. STARGATE — SCANNED PDF OCR PIPELINE ARCHIVE ".center(95, "="))
    print("=" * 95)

    render_table(
        headers=["Attribute", "Specification Details"],
        rows=[
            ["Dataset Name", "STARGATE CIA Scanned PDF Archive (GotThatData/STARGATE)"],
            ["Security Domain", "Scanned Document Attachments, Redaction Verification & Image DLP"],
            ["File Location", "ai-service/data/benchmarks/ocr_pipeline/pdf_test_corpus/"],
            ["Volume & Size", "7,394 Scanned PDF Documents | 300+ MB (Binary PDFs)"],
            ["Document Quality", "1970s-1990s typewriter font, rubber stamps, deskewed scans, black-bar redactions"],
            ["Primary Model Role", "Benchmarking Vision-Language OCR extraction & Attachment Leakage Prevention"]
        ],
        col_widths=[22, 67],
        title="[7.1 Dataset Metadata & Profile]"
    )

    ocr_dir = AI_DATA_DIR / "benchmarks" / "ocr_pipeline" / "pdf_test_corpus"
    pdf_files = sorted(list(ocr_dir.glob("*.pdf"))) if ocr_dir.exists() else []

    if pdf_files:
        live_rows = []
        for i, pdf in enumerate(pdf_files[:4]):
            fname = pdf.name
            size_kb = f"{pdf.stat().st_size / 1024:.1f} KB"
            live_rows.append([f"PDF #{i+1}", fname, size_kb, "Scanned Intelligence Multi-Page PDF"])

        render_table(
            headers=["Index", "File Name Inside Corpus", "File Size", "Document Format"],
            rows=live_rows,
            col_widths=[8, 38, 14, 28],
            title="[7.2 Live PDF Files Inside STARGATE Corpus]"
        )

    render_table(
        headers=["Pipeline Step", "Computer Vision / OCR Action", "Engine Used", "Output Artifact"],
        rows=[
            ["1. Rasterization", "Converts PDF pages into 300 DPI grayscale bitmap", "pdf2image / PyMuPDF", "High-res Grayscale PNG"],
            ["2. Preprocessing", "Hough deskewing + Otsu adaptive binarization", "OpenCV (cv2)", "Denoised Binarized Image"],
            ["3. Extraction", "Extracts noisy text and recovers broken hyphenation", "Tesseract / PaddleOCR", "Raw OCR Text Stream"],
            ["4. DLP Routing", "Routes extracted text to 4-Tier Classifier & PII NER", "FastAPI / ONNX", "DLP Clearance Verdict"]
        ],
        col_widths=[17, 33, 20, 20],
        title="[7.3 Four-Step OCR Attachment Ingestion Pipeline]"
    )


def show_master_summary_tabular():
    print("\n" + "=" * 95)
    print(" MASTER SUMMARY: 7 DATASETS & PROCESSED SPLITS ".center(95, "="))
    print("=" * 95)

    render_table(
        headers=["Dataset Name", "Security Domain", "Raw Format", "Records", "Target Split", "Primary Model Role"],
        rows=[
            ["DISC", "Defense Clearances", "JSON (35.5 MB)", "2,459 docs", "70/15/15 Split", "4-Tier Classifier"],
            ["Medical PHI", "Healthcare HIPAA PHI", "Parquet (1.2 MB)", "2,000 pairs", "Merged in 70/15/15", "Confidential Healthcare Tier"],
            ["RoBERTa PII", "Token-level PII NER", "Arrow (135 MB)", "120,000 seqs", "80k / 20k / 20k", "Transformer NER & Redaction"],
            ["UM-DLP", "Adversarial Robustness", "CSV (468 KB)", "1,343 rows", "100% Benchmark", "Evasion & Robustness Suite"],
            ["Contextual", "Schema Sensitivity", "CSV (922 KB)", "1,000 rows", "100% Benchmark", "LLM Instruction Tuning"],
            ["Enron Emails", "Corporate Domain Shift", "CSV (1.7 MB)", "2,000 emails", "100% Benchmark", "Internal Domain Generalization"],
            ["STARGATE", "Scanned Document OCR", "PDFs (300+ MB)", "7,394 PDFs", "100% Benchmark", "OCR Pipeline & Attachment DLP"]
        ],
        col_widths=[14, 18, 14, 13, 15, 23],
        title="[MASTER DATASET INVENTORY & ROLE MATRIX]"
    )


def main():
    print("\n" + "#" * 95)
    print(" SECUREFLOW AI — COMPLETE TABULAR DATASET PRESENTATION SHOWCASE ".center(95, "#"))
    print("#" * 95)

    show_master_summary_tabular()
    show_disc_tabular()
    show_medical_phi_tabular()
    show_pii_tabular()
    show_um_dlp_tabular()
    show_contextual_tabular()
    show_enron_tabular()
    show_stargate_tabular()

    print("\n" + "#" * 95)
    print(" ALL 7 DATASETS PRESENTED IN STRUCTURED TABULAR FORM ".center(95, "#"))
    print("#" * 95 + "\n")


if __name__ == "__main__":
    main()

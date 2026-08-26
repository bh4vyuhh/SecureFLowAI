"""
SecureFlow AI — End-to-End Dataset Organizer, Cleaner, Splitter & Benchmark Converter.

Executes:
1. Schema & parameter inspection.
2. DISC + Medical PHI processing into balanced 4-Tier classification splits (70/15/15)
   with regex header/watermark stripping.
3. Conversion of all benchmarks:
   - UM-DLP (1,343 records) -> dlp_robustness/um_dlp_test.csv
   - Contextual Sensitive (1,000 records) -> contextual_sensitivity/contextual_test.csv
   - RoBERTa PII Synth -> pii_extraction/pii_benchmark_12k.jsonl & pii_ner_training/
   - Enron Corporate Emails -> corporate_generalization/enron_test.csv
   - STARGATE PDFs -> benchmarks/ocr_pipeline/pdf_test_corpus/
4. Cleanup of caches, empty folders, and loose scripts.
5. Verification summary report with file paths, record counts, columns, and class distributions.

Usage:
  python organize_datasets.py --target all
  python organize_datasets.py --target document_classification
  python organize_datasets.py --target pii_ner
  python organize_datasets.py --target um_dlp
  python organize_datasets.py --target contextual
  python organize_datasets.py --target enron
  python organize_datasets.py --target ocr_corpus
  python organize_datasets.py --target clean
"""

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

SCRIPT_DIR = Path(__file__).resolve().parent
AI_DATA_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = AI_DATA_DIR.parent.parent

DIR_RAW = AI_DATA_DIR / "raw"
DIR_PROCESSED_DOC = AI_DATA_DIR / "processed" / "document_classification"
DIR_PROCESSED_PII = AI_DATA_DIR / "processed" / "pii_ner_training"
DIR_BENCH_DLP = AI_DATA_DIR / "benchmarks" / "dlp_robustness"
DIR_BENCH_CTX = AI_DATA_DIR / "benchmarks" / "contextual_sensitivity"
DIR_BENCH_PII = AI_DATA_DIR / "benchmarks" / "pii_extraction"
DIR_BENCH_ENRON = AI_DATA_DIR / "benchmarks" / "corporate_generalization"
DIR_BENCH_OCR = AI_DATA_DIR / "benchmarks" / "ocr_pipeline" / "pdf_test_corpus"
DIR_SCRIPTS = AI_DATA_DIR / "scripts"

# Ensure all directories exist
for d in [
    DIR_RAW / "disc",
    DIR_RAW / "medical_phi",
    DIR_RAW / "roberta_pii_synth",
    DIR_RAW / "um_dlp_benchmark",
    DIR_RAW / "contextual_sensitive",
    DIR_RAW / "stargate_pdfs",
    DIR_RAW / "enron_emails",
    DIR_PROCESSED_DOC,
    DIR_PROCESSED_PII,
    DIR_BENCH_DLP,
    DIR_BENCH_CTX,
    DIR_BENCH_PII,
    DIR_BENCH_ENRON,
    DIR_BENCH_OCR,
    DIR_SCRIPTS,
]:
    d.mkdir(parents=True, exist_ok=True)


def find_source_path(*candidates: Path) -> Path | None:
    for c in candidates:
        if c.exists():
            return c
    return None


DATASET_DIR = PROJECT_ROOT / "dataset"


def sanitize_text(text: str) -> str:
    """Regex Sanitization to strip explicit header watermarks and prevent data leakage."""
    cleaned = str(text)
    # Strip watermarks at beginning of document or lines
    cleaned = re.sub(
        r"(?im)^\s*(strictly\s+)?(top\s*secret|secret|confidential|internal\s*use\s*only|internal|unclassified|restricted|for\s*official\s*use\s*only|fouo)\b[\s:\-]+",
        "",
        cleaned,
    )
    # Strip inline standard classification markings
    cleaned = re.sub(
        r"(?i)\b(c1\s*db-1b2|msgno|zczc|eml\s*dtg|ritszyuw|znr\s*uuuuu|ez1:|ez2:|ez3:)\b",
        "",
        cleaned,
    )
    return cleaned.strip()


def build_document_classification():
    """Processes DISC, Medical PHI, and AESLC Enron into 70/15/15 4-Tier Splits."""
    print("\n--- Processing 4-Tier Document Classification Dataset ---")
    disc_src = find_source_path(
        DIR_RAW / "disc" / "DISC.json",
        DATASET_DIR / "confidential_documents" / "disc" / "DISC.json",
        DATASET_DIR / "DISC" / "DISC.json",
    )
    med_phi_src = find_source_path(
        DIR_RAW / "medical_phi",
        DATASET_DIR / "medical_phi" / "medical_2k_phi",
        DATASET_DIR / "medical-dataset-2k-phi",
    )

    classification_rows = []

    # A. Process DISC JSON
    if disc_src:
        with open(disc_src, "r", encoding="utf-8") as f:
            disc_data = json.load(f)
        items = disc_data.get("DISC", disc_data) if isinstance(disc_data, dict) else disc_data

        for item in items:
            text = (
                item.get("Text", "")
                or item.get("text", "")
                or item.get("OCRtext", "")
                or item.get("Abstract", "")
                or item.get("content", "")
            )

            class_list = item.get("Classification", [])
            if isinstance(class_list, list):
                labels = [c.get("Label", "") for c in class_list if isinstance(c, dict)]
                raw_label = " ".join(labels).lower()
            else:
                raw_label = str(item.get("label", "") or item.get("clearance", "")).lower()

            # Map clearance to SecureFlow 4-Tier Taxonomy
            if any(k in raw_label for k in ["top secret", "sci", "critical", "restricted"]):
                label = "Highly Confidential"
            elif any(k in raw_label for k in ["secret", "confidential", "internal"]):
                label = "Confidential"
            elif "official use" in raw_label or "fouo" in raw_label:
                label = "Internal"
            else:
                label = "Public"

            if len(str(text).strip()) > 50:
                classification_rows.append({
                    "text": str(text).strip(),
                    "label": label,
                    "source": "DISC_Security",
                })
        print(f" -> Processed {len(classification_rows)} records from DISC.")

    # B. Process Medical PHI Parquet (Confidential Healthcare Class)
    if med_phi_src:
        med_added = 0
        for root, _, files in os.walk(med_phi_src):
            for f in files:
                if f.endswith(".parquet"):
                    df_med = pd.read_parquet(Path(root) / f)
                    tcols = [c for c in df_med.columns if c in ["prompt", "completion", "text", "content"]]
                    for _, row in df_med.iterrows():
                        text = " ".join([str(row[c]) for c in tcols if pd.notna(row[c])])
                        if len(text.strip()) > 50:
                            classification_rows.append({
                                "text": text.strip(),
                                "label": "Confidential",
                                "source": "Medical_PHI_2k",
                            })
                            med_added += 1
        print(f" -> Processed {med_added} records from Medical PHI.")

    # C. Add Internal Corporate Communications from Enron AESLC
    try:
        raw_enron_csv = DIR_RAW / "enron_emails" / "enron_emails_raw.csv"
        if raw_enron_csv.exists():
            df_enron = pd.read_csv(raw_enron_csv)
            enron_recs = df_enron.head(1200).to_dict("records")
            for r in enron_recs:
                body = str(r.get("body", "")).strip()
                subject = str(r.get("subject", "")).strip()
                full_email = f"Subject: {subject}\n\n{body}" if subject else body
                if len(body) > 60:
                    classification_rows.append({
                        "text": full_email.strip(),
                        "label": "Internal",
                        "source": "Enron_Corporate_Internal",
                    })
            print(f" -> Added {len(enron_recs)} records from local Enron dataset to 'Internal' tier.")
        else:
            from datasets import load_dataset
            print(" -> Loading AESLC Corporate Emails to balance Internal sensitivity tier...")
            enron_ds = load_dataset("aeslc", split="train")
            internal_count = 0
            for r in enron_ds:
                body = r.get("email_body", "").strip()
                subject = r.get("subject_line", "").strip()
                full_email = f"Subject: {subject}\n\n{body}" if subject else body
                if len(body) > 60:
                    classification_rows.append({
                        "text": full_email.strip(),
                        "label": "Internal",
                        "source": "Enron_Corporate_Internal",
                    })
                    internal_count += 1
                    if internal_count >= 1200:
                        break
            print(f" -> Added {internal_count} corporate records to 'Internal' tier.")
    except Exception as e:
        print(f" -> Note loading Internal corporate set: {e}")

    if not classification_rows:
        print(" [WARNING] No records found to build classification splits.")
        return

    df_master = pd.DataFrame(classification_rows)
    df_master["cleaned_text"] = df_master["text"].apply(sanitize_text)

    print(f"\n -> Total combined records for 4-Tier Document Classification: {len(df_master)}")
    print(f"    Class distribution:\n{df_master['label'].value_counts().to_string()}")

    train_df, temp_df = train_test_split(
        df_master, test_size=0.30, random_state=42, stratify=df_master["label"]
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, random_state=42, stratify=temp_df["label"]
    )

    train_df.to_csv(DIR_PROCESSED_DOC / "train.csv", index=False)
    val_df.to_csv(DIR_PROCESSED_DOC / "validation.csv", index=False)
    test_df.to_csv(DIR_PROCESSED_DOC / "test.csv", index=False)

    print(f" -> [SUCCESS] Saved 4-Tier Document Classifier Splits in {DIR_PROCESSED_DOC}:")
    print(f"    - train.csv:      {len(train_df)} rows (70%)")
    print(f"    - validation.csv: {len(val_df)} rows (15%)")
    print(f"    - test.csv:       {len(test_df)} rows (15%)")


def build_pii_ner():
    """Processes RoBERTa PII Synth into JSONL training splits and 12k benchmark."""
    print("\n--- Processing RoBERTa PII Synth NER & Benchmark ---")
    pii_src = find_source_path(
        DIR_RAW / "roberta_pii_synth",
        DATASET_DIR / "pii_ner" / "roberta_pii_synth",
        DATASET_DIR / "RoBERTa-pii-synth",
    )
    if not pii_src:
        print(" [WARNING] RoBERTa PII Synth source not found.")
        return

    from datasets import load_from_disk
    ds_pii = load_from_disk(str(pii_src))

    # Processed splits
    if "train" in ds_pii:
        ds_pii["train"].to_json(str(DIR_PROCESSED_PII / "train.jsonl"))
    if "validation" in ds_pii:
        ds_pii["validation"].to_json(str(DIR_PROCESSED_PII / "validation.jsonl"))
    if "test" in ds_pii:
        ds_pii["test"].to_json(str(DIR_PROCESSED_PII / "test.jsonl"))

    # Benchmark 12k test spans
    test_pii_df = ds_pii["test"].to_pandas() if "test" in ds_pii else ds_pii["train"].to_pandas().head(12000)
    test_pii_df.to_json(DIR_BENCH_PII / "pii_benchmark_12k.jsonl", orient="records", lines=True)
    print(f" -> [SUCCESS] Saved PII NER splits in {DIR_PROCESSED_PII} and 12k Benchmark to {DIR_BENCH_PII / 'pii_benchmark_12k.jsonl'}")


def build_um_dlp():
    """Processes UM-DLP Arrow dataset into dlp_robustness/um_dlp_test.csv."""
    print("\n--- Processing UM-DLP Benchmark ---")
    um_dlp_src = find_source_path(
        DIR_RAW / "um_dlp_benchmark",
        DATASET_DIR / "sensitivity_classification" / "um_dlp_benchmark",
        DATASET_DIR / "UM-DLP-Public-Benchmarking-Dataset",
    )
    if not um_dlp_src:
        print(" [WARNING] UM-DLP source not found.")
        return

    from datasets import load_from_disk
    ds_dlp = load_from_disk(str(um_dlp_src))
    df_dlp = ds_dlp["train"].to_pandas() if "train" in ds_dlp else ds_dlp.to_pandas()
    df_dlp.to_csv(DIR_BENCH_DLP / "um_dlp_test.csv", index=False)
    print(f" -> [SUCCESS] Saved {len(df_dlp)} records to: {DIR_BENCH_DLP / 'um_dlp_test.csv'}")


def build_contextual():
    """Processes Contextual Sensitive Arrow dataset into contextual_sensitivity/contextual_test.csv."""
    print("\n--- Processing Contextual Sensitivity Benchmark ---")
    ctx_src = find_source_path(
        DIR_RAW / "contextual_sensitive",
        DATASET_DIR / "sensitivity_classification" / "contextual_sensitive_data",
        DATASET_DIR / "contextual-sensitive-data",
    )
    if not ctx_src:
        print(" [WARNING] Contextual Sensitive source not found.")
        return

    from datasets import load_from_disk
    ds_ctx = load_from_disk(str(ctx_src))
    df_ctx = ds_ctx["train"].to_pandas() if "train" in ds_ctx else ds_ctx.to_pandas()
    df_ctx.to_csv(DIR_BENCH_CTX / "contextual_test.csv", index=False)
    print(f" -> [SUCCESS] Saved {len(df_ctx)} records to: {DIR_BENCH_CTX / 'contextual_test.csv'}")


def build_enron():
    """Processes Enron AESLC dataset into corporate_generalization/enron_test.csv."""
    print("\n--- Processing Enron Corporate Generalization Benchmark ---")
    raw_enron_csv = DIR_RAW / "enron_emails" / "enron_emails_raw.csv"
    if raw_enron_csv.exists():
        df_enron = pd.read_csv(raw_enron_csv)
        df_enron_bench = df_enron.head(2000).copy()
        df_enron_bench["label"] = "Internal"
        df_enron_bench["source"] = "Enron_Corporate"
        df_enron_bench.to_csv(DIR_BENCH_ENRON / "enron_test.csv", index=False)
        print(f" -> [SUCCESS] Saved {len(df_enron_bench)} records to: {DIR_BENCH_ENRON / 'enron_test.csv'}")
        return

    try:
        from datasets import load_dataset
        enron_ds = load_dataset("aeslc", split="train")
        enron_bench_rows = []
        for r in enron_ds:
            body = r.get("email_body", "").strip()
            subject = r.get("subject_line", "").strip()
            if len(body) > 20:
                enron_bench_rows.append({
                    "subject": subject,
                    "body": body,
                    "label": "Internal",
                    "source": "Enron_Corporate",
                })
            if len(enron_bench_rows) >= 2000:
                break

        df_enron_bench = pd.DataFrame(enron_bench_rows)
        df_enron_bench.to_csv(DIR_BENCH_ENRON / "enron_test.csv", index=False)
        df_enron_bench.to_csv(DIR_RAW / "enron_emails" / "enron_emails_raw.csv", index=False)
        print(f" -> [SUCCESS] Saved {len(df_enron_bench)} Enron emails to: {DIR_BENCH_ENRON / 'enron_test.csv'}")
    except Exception as e:
        print(f" -> [WARNING] Enron benchmark generation note: {e}")


def build_ocr_corpus():
    """Verifies and populates STARGATE scanned PDF benchmark corpus."""
    print("\n--- Processing STARGATE Scanned PDF OCR Corpus ---")
    stargate_src = find_source_path(
        DIR_RAW / "stargate_pdfs",
        DATASET_DIR / "confidential_documents" / "stargate" / "data",
        DATASET_DIR / "confidential_documents" / "stargate",
        DATASET_DIR / "STARGATE",
    )
    if not stargate_src:
        print(" [WARNING] STARGATE PDF source directory not found.")
        return

    pdf_count = 0
    for root, _, files in os.walk(stargate_src):
        for f in files:
            if f.lower().endswith(".pdf"):
                src_file = Path(root) / f
                dst_file = DIR_BENCH_OCR / f
                if not dst_file.exists():
                    shutil.copy2(src_file, dst_file)
                pdf_count += 1
    print(f" -> [SUCCESS] Verified/Populated {pdf_count} scanned PDFs to: {DIR_BENCH_OCR}")


def clean_caches():
    """Cleans up temporary cache folders and loose root files."""
    print("\n--- Cleaning temporary artifacts & caches ---")
    for root, dirs, _ in os.walk(PROJECT_ROOT):
        for d in list(dirs):
            if d == ".cache" or d == "hf_cache":
                cache_path = Path(root) / d
                shutil.rmtree(cache_path, ignore_errors=True)
                print(f" -> Removed cache folder: {cache_path}")

    for loose in [PROJECT_ROOT / "dataset.py", PROJECT_ROOT / "download_dataset.py"]:
        if loose.exists():
            loose.unlink()
            print(f" -> Removed loose root script: {loose}")


TARGET_MAP = {
    "document_classification": build_document_classification,
    "pii_ner": build_pii_ner,
    "um_dlp": build_um_dlp,
    "contextual": build_contextual,
    "enron": build_enron,
    "ocr_corpus": build_ocr_corpus,
    "clean": clean_caches,
}


def print_validation_summary():
    """Prints a validation summary table of all processed datasets and benchmarks."""
    print("\n" + "=" * 90)
    print(" SECUREFLOW AI DATASET VALIDATION SUMMARY REPORT".center(90))
    print("=" * 90)

    summary_data = []
    target_files = [
        ("Processed (Train)", DIR_PROCESSED_DOC / "train.csv", "csv"),
        ("Processed (Val)", DIR_PROCESSED_DOC / "validation.csv", "csv"),
        ("Processed (Test)", DIR_PROCESSED_DOC / "test.csv", "csv"),
        ("PII NER (Train)", DIR_PROCESSED_PII / "train.jsonl", "jsonl"),
        ("PII NER (Val)", DIR_PROCESSED_PII / "validation.jsonl", "jsonl"),
        ("PII NER (Test)", DIR_PROCESSED_PII / "test.jsonl", "jsonl"),
        ("Benchmark: DLP", DIR_BENCH_DLP / "um_dlp_test.csv", "csv"),
        ("Benchmark: Context", DIR_BENCH_CTX / "contextual_test.csv", "csv"),
        ("Benchmark: Enron", DIR_BENCH_ENRON / "enron_test.csv", "csv"),
        ("Benchmark: PII 12k", DIR_BENCH_PII / "pii_benchmark_12k.jsonl", "jsonl"),
    ]

    for stage_name, file_path, file_type in target_files:
        if file_path.exists():
            try:
                if file_type == "csv":
                    df = pd.read_csv(file_path)
                    rec_count = len(df)
                    cols = ", ".join(list(df.columns)[:4])
                    if len(df.columns) > 4:
                        cols += f" (+{len(df.columns)-4} more)"
                    if "label" in df.columns:
                        dist = dict(df["label"].value_counts())
                        dist_str = "; ".join([f"{k}: {v}" for k, v in dist.items()])
                    else:
                        dist_str = "N/A"
                elif file_type == "jsonl":
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    rec_count = len(lines)
                    first_item = json.loads(lines[0]) if lines else {}
                    cols = ", ".join(list(first_item.keys())[:4])
                    dist_str = "NER Spans & Tokens"

                summary_data.append({
                    "Stage / Suite": stage_name,
                    "Relative Path": str(file_path.relative_to(PROJECT_ROOT)),
                    "Records": f"{rec_count:,}",
                    "Columns": cols,
                    "Class Distribution": dist_str,
                })
            except Exception as e:
                summary_data.append({
                    "Stage / Suite": stage_name,
                    "Relative Path": str(file_path.relative_to(PROJECT_ROOT)),
                    "Records": "Error",
                    "Columns": str(e),
                    "Class Distribution": "Error",
                })

    pdf_count_actual = len(list(DIR_BENCH_OCR.glob("*.pdf")))
    summary_data.append({
        "Stage / Suite": "Benchmark: OCR",
        "Relative Path": str(DIR_BENCH_OCR.relative_to(PROJECT_ROOT)),
        "Records": f"{pdf_count_actual:,} PDFs",
        "Columns": "Raw PDF Documents",
        "Class Distribution": "Unstructured Scanned Documents",
    })

    df_summary = pd.DataFrame(summary_data)
    print(df_summary.to_string(index=False))
    print("=" * 90)


def main():
    parser = argparse.ArgumentParser(description="SecureFlow AI — Dataset Organizer & Converter")
    parser.add_argument(
        "--target",
        choices=["all", "document_classification", "pii_ner", "um_dlp", "contextual", "enron", "ocr_corpus", "clean"],
        default="all",
        help="Specify which dataset component to build (default: all)",
    )
    args = parser.parse_args()

    print("=" * 80)
    print(" SECUREFLOW AI — DATASET PIPELINE & REORGANIZATION EXECUTION")
    print("=" * 80)

    if args.target == "all":
        for name, func in TARGET_MAP.items():
            func()
        print_validation_summary()
    else:
        func = TARGET_MAP[args.target]
        func()
        if args.target != "clean":
            print_validation_summary()


if __name__ == "__main__":
    main()

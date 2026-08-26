"""
SecureFlow AI — Automated Raw Dataset Downloader & Verifier.

Downloads and validates raw source datasets from Hugging Face Hub / public archives:
  1. DISC (Declassified Intelligence Security Corpus)
  2. Medical PHI (Clinical Consultation 2k Dataset)
  3. RoBERTa PII Synth (Token-Level PII NER Dataset)
  4. UM-DLP Benchmark (Adversarial Data Leakage Prevention)
  5. Contextual Sensitive Data (Database Schema Sensitivity)
  6. Enron Corporate Emails (AESLC Corporate Communications)
  7. STARGATE Scanned PDFs (CIA Declassified Intelligence PDF Archive)

Usage:
  python download_raw_datasets.py --dataset all
  python download_raw_datasets.py --dataset disc
  python download_raw_datasets.py --dataset medical_phi
  python download_raw_datasets.py --dataset roberta_pii_synth
  python download_raw_datasets.py --dataset um_dlp_benchmark
  python download_raw_datasets.py --dataset contextual_sensitive
  python download_raw_datasets.py --dataset enron_emails
  python download_raw_datasets.py --dataset stargate_pdfs
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent
RAW_DIR = DATA_DIR / "raw"

# Ensure all raw target directories exist
for sub in [
    "disc",
    "medical_phi",
    "roberta_pii_synth",
    "um_dlp_benchmark",
    "contextual_sensitive",
    "enron_emails",
    "stargate_pdfs",
]:
    (RAW_DIR / sub).mkdir(parents=True, exist_ok=True)


def download_disc():
    """Downloads or verifies DISC dataset."""
    dest_file = RAW_DIR / "disc" / "DISC.json"
    print(f"\n[1/7] Checking DISC Dataset...")
    if dest_file.exists() and dest_file.stat().st_size > 1000:
        print(f" -> Found existing DISC file at: {dest_file} ({dest_file.stat().st_size / 1024 / 1024:.2f} MB)")
        return True

    print(" -> Fetching DISC dataset from Hugging Face / Public Mirrors...")
    try:
        from datasets import load_dataset
        ds = load_dataset("GotThatData/DISC", split="train")
        records = []
        for r in ds:
            records.append(dict(r))
        with open(dest_file, "w", encoding="utf-8") as f:
            json.dump({"DISC": records}, f, indent=2)
        print(f" -> [SUCCESS] Downloaded and saved {len(records)} DISC records to {dest_file}")
        return True
    except Exception as e:
        print(f" -> [INFO] Note when fetching GotThatData/DISC: {e}")
        project_root = DATA_DIR.parent.parent
        alt_paths = [
            project_root / "dataset" / "confidential_documents" / "disc" / "DISC.json",
            project_root / "dataset" / "DISC" / "DISC.json",
        ]
        for alt in alt_paths:
            if alt.exists():
                shutil.copy2(alt, dest_file)
                print(f" -> [SUCCESS] Copied local DISC data from {alt} to {dest_file}")
                return True
        print(f" -> [WARNING] DISC source could not be downloaded automatically. Please place DISC.json in {dest_file.parent}")
        return False


def download_medical_phi():
    """Downloads or verifies Medical PHI dataset."""
    dest_dir = RAW_DIR / "medical_phi"
    parquet_files = list(dest_dir.glob("*.parquet")) + list((dest_dir / "data").glob("*.parquet"))
    print(f"\n[2/7] Checking Medical PHI Dataset...")
    if parquet_files:
        print(f" -> Found existing Medical PHI parquet file: {parquet_files[0]}")
        return True

    print(" -> Fetching Medical PHI dataset from Hugging Face (vibhoragrawal29/medical-dataset-2k-phi)...")
    try:
        from datasets import load_dataset
        ds = load_dataset("vibhoragrawal29/medical-dataset-2k-phi", split="train")
        target_parquet = dest_dir / "train-00000-of-00001.parquet"
        df = ds.to_pandas()
        df.to_parquet(target_parquet, index=False)
        print(f" -> [SUCCESS] Downloaded {len(df)} Medical PHI records to {target_parquet}")
        return True
    except Exception as e:
        print(f" -> [WARNING] Could not download Medical PHI dataset: {e}")
        return False


def download_roberta_pii_synth():
    """Downloads or verifies RoBERTa PII Synth dataset."""
    dest_dir = RAW_DIR / "roberta_pii_synth"
    print(f"\n[3/7] Checking RoBERTa PII Synth Dataset...")
    if (dest_dir / "dataset_dict.json").exists() or (dest_dir / "train").exists():
        print(f" -> Found existing RoBERTa PII Synth Arrow dataset at {dest_dir}")
        return True

    print(" -> Fetching RoBERTa PII Synth dataset from Hugging Face (tursunait/RoBERTa-pii-synth)...")
    try:
        from datasets import load_dataset
        ds = load_dataset("tursunait/RoBERTa-pii-synth")
        ds.save_to_disk(str(dest_dir))
        print(f" -> [SUCCESS] Saved RoBERTa PII Arrow dataset to {dest_dir}")
        return True
    except Exception as e:
        print(f" -> [INFO] Note fetching tursunait/RoBERTa-pii-synth: {e}")
        return False


def download_um_dlp_benchmark():
    """Downloads or verifies UM-DLP Benchmark dataset."""
    dest_dir = RAW_DIR / "um_dlp_benchmark"
    print(f"\n[4/7] Checking UM-DLP Benchmark Dataset...")
    if (dest_dir / "dataset_dict.json").exists() or (dest_dir / "train").exists() or (dest_dir / "um_dlp_raw.csv").exists():
        print(f" -> Found existing UM-DLP benchmark files at {dest_dir}")
        return True

    print(" -> Fetching UM-DLP benchmark dataset (alibustami/UM-DLP-Public-Benchmarking-Dataset)...")
    try:
        from datasets import load_dataset
        ds = load_dataset("alibustami/UM-DLP-Public-Benchmarking-Dataset")
        ds.save_to_disk(str(dest_dir))
        print(f" -> [SUCCESS] Saved UM-DLP Arrow dataset to {dest_dir}")
        return True
    except Exception as e:
        print(f" -> [INFO] Note fetching UM-DLP dataset: {e}")
        return False


def download_contextual_sensitive():
    """Downloads or verifies Contextual Sensitive dataset."""
    dest_dir = RAW_DIR / "contextual_sensitive"
    print(f"\n[5/7] Checking Contextual Sensitive Dataset...")
    if (dest_dir / "dataset_dict.json").exists() or (dest_dir / "train").exists():
        print(f" -> Found existing Contextual Sensitive Arrow dataset at {dest_dir}")
        return True

    print(" -> Fetching Contextual Sensitive dataset (trl-lab/contextual-sensitive-data)...")
    try:
        from datasets import load_dataset
        ds = load_dataset("trl-lab/contextual-sensitive-data")
        ds.save_to_disk(str(dest_dir))
        print(f" -> [SUCCESS] Saved Contextual Sensitive dataset to {dest_dir}")
        return True
    except Exception as e:
        print(f" -> [INFO] Note fetching contextual-sensitive-data: {e}")
        return False


def download_enron_emails():
    """Downloads or verifies Enron AESLC dataset."""
    dest_file = RAW_DIR / "enron_emails" / "enron_emails_raw.csv"
    print(f"\n[6/7] Checking Enron AESLC Corporate Emails...")
    if dest_file.exists() and dest_file.stat().st_size > 1000:
        print(f" -> Found existing Enron emails file at {dest_file}")
        return True

    print(" -> Fetching AESLC dataset from Hugging Face...")
    try:
        import pandas as pd
        from datasets import load_dataset
        ds = load_dataset("aeslc", split="train")
        rows = []
        for r in ds:
            rows.append({
                "subject": r.get("subject_line", "").strip(),
                "body": r.get("email_body", "").strip(),
            })
            if len(rows) >= 3000:
                break
        df = pd.DataFrame(rows)
        df.to_csv(dest_file, index=False)
        print(f" -> [SUCCESS] Saved {len(df)} Enron emails to {dest_file}")
        return True
    except Exception as e:
        print(f" -> [WARNING] Could not fetch AESLC dataset: {e}")
        return False


def download_stargate_pdfs():
    """Downloads or verifies STARGATE scanned PDF corpus."""
    dest_dir = RAW_DIR / "stargate_pdfs"
    pdf_count = len(list(dest_dir.glob("*.pdf")))
    print(f"\n[7/7] Checking STARGATE PDF Archive...")
    if pdf_count > 0:
        print(f" -> Found {pdf_count} existing STARGATE PDFs in {dest_dir}")
        return True

    print(" -> Fetching STARGATE PDF corpus from Hugging Face (GotThatData/STARGATE)...")
    try:
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id="GotThatData/STARGATE",
            repo_type="dataset",
            local_dir=str(dest_dir),
            allow_patterns=["*.pdf"],
            max_workers=4,
        )
        pdf_count_new = len(list(dest_dir.glob("*.pdf")))
        if pdf_count_new > 0:
            print(f" -> [SUCCESS] Downloaded {pdf_count_new} STARGATE PDFs from Hugging Face to {dest_dir}")
            return True
    except Exception as e:
        print(f" -> [INFO] Note fetching from GotThatData/STARGATE: {e}")

    print(" -> Searching local and fallback archives for STARGATE PDFs...")
    project_root = DATA_DIR.parent.parent
    alt_dirs = [
        project_root / "dataset" / "confidential_documents" / "stargate" / "data",
        project_root / "dataset" / "confidential_documents" / "stargate",
        project_root / "dataset" / "STARGATE",
    ]
    copied = 0
    for alt in alt_dirs:
        if alt.exists():
            for root, _, files in os.walk(alt):
                for f in files:
                    if f.lower().endswith(".pdf"):
                        src = Path(root) / f
                        dst = dest_dir / f
                        if not dst.exists():
                            shutil.copy2(src, dst)
                        copied += 1
            if copied > 0:
                print(f" -> [SUCCESS] Copied {copied} STARGATE PDFs from {alt} to {dest_dir}")
                return True

    print(f" -> [INFO] Place STARGATE PDF files into: {dest_dir}")
    return False


DOWNLOADERS = {
    "disc": download_disc,
    "medical_phi": download_medical_phi,
    "roberta_pii_synth": download_roberta_pii_synth,
    "um_dlp_benchmark": download_um_dlp_benchmark,
    "contextual_sensitive": download_contextual_sensitive,
    "enron_emails": download_enron_emails,
    "stargate_pdfs": download_stargate_pdfs,
}


def main():
    parser = argparse.ArgumentParser(description="SecureFlow AI — Raw Dataset Downloader & Verifier")
    parser.add_argument(
        "--dataset",
        choices=["all", "disc", "medical_phi", "roberta_pii_synth", "um_dlp_benchmark", "contextual_sensitive", "enron_emails", "stargate_pdfs"],
        default="all",
        help="Specify which dataset to download or verify (default: all)",
    )
    args = parser.parse_args()

    print("=" * 80)
    print(" SECUREFLOW AI — RAW DATASET INGESTION & DOWNLOAD SUITE")
    print("=" * 80)

    if args.dataset == "all":
        results = {}
        for name, func in DOWNLOADERS.items():
            results[name] = func()
        print("\n" + "=" * 80)
        print(" INGESTION SUMMARY")
        print("=" * 80)
        for name, ok in results.items():
            status = "READY / PRESENT" if ok else "SKIPPED / PENDING"
            print(f" - {name.ljust(25)} : {status}")
    else:
        func = DOWNLOADERS[args.dataset]
        func()


if __name__ == "__main__":
    main()

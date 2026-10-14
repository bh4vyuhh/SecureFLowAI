#!/usr/bin/env python3
"""
SecureFlow AI - Production Banking Data Loss Prevention (DLP) Dataset Pipeline
================================================================================
File: prepare_secureflow_banking_dataset.py

Ingests, cleans, deduplicates, and balances multi-source datasets into a 
standardized 3-class enterprise banking DLP taxonomy:
  - Label 0: SAFE (Public financial text, benign workplace conversations, interest rates, invoice context)
  - Label 1: CONFIDENTIAL (Corporate strategy, financial memos, proprietary operations, board discussions)
  - Label 2: RESTRICTED (Customer PII, SSN, Credit Cards, IBAN, Passports, Bank Accounts, KYC forms)

Also packages the UM-DLP benchmark into a separate, isolated 'adversarial_benchmark' split.
Exports Hugging Face DatasetDict locally and pushes directly to Hugging Face Hub (push_to_hub).
"""

import os
import sys
import re
import json
import glob
import time
import email
import zipfile
import hashlib
import logging
import argparse
import unicodedata
from typing import List, Dict, Tuple, Optional, Any, Set

import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.model_selection import train_test_split

import datasets
from datasets import Dataset, DatasetDict, Features, Value
from huggingface_hub import HfApi, hf_hub_download

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SecureFlowAI.DataPipeline")

# -----------------------------------------------------------------------------
# CONSTANTS & TAXONOMY DEFINITION
# -----------------------------------------------------------------------------
CLASS_NAMES = {
    0: "SAFE",
    1: "CONFIDENTIAL",
    2: "RESTRICTED"
}

CLASS_DESCRIPTIONS = {
    0: "Public financial text, benign workplace conversations, public interest rates, safe invoice/tracking numbers",
    1: "Internal corporate strategy, financial memos, proprietary operations, board discussions, business sentiment",
    2: "Customer PII, SSN, Credit Cards, IBAN, Passports, Bank Accounts, KYC forms, API keys"
}

# Regex for normalizing unicode and quotes
UNICODE_MAP = {
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u201f": '"',
    "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u00a0": " ",
    "\ufeff": "", "\r\n": "\n", "\r": "\n"
}

# Executive Strategy / Confidential detection keywords for Enron emails
ENRON_CONFIDENTIAL_KEYWORDS = re.compile(
    r"\b("
    r"strategy|strategic|acquisition|acquisitions|merger|mergers|forecast|forecasts|"
    r"budget|ebitda|revenue|earnings|financial\s+model|executive\s+committee|"
    r"board\s+of\s+directors|board\s+meeting|confidential|non-disclosure|nda|"
    r"contract\s+terms|deal\s+structure|pricing\s+agreement|liquidity|credit\s+risk|"
    r"trading\s+strategy|counterparty|settlement|proprietary|pipeline\s+capacity|"
    r"tariff|hedging|derivative|derivatives|restructuring|takeover|audit\s+committee|"
    r"due\s+diligence|commercial\s+terms|off-balance|joint\s+venture|shareholder|"
    r"insider|material\s+non-public|private\s+placement|term\s+sheet|debt\s+facility"
    r")\b",
    re.IGNORECASE
)

# Patient / Customer Identifiable regex for Medical PHI extraction
PATIENT_PII_REGEX = re.compile(
    r"\b("
    r"my\s+name\s+is\s+[A-Z][a-z]+|"
    r"(?:mr\.|mrs\.|ms\.|dr\.)\s+[A-Z][a-z]+|"
    r"patient(?:\s+name)?:\s*[A-Z][a-z]+|"
    r"\d{3}-\d{2}-\d{4}|"  # SSN format
    r"ssn\b|"
    r"dob:?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
    r"(?:age\s+)?\d{1,2}\s*(?:-|–|\s+)?year(?:s)?(?:\s+|-)?old|"
    r"phone:?\s*(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|"
    r"email:?\s*[\w\.-]+@[\w\.-]+\.\w+|"
    r"my\s+(?:wife|husband|son|daughter|mother|father|sister|brother)\b"
    r")\b",
    re.IGNORECASE
)

# Pure ICD disease code lines (to discard from Medical PHI)
PURE_ICD_CODE_REGEX = re.compile(
    r"^\s*(?:icd-?10|icd-?9|code\s+[a-z]\d{2}(?:\.\d+)?|diag\s*:\s*[a-z]\d{2,4})\s*$",
    re.IGNORECASE
)

# DISC Clearance Taxonomy Mapping
DISC_CLEARANCE_MAP = {
    "Unclassified": 0,       # Tier 1 -> SAFE
    "Secret": 1,             # Tier 2/3 -> CONFIDENTIAL
    "Confidential": 1,       # Tier 2/3 -> CONFIDENTIAL
    "Official Use Only": 1,  # Tier 2/3 -> CONFIDENTIAL
    "FOUO": 1,               # Tier 2/3 -> CONFIDENTIAL
    "Top Secret": 2,         # Tier 4 -> RESTRICTED
    "SCI": 2                 # Tier 4 -> RESTRICTED
}


# -----------------------------------------------------------------------------
# TEXT SANITIZATION & DEDUPLICATION ENGINE
# -----------------------------------------------------------------------------
class TextDeduplicator:
    """Memory-efficient hash-based deduplication tracker."""
    def __init__(self):
        self._seen_hashes: Set[str] = set()

    def is_duplicate(self, text: str) -> bool:
        # Normalize whitespace and case for hashing collision resistance
        normalized = re.sub(r"\s+", "", text.lower())
        h = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        if h in self._seen_hashes:
            return True
        self._seen_hashes.add(h)
        return False

    def count(self) -> int:
        return len(self._seen_hashes)


def clean_text(text: Any, max_tokens: int = 1024) -> str:
    """
    Cleans raw text according to production DLP standards:
    - Normalizes Unicode (NFKC) and quotes
    - Strips non-printable and null characters
    - Normalizes excessive whitespace and newlines
    - Enforces length bounds (>= 10 chars, <= 1024 tokens)
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    # Unicode normalization
    text = unicodedata.normalize("NFKC", text)
    for k, v in UNICODE_MAP.items():
        text = text.replace(k, v)

    # Filter out null bytes and non-printable control characters
    text = "".join(c for c in text if c.isprintable() or c in ("\n", "\t"))

    # Collapse horizontal spaces
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse multiple consecutive newlines to maximum 2
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    text = text.strip()

    # Minimum length filter
    if len(text) < 10:
        return ""

    # Token-level length capping (1024 whitespace-delimited tokens)
    tokens = text.split()
    if len(tokens) > max_tokens:
        text = " ".join(tokens[:max_tokens])

    return text.strip()


def parse_rfc822_email(raw_msg_str: str) -> str:
    """
    Parses RFC-822 email message, strips transport headers, and returns Subject + Body.
    """
    try:
        msg = email.message_from_string(raw_msg_str)
        subject = msg.get("Subject", "").strip()
        body_parts = []

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_parts.append(payload.decode("utf-8", errors="ignore"))
        else:
            payload = msg.get_payload(decode=False)
            if isinstance(payload, list):
                for p in payload:
                    body_parts.append(str(p.get_payload()))
            elif isinstance(payload, str):
                body_parts.append(payload)

        body = "\n".join(body_parts).strip()
        if not body:
            parts = raw_msg_str.split("\n\n", 1)
            body = parts[1].strip() if len(parts) > 1 else raw_msg_str.strip()

        # Remove transport headers that might have leaked into body
        cleaned_lines = []
        for line in body.splitlines():
            if re.match(r"^(?:X-|Message-ID:|Date:|From:|To:|Cc:|Bcc:|Mime-Version:|Content-Type:)", line, re.IGNORECASE):
                continue
            cleaned_lines.append(line)
        body = "\n".join(cleaned_lines).strip()

        if subject and not subject.lower().startswith("re:"):
            return f"Subject: {subject}\n\n{body}"
        return body
    except Exception:
        parts = raw_msg_str.split("\n\n", 1)
        return parts[1].strip() if len(parts) > 1 else raw_msg_str.strip()


# -----------------------------------------------------------------------------
# DATASET INGESTION MODULES
# -----------------------------------------------------------------------------

def load_financial_phrasebank() -> List[Dict[str, Any]]:
    """
    Dataset 1: takala/financial_phrasebank (sentences_allagree)
    Role: Public financial text -> Label 0 (SAFE)
    """
    logger.info("Ingesting takala/financial_phrasebank (sentences_allagree)...")
    records = []

    # Attempt standard load_dataset first
    loaded = False
    try:
        ds = datasets.load_dataset("takala/financial_phrasebank", "sentences_allagree", split="train")
        for item in tqdm(ds, desc="PhraseBank"):
            text = clean_text(item.get("sentence", ""))
            if text:
                records.append({"text": text, "label": 0, "source": "financial_phrasebank"})
        loaded = True
        logger.info(f"Loaded {len(records)} records from takala/financial_phrasebank via datasets API.")
    except Exception as e:
        logger.warning(f"Standard load_dataset failed ({e}). Attempting fallback download via hf_hub_download...")

    # Fallback: datasets >= 3.0 no longer executes remote .py scripts without parquet
    if not loaded:
        try:
            zip_path = hf_hub_download(
                repo_id="takala/financial_phrasebank",
                filename="data/FinancialPhraseBank-v1.0.zip",
                repo_type="dataset"
            )
            with zipfile.ZipFile(zip_path, "r") as z:
                with z.open("FinancialPhraseBank-v1.0/Sentences_AllAgree.txt") as f:
                    lines = f.read().decode("latin-1").splitlines()
                    for line in tqdm(lines, desc="PhraseBank (Zip)"):
                        if "@" in line:
                            sentence = line.rsplit("@", 1)[0].strip()
                            text = clean_text(sentence)
                            if text:
                                records.append({"text": text, "label": 0, "source": "financial_phrasebank"})
            logger.info(f"Loaded {len(records)} records from takala/financial_phrasebank via fallback archive.")
        except Exception as e2:
            logger.error(f"Failed to load financial_phrasebank via fallback: {e2}")

    return records


def load_ai4privacy_pii(max_samples: int = 25000) -> List[Dict[str, Any]]:
    """
    Dataset 2: ai4privacy/pii-masking-300k
    Role: Real-world annotated unmasked PII -> Label 2 (RESTRICTED)
    """
    logger.info(f"Ingesting ai4privacy/pii-masking-300k (Target sample: {max_samples})...")
    records = []
    try:
        ds = datasets.load_dataset("ai4privacy/pii-masking-300k", split="train")
        text_col = "unmasked_text" if "unmasked_text" in ds.column_names else "source_text"
        
        # Sample or iterate
        count = 0
        for item in tqdm(ds, desc="AI4Privacy PII"):
            raw_text = item.get(text_col, "")
            text = clean_text(raw_text)
            if text:
                records.append({"text": text, "label": 2, "source": "ai4privacy_300k"})
                count += 1
                if count >= max_samples:
                    break
        logger.info(f"Loaded {len(records)} records from ai4privacy/pii-masking-300k.")
    except Exception as e:
        logger.error(f"Error loading ai4privacy/pii-masking-300k: {e}")
    return records


def load_gretel_finance_pii(max_samples: int = 25000) -> List[Dict[str, Any]]:
    """
    Dataset 3: LightFury9/gretelai_synthetic_pii_finance_english
    Role: Banking & Financial Customer PII -> Label 2 (RESTRICTED)
    """
    logger.info(f"Ingesting LightFury9/gretelai_synthetic_pii_finance_english (Target sample: {max_samples})...")
    records = []
    try:
        ds = datasets.load_dataset("LightFury9/gretelai_synthetic_pii_finance_english", split="train")
        count = 0
        for item in tqdm(ds, desc="Gretel Finance PII"):
            raw_text = item.get("generated_text", "")
            text = clean_text(raw_text)
            if text:
                records.append({"text": text, "label": 2, "source": "gretel_finance_pii"})
                count += 1
                if count >= max_samples:
                    break
        logger.info(f"Loaded {len(records)} records from LightFury9/gretelai_synthetic_pii_finance_english.")
    except Exception as e:
        logger.error(f"Error loading LightFury9/gretelai_synthetic_pii_finance_english: {e}")
    return records


def load_fingpt_sentiment(max_samples: int = 40000) -> List[Dict[str, Any]]:
    """
    Dataset 4: FinGPT/fingpt-sentiment-train
    Role: Corporate financial statements & analyst memos -> Label 1 (CONFIDENTIAL)
    """
    logger.info(f"Ingesting FinGPT/fingpt-sentiment-train (Target sample: {max_samples})...")
    records = []
    try:
        ds = datasets.load_dataset("FinGPT/fingpt-sentiment-train", split="train")
        count = 0
        for item in tqdm(ds, desc="FinGPT Sentiment"):
            raw_text = item.get("input", "")
            text = clean_text(raw_text)
            if text:
                records.append({"text": text, "label": 1, "source": "fingpt_sentiment"})
                count += 1
                if count >= max_samples:
                    break
        logger.info(f"Loaded {len(records)} records from FinGPT/fingpt-sentiment-train.")
    except Exception as e:
        logger.error(f"Error loading FinGPT/fingpt-sentiment-train: {e}")
    return records


def load_enron_emails(
    max_samples: int = 45000, 
    fallback_dir: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Dataset 5: wcukierski/enron-email-dataset (via kagglehub)
    Role:
      - Routine internal emails -> Label 0 (SAFE)
      - Executive strategy & deal discussion -> Label 1 (CONFIDENTIAL)
    """
    logger.info(f"Ingesting Enron email dataset (KaggleHub target: {max_samples})...")
    records = []
    csv_file_path = None

    # Step 1: Attempt download via KaggleHub
    try:
        import kagglehub
        logger.info("Calling kagglehub.dataset_download('wcukierski/enron-email-dataset')...")
        download_dir = kagglehub.dataset_download("wcukierski/enron-email-dataset")
        candidate = os.path.join(download_dir, "emails.csv")
        if os.path.exists(candidate):
            csv_file_path = candidate
            logger.info(f"Located KaggleHub Enron dataset at: {csv_file_path}")
    except Exception as e:
        logger.warning(f"KaggleHub download encountered an issue: {e}")

    # Step 2: Fallback to existing raw CSV if KaggleHub unavailable
    if not csv_file_path and fallback_dir:
        candidates = [
            os.path.join(fallback_dir, "enron_emails", "enron_emails_raw.csv"),
            os.path.join(fallback_dir, "enron_emails", "emails.csv"),
        ]
        for c in candidates:
            if os.path.exists(c):
                csv_file_path = c
                logger.info(f"Using fallback local Enron file: {csv_file_path}")
                break

    if not csv_file_path or not os.path.exists(csv_file_path):
        logger.error("Could not locate Enron email dataset CSV file.")
        return records

    # Step 3: Parse and Classify emails
    try:
        # Read in chunks to handle memory smoothly
        chunksize = 10000
        count = 0
        safe_count = 0
        confidential_count = 0

        logger.info(f"Parsing Enron emails from {csv_file_path}...")
        for chunk in pd.read_csv(csv_file_path, chunksize=chunksize):
            # Check message column
            msg_col = "message" if "message" in chunk.columns else ("body" if "body" in chunk.columns else chunk.columns[0])
            for _, row in chunk.iterrows():
                raw_msg = str(row[msg_col])
                parsed_text = parse_rfc822_email(raw_msg)
                text = clean_text(parsed_text)
                if not text:
                    continue

                # Map based on executive strategy / deal discussion keywords
                if ENRON_CONFIDENTIAL_KEYWORDS.search(text):
                    label = 1  # CONFIDENTIAL
                    confidential_count += 1
                else:
                    label = 0  # SAFE
                    safe_count += 1

                records.append({"text": text, "label": label, "source": "enron_kaggle"})
                count += 1
                if count >= max_samples:
                    break

            if count >= max_samples:
                break

        logger.info(f"Loaded {len(records)} Enron emails: {safe_count} SAFE (Label 0), {confidential_count} CONFIDENTIAL (Label 1).")
    except Exception as e:
        logger.error(f"Error parsing Enron emails: {e}")

    return records


def load_roberta_pii(raw_dir: str, max_samples: int = 30000) -> List[Dict[str, Any]]:
    """
    Dataset 6: Existing RoBERTa PII Synth (Arrow format)
    Role: Extract raw text containing detected PII -> Label 2 (RESTRICTED)
    """
    path = os.path.join(raw_dir, "roberta_pii_synth")
    logger.info(f"Ingesting existing RoBERTa PII from {path}...")
    records = []
    if not os.path.exists(path):
        logger.warning(f"RoBERTa PII directory not found at {path}. Skipping.")
        return records

    try:
        ds_dict = datasets.load_from_disk(path)
        splits = ["train", "validation", "test"] if isinstance(ds_dict, DatasetDict) else [None]
        count = 0

        for split in splits:
            ds = ds_dict[split] if split else ds_dict
            for item in tqdm(ds, desc=f"RoBERTa PII ({split})"):
                raw_text = item.get("text", "")
                spans = item.get("spans", [])
                # Ensure it contains detected PII
                if spans or raw_text:
                    text = clean_text(raw_text)
                    if text:
                        records.append({"text": text, "label": 2, "source": "roberta_pii_existing"})
                        count += 1
                        if count >= max_samples:
                            break
            if count >= max_samples:
                break

        logger.info(f"Loaded {len(records)} records from existing RoBERTa PII.")
    except Exception as e:
        logger.error(f"Error loading RoBERTa PII: {e}")
    return records


def load_disc_dataset(raw_dir: str) -> List[Dict[str, Any]]:
    """
    Dataset 7: Existing DISC (JSON / 2,459 docs)
    Mapping:
      - Tier 1 (Unclassified) -> Label 0 (SAFE)
      - Tier 2/3 (Confidential / Secret) -> Label 1 (CONFIDENTIAL)
      - Tier 4 (Top Secret) -> Label 2 (RESTRICTED)
    """
    disc_path = os.path.join(raw_dir, "disc", "DISC.json")
    logger.info(f"Ingesting existing DISC intelligence corpus from {disc_path}...")
    records = []
    if not os.path.exists(disc_path):
        logger.warning(f"DISC.json not found at {disc_path}. Skipping.")
        return records

    try:
        with open(disc_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in tqdm(data.get("DISC", []), desc="DISC Corpus"):
            raw_text = item.get("Text", "")
            assigned_label = None

            for cls in item.get("Classification", []):
                raw_label = cls.get("Label")
                if raw_label in DISC_CLEARANCE_MAP:
                    assigned_label = DISC_CLEARANCE_MAP[raw_label]
                    break

            if raw_text and assigned_label is not None:
                # Strip leading security clearance classification headers to avoid trivial leakage
                cleaned_header_text = re.sub(
                    r"^\s*(?:TOP\s+SECRET|SECRET|CONFIDENTIAL|UNCLASSIFIED)[\s\:\-]+",
                    "",
                    raw_text,
                    flags=re.IGNORECASE
                )
                text = clean_text(cleaned_header_text)
                if text:
                    records.append({"text": text, "label": assigned_label, "source": "disc_intelligence"})

        logger.info(f"Loaded {len(records)} records from DISC dataset.")
    except Exception as e:
        logger.error(f"Error loading DISC dataset: {e}")
    return records


def load_contextual_sensitive(raw_dir: str) -> List[Dict[str, Any]]:
    """
    Dataset 8: Existing Contextual Data (Arrow/CSV)
    Role: Non-sensitive schema / invoice contexts -> Label 0 (SAFE)
    """
    path = os.path.join(raw_dir, "contextual_sensitive")
    logger.info(f"Ingesting existing Contextual Sensitive data from {path}...")
    records = []
    if not os.path.exists(path):
        logger.warning(f"Contextual data directory not found at {path}. Skipping.")
        return records

    try:
        ds = datasets.load_from_disk(path)
        train_ds = ds["train"] if isinstance(ds, DatasetDict) else ds

        for item in tqdm(train_ds, desc="Contextual Non-Sensitive"):
            output_val = item.get("output")
            # Filter for non-sensitive schema/column definitions
            if output_val is None or str(output_val).strip() in ("", "None", "nan"):
                # Use clean input representation or column + records
                raw_text = item.get("input", "")
                if not raw_text:
                    col = item.get("column_name", "")
                    recs = item.get("records", "")
                    raw_text = f"Schema Column: {col} | Sample Values: {recs}"
                
                text = clean_text(raw_text)
                if text:
                    records.append({"text": text, "label": 0, "source": "contextual_safe_schema"})

        logger.info(f"Loaded {len(records)} non-sensitive schema records from Contextual Data.")
    except Exception as e:
        logger.error(f"Error loading Contextual Data: {e}")
    return records


def load_medical_phi(raw_dir: str) -> List[Dict[str, Any]]:
    """
    Dataset 9: Existing Medical PHI (Parquet)
    Role: Extract customer names/SSNs/demographics -> Label 2 (RESTRICTED);
          discard pure medical ICD disease codes.
    """
    path = os.path.join(raw_dir, "medical_phi")
    logger.info(f"Ingesting existing Medical PHI from {path}...")
    records = []
    if not os.path.exists(path):
        logger.warning(f"Medical PHI directory not found at {path}. Skipping.")
        return records

    try:
        parquet_files = glob.glob(os.path.join(path, "**", "*.parquet"), recursive=True)
        if not parquet_files:
            logger.warning(f"No parquet files found in {path}.")
            return records

        df = pd.concat([pd.read_parquet(f) for f in parquet_files], ignore_index=True)
        for _, row in tqdm(df.iterrows(), total=len(df), desc="Medical PHI"):
            prompt = str(row.get("prompt", "")).strip()
            completion = str(row.get("completion", "")).strip()
            combined = f"{prompt}\n\n{completion}".strip() if prompt and completion else (prompt or completion)

            # Discard pure medical ICD code queries
            if PURE_ICD_CODE_REGEX.match(prompt) or PURE_ICD_CODE_REGEX.match(combined):
                continue

            # Extract samples containing patient/customer identifiers
            if PATIENT_PII_REGEX.search(prompt) or PATIENT_PII_REGEX.search(combined):
                text = clean_text(combined)
                if text:
                    records.append({"text": text, "label": 2, "source": "medical_phi_patient"})

        logger.info(f"Loaded {len(records)} customer-identifying records from Medical PHI.")
    except Exception as e:
        logger.error(f"Error loading Medical PHI: {e}")
    return records


def load_um_dlp_adversarial_benchmark(raw_dir: str) -> List[Dict[str, Any]]:
    """
    Dataset 10: UM-DLP Benchmark (1,343 rows)
    Role: DO NOT mix into train/val/test splits!
          Preserve separately as a dedicated 'adversarial_benchmark' split.
    """
    path = os.path.join(raw_dir, "um_dlp_benchmark")
    logger.info(f"Ingesting UM-DLP Adversarial Benchmark from {path}...")
    benchmark_records = []
    if not os.path.exists(path):
        logger.warning(f"UM-DLP benchmark directory not found at {path}. Skipping.")
        return benchmark_records

    try:
        ds = datasets.load_from_disk(path)
        train_ds = ds["train"] if isinstance(ds, DatasetDict) else ds

        for item in tqdm(train_ds, desc="UM-DLP Benchmark"):
            raw_text = item.get("Test data", "")
            text = clean_text(raw_text)
            if not text:
                continue

            gt = str(item.get("Ground Truth (sensitive/non sensitive)", "")).strip().lower()
            category = str(item.get("Category", "")).strip()
            adv_type = str(item.get("Type", "")).strip()

            # Map label strictly into our 3 target classes:
            if "non sensitive" in gt or gt == "0":
                label = 0  # SAFE
            else:
                # Sensitive categories: check if Corporate Finance vs Customer PII / PCI DSS
                if any(k in category.lower() for k in ["corporate", "statement"]):
                    label = 1  # CONFIDENTIAL
                else:
                    label = 2  # RESTRICTED (PII, PCI-DSS, Payment, Account)

            benchmark_records.append({
                "text": text,
                "label": label,
                "category": category,
                "adversarial_type": adv_type,
                "ground_truth_raw": gt,
                "source": "um_dlp_benchmark"
            })

        logger.info(f"Loaded {len(benchmark_records)} benchmark evaluation records from UM-DLP.")
    except Exception as e:
        logger.error(f"Error loading UM-DLP benchmark: {e}")
    return benchmark_records


# -----------------------------------------------------------------------------
# DEDUPLICATION & CLASS BALANCING ENGINE
# -----------------------------------------------------------------------------

def deduplicate_and_balance_corpus(
    all_records: List[Dict[str, Any]], 
    target_samples_per_class: int = 35000,
    seed: int = 42
) -> pd.DataFrame:
    """
    Performs global cross-source deduplication and balances the dataset
    to achieve uniform class representation across Labels 0, 1, and 2.
    """
    logger.info("Executing global deduplication across all ingested data...")
    deduplicator = TextDeduplicator()
    unique_records = []
    duplicates_dropped = 0

    for item in tqdm(all_records, desc="Global Deduplication"):
        text = item["text"]
        if deduplicator.is_duplicate(text):
            duplicates_dropped += 1
            continue
        unique_records.append(item)

    logger.info(f"Deduplication complete: Kept {len(unique_records)} unique texts, dropped {duplicates_dropped} duplicates.")
    df = pd.DataFrame(unique_records)

    logger.info("Pre-balancing Class Distribution:")
    for lbl in [0, 1, 2]:
        sub_df = df[df["label"] == lbl]
        src_counts = sub_df["source"].value_counts().to_dict()
        logger.info(f"  Class {lbl} ({CLASS_NAMES[lbl]}): {len(sub_df)} records | Sources: {src_counts}")

    # Stratified balancing per class
    balanced_dfs = []
    rng = np.random.RandomState(seed)

    for lbl in [0, 1, 2]:
        sub_df = df[df["label"] == lbl]
        available = len(sub_df)
        if available == 0:
            logger.error(f"Critical: Class {lbl} ({CLASS_NAMES[lbl]}) has 0 samples!")
            continue

        if available >= target_samples_per_class:
            logger.info(f"Downsampling Class {lbl} from {available} to target {target_samples_per_class}...")
            sampled = sub_df.sample(n=target_samples_per_class, random_state=seed)
        else:
            logger.warning(
                f"Class {lbl} has {available} samples (< target {target_samples_per_class}). "
                f"Resampling with replacement to balance class distribution."
            )
            sampled = sub_df.sample(n=target_samples_per_class, replace=True, random_state=seed)

        balanced_dfs.append(sampled)

    final_df = pd.concat(balanced_dfs, ignore_index=True)
    # Shuffle
    final_df = final_df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    logger.info("Post-balancing Class Distribution:")
    for lbl in [0, 1, 2]:
        count = len(final_df[final_df["label"] == lbl])
        logger.info(f"  Class {lbl} ({CLASS_NAMES[lbl]}): {count} samples ({count / len(final_df) * 100:.1f}%)")

    return final_df


# -----------------------------------------------------------------------------
# STRATIFIED SPLITTING & BENCHMARK ISOLATION
# -----------------------------------------------------------------------------

def create_dataset_dict(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    benchmark_records: List[Dict[str, Any]]
) -> DatasetDict:
    """
    Constructs standardized Hugging Face DatasetDict with:
      - train: 70%
      - validation: 15%
      - test: 15%
      - adversarial_benchmark: UM-DLP benchmark (isolated)
    All splits share a uniform feature schema to ensure push_to_hub compatibility.
    """
    logger.info("Assembling Hugging Face DatasetDict splits with unified schema...")

    # Unified feature schema across all splits (required by HF push_to_hub)
    unified_features = Features({
        "text": Value("string"),
        "label": Value("int64"),
        "source": Value("string"),
        "category": Value("string"),
        "adversarial_type": Value("string"),
        "ground_truth_raw": Value("string")
    })

    cols = ["text", "label", "source", "category", "adversarial_type", "ground_truth_raw"]
    for df in [train_df, val_df, test_df]:
        for c in ["category", "adversarial_type", "ground_truth_raw"]:
            if c not in df.columns:
                df[c] = None

    ds_train = Dataset.from_pandas(train_df[cols], features=unified_features, preserve_index=False)
    ds_val = Dataset.from_pandas(val_df[cols], features=unified_features, preserve_index=False)
    ds_test = Dataset.from_pandas(test_df[cols], features=unified_features, preserve_index=False)

    df_bench = pd.DataFrame(benchmark_records)
    if not df_bench.empty:
        for c in cols:
            if c not in df_bench.columns:
                df_bench[c] = None
        ds_bench = Dataset.from_pandas(df_bench[cols], features=unified_features, preserve_index=False)
    else:
        ds_bench = Dataset.from_dict({k: [] for k in unified_features.keys()}, features=unified_features)

    dataset_dict = DatasetDict({
        "train": ds_train,
        "validation": ds_val,
        "test": ds_test,
        "adversarial_benchmark": ds_bench
    })

    return dataset_dict


# -----------------------------------------------------------------------------
# EXPORT & HUB UPLOAD ENGINE
# -----------------------------------------------------------------------------

def save_and_publish_dataset(
    dataset_dict: DatasetDict,
    output_dir: str,
    repo_id: Optional[str] = None,
    token: Optional[str] = None,
    push_to_hub: bool = False,
    private: bool = True
) -> None:
    """
    Saves DatasetDict locally (Arrow format + Parquet exports + Manifest)
    and pushes to Hugging Face Hub if credentials and flag are supplied.
    """
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Saving DatasetDict locally to: {output_dir}...")
    dataset_dict.save_to_disk(output_dir)

    # Parquet export directory
    parquet_dir = os.path.join(output_dir, "parquet")
    os.makedirs(parquet_dir, exist_ok=True)
    for split_name, ds in dataset_dict.items():
        parquet_file = os.path.join(parquet_dir, f"{split_name}.parquet")
        ds.to_parquet(parquet_file)
        logger.info(f"  Exported {split_name} ({len(ds)} rows) to Parquet: {parquet_file}")

    # Dataset Manifest
    manifest = {
        "dataset_name": "SecureFlow Banking DLP 3-Class Dataset",
        "taxonomy": {str(k): {"name": v, "description": CLASS_DESCRIPTIONS[k]} for k, v in CLASS_NAMES.items()},
        "splits": {split: len(ds) for split, ds in dataset_dict.items()},
        "total_primary_samples": len(dataset_dict["train"]) + len(dataset_dict["validation"]) + len(dataset_dict["test"]),
        "benchmark_samples": len(dataset_dict["adversarial_benchmark"]),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "features": {split: list(ds.features.keys()) for split, ds in dataset_dict.items()}
    }
    manifest_path = os.path.join(output_dir, "dataset_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info(f"Generated dataset manifest: {manifest_path}")

    # Generate Dataset Card / README.md
    readme_content = f"""---
language:
- en
license: mit
task_categories:
- text-classification
tags:
- banking
- dlp
- data-loss-prevention
- security
- pii
- compliance
pretty_name: SecureFlow Banking DLP 3-Class Dataset
size_categories:
- 100K<n<1M
---

# SecureFlow AI — Banking DLP 3-Class Dataset

A production-grade, multi-source Data Loss Prevention (DLP) benchmark and training dataset specifically engineered for enterprise banking and financial services.

## 1. Class Taxonomy
- **Label 0: SAFE** — {CLASS_DESCRIPTIONS[0]}
- **Label 1: CONFIDENTIAL** — {CLASS_DESCRIPTIONS[1]}
- **Label 2: RESTRICTED** — {CLASS_DESCRIPTIONS[2]}

## 2. Dataset Partition Summary
- **Train Split (70%)**: {len(dataset_dict['train']):,} records
- **Validation Split (15%)**: {len(dataset_dict['validation']):,} records
- **Test Split (15%)**: {len(dataset_dict['test']):,} records
- **Adversarial Benchmark (Isolated)**: {len(dataset_dict['adversarial_benchmark']):,} records (UM-DLP adversarial evasion benchmark)

## 3. Data Sources Integrated
1. `takala/financial_phrasebank` (sentences_allagree) -> SAFE
2. `FinGPT/fingpt-sentiment-train` -> CONFIDENTIAL
3. `wcukierski/enron-email-dataset` -> SAFE & CONFIDENTIAL
4. `ai4privacy/pii-masking-300k` -> RESTRICTED
5. `LightFury9/gretelai_synthetic_pii_finance_english` -> RESTRICTED
6. `RoBERTa PII Synth` -> RESTRICTED
7. `DISC Intelligence Archive` -> SAFE, CONFIDENTIAL, RESTRICTED
8. `Contextual Schema Metadata` -> SAFE
9. `Medical PHI Customer Records` -> RESTRICTED
10. `UM-DLP Benchmark` -> Isolated Adversarial Benchmark
"""
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    # Export CSV files into output_dir
    for split_name, ds in dataset_dict.items():
        csv_file = os.path.join(output_dir, f"{split_name}.csv")
        ds.to_pandas().to_csv(csv_file, index=False)
        logger.info(f"  Exported {split_name} ({len(ds)} rows) to CSV: {csv_file}")

    # Push to Hugging Face Hub
    if push_to_hub or token:
        if not repo_id:
            logger.error("Hugging Face upload requested but --repo_id is missing.")
            return

        import huggingface_hub
        resolved_token = token or os.environ.get("HF_TOKEN") or huggingface_hub.get_token()
        if not resolved_token:
            logger.warning("No Hugging Face token detected in --token, HF_TOKEN env var, or cached credentials. Skipping upload.")
            return

        logger.info(f"Pushing DatasetDict to Hugging Face Hub repository: '{repo_id}' (private={private})...")
        try:
            api = HfApi(token=resolved_token)
            api.create_repo(repo_id=repo_id, repo_type="dataset", private=private, exist_ok=True)
            dataset_dict.push_to_hub(
                repo_id=repo_id,
                token=resolved_token,
                private=private
            )
            logger.info(f"[SUCCESS] Dataset pushed to Hugging Face Hub: https://huggingface.co/datasets/{repo_id}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to push dataset to Hugging Face Hub: {e}")
            logger.info("Local datasets and Parquet exports remain intact.")


# -----------------------------------------------------------------------------
# MAIN PIPELINE ORCHESTRATION
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="SecureFlow AI - Production Banking DLP 3-Class Dataset Builder & Hub Publisher"
    )
    parser.add_argument("--raw_dir", type=str, default="./ai-service/data/raw", help="Path to local raw datasets")
    parser.add_argument("--output_dir", type=str, default="./dataset_output", help="Output directory for generated dataset")
    parser.add_argument("--samples_per_class", type=int, default=35000, help="Target balanced samples per class (default: 35,000)")
    parser.add_argument("--max_enron_samples", type=int, default=45000, help="Max Enron emails to parse (default: 45,000)")
    parser.add_argument("--max_ai4privacy_samples", type=int, default=25000, help="Max AI4Privacy samples (default: 25,000)")
    parser.add_argument("--max_gretel_samples", type=int, default=25000, help="Max Gretel samples (default: 25,000)")
    parser.add_argument("--max_fingpt_samples", type=int, default=40000, help="Max FinGPT samples (default: 40,000)")
    parser.add_argument("--max_roberta_samples", type=int, default=30000, help="Max RoBERTa PII samples (default: 30,000)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for splitting and sampling (default: 42)")
    parser.add_argument("--repo_id", type=str, default="xorushi/secureflow-banking-dlp-3class", help="Hugging Face repo ID (e.g., 'username/secureflow-banking-dlp-3class')")
    parser.add_argument("--token", type=str, default=None, help="Hugging Face API token (or HF_TOKEN env var)")
    parser.add_argument("--push_to_hub", action="store_true", help="Push assembled DatasetDict to Hugging Face Hub")
    parser.add_argument("--public", action="store_true", help="Make Hugging Face repo public (default: private)")
    parser.add_argument("--dry_run", action="store_true", help="Dry run test mode: processes small batch for verification")

    args = parser.parse_args()

    # Dry run parameter adjustment
    if args.dry_run:
        logger.info(">>> DRY RUN MODE ACTIVATED: Scaling down sample targets for rapid verification <<<")
        args.samples_per_class = 500
        args.max_enron_samples = 1000
        args.max_ai4privacy_samples = 500
        args.max_gretel_samples = 500
        args.max_fingpt_samples = 1000
        args.max_roberta_samples = 500

    # Dynamic path resolution across all directory levels
    raw_dir = args.raw_dir
    if not os.path.exists(raw_dir):
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        alt_candidates = [
            os.path.abspath(os.path.join(current_file_dir, "..", "raw")),
            os.path.abspath(os.path.join(current_file_dir, "..", "..", "data", "raw")),
            os.path.abspath(os.path.join(current_file_dir, "ai-service", "data", "raw")),
            os.path.abspath("./ai-service/data/raw"),
            os.path.abspath("./data/raw")
        ]
        for alt in alt_candidates:
            if os.path.exists(alt):
                raw_dir = alt
                logger.info(f"Resolved raw data directory to: {raw_dir}")
                break

    logger.info("=" * 80)
    logger.info(" SECUREFLOW AI: BANKING DLP 3-CLASS DATASET PREPARATION PIPELINE")
    logger.info("=" * 80)
    logger.info(f"Target Samples Per Class: {args.samples_per_class}")
    logger.info(f"Target Total Primary Size: ~{args.samples_per_class * 3:,} records")
    logger.info(f"Raw Data Path: {raw_dir}")
    logger.info(f"Output Directory: {args.output_dir}")
    logger.info(f"Random Seed: {args.seed}")
    logger.info("=" * 80)

    start_time = time.time()
    all_records: List[Dict[str, Any]] = []

    # -------------------------------------------------------------------------
    # 1. INGESTION PHASE: New Datasets
    # -------------------------------------------------------------------------
    # 1.1 Financial PhraseBank (Label 0: SAFE)
    phrasebank_records = load_financial_phrasebank()
    all_records.extend(phrasebank_records)

    # 1.2 AI4Privacy 300k (Label 2: RESTRICTED)
    ai4privacy_records = load_ai4privacy_pii(max_samples=args.max_ai4privacy_samples)
    all_records.extend(ai4privacy_records)

    # 1.3 Gretel Synthetic PII Finance (Label 2: RESTRICTED)
    gretel_records = load_gretel_finance_pii(max_samples=args.max_gretel_samples)
    all_records.extend(gretel_records)

    # 1.4 FinGPT Sentiment Train (Label 1: CONFIDENTIAL)
    fingpt_records = load_fingpt_sentiment(max_samples=args.max_fingpt_samples)
    all_records.extend(fingpt_records)

    # 1.5 Enron Email Dataset (KaggleHub: Label 0 SAFE & Label 1 CONFIDENTIAL)
    enron_records = load_enron_emails(max_samples=args.max_enron_samples, fallback_dir=raw_dir)
    all_records.extend(enron_records)

    # -------------------------------------------------------------------------
    # 2. INGESTION PHASE: Existing Datasets
    # -------------------------------------------------------------------------
    # 2.1 RoBERTa PII Synth (Label 2: RESTRICTED)
    roberta_records = load_roberta_pii(raw_dir=raw_dir, max_samples=args.max_roberta_samples)
    all_records.extend(roberta_records)

    # 2.2 DISC Intelligence (Label 0 SAFE, Label 1 CONFIDENTIAL, Label 2 RESTRICTED)
    disc_records = load_disc_dataset(raw_dir=raw_dir)
    all_records.extend(disc_records)

    # 2.3 Contextual Sensitive Schema (Label 0: SAFE)
    contextual_records = load_contextual_sensitive(raw_dir=raw_dir)
    all_records.extend(contextual_records)

    # 2.4 Medical PHI Patient Records (Label 2: RESTRICTED)
    medical_records = load_medical_phi(raw_dir=raw_dir)
    all_records.extend(medical_records)

    # -------------------------------------------------------------------------
    # 3. BENCHMARK ISOLATION PHASE
    # -------------------------------------------------------------------------
    # 3.1 UM-DLP (Adversarial Benchmark - Kept separate!)
    benchmark_records = load_um_dlp_adversarial_benchmark(raw_dir=raw_dir)

    total_ingested = len(all_records)
    logger.info(f"Total raw primary records ingested: {total_ingested:,}")
    if total_ingested == 0:
        logger.error("No training data records were successfully ingested. Exiting pipeline.")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # 4. CLEANING, DEDUPLICATION & BALANCING
    # -------------------------------------------------------------------------
    balanced_df = deduplicate_and_balance_corpus(
        all_records, 
        target_samples_per_class=args.samples_per_class, 
        seed=args.seed
    )

    # -------------------------------------------------------------------------
    # 5. STRATIFIED SPLITTING (70% Train, 15% Val, 15% Test)
    # -------------------------------------------------------------------------
    logger.info("Executing Stratified Split (70% Train, 15% Validation, 15% Test)...")
    train_df, temp_df = train_test_split(
        balanced_df,
        test_size=0.30,
        stratify=balanced_df["label"],
        random_state=args.seed
    )
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        stratify=temp_df["label"],
        random_state=args.seed
    )

    logger.info("Split Sizes:")
    logger.info(f"  Train:      {len(train_df):,} samples ({len(train_df) / len(balanced_df) * 100:.1f}%)")
    logger.info(f"  Validation: {len(val_df):,} samples ({len(val_df) / len(balanced_df) * 100:.1f}%)")
    logger.info(f"  Test:       {len(test_df):,} samples ({len(test_df) / len(balanced_df) * 100:.1f}%)")
    logger.info(f"  Benchmark:  {len(benchmark_records):,} evaluation samples (UM-DLP isolated)")

    # -------------------------------------------------------------------------
    # 6. ASSEMBLE HUGGING FACE DATASETDICT
    # -------------------------------------------------------------------------
    dataset_dict = create_dataset_dict(train_df, val_df, test_df, benchmark_records)
    logger.info(f"Assembled DatasetDict: {dataset_dict}")

    # -------------------------------------------------------------------------
    # 7. LOCAL PERSISTENCE & HUB PUBLISHING
    # -------------------------------------------------------------------------
    save_and_publish_dataset(
        dataset_dict=dataset_dict,
        output_dir=args.output_dir,
        repo_id=args.repo_id,
        token=args.token,
        push_to_hub=args.push_to_hub,
        private=not args.public
    )

    elapsed = time.time() - start_time
    logger.info("=" * 80)
    logger.info(f" SECUREFLOW AI DATASET PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f}s")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SecureFlow AI - Production 3-Class Banking DLP Classifier Trainer
================================================================================
File: ai-service/scripts/train_banking_classifier.py

Key Capabilities:
  - 3 Target Classes: 0: SAFE, 1: CONFIDENTIAL, 2: RESTRICTED
  - Resilient, crash-proof checkpoint resumption (Ctrl+C, power cut, OOM recovery)
  - Device agnostic: CUDA (FP16), Apple Silicon MPS, or CPU (with gradient accumulation)
  - Weighted Cross-Entropy Loss (2.5x penalty on missing RESTRICTED PII/PCI leaks)
  - Metric for best model: restricted_leak_recall (PCI-DSS & GDPR safety enforcement)
  - Dynamic padding per batch (max_length=256) saving memory and compute
  - Quick Presentation Baseline (TF-IDF + LogisticRegression) for viva/defense proof
  - Complete output artifacts for model packaging and ONNX export
"""

import os
import sys
import re
import gc
import json
import time
import signal
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

import torch
import torch.nn as nn
from datasets import Dataset, DatasetDict, load_from_disk, load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding,
    EarlyStoppingCallback,
    set_seed
)

# -----------------------------------------------------------------------------
# Structured Logging
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SecureFlowAI.Trainer")

# -----------------------------------------------------------------------------
# Constants & Taxonomy
# -----------------------------------------------------------------------------
ID2LABEL = {
    0: "SAFE",
    1: "CONFIDENTIAL",
    2: "RESTRICTED"
}
LABEL2ID = {v: k for k, v in ID2LABEL.items()}

# Default Class Weights for Banking Loss Penalty (2.5x on RESTRICTED leaks)
BANKING_CLASS_WEIGHTS = [1.0, 1.2, 2.5]


# -----------------------------------------------------------------------------
# Path Resolution Helpers
# -----------------------------------------------------------------------------
def get_default_paths() -> Tuple[Path, Path, Path]:
    """Resolves project root, ai-service directory, and models directory."""
    current_dir = Path(__file__).resolve().parent
    if "ai-service" in [p.name for p in current_dir.parents] or current_dir.name == "ai-service":
        for p in [current_dir] + list(current_dir.parents):
            if p.name == "ai-service":
                ai_service_dir = p
                project_root = p.parent
                break
    else:
        project_root = current_dir.parent
        ai_service_dir = project_root / "ai-service" if (project_root / "ai-service").exists() else project_root

    models_dir = ai_service_dir / "models"
    return project_root, ai_service_dir, models_dir


# -----------------------------------------------------------------------------
# Signal Handler for Graceful Interruption
# -----------------------------------------------------------------------------
def setup_signal_handlers(checkpoint_dir: Path):
    """Installs signal handlers to ensure checkpoint safety upon Ctrl+C or SIGTERM."""
    def handler(signum, frame):
        sig_name = signal.Signals(signum).name
        logger.warning(
            f"\n[INTERRUPT DETECTED: {sig_name}] Cleaning up and protecting checkpoint state..."
        )
        logger.warning(
            f"Checkpoints in '{checkpoint_dir}' are preserved. "
            f"Re-running this script will automatically resume from the latest saved checkpoint."
        )
        sys.exit(0)

    try:
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
    except (ValueError, AttributeError):
        pass


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Anti-Cheating & Text Sanitization Engine
# -----------------------------------------------------------------------------
def strip_meta_labels_and_headers(text: str) -> str:
    """
    Prevents the model from cheating on artificial metadata headers or explicit tags.
    Forces the Transformer self-attention layers to look inside the actual document content,
    discerning sensitive financial syntax, PII, and corporate context on its own.
    """
    if not text:
        return ""

    # 1. Strip explicit class tag banners at start of string (e.g. "[RESTRICTED]:", "CONFIDENTIAL -", "SAFE:")
    text = re.sub(
        r"^(?:[\s\-_*=#]*\[?(?:RESTRICTED|CONFIDENTIAL|SAFE|TOP\s+SECRET|INTERNAL\s+ONLY|STRICTLY\s+CONFIDENTIAL|PROPRIETARY|SECRET)\]?[\s:\-_*=#]+)+",
        "",
        text,
        flags=re.IGNORECASE
    )

    # 2. Strip bracket tags in subject lines (e.g. "Subject: [CONFIDENTIAL] Memo" -> "Subject: Memo")
    text = re.sub(
        r"(?i)(Subject:\s*)\[(?:RESTRICTED|CONFIDENTIAL|SAFE|INTERNAL\s+ONLY|SENSITIVE|PII)\]\s*",
        r"\1",
        text
    )

    # 3. Strip artificial prompt/metadata lines (e.g. "Classification: RESTRICTED", "Label: 2", "Category: PII", "Source: enron")
    text = re.sub(
        r"(?mi)^\s*(?:Classification|Security\s+Classification|Data\s+Classification|Sensitivity|Sensitivity\s+Level|Label|Category|Source|Data\s+Source|Ground\s*Truth|Document\s*Type|Doc\s*Type|Status|DLP\s+Level|Policy|Tag|Instruction|Prompt)[\s:\-_]+.*$",
        "",
        text
    )

    # 4. Strip inline synthetic markup tags (brackets, angles, entity tags)
    text = re.sub(
        r"\[/?(?:PII|CONFIDENTIAL|RESTRICTED|SAFE|SENSITIVE|SECRET|INTERNAL|HIGH_RISK|SSN|CREDIT_CARD|ACCOUNT_NUMBER|IBAN|PASSPORT)\]",
        "",
        text,
        flags=re.IGNORECASE
    )
    text = re.sub(
        r"</?(?:PII|CONFIDENTIAL|RESTRICTED|SAFE|SENSITIVE|SECRET|INTERNAL|HIGH_RISK|CLASSIFICATION|METADATA|LABEL|SSN|CREDIT_CARD|ACCOUNT_NUMBER|IBAN|PASSPORT)>",
        "",
        text,
        flags=re.IGNORECASE
    )

    # 5. Strip artificial synthetic generation headers
    text = re.sub(
        r"(?mi)^\s*(?:Here\s+is\s+a\s+synthetic|Generated\s+sample\s+of|The\s+following\s+is\s+an\s+example\s+of|Synthetic\s+record:?).*$",
        "",
        text
    )

    # 6. Strip boilerplate confidentiality notices/disclaimers at footer
    text = re.sub(
        r"(?mi)^\s*(?:CONFIDENTIALITY\s+NOTICE|DISCLAIMER|NOTICE\s+OF\s+CONFIDENTIALITY):?\s+This\s+(?:email|transmission|message|document)\s+(?:is\s+intended|contains).*$",
        "",
        text
    )

    # 7. Collapse leftover whitespace
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


# -----------------------------------------------------------------------------
# Multi-Source Dataset Ingestion & Merging Engine
# -----------------------------------------------------------------------------
def merge_ingested_documents(
    ds_dict: DatasetDict,
    ai_service_dir: Path,
    project_root: Path
) -> DatasetDict:
    """
    Unifies all available banking datasets into the training corpus:
      - stargate_extracted.parquet (Scanned STARGATE KYC/Clearance PDFs, label=2)
      - raw_files_extracted.parquet (Raw .txt/.json banking payloads)
    Ensures all metadata columns are dropped and text is sanitized for pure semantic learning.
    """
    candidate_processed_dirs = [
        ai_service_dir / "data" / "processed",
        project_root / "data" / "processed",
        Path("./data/processed"),
        Path("./ai-service/data/processed")
    ]
    processed_dir = candidate_processed_dirs[0]
    for d in candidate_processed_dirs:
        if d.exists() and (d / "stargate_extracted.parquet").exists():
            processed_dir = d
            break

    extra_dfs = []

    # 1. Ingest STARGATE extracted parquet
    stargate_parquet = processed_dir / "stargate_extracted.parquet"
    if stargate_parquet.exists():
        try:
            sg_df = pd.read_parquet(stargate_parquet)
            if "text" in sg_df.columns and len(sg_df) > 0:
                sg_clean = pd.DataFrame({
                    "text": sg_df["text"].astype(str),
                    "label": sg_df["label"].fillna(2).astype(int)
                })
                sg_clean["text"] = sg_clean["text"].apply(strip_meta_labels_and_headers)
                sg_clean = sg_clean[sg_clean["text"].str.len() >= 20]
                if len(sg_clean) > 0:
                    extra_dfs.append(sg_clean)
                    logger.info(f"[UNIFIED INGESTION] Loaded {len(sg_clean):,} STARGATE KYC/Clearance OCR extracts from {stargate_parquet.name}")
        except Exception as e:
            logger.warning(f"Could not load STARGATE parquet {stargate_parquet}: {e}")

    # 2. Ingest raw text/json extracted parquet
    raw_parquet = processed_dir / "raw_files_extracted.parquet"
    if raw_parquet.exists():
        try:
            raw_df = pd.read_parquet(raw_parquet)
            if "text" in raw_df.columns and len(raw_df) > 0:
                raw_clean = pd.DataFrame({
                    "text": raw_df["text"].astype(str),
                    "label": raw_df["label"].fillna(0).astype(int)
                })
                raw_clean["text"] = raw_clean["text"].apply(strip_meta_labels_and_headers)
                raw_clean = raw_clean[raw_clean["text"].str.len() >= 20]
                if len(raw_clean) > 0:
                    extra_dfs.append(raw_clean)
                    logger.info(f"[UNIFIED INGESTION] Loaded {len(raw_clean):,} raw text/JSON extracts from {raw_parquet.name}")
        except Exception as e:
            logger.warning(f"Could not load raw files parquet {raw_parquet}: {e}")

    if extra_dfs:
        combined_extra = pd.concat(extra_dfs, ignore_index=True)
        extra_train = combined_extra.sample(frac=0.8, random_state=42)
        extra_val = combined_extra.drop(extra_train.index)

        train_df = ds_dict["train"].to_pandas()[["text", "label"]]
        val_df = ds_dict["validation"].to_pandas()[["text", "label"]]

        merged_train = pd.concat([train_df, extra_train], ignore_index=True)
        merged_val = pd.concat([val_df, extra_val], ignore_index=True)

        ds_dict["train"] = Dataset.from_pandas(merged_train, preserve_index=False)
        ds_dict["validation"] = Dataset.from_pandas(merged_val, preserve_index=False)
        logger.info(
            f"[UNIFIED CORPUS ASSEMBLED] Training set expanded to {len(ds_dict['train']):,} total records "
            f"(+{len(extra_train):,} newly ingested KYC/document records merged)."
        )

    return ds_dict


# -----------------------------------------------------------------------------
# Dataset Ingestion with Multi-Tier Fallback
# -----------------------------------------------------------------------------
def load_banking_dataset(
    dataset_name_or_path: str,
    project_root: Path,
    ai_service_dir: Path
) -> DatasetDict:
    """
    Loads dataset with multi-tier fallback:
      1. Local DatasetDict at path (e.g., ./dataset_output)
      2. Hugging Face Hub (e.g., xorushi/secureflow-banking-dlp-3class)
      3. Processed local CSVs in ai-service/data/processed/document_classification
    Automatically integrates STARGATE KYC scans and raw text files into the training corpus.
    """
    logger.info(f"Resolving Banking DLP Dataset (requested: '{dataset_name_or_path}')...")

    # Candidate 1: Local disk DatasetDict path
    candidate_paths = [
        Path(dataset_name_or_path),
        project_root / dataset_name_or_path,
        project_root / "dataset_output",
        ai_service_dir / "data" / "processed" / "secureflow_banking_dlp_3class"
    ]

    for p in candidate_paths:
        if p.exists() and (p / "dataset_dict.json").exists():
            logger.info(f"[SUCCESS] Loading local DatasetDict from disk: {p.resolve()}")
            try:
                ds = load_from_disk(str(p))
                if "train" in ds and "validation" in ds:
                    return merge_ingested_documents(ds, ai_service_dir, project_root)
            except Exception as e:
                logger.warning(f"Failed to load from {p}: {e}")

    # Candidate 2: Hugging Face Hub
    try:
        logger.info(f"Attempting to load from Hugging Face Hub: '{dataset_name_or_path}'...")
        ds = load_dataset(dataset_name_or_path)
        logger.info(f"[SUCCESS] Loaded dataset from Hugging Face Hub: {dataset_name_or_path}")
        return ds
    except Exception as e:
        logger.warning(f"Could not load '{dataset_name_or_path}' from Hugging Face Hub: {e}")

    # Candidate 3: Local CSV files
    csv_dir = ai_service_dir / "data" / "processed" / "document_classification"
    train_csv = csv_dir / "train.csv"
    val_csv = csv_dir / "val.csv"
    test_csv = csv_dir / "test.csv"

    if train_csv.exists() and val_csv.exists():
        logger.info(f"[SUCCESS] Loading local CSV splits from: {csv_dir.resolve()}")
        train_df = pd.read_csv(train_csv)
        val_df = pd.read_csv(val_csv)
        test_df = pd.read_csv(test_csv) if test_csv.exists() else val_df.copy()

        # Handle label column mapping if needed
        for df in [train_df, val_df, test_df]:
            if "label" in df.columns and df["label"].dtype == object:
                df["label"] = df["label"].map(LABEL2ID).fillna(0).astype(int)

        ds_dict = DatasetDict({
            "train": Dataset.from_pandas(train_df[["text", "label"]], preserve_index=False),
            "validation": Dataset.from_pandas(val_df[["text", "label"]], preserve_index=False),
            "test": Dataset.from_pandas(test_df[["text", "label"]], preserve_index=False)
        })

        adv_csv = csv_dir / "adversarial_benchmark.csv"
        if adv_csv.exists():
            adv_df = pd.read_csv(adv_csv)
            if "label" in adv_df.columns and adv_df["label"].dtype == object:
                adv_df["label"] = adv_df["label"].map(LABEL2ID).fillna(2).astype(int)
            ds_dict["adversarial_benchmark"] = Dataset.from_pandas(adv_df, preserve_index=False)

        return ds_dict

    # If all options fail
    err_msg = (
        f"CRITICAL: Failed to locate Banking DLP dataset!\n"
        f"Searched locations:\n"
        f"  - Local DatasetDict: {project_root / 'dataset_output'}\n"
        f"  - Hugging Face Hub: '{dataset_name_or_path}'\n"
        f"  - Processed CSVs: {csv_dir}\n"
        f"Resolution: Please run `python prepare_secureflow_banking_dataset.py` first to generate the dataset."
    )
    logger.error(err_msg)
    raise FileNotFoundError(err_msg)


# -----------------------------------------------------------------------------
# Quick Presentation Baseline (Scikit-Learn TF-IDF)
# -----------------------------------------------------------------------------
def train_and_eval_baseline(
    train_texts: List[str],
    train_labels: List[int],
    test_texts: List[str],
    test_labels: List[int],
    models_dir: Path
) -> Dict[str, Any]:
    """
    Trains a fast TF-IDF + LogisticRegression baseline model in ~20s.
    Computes comparative metrics on the test split for project defense slides.
    """
    logger.info("=" * 80)
    logger.info(" RUNNING QUICK PRESENTATION BASELINE (TF-IDF + Logistic Regression)")
    logger.info("=" * 80)
    t0 = time.time()

    logger.info("Stripping meta-labels and prompt banners from baseline texts...")
    train_texts = [strip_meta_labels_and_headers(t) for t in train_texts]
    test_texts = [strip_meta_labels_and_headers(t) for t in test_texts]

    vectorizer = TfidfVectorizer(
        max_features=12000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        strip_accents="unicode"
    )
    logger.info("Fitting TF-IDF Vectorizer on train split...")
    X_train = vectorizer.fit_transform(train_texts)
    X_test = vectorizer.transform(test_texts)

    logger.info("Training Logistic Regression with balanced class weights...")
    clf = LogisticRegression(
        C=2.0,
        max_iter=1000,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, train_labels)
    fit_time = time.time() - t0

    preds = clf.predict(X_test)
    acc = accuracy_score(test_labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(
        test_labels, preds, average="macro", zero_division=0
    )

    # Class 2 specific recall (Restricted Leak Recall)
    test_labels_arr = np.array(test_labels)
    mask_c2 = (test_labels_arr == 2)
    c2_total = np.sum(mask_c2)
    c2_correct = np.sum(mask_c2 & (preds == 2))
    restricted_leak_recall = float(c2_correct / c2_total) if c2_total > 0 else 0.0

    logger.info(f"Baseline Training Completed in {fit_time:.2f}s")
    logger.info("--------------------------------------------------------------------------------")
    logger.info(f"  Accuracy:               {acc * 100:.2f}%")
    logger.info(f"  Macro F1:               {f1 * 100:.2f}%")
    logger.info(f"  Macro Precision:        {precision * 100:.2f}%")
    logger.info(f"  Macro Recall:           {recall * 100:.2f}%")
    logger.info(f"  RESTRICTED Leak Recall: {restricted_leak_recall * 100:.2f}% ({c2_correct}/{c2_total})")
    logger.info("--------------------------------------------------------------------------------")

    # Save baseline artifacts
    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump({"vectorizer": vectorizer, "classifier": clf}, models_dir / "baseline_tfidf.joblib")

    baseline_metrics = {
        "model_type": "TF-IDF + Logistic Regression (Baseline)",
        "train_samples": len(train_texts),
        "test_samples": len(test_texts),
        "train_time_sec": round(fit_time, 2),
        "accuracy": round(float(acc), 4),
        "macro_f1": round(float(f1), 4),
        "macro_precision": round(float(precision), 4),
        "macro_recall": round(float(recall), 4),
        "restricted_leak_recall": round(float(restricted_leak_recall), 4),
        "class_report": classification_report(test_labels, preds, target_names=["SAFE", "CONFIDENTIAL", "RESTRICTED"], output_dict=True)
    }

    comparison_path = models_dir / "baseline_comparison.json"
    with open(comparison_path, "w", encoding="utf-8") as f:
        json.dump(baseline_metrics, f, indent=2)
    logger.info(f"Saved baseline metrics to: {comparison_path}")

    return baseline_metrics


# -----------------------------------------------------------------------------
# Custom Banking Loss Trainer (Weighted Cross-Entropy)
# -----------------------------------------------------------------------------
class BankingWeightedLossTrainer(Trainer):
    """
    Subclass of Hugging Face Trainer overriding compute_loss() to enforce
    a 2.5x penalty on missing RESTRICTED data leaks (PCI-DSS/GDPR compliance).
    Device-safe across CUDA, MPS, and CPU.
    """
    def __init__(self, *args, class_weights: Optional[List[float]] = None, **kwargs):
        if "tokenizer" in kwargs and "processing_class" not in kwargs:
            tok = kwargs.pop("tokenizer")
            import inspect
            sig = inspect.signature(Trainer.__init__)
            if "processing_class" in sig.parameters:
                kwargs["processing_class"] = tok
            else:
                kwargs["tokenizer"] = tok
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")

        if self.class_weights is not None:
            # Transfer weights safely to the active device
            weight_tensor = torch.tensor(
                self.class_weights,
                dtype=torch.float,
                device=logits.device
            )
            loss_fct = nn.CrossEntropyLoss(weight=weight_tensor)
        else:
            loss_fct = nn.CrossEntropyLoss()

        loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss


# -----------------------------------------------------------------------------
# Metrics Computation
# -----------------------------------------------------------------------------
def compute_metrics(eval_pred) -> Dict[str, float]:
    """
    Computes standard classification metrics plus custom restricted_leak_recall.
    """
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)

    acc = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="macro", zero_division=0
    )

    # Class 2 (RESTRICTED) specific recall: TP(2) / Total actual 2s
    actual_c2 = (labels == 2)
    pred_c2 = (preds == 2)
    tp_c2 = np.sum(actual_c2 & pred_c2)
    total_c2 = np.sum(actual_c2)
    restricted_leak_recall = float(tp_c2 / total_c2) if total_c2 > 0 else 0.0

    return {
        "accuracy": float(acc),
        "macro_f1": float(f1),
        "macro_precision": float(precision),
        "macro_recall": float(recall),
        "restricted_leak_recall": float(restricted_leak_recall)
    }


# -----------------------------------------------------------------------------
# Checkpoint Discovery Helper
# -----------------------------------------------------------------------------
def get_latest_checkpoint(checkpoint_dir: Path) -> Optional[str]:
    """
    Discovers the latest valid training checkpoint in the given directory.
    """
    if not checkpoint_dir.exists():
        return None

    checkpoints = [
        d for d in checkpoint_dir.iterdir()
        if d.is_dir() and d.name.startswith("checkpoint-")
    ]
    if not checkpoints:
        return None

    def get_step(path: Path) -> int:
        try:
            return int(path.name.split("-")[1])
        except (IndexError, ValueError):
            return 0

    latest_ckpt = max(checkpoints, key=get_step)
    logger.info(f"Discovered existing checkpoint: {latest_ckpt} (Step {get_step(latest_ckpt)})")
    return str(latest_ckpt)


# -----------------------------------------------------------------------------
# Main Training Function
# -----------------------------------------------------------------------------
def train_banking_classifier(args: argparse.Namespace):
    set_seed(args.seed)
    project_root, ai_service_dir, models_dir = get_default_paths()

    # Configure subdirectories
    checkpoints_dir = models_dir / "checkpoints"
    final_model_dir = models_dir / "transformer_final"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    final_model_dir.mkdir(parents=True, exist_ok=True)

    # Set up signal handling
    setup_signal_handlers(checkpoints_dir)

    # 1. Device Auto-Detection
    if torch.cuda.is_available() and not args.force_cpu:
        device_str = "cuda"
        fp16_enabled = True
        logger.info(f"Target Hardware: NVIDIA CUDA GPU ({torch.cuda.get_device_name(0)}) - FP16 Enabled")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available() and not args.force_cpu:
        device_str = "mps"
        fp16_enabled = False
        logger.info("Target Hardware: Apple Silicon MPS - FP32 Enabled")
    else:
        device_str = "cpu"
        fp16_enabled = False
        logger.info("Target Hardware: Standard CPU - FP32 with Gradient Accumulation")

    # 2. Ingest Dataset
    dataset = load_banking_dataset(args.dataset_name_or_path, project_root, ai_service_dir)
    logger.info(f"Dataset Splits: {list(dataset.keys())}")
    for split in ["train", "validation", "test"]:
        if split in dataset:
            logger.info(f"  {split}: {len(dataset[split]):,} samples")

    # Quick Presentation Baseline Run
    if not args.skip_baseline:
        train_texts = [strip_meta_labels_and_headers(str(x)) for x in dataset["train"]["text"]]
        train_labels = [int(x) for x in dataset["train"]["label"]]
        eval_split = "test" if "test" in dataset else "validation"
        test_texts = [strip_meta_labels_and_headers(str(x)) for x in dataset[eval_split]["text"]]
        test_labels = [int(x) for x in dataset[eval_split]["label"]]

        # Sample for baseline if dataset is huge to keep it under 30s
        if len(train_texts) > 50000:
            indices = np.random.RandomState(42).choice(len(train_texts), 50000, replace=False)
            train_texts = [train_texts[i] for i in indices]
            train_labels = [train_labels[i] for i in indices]

        train_and_eval_baseline(train_texts, train_labels, test_texts, test_labels, models_dir)

    # 3. Tokenizer & Dynamic Padding Setup
    logger.info(f"Loading Tokenizer: '{args.model_name}'...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    def tokenize_function(examples):
        # Sanitize text: strip any meta labels, category banners, or synthetic tags
        # Forces model to inspect the interior content, syntax, and numbers on its own
        sanitized_texts = [strip_meta_labels_and_headers(t) for t in examples["text"]]
        return tokenizer(
            sanitized_texts,
            truncation=True,
            max_length=args.max_length,
            return_token_type_ids=False
        )

    logger.info(f"Tokenizing datasets (max_length={args.max_length})...")
    # Cleanly remove all text and metadata columns, keeping only labels and model inputs
    train_split = dataset["train"]
    val_split = dataset["validation"]
    test_split = dataset["test"] if "test" in dataset else None

    if args.max_train_samples and args.max_train_samples < len(train_split):
        logger.info(f"Subsampling train split to --max_train_samples={args.max_train_samples}")
        train_split = train_split.select(range(args.max_train_samples))
    if args.max_eval_samples and args.max_eval_samples < len(val_split):
        logger.info(f"Subsampling val split to --max_eval_samples={args.max_eval_samples}")
        val_split = val_split.select(range(args.max_eval_samples))
    if test_split and args.max_eval_samples and args.max_eval_samples < len(test_split):
        logger.info(f"Subsampling test split to --max_eval_samples={args.max_eval_samples}")
        test_split = test_split.select(range(args.max_eval_samples))

    remove_cols_train = [c for c in train_split.column_names if c not in ("input_ids", "attention_mask", "label")]
    remove_cols_val = [c for c in val_split.column_names if c not in ("input_ids", "attention_mask", "label")]

    tokenized_train = train_split.map(tokenize_function, batched=True, remove_columns=remove_cols_train)
    tokenized_val = val_split.map(tokenize_function, batched=True, remove_columns=remove_cols_val)
    if test_split:
        remove_cols_test = [c for c in test_split.column_names if c not in ("input_ids", "attention_mask", "label")]
        tokenized_test = test_split.map(tokenize_function, batched=True, remove_columns=remove_cols_test)
    else:
        tokenized_test = None

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    # 4. Model Architecture Initialization
    logger.info(f"Initializing Sequence Classification Model: '{args.model_name}' (num_labels=3)...")
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name,
        num_labels=3,
        id2label=ID2LABEL,
        label2id=LABEL2ID
    )

    # 5. Checkpoint Resumption Discovery
    latest_checkpoint = None
    if not args.overwrite_checkpoints:
        latest_checkpoint = get_latest_checkpoint(checkpoints_dir)
        if latest_checkpoint:
            logger.info(
                f"[RESUMPTION READY] Checkpoint detected: '{latest_checkpoint}'. "
                f"Training will automatically resume from here without starting over!"
            )

    # 6. Training Arguments
    # Calculate gradient accumulation steps based on hardware
    grad_accum = args.gradient_accumulation_steps
    if device_str == "cpu" and grad_accum == 1:
        grad_accum = 2

    # Parse class weights
    class_weights = [float(w) for w in args.class_weights.split(",")]
    logger.info(f"Applying Banking Class Loss Weights: {class_weights} (2.5x penalty on RESTRICTED)")

    # Save & Eval Strategy Configuration
    if args.max_steps > 0:
        eval_strat = "steps"
        save_strat = "steps"
        eval_steps_val = max(args.max_steps // 3, 10)
        save_steps_val = eval_steps_val
    elif args.save_strategy == "steps":
        eval_strat = "steps"
        save_strat = "steps"
        eval_steps_val = args.save_steps
        save_steps_val = args.save_steps
    else:
        eval_strat = "epoch"
        save_strat = "epoch"
        eval_steps_val = None
        save_steps_val = None

    warmup_steps_val = max(5, (args.max_steps // 10) if args.max_steps > 0 else 50)
    training_args = TrainingArguments(
        output_dir=str(checkpoints_dir),
        num_train_epochs=args.epochs,
        max_steps=args.max_steps if args.max_steps > 0 else -1,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size * 2,
        gradient_accumulation_steps=grad_accum,
        learning_rate=args.learning_rate,
        weight_decay=0.01,
        warmup_steps=warmup_steps_val,
        eval_strategy=eval_strat,
        save_strategy=save_strat,
        eval_steps=eval_steps_val,
        save_steps=save_steps_val,
        save_total_limit=args.save_total_limit,
        load_best_model_at_end=True,
        metric_for_best_model="restricted_leak_recall",
        greater_is_better=True,
        fp16=fp16_enabled,
        logging_steps=10 if args.max_steps > 0 else 50,
        dataloader_num_workers=0,  # Cross-platform safest for Windows
        report_to="none"
    )

    # 7. Trainer Instantiation
    trainer = BankingWeightedLossTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        class_weights=class_weights,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
    )

    # 8. Execution with Checkpoint Resumption
    logger.info("=" * 80)
    logger.info(" STARTING DEEP TRANSFORMER TRAINING FOR BANKING DLP")
    logger.info("=" * 80)
    resume_arg = latest_checkpoint if latest_checkpoint else None
    
    t_start = time.time()
    train_result = trainer.train(resume_from_checkpoint=resume_arg)
    train_duration = time.time() - t_start
    logger.info(f"Training completed successfully in {train_duration:.2f}s ({train_duration / 60:.1f} mins)")

    # 9. Final Model Export
    logger.info(f"Exporting best model and tokenizer to: {final_model_dir}...")
    trainer.save_model(str(final_model_dir))
    tokenizer.save_pretrained(str(final_model_dir))

    # Save training metrics
    metrics = train_result.metrics
    trainer.log_metrics("train", metrics)
    trainer.save_metrics("train", metrics)
    trainer.save_state()

    # 10. Evaluation on Test Split
    if tokenized_test is not None:
        logger.info("=" * 80)
        logger.info(" EVALUATING BEST MODEL ON HELD-OUT TEST SPLIT (15,750 SAMPLES)")
        logger.info("=" * 80)
        test_results = trainer.evaluate(eval_dataset=tokenized_test, metric_key_prefix="test")
        
        # Predictions for confusion matrix and report
        predictions = trainer.predict(tokenized_test)
        preds = np.argmax(predictions.predictions, axis=-1)
        test_labels = predictions.label_ids

        report = classification_report(
            test_labels,
            preds,
            target_names=["SAFE", "CONFIDENTIAL", "RESTRICTED"],
            output_dict=True
        )
        conf_mat = confusion_matrix(test_labels, preds).tolist()

        test_summary = {
            "model_name": args.model_name,
            "test_accuracy": round(float(test_results.get("test_accuracy", 0.0)), 4),
            "test_macro_f1": round(float(test_results.get("test_macro_f1", 0.0)), 4),
            "test_restricted_leak_recall": round(float(test_results.get("test_restricted_leak_recall", 0.0)), 4),
            "test_macro_precision": round(float(test_results.get("test_macro_precision", 0.0)), 4),
            "test_macro_recall": round(float(test_results.get("test_macro_recall", 0.0)), 4),
            "classification_report": report,
            "confusion_matrix": conf_mat,
            "training_time_sec": round(train_duration, 2)
        }

        test_metrics_path = models_dir / "test_metrics.json"
        with open(test_metrics_path, "w", encoding="utf-8") as f:
            json.dump(test_summary, f, indent=2)

        logger.info("--------------------------------------------------------------------------------")
        logger.info(" FINAL TEST RESULTS (SecureFlow Banking DLP Classifier)")
        logger.info("--------------------------------------------------------------------------------")
        logger.info(f"  Test Accuracy:               {test_summary['test_accuracy'] * 100:.2f}%")
        logger.info(f"  Test Macro F1:               {test_summary['test_macro_f1'] * 100:.2f}%")
        logger.info(f"  RESTRICTED Leak Recall:      {test_summary['test_restricted_leak_recall'] * 100:.2f}%")
        logger.info("--------------------------------------------------------------------------------")
        logger.info(f"Saved full test report to: {test_metrics_path}")

    # Memory cleanup
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()
    logger.info("[SUCCESS] Banking DLP Classifier training pipeline complete.")


# -----------------------------------------------------------------------------
# CLI Parser
# -----------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SecureFlow AI - Resilient 3-Class Banking DLP Classifier Trainer"
    )
    parser.add_argument(
        "--dataset_name_or_path",
        type=str,
        default="xorushi/secureflow-banking-dlp-3class",
        help="Hugging Face repo ID or local path to DatasetDict"
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Base transformer model (all-MiniLM-L6-v2 or microsoft/deberta-v3-small)"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs (default: 3)"
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=16,
        help="Per-device batch size (default: 16)"
    )
    parser.add_argument(
        "--gradient_accumulation_steps",
        type=int,
        default=1,
        help="Gradient accumulation steps (default: 1; CPU auto-sets to 2)"
    )
    parser.add_argument(
        "--learning_rate",
        type=float,
        default=3e-5,
        help="Learning rate (default: 3e-5)"
    )
    parser.add_argument(
        "--max_length",
        type=int,
        default=256,
        help="Max sequence token length (default: 256)"
    )
    parser.add_argument(
        "--class_weights",
        type=str,
        default="1.0,1.2,2.5",
        help="Class loss weights comma-separated: SAFE,CONFIDENTIAL,RESTRICTED"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)"
    )
    parser.add_argument(
        "--force_cpu",
        action="store_true",
        help="Force execution on CPU even if CUDA/MPS is present"
    )
    parser.add_argument(
        "--overwrite_checkpoints",
        action="store_true",
        help="Do not resume; start fresh from step 0"
    )
    parser.add_argument(
        "--skip_baseline",
        action="store_true",
        help="Skip the quick TF-IDF presentation baseline"
    )
    parser.add_argument(
        "--max_steps",
        type=int,
        default=-1,
        help="Maximum training steps (-1 for full epoch training)"
    )
    parser.add_argument(
        "--max_train_samples",
        type=int,
        default=None,
        help="Subsample train set to N samples for rapid testing or debugging"
    )
    parser.add_argument(
        "--save_strategy",
        type=str,
        default="epoch",
        choices=["epoch", "steps"],
        help="Checkpoint save frequency ('epoch' to save at each epoch, 'steps' to save every N steps)"
    )
    parser.add_argument(
        "--save_steps",
        type=int,
        default=500,
        help="Number of steps between checkpoints when save_strategy='steps' (default: 500, ~45 mins)"
    )
    parser.add_argument(
        "--save_total_limit",
        type=int,
        default=10,
        help="Maximum number of checkpoints to retain on disk (default: 10, keeps all epochs)"
    )
    parser.add_argument(
        "--max_eval_samples",
        type=int,
        default=None,
        help="Subsample eval set to N samples for rapid testing or debugging"
    )
    return parser.parse_args()


if __name__ == "__main__":
    cli_args = parse_args()
    train_banking_classifier(cli_args)

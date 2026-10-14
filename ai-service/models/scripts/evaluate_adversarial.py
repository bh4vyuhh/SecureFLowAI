#!/usr/bin/env python3
"""
SecureFlow AI - Adversarial Evasion Robustness Benchmark Harness
================================================================================
File: ai-service/scripts/evaluate_adversarial.py

Evaluates the Banking DLP model against 1,343 UM-DLP evasion test cases:
  1. Leetspeak & Character Substitution (e.g., cr3d1t c@rd, P@ssw0rd, 5sn)
  2. Delimiter Stuffing (e.g., 4 5 3 2 - 8 9 2 1 - 0 0 4 3, s s n : 1 2 3)
  3. Contextual Traps & Hard Negatives (benign invoice numbers, git hashes, false keyword traps)

Supports both PyTorch (.pt/safetensors) and Quantized ONNX (.onnx) runtime engines.
Outputs:
  - Overall Defense Accuracy % (Target >= 90%)
  - Evasion Rate % (100% - Defense Accuracy)
  - Per-category breakdown table
  - models/evasion_failures.csv for compliance audit
  - models/adversarial_eval_report.json
"""

import os
import sys
import re
import json
import time
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report

# -----------------------------------------------------------------------------
# Structured Logging
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SecureFlowAI.AdversarialEval")

# -----------------------------------------------------------------------------
# Constants & Taxonomy
# -----------------------------------------------------------------------------
ID2LABEL = {0: "SAFE", 1: "CONFIDENTIAL", 2: "RESTRICTED"}
LABEL2ID = {v: k for k, v in ID2LABEL.items()}

# Heuristic patterns for categorizing attack vectors
LEETSPEAK_REGEX = re.compile(
    r"(?:[c[<]r[3e][dld]1t|c[@a]rd|p[@a]ss|p4ss|s5n|5sn|[@01345\$]{2,}|[a-z]+[0-9@\$]+[a-z]+)",
    re.IGNORECASE
)
DELIMITER_STUFFING_REGEX = re.compile(
    r"(?:\d[\s\-_.\/]\d[\s\-_.\/]\d|\b[a-zA-Z]\s+[a-zA-Z]\s+[a-zA-Z]\b|\d{4}\s+\d{4}\s+\d{4})",
    re.IGNORECASE
)


# -----------------------------------------------------------------------------
# Attack Vector Categorization
# -----------------------------------------------------------------------------
def classify_attack_vector(row: pd.Series) -> str:
    """
    Categorizes the attack type based on text content and benchmark metadata.
    """
    text = str(row.get("text", row.get("Test data", "")))
    raw_type = str(row.get("adversarial_type", row.get("Type", ""))).strip().lower()

    # Rule 1: Explicit type from UM-DLP metadata
    if "typo" in raw_type or "substitution" in raw_type:
        return "Leetspeak / Character Substitution"
    elif "keyword" in raw_type or "random" in raw_type or "contextual" in raw_type:
        # Check if negative trap
        if "negative" in raw_type:
            return "Contextual Traps / Hard Negatives"

    # Rule 2: Pattern match on text
    if DELIMITER_STUFFING_REGEX.search(text):
        return "Delimiter Stuffing"
    elif LEETSPEAK_REGEX.search(text):
        return "Leetspeak / Character Substitution"
    elif "false keyword" in raw_type or "invoice" in text.lower() or "order" in text.lower():
        return "Contextual Traps / Hard Negatives"
    elif "positive direct" in raw_type:
        return "Direct Cleartext (Baseline)"
    else:
        return "Contextual Variation / Obfuscation"


# -----------------------------------------------------------------------------
# Benchmark Data Ingestion
# -----------------------------------------------------------------------------
def load_adversarial_benchmark(
    benchmark_csv: Optional[str] = None,
    project_root: Optional[Path] = None,
    ai_service_dir: Optional[Path] = None
) -> pd.DataFrame:
    """
    Ingests the 1,343 UM-DLP adversarial evaluation test cases.
    """
    candidates = []
    if benchmark_csv:
        candidates.append(Path(benchmark_csv))

    if project_root:
        candidates.extend([
            ai_service_dir / "data" / "processed" / "document_classification" / "adversarial_benchmark.csv",
            ai_service_dir / "data" / "processed" / "secureflow_banking_dlp_3class" / "adversarial_benchmark.csv",
            project_root / "dataset_output" / "adversarial_benchmark.csv"
        ])

    for c in candidates:
        if c.exists():
            logger.info(f"Loading adversarial benchmark from: {c.resolve()}")
            df = pd.read_csv(c)
            # Ensure required columns
            if "text" not in df.columns and "Test data" in df.columns:
                df["text"] = df["Test data"]
            if "label" not in df.columns and "Ground Truth (sensitive/non sensitive)" in df.columns:
                # Map sensitive -> 2, non sensitive -> 0
                df["label"] = df["Ground Truth (sensitive/non sensitive)"].apply(
                    lambda x: 0 if "non" in str(x).lower() else 2
                )
            logger.info(f"Loaded {len(df)} adversarial evaluation records.")
            return df

    # Fallback to loading DatasetDict from disk
    try:
        from datasets import load_from_disk
        ds_path = project_root / "dataset_output"
        if ds_path.exists():
            ds = load_from_disk(str(ds_path))
            if "adversarial_benchmark" in ds:
                df = ds["adversarial_benchmark"].to_pandas()
                logger.info(f"Loaded {len(df)} records from DatasetDict['adversarial_benchmark']")
                return df
    except Exception as e:
        logger.warning(f"Could not load DatasetDict from disk: {e}")

    raise FileNotFoundError(
        "Could not locate adversarial_benchmark.csv. "
        "Please specify --benchmark_csv or run prepare_secureflow_banking_dataset.py first."
    )


# -----------------------------------------------------------------------------
# Model Predictor Interfaces (PyTorch & ONNX)
# -----------------------------------------------------------------------------
class PyTorchPredictor:
    def __init__(self, model_dir: Path, max_length: int = 256):
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Loading PyTorch Model from '{model_dir}' onto {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
        self.model = AutoModelForSequenceClassification.from_pretrained(str(model_dir))
        self.model.to(self.device)
        self.model.eval()
        self.max_length = max_length

    def predict_batch(self, texts: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        import torch
        inputs = self.tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=self.max_length,
            return_tensors="pt"
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits.detach().cpu().numpy()
            probs = torch.softmax(outputs.logits, dim=-1).detach().cpu().numpy()
            preds = np.argmax(logits, axis=-1)
        return preds, probs


class ONNXPredictor:
    def __init__(self, onnx_model_path: Path, tokenizer_dir: Path, max_length: int = 256):
        import onnxruntime as ort
        from transformers import AutoTokenizer

        logger.info(f"Initializing ONNX Runtime Session for: {onnx_model_path}...")
        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = os.cpu_count() or 4
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        self.session = ort.InferenceSession(
            str(onnx_model_path),
            sess_options=sess_options,
            providers=["CPUExecutionProvider"]
        )
        logger.info(f"Loading Tokenizer from: {tokenizer_dir}...")
        self.tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_dir))
        self.max_length = max_length
        self.input_names = [i.name for i in self.session.get_inputs()]
        self.output_names = [o.name for o in self.session.get_outputs()]

    def predict_batch(self, texts: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        encoded = self.tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=self.max_length,
            return_tensors="np"
        )
        feed_dict = {
            "input_ids": encoded["input_ids"].astype(np.int64),
            "attention_mask": encoded["attention_mask"].astype(np.int64)
        }
        raw_outputs = self.session.run(self.output_names, feed_dict)
        logits = raw_outputs[0]
        # Softmax
        exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
        preds = np.argmax(probs, axis=-1)
        return preds, probs


# -----------------------------------------------------------------------------
# Main Adversarial Evaluation Harness
# -----------------------------------------------------------------------------
def run_adversarial_evaluation(args: argparse.Namespace):
    current_dir = Path(__file__).resolve().parent
    ai_service_dir = current_dir.parent
    project_root = ai_service_dir.parent
    models_dir = ai_service_dir / "models"

    # 1. Ingest Benchmark Data
    df = load_adversarial_benchmark(args.benchmark_csv, project_root, ai_service_dir)

    # 2. Enrich with Attack Vector Categorization
    df["attack_vector"] = df.apply(classify_attack_vector, axis=1)

    # 3. Model Resolution (PyTorch vs ONNX)
    onnx_file = None
    if args.onnx_path:
        onnx_file = Path(args.onnx_path)
    elif (models_dir / "onnx" / "model_int8.onnx").exists():
        onnx_file = models_dir / "onnx" / "model_int8.onnx"

    pytorch_dir = Path(args.model_path) if args.model_path else (models_dir / "transformer_final")

    if onnx_file and onnx_file.exists() and not args.force_pytorch:
        tok_dir = models_dir / "onnx" if (models_dir / "onnx" / "tokenizer_config.json").exists() else pytorch_dir
        logger.info(f"Target Predictor: ONNX INT8 Engine ({onnx_file})")
        predictor = ONNXPredictor(onnx_file, tok_dir, max_length=args.max_length)
        model_type_str = f"ONNX INT8 ({onnx_file.name})"
    elif pytorch_dir.exists():
        logger.info(f"Target Predictor: PyTorch Transformer Engine ({pytorch_dir})")
        predictor = PyTorchPredictor(pytorch_dir, max_length=args.max_length)
        model_type_str = f"PyTorch FP32 ({pytorch_dir.name})"
    else:
        raise FileNotFoundError(
            f"Neither PyTorch model at '{pytorch_dir}' nor ONNX model at '{onnx_file}' exists. "
            f"Please run `train_banking_classifier.py` and `export_onnx.py` first."
        )

    # 4. Evaluation Loop
    texts = df["text"].tolist()
    true_labels = df["label"].astype(int).tolist()

    logger.info(f"Running inference on {len(texts)} adversarial samples (batch_size={args.batch_size})...")
    all_preds = []
    all_probs = []
    t0 = time.time()

    for i in range(0, len(texts), args.batch_size):
        batch_texts = texts[i:i + args.batch_size]
        preds, probs = predictor.predict_batch(batch_texts)
        all_preds.extend(preds)
        all_probs.extend(probs)

    eval_duration = time.time() - t0
    df["predicted_label"] = all_preds
    df["predicted_label_name"] = [ID2LABEL[p] for p in all_preds]
    df["true_label_name"] = [ID2LABEL[t] for t in true_labels]
    df["correct"] = (df["predicted_label"] == df["label"])

    # 5. Core Metric Calculations
    overall_accuracy = accuracy_score(true_labels, all_preds)
    evasion_rate = 1.0 - overall_accuracy

    # Restricted leak recall
    mask_c2 = (df["label"] == 2)
    c2_total = mask_c2.sum()
    c2_detected = (mask_c2 & (df["predicted_label"] == 2)).sum()
    restricted_recall = float(c2_detected / c2_total) if c2_total > 0 else 0.0

    logger.info("=" * 80)
    logger.info(" ADVERSARIAL BENCHMARK EVALUATION SUMMARY (UM-DLP)")
    logger.info("=" * 80)
    logger.info(f"  Model Under Test:           {model_type_str}")
    logger.info(f"  Total Test Cases:           {len(df):,}")
    logger.info(f"  Overall Defense Accuracy:   {overall_accuracy * 100:.2f}% (Target: >= 90.0%)")
    logger.info(f"  Adversarial Evasion Rate:   {evasion_rate * 100:.2f}% (Target: <= 10.0%)")
    logger.info(f"  RESTRICTED Leak Recall:     {restricted_recall * 100:.2f}% ({c2_detected}/{c2_total})")
    logger.info(f"  Evaluation Time:            {eval_duration:.2f}s ({len(df) / eval_duration:.1f} samples/sec)")
    logger.info("-" * 80)

    # 6. Per-Attack-Vector Breakdown
    logger.info(f"{'Attack Category':<35} | {'Samples':<8} | {'Defended':<8} | {'Evaded':<8} | {'Defense Acc %':<14} | {'Evasion %':<10}")
    logger.info("-" * 95)
    category_metrics = {}

    for cat, group in df.groupby("attack_vector"):
        total = len(group)
        correct = group["correct"].sum()
        evaded = total - correct
        acc = (correct / total) * 100
        eva = (evaded / total) * 100

        category_metrics[cat] = {
            "samples": int(total),
            "defended": int(correct),
            "evaded": int(evaded),
            "defense_accuracy_pct": round(acc, 2),
            "evasion_rate_pct": round(eva, 2)
        }
        logger.info(f"{cat:<35} | {total:<8} | {correct:<8} | {evaded:<8} | {acc:>12.2f}% | {eva:>8.2f}%")

    # 7. Standard UM-DLP Category Breakdown (PCI DSS, PII-Financial, etc.)
    if "category" in df.columns or "Category" in df.columns:
        cat_col = "category" if "category" in df.columns else "Category"
        logger.info("-" * 95)
        logger.info(f"{'UM-DLP Banking Category':<35} | {'Samples':<8} | {'Defended':<8} | {'Evaded':<8} | {'Defense Acc %':<14} | {'Evasion %':<10}")
        logger.info("-" * 95)
        for cat, group in df.groupby(cat_col):
            cat_str = str(cat).strip()[:35]
            total = len(group)
            correct = group["correct"].sum()
            evaded = total - correct
            acc = (correct / total) * 100
            eva = (evaded / total) * 100
            logger.info(f"{cat_str:<35} | {total:<8} | {correct:<8} | {evaded:<8} | {acc:>12.2f}% | {eva:>8.2f}%")

    logger.info("=" * 80)

    # 8. Save Evasion Failures (False Negatives) for Compliance Audit
    failures_df = df[~df["correct"]].copy()
    failures_path = models_dir / "evasion_failures.csv"
    save_cols = [
        "text", "label", "predicted_label", "true_label_name",
        "predicted_label_name", "attack_vector"
    ]
    if "Category" in df.columns:
        save_cols.append("Category")
    if "adversarial_type" in df.columns:
        save_cols.append("adversarial_type")

    failures_df[[c for c in save_cols if c in failures_df.columns]].to_csv(failures_path, index=False)
    logger.info(f"Saved {len(failures_df)} evasion failure edge-cases to: {failures_path}")

    # 9. Save Full Adversarial Audit Report JSON
    report = {
        "model_type": model_type_str,
        "total_test_cases": len(df),
        "overall_defense_accuracy": round(float(overall_accuracy), 4),
        "overall_evasion_rate": round(float(evasion_rate), 4),
        "restricted_leak_recall": round(float(restricted_recall), 4),
        "sla_target_met": bool(overall_accuracy >= 0.90),
        "category_breakdown": category_metrics,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }
    report_path = models_dir / "adversarial_eval_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    logger.info(f"Saved complete audit report to: {report_path}")

    if overall_accuracy >= 0.90:
        logger.info("[VERIFICATION PASSED] Model satisfies the >= 90% Defense Accuracy requirement against adversarial evasion!")
    else:
        logger.warning("[VERIFICATION WARNING] Defense Accuracy is below 90% target. Review evasion_failures.csv.")


# -----------------------------------------------------------------------------
# CLI Parser
# -----------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SecureFlow AI - UM-DLP 1,343-Case Adversarial Robustness Benchmark"
    )
    parser.add_argument(
        "--benchmark_csv",
        type=str,
        default=None,
        help="Path to adversarial_benchmark.csv"
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default=None,
        help="Path to fine-tuned PyTorch model directory (default: models/transformer_final)"
    )
    parser.add_argument(
        "--onnx_path",
        type=str,
        default=None,
        help="Path to quantized ONNX model (default: models/onnx/model_int8.onnx)"
    )
    parser.add_argument(
        "--force_pytorch",
        action="store_true",
        help="Force evaluation on PyTorch model even if ONNX exists"
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=32,
        help="Batch size for evaluation inference"
    )
    parser.add_argument(
        "--max_length",
        type=int,
        default=256,
        help="Max sequence length"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_adversarial_evaluation(args)

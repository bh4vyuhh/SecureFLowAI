#!/usr/bin/env python3
"""
SecureFlow AI - Production ONNX Inference Engine & Live Classifier
================================================================================
File: ai-service/models/scripts/predict_sample.py

Demonstrates real-time, low-latency (< 5ms) 3-class DLP classification:
  - 0: SAFE
  - 1: CONFIDENTIAL
  - 2: RESTRICTED
"""

import sys
import time
from pathlib import Path
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer

ID2LABEL = {0: "SAFE", 1: "CONFIDENTIAL", 2: "RESTRICTED"}

def load_predictor():
    current_dir = Path(__file__).resolve().parent
    models_dir = current_dir.parent
    onnx_path = models_dir / "onnx" / "model_int8.onnx"
    tok_path = models_dir / "onnx"

    if not onnx_path.exists():
        raise FileNotFoundError(f"Model not found at: {onnx_path}")

    tokenizer = AutoTokenizer.from_pretrained(str(tok_path))
    opts = ort.SessionOptions()
    opts.intra_op_num_threads = 4
    opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    session = ort.InferenceSession(str(onnx_path), opts, providers=["CPUExecutionProvider"])
    
    return tokenizer, session

def classify_text(text: str, tokenizer, session):
    t0 = time.perf_counter()
    encoded = tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=256,
        return_tensors="np"
    )
    feed_dict = {
        "input_ids": encoded["input_ids"].astype(np.int64),
        "attention_mask": encoded["attention_mask"].astype(np.int64)
    }
    logits = session.run(None, feed_dict)[0]
    exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    probs = (exp_logits / np.sum(exp_logits, axis=-1, keepdims=True))[0]
    pred_idx = int(np.argmax(probs))
    duration_ms = (time.perf_counter() - t0) * 1000.0

    return ID2LABEL[pred_idx], float(probs[pred_idx]), probs.tolist(), duration_ms

def main():
    print("=" * 80)
    print(" SecureFlowAI - Real-Time Banking DLP Classifier (INT8 ONNX)")
    print("=" * 80)
    
    tokenizer, session = load_predictor()
    print("[READY] Loaded INT8 ONNX Model & Tokenizer into memory.\n")

    test_samples = [
        {
            "category": "WORKPLACE COMMUNICATION",
            "expected": "SAFE",
            "text": "Hi Team, please find attached the agenda and slide deck for tomorrow's all-hands meeting at 10 AM in Conference Room B."
        },
        {
            "category": "PUBLIC FINANCIAL NEWS",
            "expected": "SAFE",
            "text": "The European Central Bank maintained its benchmark deposit rate today, stating that inflation has aligned with official targets."
        },
        {
            "category": "INTERNAL STRATEGY MEMO",
            "expected": "CONFIDENTIAL",
            "text": "Project Falcon M&A update: EBITDA margin is projected at 24.2% with $42.5M in net income for Q4. Discussion restricted to executive committee."
        },
        {
            "category": "INTERNAL AUDIT FINDINGS",
            "expected": "CONFIDENTIAL",
            "text": "Internal Audit Report: Review of commercial loan underwriting identified control deficiencies in secondary collateral verification protocols."
        },
        {
            "category": "CUSTOMER KYC & SSN LEAK",
            "expected": "RESTRICTED",
            "text": "Customer Enhanced Due Diligence (EDD): Bryan Watson, SSN: 010-716-3079, Account Number: 4092-8819-2041, Date of Birth: 12/08/1982."
        },
        {
            "category": "CREDIT CARD & PASSPORT EXFILTRATION",
            "expected": "RESTRICTED",
            "text": "Wire Transfer Authorization Form: Cardholder: Jane Smith, Visa Card: 4532-8921-0043-9182, Expiry: 08/29, CVV: 841, Passport ID: 628446115."
        }
    ]

    for i, sample in enumerate(test_samples, 1):
        label, conf, all_probs, latency = classify_text(sample["text"], tokenizer, session)
        
        status = "[MATCH]" if label == sample["expected"] else "[MISMATCH]"
        
        print(f"Sample {i}: [{sample['category']}]")
        print(f"  Input:    \"{sample['text']}\"")
        print(f"  Expected: {sample['expected']}")
        print(f"  Result:   {label} (Confidence: {conf*100:.1f}%) | Latency: {latency:.2f}ms  {status}")
        print(f"  Probs:    SAFE: {all_probs[0]*100:.1f}% | CONFIDENTIAL: {all_probs[1]*100:.1f}% | RESTRICTED: {all_probs[2]*100:.1f}%\n")

    print("=" * 80)
    print(" Live Inference Test Completed Successfully.")
    print("=" * 80)

if __name__ == "__main__":
    main()

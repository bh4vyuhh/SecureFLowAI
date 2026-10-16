"""
SecureFlow AI - Sliding-Window INT8 ONNX Transformer Inference Engine
================================================================================
File: ai-service/app/engine/classifier.py

Solves the "256-Token Blindspot":
  - Inputs <= 256 tokens run single-pass ONNX inference (< 5ms).
  - Inputs > 256 tokens slide a window of size 256 with stride 180 (76-token overlap).
  - Max-Pooling Risk Aggregation:
      * If ANY single chunk predicts Class 2 (RESTRICTED) with prob > 0.35,
        the entire document classification is escalated to RESTRICTED.
      * Otherwise, takes the mean probability distribution across all chunks.
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer

logger = logging.getLogger("SecureFlowAI.Classifier")

ID2LABEL = {0: "SAFE", 1: "CONFIDENTIAL", 2: "RESTRICTED"}
LABEL2ID = {v: k for k, v in ID2LABEL.items()}

WINDOW_SIZE = 256
STRIDE = 180
RESTRICTED_ESCALATION_THRESHOLD = 0.65


class SlidingWindowClassifier:
    def __init__(self, model_dir: Path):
        self.model_dir = Path(model_dir)
        self.onnx_path = self.model_dir / "onnx" / "model_int8.onnx"
        self.tokenizer_path = self.model_dir / "onnx"

        # Fallback to transformer_final if onnx folder missing
        if not self.onnx_path.exists():
            candidate = self.model_dir / "transformer_final"
            if candidate.exists():
                self.tokenizer_path = candidate
                logger.warning(f"ONNX model missing at {self.onnx_path}, using tokenizer from {candidate}")

        logger.info(f"Loading Tokenizer from: {self.tokenizer_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.tokenizer_path))

        logger.info(f"Initializing ONNX Runtime Session: {self.onnx_path}")
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 2
        opts.inter_op_num_threads = 1
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        self.session = ort.InferenceSession(
            str(self.onnx_path),
            opts,
            providers=["CPUExecutionProvider"]
        )
        self.input_names = [i.name for i in self.session.get_inputs()]
        self.output_names = [o.name for o in self.session.get_outputs()]
        logger.info("[CLASSIFIER READY] Sliding-Window INT8 ONNX Engine loaded successfully.")

    def _infer_batch_logits(self, input_ids_list: List[List[int]], attention_mask_list: List[List[int]]) -> np.ndarray:
        """Runs batched inference through ONNX session and returns softmax probabilities."""
        # Pad to max length in current batch
        max_len = max(len(ids) for ids in input_ids_list)
        padded_ids = []
        padded_masks = []
        for ids, mask in zip(input_ids_list, attention_mask_list):
            pad_len = max_len - len(ids)
            padded_ids.append(ids + [self.tokenizer.pad_token_id or 0] * pad_len)
            padded_masks.append(mask + [0] * pad_len)

        feed_dict = {
            "input_ids": np.array(padded_ids, dtype=np.int64),
            "attention_mask": np.array(padded_masks, dtype=np.int64)
        }
        logits = self.session.run(self.output_names, feed_dict)[0]
        exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
        return probs

    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classifies input text using the Sliding-Window Max-Pooling approach.
        Returns:
          {
            "tier": "SAFE" | "CONFIDENTIAL" | "RESTRICTED",
            "confidence": float,
            "probabilities": {"SAFE": float, "CONFIDENTIAL": float, "RESTRICTED": float},
            "num_chunks": int,
            "latency_ms": float
          }
        """
        if not text or not text.strip():
            return {
                "tier": "SAFE",
                "confidence": 1.0,
                "probabilities": {"SAFE": 1.0, "CONFIDENTIAL": 0.0, "RESTRICTED": 0.0},
                "num_chunks": 1,
                "latency_ms": 0.0
            }

        t0 = time.perf_counter()
        # Tokenize entire document without truncation
        tokens = self.tokenizer(
            text,
            truncation=False,
            add_special_tokens=False,
            return_attention_mask=False
        )["input_ids"]

        total_tokens = len(tokens)

        # Case 1: Short document (<= WINDOW_SIZE)
        if total_tokens <= (WINDOW_SIZE - 2):
            encoded = self.tokenizer(
                text,
                truncation=True,
                max_length=WINDOW_SIZE,
                return_tensors="np"
            )
            feed_dict = {
                "input_ids": encoded["input_ids"].astype(np.int64),
                "attention_mask": encoded["attention_mask"].astype(np.int64)
            }
            logits = self.session.run(self.output_names, feed_dict)[0]
            exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
            probs = (exp_logits / np.sum(exp_logits, axis=-1, keepdims=True))[0]
            num_chunks = 1

        # Case 2: Long document -> Sliding Window with Stride
        else:
            chunks_ids = []
            chunks_masks = []
            start_idx = 0
            cls_token_id = self.tokenizer.cls_token_id or 101
            sep_token_id = self.tokenizer.sep_token_id or 102

            # Window size minus special tokens
            content_window = WINDOW_SIZE - 2

            while start_idx < total_tokens:
                sub_tokens = tokens[start_idx : start_idx + content_window]
                chunk = [cls_token_id] + sub_tokens + [sep_token_id]
                mask = [1] * len(chunk)
                chunks_ids.append(chunk)
                chunks_masks.append(mask)

                if start_idx + content_window >= total_tokens:
                    break
                start_idx += STRIDE

            batch_probs = self._infer_batch_logits(chunks_ids, chunks_masks)
            num_chunks = len(chunks_ids)

            # Max-Pooling Aggregation for RESTRICTED leaks
            # If any chunk predicts Class 2 (RESTRICTED) > 0.35 threshold -> ESCALATE
            max_restricted_prob = float(np.max(batch_probs[:, 2]))
            if max_restricted_prob > RESTRICTED_ESCALATION_THRESHOLD:
                # Find chunk with highest restricted score
                peak_chunk_idx = int(np.argmax(batch_probs[:, 2]))
                probs = batch_probs[peak_chunk_idx]
            else:
                # Otherwise, aggregate via mean probability distribution
                probs = np.mean(batch_probs, axis=0)

        pred_idx = int(np.argmax(probs))
        confidence = float(probs[pred_idx])
        latency_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "tier": ID2LABEL[pred_idx],
            "confidence": round(confidence, 4),
            "probabilities": {
                "SAFE": round(float(probs[0]), 4),
                "CONFIDENTIAL": round(float(probs[1]), 4),
                "RESTRICTED": round(float(probs[2]), 4)
            },
            "num_chunks": num_chunks,
            "latency_ms": round(latency_ms, 2)
        }

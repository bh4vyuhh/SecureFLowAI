# SecureFlowAI: Banking DLP Model Training & Multi-Day Execution Guide

This guide provides accurate hardware timing calculations, the directory layout, and step-by-step instructions for training the **3-Class Banking DLP Classifier** on CPU across multiple days or sessions.

---

## 1. Directory Structure

```text
ai-service/
├── data/
│   ├── raw/                             # Raw source datasets (Enron, AI4Privacy, FinGPT, STARGATE PDFs)
│   ├── processed/                       # Local CSV splits and Parquet exports
│   ├── docs/                            # Dataset documentation, specifications, and slide notes
│   │   ├── DATASET_SPECIFICATION_AND_IMPLEMENTATIONS.md
│   │   ├── PRE_TRAINING_GUIDE.md
│   │   ├── PRESENTATION_SLIDES_AND_SNIPPETS.md
│   │   └── SecureFlowAI_Dataset_Specification_and_Implementation_Guide.docx
│   └── scripts/                         # All dataset ingestion & preparation scripts
│       ├── prepare_secureflow_banking_dataset.py
│       ├── ingest_stargate_and_raw_files.py
│       ├── download_datasets.py
│       ├── generate_synthetic_data.py
│       ├── organize_and_build_datasets.py
│       └── upload_datasets.py
│
└── models/
    ├── scripts/                         # All model training, export & benchmarking scripts
    │   ├── train_banking_classifier.py
    │   ├── export_onnx.py
    │   └── evaluate_adversarial.py
    ├── checkpoints/                     # Step & epoch checkpoints (auto-resumed)
    ├── transformer_final/               # Best PyTorch model + Tokenizer
    ├── onnx/                            # Quantized model_int8.onnx (<30MB, <25ms P95)
    ├── baseline_comparison.json         # Presentation baseline performance proof
    ├── test_metrics.json                # Test split metrics
    ├── adversarial_eval_report.json     # Adversarial evaluation summary
    └── evasion_failures.csv             # Full evasion failure audit log
```

---

## 2. Anti-Cheating & Intrinsic Learning Engine

To ensure the model learns true semantic syntax, numerical patterns, and banking context instead of memorizing superficial "cheat tags", the training pipeline enforces a **7-Stage Sanitization Engine** before tokenization:

1. **Class Banner Stripping**: Removes start-of-document banners like `[RESTRICTED]:`, `CONFIDENTIAL -`, `*** SAFE ***`, `TOP SECRET:`.
2. **Subject Header Cleaning**: Cleans subject lines (e.g. `Subject: [CONFIDENTIAL] M&A Strategy` $\rightarrow$ `Subject: M&A Strategy`).
3. **Artificial Metadata Removal**: Strips lines starting with `Classification:`, `Label:`, `Category:`, `Source:`, `Doc Type:`, `Sensitivity:`, `Status:`.
4. **Synthetic Entity Tag Removal**: Strips markup like `[PII]`, `[/PII]`, `<SSN>`, `</SSN>`, `[CREDIT_CARD]`, `<IBAN>`.
5. **Prompt Artifact Stripping**: Strips generator prompt headers like `Here is a synthetic restricted document:`, `Generated sample of banking PII:`.
6. **Boilerplate Legal Disclaimers**: Removes standard footer disclaimers (`CONFIDENTIALITY NOTICE: This transmission is intended only...`).
7. **Metadata Column Dropping**: Drops all non-tensor metadata columns (`source`, `category`, `adversarial_type`, `ground_truth_raw`, `id`, `extraction_method`) so only pure document text is tokenized.

### How the Model "Looks Inside" & Learns on Its Own:
- **`0: SAFE`**: Discerning daily meeting arrangements, public financial press releases, generic logistics, and benign business correspondence.
- **`1: CONFIDENTIAL`**: Reading corporate memos, EBITDA/P&L calculations, risk committee audit reports, regulatory filings, and acquisition discussions.
- **`2: RESTRICTED`**: Parsing structural patterns of 9-digit SSNs (`XXX-XX-XXXX`), 16-digit credit card sequences, IBAN codes, routing transit numbers, and KYC passport scans.

---

## 3. Accurate Timing & Mathematical Calculations (CPU Reality Check)

### A. STARGATE OCR Ingestion (7,394 Scanned PDFs)
- **Nature of Files**: STARGATE PDFs are raw 1970s scanned CIA declassified photocopies (pure image scans without embedded text layer).
- **Time per PDF**: ~15 to 40 seconds (converting 3–5 pages to images + contrast thresholding + EasyOCR).
- **Total for 7,394 PDFs on 4 CPU cores**: $\sim 7,394 \times 30\text{s} / 4 \approx 55,455\text{ seconds} \approx \mathbf{15.4\text{ hours}}$.
- **Strategy**: The script [`ingest_stargate_and_raw_files.py`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/scripts/ingest_stargate_and_raw_files.py) uses `stargate_progress.json` as a persistent cache. You do **not** need to wait for 7,394 PDFs before training because the 105,000-sample core banking dataset (`dataset_output`) is already compiled, balanced, and ready for training!

### B. Transformer Model Training (`sentence-transformers/all-MiniLM-L6-v2`)
- **Train split size**: 73,500 banking text samples (+ newly ingested STARGATE/raw records).
- **Batch size**: 16 per device, `gradient_accumulation_steps=2` (effective batch size: 32).
- **Steps per epoch**: $73,510 / 32 = \mathbf{2,297\text{ optimization steps}}$ per epoch.
- **Observed CPU speed**: ~5.4 seconds per step on this host.
- **Calculated time per epoch**:
  $$2,297 \text{ steps} \times 5.4 \text{ s/step} = 12,403 \text{ seconds} \approx \mathbf{3.44 \text{ hours per epoch}}$$
- **3 full epochs**: $\approx \mathbf{10.3 \text{ hours}}$.
- **1-hour session throughput**: ~660 optimization steps (~21,120 samples processed).

---

## 4. Recommended Multi-Day Training Workflow

Because 1 epoch takes ~3.5 hours on CPU, you can split training comfortably across days. The script automatically checkpoints every epoch (and every 500 steps), and automatically resumes from the latest checkpoint when re-launched.

### Day 1: Train Epoch 1 (~3.5 hours, or 1 hour = ~660 steps)
Run Epoch 1:
```powershell
.venv\Scripts\python ai-service/models/scripts/train_banking_classifier.py --dataset_name_or_path ./dataset_output --epochs 1 --batch_size 16 --save_strategy epoch --save_total_limit 10
```
- When finished, it saves the model and tokenizer to `models/transformer_final/` and saves checkpoint to `models/checkpoints/checkpoint-2297/`.
- If you stop earlier (e.g. after 1 hour), add `--save_strategy steps --save_steps 500`.

### Day 2: Train Epoch 2 (Automatic Resumption)
Simply run with `--epochs 2`:
```powershell
.venv\Scripts\python ai-service/models/scripts/train_banking_classifier.py --dataset_name_or_path ./dataset_output --epochs 2 --batch_size 16 --save_strategy epoch --save_total_limit 10
```
- The script automatically detects `checkpoint-2297`, passes `resume_from_checkpoint=True`, and begins immediately at step 2,298 without re-training Epoch 1!

### Day 3: Train Epoch 3 (Final Convergence)
Run with `--epochs 3`:
```powershell
.venv\Scripts\python ai-service/models/scripts/train_banking_classifier.py --dataset_name_or_path ./dataset_output --epochs 3 --batch_size 16 --save_strategy epoch --save_total_limit 10
```

---

## 5. Post-Training Export & Benchmark Commands

Once training finishes, run the downstream export and robustness benchmarks:

### Step 1: Export to ONNX INT8 (< 30MB) & Run Latency SLA Check (< 25ms)
```powershell
.venv\Scripts\python ai-service/models/scripts/export_onnx.py
```
Outputs:
- `models/onnx/model_int8.onnx` (~22 MB)
- `models/onnx/latency_benchmark.json` (P95 latency audit)

### Step 2: Adversarial Robustness Benchmark (1,343 UM-DLP cases)
```powershell
.venv\Scripts\python ai-service/models/scripts/evaluate_adversarial.py
```
Outputs:
- `models/adversarial_eval_report.json`
- `models/evasion_failures.csv`

---

## 6. Dataset Training Phase B (STARGATE OCR Ingestion)

When you are ready to expand the model's training data with the full scanned STARGATE dataset:

### Step 1: Run OCR Ingestion
Extracts text from scanned KYC, identity cards, and declassified banking scans, exporting to `ai-service/data/processed/stargate_extracted.parquet`:
```powershell
# Extract a batch of 200 STARGATE PDFs:
.venv\Scripts\python ai-service/data/scripts/ingest_stargate_and_raw_files.py --sample_limit 200 --workers 6

# Or run full extraction across all 7,394 PDFs (progress cached in stargate_progress.json):
.venv\Scripts\python ai-service/data/scripts/ingest_stargate_and_raw_files.py --workers 6
```

### Step 2: Retrain with Unified STARGATE Data
The training script will automatically detect `stargate_extracted.parquet`, merge the new RESTRICTED documents into the training split, sanitize the text, and fine-tune the classifier:
```powershell
.venv\Scripts\python ai-service/models/scripts/train_banking_classifier.py --dataset_name_or_path ./dataset_output --epochs 1 --save_strategy epoch
```

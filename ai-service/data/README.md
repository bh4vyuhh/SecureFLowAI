# SecureFlow AI — Comprehensive Dataset Architecture & Catalog

This document provides complete, publication-grade specifications for every dataset in the **SecureFlow AI** Data Leakage Prevention (DLP) ecosystem. It covers dataset origins, exact schemas, security classifications, compliance mappings, preprocessing transformations, and evaluation benchmark roles.

---

## ⚡ Quickstart Dataset Reproduction

To reproduce all datasets, benchmarks, and baseline models in a single command:

```bash
cd ai-service/data/scripts

# 1. Master one-click end-to-end reproduction (download -> process -> showcase -> train)
python reproduce_all.py --all

# Or run individual stages:
# Download / verify raw datasets only
python download_raw_datasets.py --dataset all

# Build all processed splits and benchmarks
python organize_datasets.py --target all

# Run specific single-dataset targets:
python organize_datasets.py --target document_classification
python organize_datasets.py --target pii_ner
python organize_datasets.py --target um_dlp
python organize_datasets.py --target contextual
python organize_datasets.py --target enron
python organize_datasets.py --target ocr_corpus

# View structured validation showcase table
python present_datasets.py

# Train baseline 4-tier document classifier
python train_classifier.py
```

---

## 🏛️ System Data Hierarchy

```
ai-service/data/
├── raw/                                      # Cleaned, immutable raw data archives
│   ├── disc/                                 # DISC.json (35.5 MB)
│   ├── medical_phi/                          # HIPAA PHI Parquet file (1.2 MB)
│   ├── roberta_pii_synth/                    # 120k Arrow PII dataset
│   ├── um_dlp_benchmark/                     # 1,343 Arrow DLP records
│   ├── contextual_sensitive/                 # 1,000 Arrow context records
│   ├── stargate_pdfs/                        # 7,394 Scanned PDF documents
│   └── enron_emails/                         # enron_emails_raw.csv (1.7 MB)
│
├── processed/                                # CORE MODEL TRAINING PARTITIONS
│   ├── document_classification/              # 4-Tier Sensitivity Classifier
│   │   ├── train.csv                         # 5,330 rows (70% Stratified Training Set)
│   │   ├── validation.csv                    # 1,142 rows (15% Stratified Validation Set)
│   │   └── test.csv                          # 1,143 rows (15% Stratified Test Set)
│   │
│   └── pii_ner_training/                     # Transformer NER Token Classification
│       ├── train.jsonl                       # 96,000 PII training spans
│       ├── validation.jsonl                  # 12,000 PII validation spans
│       └── test.jsonl                        # 12,000 PII test spans
│
├── benchmarks/                               # INDEPENDENT EVALUATION SUITES
│   ├── dlp_robustness/
│   │   └── um_dlp_test.csv                   # 1,343 DLP adversarial & noise records
│   ├── contextual_sensitivity/
│   │   └── contextual_test.csv               # 1,000 Context ambiguity records
│   ├── corporate_generalization/
│   │   └── enron_test.csv                    # 2,000 Real corporate emails from AESLC
│   ├── pii_extraction/
│   │   └── pii_benchmark_12k.jsonl           # 12,000 Character-level PII test spans
│   └── ocr_pipeline/
│       └── pdf_test_corpus/                  # 7,394 STARGATE PDFs for OCR testing
│
└── scripts/                                  # Centralized data processing scripts
    ├── organize_datasets.py                  # Automated reorganizer, cleaner & splitter
    └── train_classifier.py                   # Baseline 4-tier model training script
```

---

## 📋 Comprehensive Dataset Specifications

---

### 1. DISC (Declassified Intelligence Security Corpus)
- **Local Path**: [`ai-service/data/raw/disc/DISC.json`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/raw/disc/DISC.json)
- **Primary Processed Target**: [`ai-service/data/processed/document_classification/`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/processed/document_classification)
- **Modality & Format**: Single JSON file (~35.5 MB)
- **Volume**: 2,459 documents
- **Origin / Provenance**: Digital National Security Archive (DNSA) declassified intelligence cables and diplomatic memos (Department of State, CIA, DIA, JCS).
- **Compliance & Threat Model**: Defense security clearance mapping, government classified information leakage, defense-grade access control (DoD 5200.01 / ISO 27001).

#### Schema Definition
| Field | Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `DocID` | `integer` | Unique record index | `1` |
| `Title` | `string` | Intelligence report subject title | `"Mujahedin Cross Border Cow Raid into Soviet Union..."` |
| `Text` | `string` | Cleaned full body text | `"Net VOW IDE 1% vue Of oo il cause..."` |
| `OCRtext` | `string` | Raw OCR extraction containing noise | `"Net VOW IDE 1% vue Of oo il cause ~ wes..."` |
| `Abstract` | `string` | Human-curated document summary | `"Soviet Union Armed Forces retaliate..."` |
| `Classification` | `list[dict]` | Security tags and release dates | `[{"ClassID": "1_1", "Label": "Top Secret", "Date": "June 14, 1987"}, {"ClassID": "1_2", "Label": "Unclassified"}]` |
| `Database` | `string` | Source repository | `"Digital National Security Archive"` |
| `Domain` | `string` | Topic domain | `"Afghanistan: The Making of U.S. Policy, 1973-1990"` |
| `Author` | `string` | Reporting agency | `"United States Consulate. Peshawar"` |
| `StoreId` | `integer` | Storage index | `1679059219` |

#### SecureFlow AI Mapping & Processing
- **Clearance Mapping**:
  - `Top Secret`, `SCI`, `Restricted` $\longrightarrow$ **`Highly Confidential`**
  - `Secret`, `Confidential` $\longrightarrow$ **`Confidential`**
  - `Official Use Only`, `FOUO` $\longrightarrow$ **`Internal`**
  - `Unclassified` $\longrightarrow$ **`Public`**
- **Watermark Stripping**: Regex removes leading security headers (e.g. `TOP SECRET`, `SECRET PESHAWAR 1084`) to prevent model shortcut learning.

---

### 2. Medical PHI (Protected Health Information)
- **Local Path**: [`ai-service/data/raw/medical_phi/train-00000-of-00001.parquet`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/raw/medical_phi/train-00000-of-00001.parquet)
- **Primary Processed Target**: [`ai-service/data/processed/document_classification/`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/processed/document_classification)
- **Modality & Format**: Apache Parquet (~1.2 MB)
- **Volume**: 2,000 clinical question-answer pairs
- **Origin / Provenance**: Healthcare and patient inquiry medical dataset (HCM corpus).
- **Compliance & Threat Model**: HIPAA Privacy Rule (45 CFR § 164.514), patient clinical records leakage, medical history exposure.

#### Schema Definition
| Field | Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `prompt` | `string` | Patient question detailing symptoms & history | `"last year my wife was went through a surgery for appendix cancer..."` |
| `completion` | `string` | Physician response with clinical diagnosis & advice | `"Hi and welcome to HCM. First, you dont have to worry. This cant be tumour..."` |

#### SecureFlow AI Mapping & Processing
- **Classification Assignment**: Mapped to **`Confidential`** (Healthcare/PHI domain).
- **Feature Extraction**: Combined `prompt + " " + completion` into unified narrative text for the 4-tier document classifier.

---

### 3. RoBERTa-PII-Synth (Synthetic PII Token NER)
- **Local Path**: [`ai-service/data/raw/roberta_pii_synth/`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/raw/roberta_pii_synth)
- **Processed & Benchmark Targets**:
  - Training Spans: [`ai-service/data/processed/pii_ner_training/`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/processed/pii_ner_training) (96k train / 12k val / 12k test JSONL)
  - Benchmark Suite: [`ai-service/data/benchmarks/pii_extraction/pii_benchmark_12k.jsonl`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/benchmarks/pii_extraction/pii_benchmark_12k.jsonl) (12,000 records)
- **Modality & Format**: HuggingFace Arrow (`DatasetDict`) (~135 MB)
- **Volume**: 120,000 total annotated sequences (96k train, 12k validation, 12k test)
- **Origin / Provenance**: `tursunait/RoBERTa-pii-synth` (Hugging Face)
- **Compliance & Threat Model**: GDPR Article 4(1), CCPA/CPRA, PCI-DSS, NIST SP 800-122 (Guide to Protecting PII Confidentiality).

#### Schema Definition
| Field | Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `text` | `string` | Raw noisy sentence containing synthetic PII | `"DON'T SHACE buX uZrE's 1970rodney.lewis'S coMatctD sarahperez@aol.com /g2118x174 / ssn 0651734596"` |
| `spans` | `list[struct]` | Character start/end boundaries and entity tags | `[{"start": 23, "end": 39, "label": "PERSON"}, {"start": 51, "end": 69, "label": "EMAIL"}, {"start": 72, "end": 80, "label": "PHONE"}, {"start": 87, "end": 97, "label": "SSN"}]` |
| `tokens` | `list[string]` | Tokenized word representations | `["DON'T", "SHACE", "buX", ...]` |
| `labels` | `list[int64]` | BIO token classification tags | `[0, 0, 0, 1, 2, ...]` |
| `input_ids` | `list[int32]` | Pre-encoded RoBERTa subword IDs | `[0, 15309, 6, ...]` |
| `attention_mask`| `list[int8]` | Self-attention mask | `[1, 1, 1, ...]` |

#### Supported Entity Types
`PERSON`, `EMAIL`, `PHONE`, `SSN`, `ADDRESS`, `CREDIT_CARD`, `PASSPORT_NUMBER`, `DATE_OF_BIRTH`, `IP_ADDRESS`, `USERNAME`, `PASSWORD`.

---

### 4. UM-DLP Public Benchmarking Dataset
- **Local Path**: [`ai-service/data/raw/um_dlp_benchmark/`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/raw/um_dlp_benchmark)
- **Benchmark Target**: [`ai-service/data/benchmarks/dlp_robustness/um_dlp_test.csv`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/benchmarks/dlp_robustness/um_dlp_test.csv)
- **Modality & Format**: CSV benchmark file (~468 KB)
- **Volume**: 1,343 test records
- **Origin / Provenance**: `alibustami/UM-DLP-Public-Benchmarking-Dataset` (University of Malaya)
- **Compliance & Threat Model**: DLP evasion detection, adversarial character substitutions, obfuscation robustness, false-positive suppression.

#### Schema Definition
| Field | Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `ID` | `int64` | Test case identifier | `1` |
| `Category` | `string` | Data domain tested | `"Personal Identifiable Information (PII-Financial related)"` |
| `Type` | `string` | Attack or payload category | `"Positive Direct"`, `"Positive Obfuscated"`, `"Negative Keyword"` |
| `Test data` | `string` | Exact text prompt sent to DLP engine | `"Please help me verify if my credit card number 6011-2398-5674-9012 has been comp..."` |
| `Ground Truth (sensitive/non sensitive)` | `string` | True binary sensitivity label | `"sensitive"` or `"non sensitive"` |
| `UM MAISON Detection` | `string` | Reference system prediction | `"sensitive"` |
| `Your detection (sensitive/non sensitive)` | `float/null` | Evaluation placeholder | `null` |

---

### 5. Contextual Sensitive Data
- **Local Path**: [`ai-service/data/raw/contextual_sensitive/`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/raw/contextual_sensitive)
- **Benchmark Target**: [`ai-service/data/benchmarks/contextual_sensitivity/contextual_test.csv`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/benchmarks/contextual_sensitivity/contextual_test.csv)
- **Modality & Format**: CSV benchmark file (~922 KB)
- **Volume**: 1,000 instruction-tuning & evaluation records
- **Origin / Provenance**: `trl-lab/contextual-sensitive-data` (Hugging Face)
- **Compliance & Threat Model**: Context-aware sensitivity classification, database schema discovery, distinguishing dummy/documentation values from active credentials.

#### Schema Definition
| Field | Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `column_name` | `string` | Database or table attribute name | `"condition"` |
| `records` | `string` | Sample values extracted from column | `"['0', 'active', 'active', '1', '1']"` |
| `instruction` | `string` | System instruction prompt | `"You are a PII classification system. Given a column name and records, determine..."` |
| `input` | `string` | Formatted prompt input | `"Column name: condition\nRecords: ['0', 'active', 'active', '1', '1']"` |
| `output` | `string` | Ground-truth sensitivity classification & reasoning | `"Non-Sensitive (Categorical system state)"` |

---

### 6. Enron Corporate Email Corpus (AESLC)
- **Local Path**: [`ai-service/data/raw/enron_emails/enron_emails_raw.csv`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/raw/enron_emails/enron_emails_raw.csv)
- **Benchmark Target**: [`ai-service/data/benchmarks/corporate_generalization/enron_test.csv`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/benchmarks/corporate_generalization/enron_test.csv)
- **Modality & Format**: CSV file (~1.7 MB)
- **Volume**: 2,000 corporate emails
- **Origin / Provenance**: Annotated Enron Subject Line Corpus (`aeslc` / Enron Email Archive).
- **Compliance & Threat Model**: Business communication DLP, corporate internal domain shifts, commercial trade secrets.

#### Schema Definition
| Field | Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `subject` | `string` | Email subject header | `"Service Agreement"` |
| `body` | `string` | Full corporate email body | `"Greg/Phillip, Attached is the Grande Communications Service Agreement. The business points can be f..."` |
| `label` | `string` | Sensitivity classification | `"Internal"` |
| `source` | `string` | Data provenance | `"Enron_Corporate"` |

---

### 7. STARGATE CIA Scanned PDF Archive
- **Local Path**: [`ai-service/data/raw/stargate_pdfs/`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/raw/stargate_pdfs)
- **Benchmark Target**: [`ai-service/data/benchmarks/ocr_pipeline/pdf_test_corpus/`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/benchmarks/ocr_pipeline/pdf_test_corpus)
- **Modality & Format**: Scanned PDF files (~300+ MB)
- **Volume**: 7,394 scanned PDF documents
- **Origin / Provenance**: `GotThatData/STARGATE` / CIA CREST declassified PDF archive (Grill Flame, Center Lane, Sun Streak, Star Gate).
- **Compliance & Threat Model**: OCR text extraction, scanned image leak detection, noisy document binarization, declassified archive redaction verification.

#### Characteristics
- **Format**: Scanned multipage PDFs (300 DPI, greyscale/bilevel, 1970s–1990s typewriter font).
- **Visual Artifacts**: Redaction black-bars, official stamps (`TOP SECRET`, `DECLASSIFIED`), handwritten marginalia, degraded typewriter text.

---

## 🔬 Model Training & Split Summary

The primary 4-tier document classifier in [`ai-service/data/scripts/train_classifier.py`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/scripts/train_classifier.py) was trained on the processed splits:

### Class Partition Breakdown
```
Total Records: 7,615
├── 70% Train:      5,330 rows (Confidential: 3725, Internal: 840, Public: 664, Highly Confidential: 101)
├── 15% Validation: 1,142 rows (Confidential: 798,  Internal: 180, Public: 142, Highly Confidential: 22)
└── 15% Test:       1,143 rows (Confidential: 799,  Internal: 180, Public: 142, Highly Confidential: 22)
```

### Baseline Model Evaluation Metrics
```
                     precision    recall  f1-score   support

       Confidential       0.99      0.91      0.95       799
Highly Confidential       0.47      0.82      0.60        22
           Internal       0.99      0.99      0.99       180
             Public       0.71      0.96      0.82       142

           accuracy                           0.93      1143
          macro avg       0.79      0.92      0.84      1143
       weighted avg       0.95      0.93      0.93      1143
```
- **Trained Model Artifact**: [`ai-service/models/document_classifier_baseline.joblib`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/models/document_classifier_baseline.joblib)

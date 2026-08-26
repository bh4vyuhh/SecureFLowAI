# SecureFlow AI — Dataset Specification & Implementation Blueprint

A Microsoft Word version of this document has been compiled and saved to:
- [`SecureFlowAI_Dataset_Specification_and_Implementation_Guide.docx`](file:///c:/Users/RUSHIKESH/SecureFLowAI/SecureFlowAI_Dataset_Specification_and_Implementation_Guide.docx)
- [`ai-service/data/SecureFlowAI_Dataset_Specification_and_Implementation_Guide.docx`](file:///c:/Users/RUSHIKESH/SecureFLowAI/ai-service/data/SecureFlowAI_Dataset_Specification_and_Implementation_Guide.docx)

---

## 1. Executive Summary & 3-Stage Pipeline Architecture
SecureFlow AI is an enterprise Data Leakage Prevention (DLP) platform engineered to detect, classify, and sanitize sensitive data across text, structured records, emails, clinical consultations, and scanned document attachments.

The data layer is partitioned into three immutable stages under `ai-service/data/`:
1. **`raw/`**: Immutable, cleaned raw archives preserving the original source datasets.
2. **`processed/`**: Core training, validation, and testing partitions structured for supervised learning (70% Train, 15% Val, 15% Test).
3. **`benchmarks/`**: Independent evaluation suites targeting DLP evasion robustness, PII extraction precision, contextual sensitivity reasoning, corporate domain shifts, and OCR attachment binarization.

---

## 2. Master Dataset Inventory & Role Matrix

| Dataset Name | Domain / Task | Raw Format | Records | Target Split | Primary Model Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DISC** | Security Clearance Classification | JSON (35.5 MB) | 2,459 docs | 70/15/15 Split | 4-Tier Document Classifier |
| **Medical PHI** | Healthcare & HIPAA PHI | Parquet (1.2 MB) | 2,000 pairs | Merged into 70/15/15 | Confidential Healthcare Tier |
| **RoBERTa PII** | Token-level PII NER & Redaction | Arrow (135 MB) | 120,000 seqs | 80k Train / 20k Val / 20k Test | Transformer NER Fine-Tuning |
| **UM-DLP** | DLP Adversarial Robustness | Arrow / CSV (468 KB) | 1,343 rows | 100% Benchmark | Robustness & Evasion Suite |
| **Contextual Data** | Context Sensitivity & Schema | Arrow / CSV (922 KB) | 1,000 rows | 100% Benchmark | LLM Instruction Tuning |
| **Enron Emails** | Corporate Generalization | CSV (1.7 MB) | 2,000 emails | 100% Benchmark + Internal | Domain Shift Generalization |
| **STARGATE** | Scanned Document OCR | PDFs (300+ MB) | 7,394 PDFs | 100% Benchmark | OCR Pipeline & Attachment DLP |

---

## 3. Dataset Deep Dives & Further Implementations

### 3.1 DISC — Declassified Intelligence Security Corpus
- **Origin & Provenance**: Digital National Security Archive (DNSA). Declassified diplomatic cables and intelligence reports from Department of State, CIA, DIA, and JCS.
- **Compliance Standard**: DoD 5200.01 (DoD Information Security Program), ISO/IEC 27001 Annex A.8.
- **Volume & Format**: 2,459 documents in JSON format (35.5 MB).
- **4-Tier Security Mapping**:
  - `Top Secret`/`SCI` $\to$ **`Highly Confidential`**
  - `Secret`/`Confidential` $\to$ **`Confidential`**
  - `Official Use Only`/`FOUO` $\to$ **`Internal`**
  - `Unclassified` $\to$ **`Public`**

#### Pre-Training & Sanitization Workflow:
1. **Watermark & Header Stripping**: Regex removes leading clearance markings (e.g. `TOP SECRET`, `SECRET PESHAWAR`) to prevent model from memorizing header tokens instead of narrative semantics.
2. **Telegram Denoising**: Strips telegram transmission headers (`ZNY SSSSS`, `RITSZYUW`, `EZ1:`) and corrupted OCR artifact sequences.
3. **Sliding Window Chunking**: Documents exceeding 512 subwords are chunked into 512-token segments with 64-token stride to preserve context across boundaries.
4. **Class Imbalance Handling**: Focal Loss ($\gamma=2.0$) or class weighting is applied to compensate for the smaller sample size of Highly Confidential documents (145 records).

#### Further Implementation Blueprint:
- **Model Architecture**: Fine-tuned `microsoft/deberta-v3-base` with a 4-class classification head.
- **Real-Time Egress Middleware**: Deployed as a high-throughput FastAPI inference microservice inspecting outbound corporate webhooks and email gateways.
- **Latency SLA**: Sub-25ms response time on 512-token chunks via ONNX Runtime with INT8 quantization.

---

### 3.2 Medical PHI — Protected Health Information Corpus
- **Origin & Provenance**: Healthcare consultation and physician response dialogue corpus (HCM).
- **Compliance Standard**: HIPAA Privacy Rule (45 CFR § 164.514), HITECH Act, GDPR Special Category Data (Article 9).
- **Volume & Format**: 2,000 paired clinical records stored in Apache Parquet format (1.2 MB).
- **Classification Assignment**: Injected into the `Confidential` sensitivity tier for the primary classifier.

#### Pre-Training & Sanitization Workflow:
1. **Dialogue Synthesis**: Concatenate `prompt` (patient complaint/symptoms) and `completion` (doctor's clinical findings, diagnosis, prescription) into a unified clinical narrative.
2. **Vocabulary Alignment**: Ensure subword tokenizers preserve medical nomenclature (e.g. `metastasis`, `biopsy`, `mg/dL`) without excessive splitting.
3. **Minimum Length Filtering**: Filter out empty or single-word conversational filler to guarantee dense clinical context.

#### Further Implementation Blueprint:
- **Multi-Modal PHI Scanner**: Combine rule-based medical entity dictionaries (ICD-10, RxNorm) with ClinicalBERT classification.
- **Automatic Patient De-Identification**: Integrate with SecureFlow AI's masking engine to automatically redact patient identifiers prior to cloud LLM forwarding.

---

### 3.3 RoBERTa-PII-Synth — Synthetic Token-Level PII & NER
- **Origin & Provenance**: `tursunait/RoBERTa-pii-synth` (Hugging Face).
- **Compliance Standard**: GDPR Article 4(1), CCPA/CPRA, PCI-DSS (Requirement 3), NIST SP 800-122.
- **Volume & Format**: 120,000 total annotated sequences in Arrow format (96k Train, 12k Validation, 12k Test).
- **Entity Coverage**: `PERSON`, `EMAIL`, `PHONE`, `SSN`, `ADDRESS`, `CREDIT_CARD`, `PASSPORT_NUMBER`, `IP_ADDRESS`, `USERNAME`, `PASSWORD`.

#### Pre-Training & Sanitization Workflow:
1. **FastTokenizer Offset Alignment**: Use Hugging Face `FastTokenizer` with `return_offsets_mapping=True` to align character-level start/end indices with BPE subword tokens.
2. **BIO Subword Labeling**: Assign `B-TAG` to the leading subword and `I-TAG` (or `-100` ignore index) to continuation subwords.
3. **Boundary Validation**: Enforce `0 <= span['start'] < span['end'] <= len(text)` across all 120,000 samples.

#### Further Implementation Blueprint:
- **Hybrid Extraction Engine**: Deploy a dual-stage pipeline combining compiled Regex patterns for high-precision deterministic entities (`SSN`, `Email`, `IP`) with RoBERTa-NER for context-dependent entities (`Names`, `Addresses`, `Job Titles`).
- **Reversible Cryptographic Tokenization**: Redact sensitive tokens with HMAC-SHA256 tokens allowing authorized downstream re-identification under strict role-based access control (RBAC).

---

### 3.4 UM-DLP — Adversarial Robustness & Evasion Benchmark
- **Origin & Provenance**: `alibustami/UM-DLP-Public-Benchmarking-Dataset` (University of Malaya).
- **Volume & Format**: 1,343 benchmark evaluation test cases in CSV format (468 KB).
- **Benchmark Evaluation Slices**: Positive Direct, Positive Obfuscated (leetspeak, whitespace injection), Negative Keyword (benign text containing sensitive terms).

#### Pre-Evaluation & Sanitization Workflow:
1. **Case & Noise Preservation**: Do NOT apply lowercasing, punctuation stripping, or spelling correction; adversarial testing requires verbatim inputs.
2. **Binary Target Mapping**: Map ground-truth strings (`'sensitive'` $\to 1$, `'non sensitive'` $\to 0$).

#### Further Implementation Blueprint:
- **CI/CD Quality Gate**: Automated evaluation harness executing on every git release. Threshold requirement: $\ge 95\%$ Recall on Positive Obfuscated and $\le 3\%$ False Positive Rate on Negative Keywords.

---

### 3.5 Contextual Sensitive Data — Table & Instruction Sensitivity
- **Origin & Provenance**: `trl-lab/contextual-sensitive-data` (Hugging Face).
- **Volume & Format**: 1,000 instruction-tuning and evaluation records in CSV format (922 KB).
- **Threat Model**: Distinguishing live database credentials from dummy test numbers; automated database column classification.

#### Pre-Training & Formatting Workflow:
1. **ChatML Template Construction**: Convert rows into formatted prompts with system instructions, column names, and row value samples.
2. **Loss Masking**: Set `labels = -100` on system prompt and user input tokens during LLM fine-tuning.

#### Further Implementation Blueprint:
- **Enterprise Data Catalog Scanner**: An asynchronous crawler connecting to PostgreSQL, Snowflake, and BigQuery to automatically categorize table schemas according to privacy sensitivity tiers.

---

### 3.6 Enron Corporate Email Corpus — Business Domain Shift
- **Origin & Provenance**: Annotated Enron Subject Line Corpus (AESLC).
- **Volume & Format**: 2,000 corporate emails in CSV format (1.7 MB).
- **Classification Assignment**: Populates the `Internal` sensitivity tier in document classification.

#### Pre-Training & Cleaning Workflow:
1. **Disclaimer & Signature Stripping**: Strip automated corporate legal footers and forwarding email chains.
2. **Subject Integration**: Synthesize subject line into email body context (`'Subject: {subject}\n\n{body}'`).

#### Further Implementation Blueprint:
- **Exchange / Outlook DLP Plugin**: Integrate model into Microsoft Graph API / Google Workspace email gateways to inspect outbound attachments and sensitive financial discussion.

---

### 3.7 STARGATE — CIA Scanned PDF OCR Archive
- **Origin & Provenance**: CIA CREST Remote Viewing Archive (`GotThatData/STARGATE`).
- **Volume & Format**: 7,394 declassified scanned PDF documents (~300+ MB).
- **Threat Model**: Optical character recognition on low-quality scanned image attachments; detecting black-bar redaction leakage.

#### Pre-OCR Image Pipeline Workflow:
1. **300 DPI Rasterization**: Convert PDF pages to high-resolution uncompressed grayscale images.
2. **Adaptive OpenCV Preprocessing**: Apply Hough transform deskewing, Otsu adaptive binarization, and morphological opening to remove scan speckling.
3. **OCR Post-Correction**: Fix common typewriter character confusions (`'1'` vs `'l'`, `'0'` vs `'O'`) using regex grammar.

#### Further Implementation Blueprint:
- **Asynchronous Attachment Scanner**: Celery/Redis background worker extracting text from uploaded PDFs/PNGs before forwarding extracted text to the 4-Tier Document Classifier and PII NER engines.

---

## 4. Production Deployment Architecture & API Roadmap

### Core Microservice API Endpoints
- `POST /api/v1/dlp/classify`: Accepts arbitrary text payloads and returns sensitivity tier (`Highly Confidential`, `Confidential`, `Internal`, `Public`) along with softmax confidence scores.
- `POST /api/v1/dlp/redact-pii`: Extracts entity spans and returns sanitized text with selectable redaction modes (Masking, Hashing, Synthetic Replacement).
- `POST /api/v1/dlp/scan-attachment`: Multi-part file upload processing PDFs and images through the OCR binarization pipeline and returning sensitivity clearance reports.

### Latency Budgets & Target Performance
- **Text Classification Latency**: $< 25\text{ ms}$ on 512-token payloads via ONNX Runtime.
- **NER Extraction Latency**: $< 40\text{ ms}$ for full-page text with token-level span resolution.
- **OCR Attachment Ingestion**: $< 180\text{ ms}$ per page with OpenCV adaptive binarization.

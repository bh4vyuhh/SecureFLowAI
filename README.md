# 🛡️ SecureFlow AI: Enterprise-Grade Banking Data Leakage Prevention (DLP)

[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.13-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg)]()
[![ONNX Runtime](https://img.shields.io/badge/ONNX%20Runtime-INT8%20Quantized-orange.svg)]()
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.5.4-brightgreen.svg)]()
[![React](https://img.shields.io/badge/React-19.0-61dafb.svg)]()
[![Compliance](https://img.shields.io/badge/Compliance-PCI--DSS%20%7C%20GDPR%20%7C%20GLBA-purple.svg)]()

**SecureFlow AI** is an enterprise-grade, high-throughput, bank-compliant Data Leakage Prevention (DLP) platform. It provides real-time semantic document classification, deterministic mathematical checksum verification, optical character recognition (OCR) for scanned documents, and automated client-side prevention across browser forms, desktop clipboards, and outbound email channels.

---

## 🏛️ System Architecture

```
                                  [DATA SOURCES]
  Browser Extension        Desktop Clipboard & Files       Email Inbound/Outbound
  (Chrome / Edge MV3)      (Ctrl+C, Downloads Folder)      (SMTP/IMAP, .eml files)
           │                           │                              │
           └───────────────────────────┼──────────────────────────────┘
                                       │
                                       ▼
                       POST /api/v1/events/ingest
                       POST /api/v1/dlp/scan
                                       │
           ┌───────────────────────────┴───────────────────────────┐
           │                     ai-service/                       │
           │                                                       │
           │  [LAYER 1: MULTI-FORMAT EXTRACTION & OCR]             │
           │  • Digital PDF / DOCX / XLSX / CSV / TXT Streaming    │
           │  • Scanned PDF / Image (.png, .jpg) -> In-Memory OCR  │
           │  • DoS Protection: Cap 5 pages, 10k words, size limits│
           │                                                       │
           │  [LAYER 2: ADVERSARIAL NORMALIZATION & ANTI-EVASION]  │
           │  • Zero-width unicode & hidden character stripping    │
           │  • Homoglyph & Confusable normalization               │
           │  • Whitespace & symbol digit-delinking restoration    │
           │  • Automatic Base64 payload detection & inline decode │
           │                                                       │
           │  [LAYER 3: HYBRID DETECTION ENGINE]                   │
           │  • Sliding-Window INT8 ONNX Transformer (256/180)     │
           │  • Deterministic Checksums: Luhn, MOD-97, Fed ABA, SSN│
           │  • Contextual Token NER: Customer, Partner Banks, Loc │
           │                                                       │
           │  [LAYER 4: RESOLVER & MULTI-MODE SANITIZER]           │
           │  • Greedy Interval Conflict Resolver (Zero drift)     │
           │  • Mode A: Partial Masking [CARD_****9182]            │
           │  • Mode B: Reversible HMAC-SHA256 Tokenization        │
           │                                                       │
           │  [LAYER 5: UNIFIED RISK MATRIX & ZERO-LEAK AUDITING]  │
           │  • Score 0-100 -> Decision: ALLOW / ENCRYPT / BLOCK   │
           │  • SHA-256 Payload Hash Logging (Zero customer PII)   │
           └───────────────────────────┬───────────────────────────┘
                                       │
                                       ▼
                       [REAL-TIME CLIENT ENFORCEMENT]
        • BLOCK: DOM Event Aborted / Clipboard Wiped / Toast Alert
        • ENCRYPT: Transparent Tokenization Substitution
        • ALLOW: Clean Business Traffic Proceed
```

---

## 📂 Repository Directory Layout

The repository is structured as a clean, modular multi-service monorepo:

```text
SecureFlowAI/
├── ai-service/                  # Core AI Intelligence & DLP Microservice
│   ├── app/
│   │   ├── engine/              # Detection, OCR, Normalization, & Redaction Engines
│   │   │   ├── classifier.py    # Sliding-Window INT8 ONNX Transformer
│   │   │   ├── extractor.py     # Multi-Format Parser & In-Memory EasyOCR
│   │   │   ├── ner.py           # Contextual Token NER (PERSON, ORG, LOC)
│   │   │   ├── normalizer.py    # Anti-Evasion (Zero-width, Homoglyphs, Base64)
│   │   │   ├── redactor.py      # Reverse-Offset Masking & HMAC Tokenization
│   │   │   ├── resolver.py      # Greedy Interval Span Conflict Merger
│   │   │   └── rules.py         # Deterministic Checksums (Luhn, MOD-97, ABA, SSN)
│   │   ├── main.py              # FastAPI Application, Lifespan Cache, & Audit Logger
│   │   └── schemas.py           # Strict Pydantic v2 Request & Response Contracts
│   ├── data/                    # Dataset Pipeline, Raw Sources, & Specs
│   ├── models/                  # Checkpoints, Final PyTorch & Quantized INT8 ONNX
│   ├── tests/                   # 32 Automated Unit & Integration Tests (100% Green)
│   ├── Dockerfile               # Production Multi-Stage Container Spec
│   └── requirements.txt         # Production Runtime Dependencies
│
├── backend/                     # Java 21 / Spring Boot 3.5 Enterprise Gateway & SOC API
├── frontend/                    # React 19 / Vite Dark-Mode Admin & DLP Dashboard
├── desktop-agent/               # System Tray Daemon (Clipboard Monitor & File Watcher)
├── browser-extension/           # Chrome / Edge Manifest V3 In-Page Interception Agent
├── email-connector/             # Outbound / Inbound SMTP & IMAP Mailbox DLP Inspector
│   └── samples/                 # Sample Demo .eml Files
├── docker/                      # Supplementary Docker Configurations
├── scripts/                     # Standardized Operator Batch & Bash Utility Scripts
│   ├── run_ai_service.bat       # Launch FastAPI ONNX Server on Port 8000
│   ├── run_training.bat         # Launch Multi-Epoch Transformer Model Trainer
│   └── run_tests.bat            # Execute Pytest Across Entire 32-Test Suite
├── docker-compose.yml           # Unified Multi-Service Docker Orchestration Spec
├── pytest.ini                   # Python Test Runner Configuration
└── LICENSE                      # Apache License 2.0
```

---

## ⚡ Quick Start Guide

### Option 1: Full Stack via Docker Compose (Recommended)

Boot PostgreSQL and the containerized AI Service with a single command:

```bash
docker compose up --build
```
* **AI DLP Microservice**: `http://localhost:8000`
* **Interactive API Documentation**: `http://localhost:8000/docs`
* **Health Check**: `http://localhost:8000/health`

---

### Option 2: Local Development Execution

#### 1. Start the AI Microservice
```powershell
# Using utility script:
.\scripts\run_ai_service.bat

# Or manually via venv:
.\.venv\Scripts\uvicorn.exe app.main:app --app-dir ai-service --host 0.0.0.0 --port 8000 --reload
```

#### 2. Run the Automated Test Suite (32 Tests)
```powershell
# Using utility script:
.\scripts\run_tests.bat

# Or manually:
.\.venv\Scripts\pytest.exe -v
```

#### 3. Run the Desktop Clipboard & File Watcher
```powershell
.\.venv\Scripts\python.exe desktop-agent/main.py
```

#### 4. Load the Browser Extension (Chrome / Edge)
1. Navigate to `chrome://extensions` (or `edge://extensions`).
2. Toggle on **Developer mode** in the top right.
3. Click **Load unpacked** and select the [`browser-extension/`](file:///c:/Users/RUSHIKESH/SecureFLowAI/browser-extension/) directory.
4. Try pasting sensitive credentials or financial cards into web forms or ChatGPT to observe instant on-page blocking.

---

## 🧠 Core Engine Capabilities

| Engine Layer | Technology | Primary Function |
| :--- | :--- | :--- |
| **Semantic Classifier** | INT8 Quantized Transformer | 3-Class Document Intent (`SAFE`, `CONFIDENTIAL`, `RESTRICTED`) using sliding window (size 256, stride 180). |
| **Deterministic Rules** | Pure Python Math Algorithms | **Luhn (MOD-10)** for Cards, **ISO 7064 MOD-97-10** for IBANs, **Federal Reserve 9-Digit Checksum** for ABA Routing, and valid SSN prefixes. Zero false positives on invoices. |
| **Contextual Token NER** | Lightweight spaCy (`en_core_web_sm`) | Extracts Customer Names (`PERSON`), Corporate Banks (`ORG`), and Addresses (`LOCATION`). |
| **Anti-Evasion Normalizer** | Custom Unicode & Regex Engine | Defeats zero-width characters (`\u200B`), Cyrillic homoglyphs (`а`, `е`, `о`), spaced digits (`4 5 3 0 ...`), and decodes base64 payload strings. |
| **In-Memory OCR** | PyMuPDF (`fitz`) + EasyOCR | Extracts text from screenshots (`.png`, `.jpg`) and scanned photocopied PDFs with zero disk leakage. |
| **Redaction & Tokenizer** | Reverse-Offset Replacement & HMAC-SHA256 | Mode A: Partial Masking (`[CARD_****9182]`). Mode B: Deterministic Cryptographic Tokenization (`[TOKEN_<hash>]`). |

---

## 🔒 Security & Compliance Standards

* **Zero Customer Plaintext Logging**: The anti-leak logging middleware fingerprints all payloads using cryptographic SHA-256 hashes. Unmasked customer PII is strictly forbidden from stdout and disk logs.
* **PCI-DSS Compliance**: Strict Luhn algorithm verification eliminates false positives; real card numbers are masked to preserve only the trailing 4 digits.
* **DoS Protection**: Document ingestion is bounded by strict limits (first 5 pages or 10,000 words; max image resolution $2048 \times 2048$) to prevent memory exhaustion attacks.

---

## 📜 License

Distributed under the Apache 2.0 License. See [`LICENSE`](file:///c:/Users/RUSHIKESH/SecureFLowAI/LICENSE) for details.
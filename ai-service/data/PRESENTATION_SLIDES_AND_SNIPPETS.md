# SecureFlow AI — Dataset Presentation Deck & Demo Snippets

This guide provides presentation-ready visual cards, talking points, and before/after snippets for each dataset in **SecureFlow AI**.

---

## 🖥️ Live Terminal Presentation Command
During a live demo or presentation, you can run:
```bash
python present_datasets.py
```
*(or `python ai-service/data/scripts/present_datasets.py`)*

---

## 📊 Presentation Slide Cards (Copy-Paste for Slides)

---

### Slide 1: DISC (Defense & Security Clearance Classification)

```
+------------------------------------------------------------------------------+
| 1. DISC — Security Clearance Intelligence Corpus                             |
+------------------------------------------------------------------------------+
| Domain:          Defense Intelligence & Clearance Marking                   |
| Size & Format:   2,459 Documents | JSON (35.5 MB)                            |
| Platform Role:   Primary 4-Tier Document Sensitivity Classifier              |
+------------------------------------------------------------------------------+
```

#### 🔍 Visual Snippet:
- **Raw Intelligence Cable**:
  > *"SECRET PESHAWAR 1084 ... SUBJECT: MUJAHEDIN CROSS BORDER COW RAID INTO THE SOVIET UNION INVITES COSTLY RETALIATION ... FAILING TO ACHIEVE THEIR OBJECTIVE OF ATTACKING SOVIET POSTS INSIDE TAJIKISTAN..."*
- **Original Classification Tag**: `[{"Label": "Top Secret"}, {"Label": "Unclassified"}]`
- **SecureFlow Sanitized Output**:
  > **Assigned Tier**: `Highly Confidential`  
  > **Sanitized Text (Watermark Removed)**: *"SUBJECT: MUJAHEDIN CROSS BORDER COW RAID INTO THE SOVIET UNION..."*
- **Talking Points**:
  - *"We map raw intelligence cables to our 4-tier taxonomy (Highly Confidential, Confidential, Internal, Public)."*
  - *"We apply regex sanitization to strip classification watermarks so our DeBERTa model learns document semantics rather than memorizing header text."*

---

### Slide 2: Medical PHI (HIPAA & Healthcare Consultation Records)

```
+------------------------------------------------------------------------------+
| 2. Medical PHI — Clinical & Patient Records                                  |
+------------------------------------------------------------------------------+
| Domain:          Healthcare & Protected Health Information (HIPAA)           |
| Size & Format:   2,000 Consultation Pairs | Apache Parquet (1.2 MB)          |
| Platform Role:   Confidential Healthcare Tier (4-Tier Classifier)            |
+------------------------------------------------------------------------------+
```

#### 🔍 Visual Snippet:
- **Patient Prompt**: *"last year my wife was went through a surgery for appendix cancer, that appendix was removed , that appendix slice tested in lab and found so called adino carci..."*
- **Physician Completion**: *"Hi and welcome to HCM. First, you dont have to worry. This cant be tumour relaps because this is lesion in abdominall wall, obviously some local infection..."*
- **SecureFlow Unified Record**:
  > **Assigned Tier**: `Confidential (Healthcare / PHI)`  
  > **Unified Context**: `Patient Consultation: Appendix cancer inquiry ... | Clinical Assessment: Post-surgical lesion diagnosis ...`
- **Talking Points**:
  - *"Clinical records are paired and mapped directly into our 'Confidential' healthcare tier."*
  - *"Ensures compliance with HIPAA 45 CFR § 164.514 and prevents accidental medical history leakage."*

---

### Slide 3: RoBERTa-PII-Synth (Token-Level PII & NER Redaction)

```
+------------------------------------------------------------------------------+
| 3. RoBERTa-PII-Synth — Synthetic Token NER                                   |
+------------------------------------------------------------------------------+
| Domain:          Personally Identifiable Information (PII)                   |
| Size & Format:   120,000 Annotated Sequences | Arrow (135 MB)                |
| Platform Role:   Transformer Token Classification & Reversible Redaction     |
+------------------------------------------------------------------------------+
```

#### 🔍 Visual Snippet:
- **Raw Input String**:
  > `"DON'T SHACE buX uZrE's 1970rodney.lewis'S coMatctD sarahperez@aol.com /g2118x174 / ssn 0651734596"`
- **Annotated Spans**:
  - `[23:39]` `PERSON` $\to$ `"1970rodney.lewis"`
  - `[51:69]` `EMAIL` $\to$ `"sarahperez@aol.com"`
  - `[72:80]` `PHONE` $\to$ `"2118x174"`
  - `[87:97]` `SSN` $\to$ `"0651734596"`
- **SecureFlow Redacted Output**:
  > `"DON'T SHACE buX uZrE's [PERSON_REDACTED]'S coMatctD [EMAIL_REDACTED] /g[PHONE_REDACTED] / ssn [SSN_REDACTED]"`
- **Talking Points**:
  - *"Fine-tunes our subword token NER model across 120,000 synthetic sentences."*
  - *"Supports precision in-place masking, hashing, and reversible tokenization for GDPR and PCI-DSS compliance."*

---

### Slide 4: UM-DLP (Adversarial Robustness & Evasion Benchmark)

```
+------------------------------------------------------------------------------+
| 4. UM-DLP — Adversarial Robustness Benchmark                                 |
+------------------------------------------------------------------------------+
| Domain:          Adversarial Obfuscation & Evasion Testing                   |
| Size & Format:   1,343 Evaluation Cases | CSV (468 KB)                       |
| Platform Role:   Empirical DLP Quality Gate & Evasion Robustness             |
+------------------------------------------------------------------------------+
```

#### 🔍 Visual Snippet:
- **Test ID #1 (Positive Obfuscated)**:
  > *"Please help me verify if my credit card number 6011-2398-5674-9012 has been compromised in the recent data breach at Greenview Bank. Expiry date is 04/26, CVV 837..."*
- **Ground Truth**: `sensitive`
- **Adversarial Test Slices**:
  - `Positive Direct`: Plaintext credit card and PII leaks.
  - `Positive Obfuscated`: Leetspeak (`crdit c@rd`), spacing insertion (`5 5 5 - 0 1 9 9`).
  - `Negative Keyword`: Benign financial news containing terms like *"credit card"* without actual data.
- **Talking Points**:
  - *"An independent benchmark acting as our CI/CD quality gate."*
  - *"Enforces $\ge 95\%$ recall on obfuscations and $\le 3\%$ false alarm rate on benign text."*

---

### Slide 5: Contextual Sensitive Data (Database Schema Sensitivity)

```
+------------------------------------------------------------------------------+
| 5. Contextual Sensitive Data — Schema Sensitivity                            |
+------------------------------------------------------------------------------+
| Domain:          Database Attribute Classification & Context Disambiguation  |
| Size & Format:   1,000 Instruction Records | CSV (922 KB)                    |
| Platform Role:   LLM Contextual Sensitivity Reasoning & Schema Crawler       |
+------------------------------------------------------------------------------+
```

#### 🔍 Visual Snippet:
- **Column Name**: `condition`
- **Extracted Column Values**: `['0', 'active', 'active', '1', '1']`
- **System Instruction**: *"You are a PII classification system. Given a column name and records, determine if this column contains sensitive data..."*
- **Model Output**: `Non-Sensitive (Categorical system state flag)`
- **Talking Points**:
  - *"Disambiguates column sensitivity based on real data distributions."*
  - *"Powers our automated SQL crawler for PostgreSQL, Snowflake, and BigQuery."*

---

### Slide 6: Enron Corporate Emails (Internal Domain Generalization)

```
+------------------------------------------------------------------------------+
| 6. Enron Corporate Emails — Business Domain Generalization                   |
+------------------------------------------------------------------------------+
| Domain:          Corporate Communications & Trade Secrets                    |
| Size & Format:   2,000 Emails | CSV (1.7 MB)                                 |
| Platform Role:   Internal Domain Generalization & Exfiltration Detection     |
+------------------------------------------------------------------------------+
```

#### 🔍 Visual Snippet:
- **Subject**: `"Service Agreement"`
- **Body Snippet**: *"Greg/Phillip, Attached is the Grande Communications Service Agreement. The business points can be found in Exhibit C. I can get the Non-Disturbance agreement after it has been executed..."*
- **Assigned Tier**: `Internal (Corporate Communications)`
- **Talking Points**:
  - *"Tests model robustness against messy, informal business discourse."*
  - *"Detects unauthorized forwarding of internal vendor pricing, executive agreements, and trade secrets."*

---

### Slide 7: STARGATE (Scanned PDF OCR Attachment Pipeline)

```
+------------------------------------------------------------------------------+
| 7. STARGATE — Scanned PDF OCR Archive                                        |
+------------------------------------------------------------------------------+
| Domain:          Unstructured Document Intelligence & Scanned Attachments    |
| Size & Format:   7,394 Scanned Documents | PDF Files (300+ MB)               |
| Platform Role:   OCR Image Preprocessing, Binarization & Attachment DLP      |
+------------------------------------------------------------------------------+
```

#### 🔍 Visual Snippet:
- **Available Corpus**: 7,394 declassified CIA scanned PDFs (e.g. `CIA-RDP79-00999A000200010001-4.pdf`)
- **Attachment Ingestion Flow**:
  1. `PDF Page` $\longrightarrow$ 300 DPI Grayscale Image
  2. `OpenCV Pipeline` $\longrightarrow$ Deskewing (Hough Transform) + Otsu Adaptive Binarization
  3. `Tesseract OCR` $\longrightarrow$ Noisy text extraction + spell repair
  4. `DLP Inspection` $\longrightarrow$ 4-Tier Classifier + PII Redactor
- **Talking Points**:
  - *"Enables DLP inspection on scanned document attachments, PDFs, and screenshots."*
  - *"Prevents data exfiltration disguised as scanned image files."*

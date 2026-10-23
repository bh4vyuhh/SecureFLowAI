# SecureFlow AI - Executive Demonstration & Presentation Guide

**Autonomous Edge-Native Data Loss Prevention (DLP) & Cryptographic Threat Defense System**

---

## 🎯 Demonstration Scenarios Overview

This directory (`demonstration_data/`) provides curated, realistic banking payloads and test cases designed to demonstrate the complete SecureFlow AI platform to evaluators, auditors, and stakeholders.

| # | Demo Scenario | Test File / Action | Target Subsystem | Expected Enforcement |
|---|---|---|---|---|
| **1** | **Live Browser Interception** | Form typing / paste on web page | Chrome Extension -> Spring Boot (9090) / FastAPI (8000) | **BLOCK** exfiltration & display red security banner |
| **2** | **Desktop Clipboard Scrubbing** | Copy payload to Windows clipboard | Desktop Agent background daemon (`desktop-agent/main.py`) | **WIPE** clipboard contents within <15ms & log incident |
| **3** | **Live Payload Classification** | Paste payload into SOC Console | `http://localhost:5174/?view=live` | **ONNX INT8** inference, spaCy NER, HMAC tokenization |
| **4** | **Multi-Format Document Scanner** | Upload CSV / PDF / TXT document | `http://localhost:5174/?view=scanner` | **OCR + Heuristic Detection**, tabular entity preview |
| **5** | **Cryptographic Ledger Audit** | Inspect Merkle audit chain | `http://localhost:5174/?view=audit` | **SHA-256 Hash Chain** validation & Detokenization Vault |
| **6** | **Conversational Copilot** | Query incidents & explain compliance | `http://localhost:5174/?view=copilot` | **Gemini 1.5 Flash** grounded incident triage |

---

## 🚀 Scenario 1: Real-Time Browser Extension Interception

### Objective
Demonstrate that an employee attempting to paste sensitive credit cards or corporate secrets into an external web form (e.g., ChatGPT, Claude, Pastebin, Google Forms) is **immediately blocked before the data leaves the browser**.

### Steps to Reproduce:
1. Open Google Chrome or Microsoft Edge.
2. Navigate to `chrome://extensions/` (or `edge://extensions/`).
3. Ensure **Developer mode** is turned on in the top-right.
4. Click **Load unpacked** and select the folder:
   ```
   C:\Users\RUSHIKESH\SecureFLowAI\browser-extension
   ```
5. Open the built-in test playground in your browser:
   ```
   http://localhost:5174/test_playground.html
   ```
6. Copy the Credit Card payload from `01_CRITICAL_EXFILTRATION_PAYLOADS.txt`:
   ```
   Alice M. Sterling, Card: 4532 8912 3456 9812, CVV: 891, Exp: 08/28
   ```
7. Paste or type into the playground form.
8. **Result**: 
   - The browser extension intercepts the keystroke/paste via capture phase.
   - Text is cleared immediately.
   - A red high-severity warning banner pops up explaining the PCI-DSS violation.
   - An incident is transmitted to `http://localhost:5174/?view=dashboard` in real-time.

---

## 📋 Scenario 2: Background Desktop Clipboard Scrubbing

### Objective
Demonstrate background endpoint DLP running as a native Windows service monitoring clipboard transfers.

### Steps to Reproduce:
1. Ensure the desktop agent is running (`desktop-agent/main.py` is started by `RUN_SECUREFLOW_PRODUCTION.bat`).
2. Copy any credit card number from `01_CRITICAL_EXFILTRATION_PAYLOADS.txt` using `Ctrl+C`.
3. Open Notepad or any text editor and press `Ctrl+V`.
4. **Result**:
   - The clipboard content has been scrubbed/emptied by the agent.
   - A Windows desktop notification warns the user that sensitive financial data cannot be stored in system clipboard memory.

---

## 🧠 Scenario 3: Live Classification & HMAC Detokenization

### Objective
Demonstrate INT8 quantized ONNX Transformer inference with sub-15ms latency and reversible HMAC-SHA256 tokenization.

### Steps to Reproduce:
1. Open the SOC Console at `http://localhost:5174/?view=live`.
2. Paste the contents of `02_CONFIDENTIAL_WIRE_TRANSFER_MEMO.txt` into the payload inspection console.
3. Click **Scan Payload**.
4. **Result**:
   - Real inference latency reported (e.g., `12.4ms`).
   - Risk score: `95% (HIGH SEVERITY)`.
   - Classification: `RESTRICTED / TIER 1`.
   - Detected Entities: `SWIFT_BIC`, `IBAN`, `ABA_ROUTING`, `ORG`, `PERSON`.
   - Reversible tokenized preview generated replacing plaintext with secure cryptographic placeholders: `[IBAN_TOKEN_#a8f9...]`.

---

## 📁 Scenario 4: Bulk Document & File Scanner

### Objective
Demonstrate multi-format document scanning supporting CSV, TXT, and PDF files.

### Steps to Reproduce:
1. Open the SOC Console at `http://localhost:5174/?view=scanner`.
2. Drag and drop `03_EXECUTIVE_PAYROLL_AND_COMPENSATION.csv` onto the upload zone.
3. Click **Execute Deep DLP Scan**.
4. **Result**:
   - The parser inspects all rows, detecting multiple Social Security Numbers, ABA Routing numbers, and compensation details.
   - File is classified as `CONFIDENTIAL / RESTRICTED`.
   - Option to download the auto-sanitized / masked version of the document.

---

## 🔒 Scenario 5: Cryptographic Merkle Ledger Verification

### Objective
Demonstrate that all DLP transactions are immutably logged into an append-only SHA-256 cryptographic chain that proves zero database tampering.

### Steps to Reproduce:
1. Open the SOC Console at `http://localhost:5174/?view=audit`.
2. Click the **Verify Ledger Integrity** button in the header.
3. **Result**:
   - The system verifies the cryptographic hash chain:
     $$\text{audit\_hash}_i = \text{SHA256}(\text{id} \parallel \text{timestamp} \parallel \text{payload\_sha256} \parallel \text{prev\_hash}_{i-1})$$
   - Green confirmation banner: **LEDGER INTEGRITY VERIFIED: 100% UNTAMPERED**.
4. Click on any transaction row to open the **Forensic Incident Inspection Modal**.
5. Test **Detokenize in Vault**: enter the CISO authorization key (`SecureFlowAI-Production-Banking-Key-32BytesLong!`) to reveal the original plaintext entity securely from the HSM vault.

---

## 🤖 Scenario 6: AI Copilot Incident Triage

### Objective
Demonstrate the conversational AI assistant assisting SOC analysts with incident review and policy guidance.

### Steps to Reproduce:
1. Open the SOC Console at `http://localhost:5174/?view=copilot`.
2. Ask questions such as:
   - *"What were the top security threats blocked today?"*
   - *"Explain why wire transfers with IBANs are classified as Tier 1 Restricted."*
   - *"Summarize incident evt-4d5e6f7a for an audit report."*
3. **Result**:
   - Gemini 1.5 Flash generates contextual, grounded responses referencing the actual SQLite incident database.

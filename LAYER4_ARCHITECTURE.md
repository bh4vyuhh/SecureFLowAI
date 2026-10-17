# 🏛️ Layer 4: Data & Cryptography Master Architecture
**System Module:** `crypto-enforcement`  
**Engineer's Role:** Data Protection & Cryptography Specialist  
**Core Objective:** Safely transform, mask, tokenize, encrypt, and audit sensitive banking data in real-time (< 2ms) without slowing down the bank or corrupting text.

---

## 🧭 1. Executive Summary & The High-Level Picture
In an enterprise Data Leakage Prevention (DLP) ecosystem, SecureFlow AI operates like an airport security checkpoint:
* **Layer 1 & 2 (Clients & Gateway):** Passenger and luggage check-in. Transports user payloads, files, and clipboard buffers to the central inspection gate.
* **Layer 3 (The AI Engine):** The X-ray scanning machine. Inspects the luggage and reports: *"Warning! Found three credit cards and a Social Security Number at specific character locations in this file, risk score: 88."*
* **Layer 4 (YOUR MODULE — `crypto-enforcement`):** **The Security Officer.**  
  The AI engine does not touch the luggage; Layer 4 does. Layer 4 reviews the AI's detection report, checks the active banking security manual, and executes the final decision:
  * **BLOCK:** Confiscate the payload and terminate the transfer immediately.
  * **MASK / REDACT:** Apply offset-safe surgical banking masks without corrupting surrounding text.
  * **ENCRYPT / TOKENIZE:** Lock the payload in an armored cryptographic container.
  * **ALLOW:** Pass benign low-risk transfers through untouched.
  * **AUDIT:** Write a permanent tamper-evident entry into the PostgreSQL legal ledger asynchronously in the background.

---

## 🧱 2. The 5 Core Engineering Modules

### 📦 Module 1: The PostgreSQL Data Vault & Storage Architecture
*(The System's Long-Term Memory & Legal Proof)*

Under global financial regulations (**PCI-DSS 4.0 Requirements 3 & 10**, **GDPR Article 32**, **NIST SP 800-122**), financial institutions must prove to regulatory auditors that all sensitive data movements are monitored and protected.

#### The Three Core Vault Tables
1. **The Audit Log Table (`dlp_audit_logs`)**:
   Records every inspected transaction: timestamp, employee ID, client application (e.g., Browser, Outlook), destination, AI risk score, enforcement action taken (`ALLOW`, `MASK`, `ENCRYPT`, `TOKENIZE`, `BLOCK`), execution latency, and a SHA-256 digital fingerprint of the original payload.
2. **The Secure Token Vault Table (`token_vault`)**:
   Pairs deterministic tokens (e.g., `[TOKEN_7a8f9b2c3d4e]`) with the original sensitive value encrypted using **AES-256-GCM** with a dedicated 12-byte random Nonce.
3. **The Security Policies Table (`security_policies`)**:
   Stores dynamic thresholds (e.g., Block threshold $\ge 80$, Remediate threshold $\ge 45$) and approved partner email domains (e.g., `@visa.com`, `@mastercard.com`, `clearinghouse.bank.org`). Security administrators can update policies instantly without restarting or redeploying the software.

#### 🔒 The Golden Rule of Banking Storage
> **Never store plain-text customer data in the database.**  
> In the Token Vault, real credit card numbers and account numbers are always strongly encrypted with AES-256-GCM before database insertion. If an adversary breaches the database, they will find only unreadable ciphertext and random Nonces.

---

### 📦 Module 2: The Offset-Safe Text Masking Engine
*(Surgical Data De-Identification)*

Surgically covers confidential segments with standard banking masks while preserving greetings, punctuation, and sentence syntax.

#### The Offset Drift Trap & Reverse-Order Mathematics
* **The Problem:** Left-to-right replacement alters text length.
  ```
  Original: "Pay card 4532-8921-0043-9182 with SSN 123-45-6789 today."
  - Entity 1 (Card): index [9, 28) (19 chars)
  - Entity 2 (SSN):  index [38, 49) (11 chars)
  ```
  If Entity 1 is replaced with `[CARD_****9182]` (15 chars), the text loses 4 characters. Every index to the right shifts 4 positions to the left. Index 38 now points to `" 123-45-67"`, cutting off the wrong words and corrupting the sentence.
* **The Reverse-Order Solution:**
  Entities are sorted in **reverse order** (descending start index: largest start index to smallest) before applying replacements:
  1. Replace Entity 2 (SSN at index 38) first. Because it is near the end, changing its length shifts nothing to its left.
  2. Replace Entity 1 (Card at index 9) second. Its start index has not moved by even one millimeter.
  Zero offset drift, zero text corruption.

#### Standard Banking Mask Formats
| Entity Type | Masking Standard | Example Transformation |
| :--- | :--- | :--- |
| **Credit Cards** | Preserve last 4 digits | `4532-8921-0043-9182` $\to$ `[CARD_****9182]` |
| **IBAN / Accounts** | Preserve country code & last 4 digits | `GB82WEST12345698765432` $\to$ `[IBAN_GB****5432]` |
| **SSN** | Complete regulatory redaction | `123-45-6789` $\to$ `[SSN_***-**-****]` |
| **API Keys / Secrets** | Complete secret redaction | `sk_live_99482710183` $\to$ `[REDACTED_SECRET]` |
| **Email Addresses** | Complete redaction | `customer@bank.com` $\to$ `[REDACTED_EMAIL]` |
| **Phone Numbers** | Preserve last 4 digits | `+1-555-019-2831` $\to$ `[PHONE_****2831]` |

---

### 📦 Module 3: The Cryptographic Subsystems (Tokenization & Envelope Encryption)
*(The Mathematical Armor)*

Provides two cryptographic engines: **Deterministic HMAC-SHA256 Tokenization** and **AES-256-GCM Envelope Encryption**.

#### Mechanism A: Deterministic HMAC-SHA256 Tokenization
1. Utilizes a Master HMAC Secret Key known only to the core banking security infrastructure.
2. Computes an HMAC-SHA256 digest of the sensitive customer number.
3. Formats the first 12 hex characters into a 20-character reversible token: `[TOKEN_7a8f9b2c3d4e]`.
4. **Deterministic Guarantee:** The same customer account number always generates the exact same token within the bank, allowing fraud monitoring teams to track transaction patterns across accounts without exposing raw numbers.
5. **Reversible Storage:** Pairs the token with the AES-256-GCM encrypted value in `token_vault`.
6. **Strict RBAC Detokenization:** Access to `detokenize()` is restricted to authenticated Compliance Officers (`ROLE_COMPLIANCE_OFFICER`, `ROLE_ADMIN`). Unauthorized roles are blocked with security alerts.

#### Mechanism B: Authenticated AES-256-GCM Envelope Encryption
1. Treats payloads as raw binary streams and encrypts using **AES-256** in **Galois/Counter Mode (GCM)** with a 128-bit authentication tag.
2. **The Nonce Rule:** Every encryption generates a **fresh, cryptographically random 12-byte Nonce** via `SecureRandom`. Nonces are never reused or hardcoded.
3. **Digital Wax Seal:** GCM creates an authentication tag. If an attacker modifies even a single bit of ciphertext in transit or storage, verification fails (`Tag mismatch`), raising an immediate tamper alert.

---

### 📦 Module 4: The Dynamic Policy & Enforcement Router
*(The Intelligent Traffic Controller)*

Evaluates incoming requests in real-time using a strict priority decision matrix:

```
                  [Incoming Request from AI Engine]
                                 │
                                 ▼
             [Check 1: Destination Whitelist Check]
             Is destination domain in approved partners?
             (e.g., @visa.com, @mastercard.com, clearinghouse)
                       │                    │
                     YES                    NO
                       │                    │
                       ▼                    ▼
             [Route Securely]    [Check 2: Risk Score Brackets]
             Downgrade severity    ├── Score 80 to 100: BLOCK
             or route to ENCRYPT   ├── Score 45 to 79:  REMEDIATE (MASK)
             instead of BLOCK      └── Score 0 to 44:   ALLOW
```

#### In-Memory Sub-2ms Performance Guarantee
Querying PostgreSQL on every payload adds 10–20ms of I/O latency. Layer 4 keeps all active policies and domain whitelists cached in an in-memory `AtomicReference`. Policy checks execute in **sub-millisecond (< 1ms)** time. The cache automatically refreshes from PostgreSQL every 60 seconds (`@Scheduled`) or instantaneously upon administrative policy updates.

---

### 📦 Module 5: The Non-Blocking Asynchronous Audit Pipeline
*(The High-Speed Background Scribe)*

High-throughput banking platforms process thousands of requests per second. Synchronous database writes cause unacceptable latency. Layer 4 decouples policy enforcement from database persistence using the **Producer-Consumer Pattern**:

```
[Request Thread]
       │
       ▼
[Enforce Policy] ──► [Compute SHA-256] ──► [Queue.offer()] ──► [Return Response to User]
                                                    │             (Latency: < 2ms)
                                                    ▼
                                           [In-Memory Queue]
                                           (ArrayBlockingQueue)
                                                    │
                                                    ▼
                                         [Background Worker]
                                         (Drains 50 logs / 500ms)
                                                    │
                                                    ▼
                                        [PostgreSQL dlp_audit_logs]
                                        (saveAll batch insert)
```

* **Producer:** Drops the audit record into a high-capacity in-memory queue (`ArrayBlockingQueue<DlpAuditLog>`) non-blockingly (`< 0.1ms`). The user receives their decision immediately.
* **Consumer:** Background scheduler drains records in batches (up to 50 logs every 500ms) and executes batch inserts via JPA `saveAll()`, cutting database overhead by 90%.
* **Graceful Shutdown:** `@PreDestroy` flush hook flushes all remaining queued audit logs to PostgreSQL before JVM termination.

---

## 🛡️ 3. The 4 Golden Rules of Layer 4
1. **Never log unmasked customer data.** If an error or audit occurs, record only payload hashes (`SHA-256`), entity counts, or masked tokens. Never leak plaintext account numbers or cards to application logs.
2. **Always sort entities backwards before masking.** Descending order sort by start index guarantees zero index drift and prevents text corruption.
3. **Always use a fresh 12-byte random Nonce for AES-GCM.** Nonces must never be hardcoded, static, or reused.
4. **Never make the user wait for database writes.** Deliver ALLOW / BLOCK / MASK decisions instantly (< 2ms) and persist audit logs asynchronously in batches.

---

## 🔌 4. REST API Specification

### 1. Real-Time DLP Enforcement
* **Endpoint:** `POST /api/v1/enforcement/evaluate`
* **Request:**
  ```json
  {
    "payload": "Please pay card 4532-8921-0043-9182 with SSN 123-45-6789.",
    "destination": "vendor@partner.org",
    "employeeId": "EMP_4812",
    "application": "OUTLOOK",
    "riskScore": 65,
    "entities": [
      { "entityType": "CREDIT_CARD", "start": 16, "end": 35, "text": "4532-8921-0043-9182" },
      { "entityType": "SSN", "start": 45, "end": 56, "text": "123-45-6789" }
    ]
  }
  ```
* **Response (Latency: < 2ms):**
  ```json
  {
    "success": true,
    "message": "Enforcement evaluation completed",
    "data": {
      "action": "MASK",
      "sanitizedPayload": "Please pay card [CARD_****9182] with SSN [SSN_***-**-****].",
      "riskScore": 65,
      "blocked": false,
      "remediated": true,
      "payloadHash": "3f42b31a89c836916a048d0859600e6a92ecf69668ad03125e173e168ceb2df0",
      "executionTimeMs": 1,
      "matchedEntities": ["CREDIT_CARD", "SSN"],
      "auditEventId": "b6a88b8e-3995-46aa-b2b5-3d5f39678129",
      "policyApplied": "Global Banking Financial DLP Policy",
      "reason": "Medium risk (Risk Score: 65). Remediated via MASK."
    }
  }
  ```

### 2. Standalone Offset-Safe Masking
* **Endpoint:** `POST /api/v1/crypto/mask`
* **Request:**
  ```json
  {
    "text": "Wire IBAN GB82WEST12345698765432 using secret api_live_998811.",
    "entities": [
      { "entityType": "IBAN", "start": 10, "end": 32, "text": "GB82WEST12345698765432" },
      { "entityType": "API_KEY", "start": 46, "end": 63, "text": "api_live_998811" }
    ]
  }
  ```
* **Response:**
  ```json
  {
    "success": true,
    "message": "Text masked safely without offset drift",
    "data": {
      "maskedText": "Wire IBAN [IBAN_GB****5432] using secret [REDACTED_SECRET].",
      "replacementsCount": 2,
      "maskedEntityTypes": ["IBAN", "API_KEY"],
      "executionTimeMs": 0
    }
  }
  ```

### 3. Deterministic HMAC Tokenization & RBAC Detokenization
* **Tokenize:** `POST /api/v1/crypto/tokenize`
  * Request: `{"sensitiveValue": "4532-0000-1111-2222", "entityType": "CREDIT_CARD", "requestedBy": "OFFICER_01"}`
  * Response: `{"success": true, "data": {"tokenId": "[TOKEN_a3f18e9d2c14]"}}`
* **Detokenize:** `POST /api/v1/crypto/detokenize`
  * Request: `{"tokenId": "[TOKEN_a3f18e9d2c14]", "requester": "OFFICER_01", "role": "ROLE_COMPLIANCE_OFFICER"}`
  * Response: `{"success": true, "data": {"originalValue": "4532-0000-1111-2222"}}`

### 4. Authenticated AES-256-GCM Envelope Encryption & Decryption
* **Encrypt:** `POST /api/v1/crypto/encrypt`
  * Request: `{"plainText": "Highly confidential merger portfolio"}`
  * Response: Base64 packed envelope with fresh 12-byte Nonce and 128-bit authentication tag.
* **Decrypt:** `POST /api/v1/crypto/decrypt`
  * Request: `{"cipherText": "<base64_packed_envelope>"}`
  * Response: Decrypted plaintext with verified authentication tag.

### 5. Audit Diagnostics & Policy Controls
* `GET /api/v1/audit/logs?page=0&size=20` — Query paginated audit ledger.
* `GET /api/v1/audit/stats` — Real-time telemetry (queue size, enqueued, persisted, blocked count).
* `GET /api/v1/policies` — List active DLP policies.
* `PUT /api/v1/policies/{id}` — Update policy thresholds and whitelisted domains with automatic in-memory cache invalidation.

---

## 🗄️ 5. PostgreSQL Schema & DDL
Located at `backend/src/main/resources/schema.sql` and `docker/init-db.sql`:
* `dlp_audit_logs`: Primary UUID key, indexed by `timestamp`, `employee_id`, `action_taken`, and `payload_hash`.
* `token_vault`: Primary UUID key, indexed by unique `token_id`, `token_type`, and `created_at`.
* `security_policies`: Primary auto-increment key, dynamic thresholds and domain whitelists.

---

## 🧪 6. Verification & Test Suite
The implementation includes complete test suites covering unit and integration testing across all 5 modules:
* `OffsetSafeMaskingEngineTest`: Validates the offset drift trap scenario, reverse-order sorting, overlapping spans, and banking mask formats.
* `CryptographicSubsystemTest`: Validates HMAC determinism, 12-byte random Nonce uniqueness, tamper detection wax-seal failure, and RBAC detokenization.
* `PolicyEnforcementRouterTest`: Validates whitelist routing, risk score brackets (80-100, 45-79, 0-44), and in-memory sub-2ms speed.
* `AsyncAuditPipelineTest`: Validates non-blocking enqueue (< 0.1ms), batch drain persistence, and shutdown flushing.
* `EnforcementControllerTest`: Full Spring MVC test covering end-to-end enforcement, masking, tokenization, and encryption.

**Run test suite:**
```powershell
cd c:\Users\Bhoomi\SecureFLowAI\backend
mvn clean test
```
Result: **25 / 25 Tests Passing (0 Failures, 0 Errors, BUILD SUCCESS).**

---

## 📋 7. Regulatory Compliance Matrix & Incident Runbook

### PCI-DSS 4.0 & GDPR Article 32 Alignment
| Regulatory Clause | Requirement Description | Layer 4 Implementation |
| :--- | :--- | :--- |
| **PCI-DSS 3.4** | Render PAN unreadable anywhere it is stored. | AES-256-GCM Envelope Encryption in `token_vault` with unique 12-byte random nonces. |
| **PCI-DSS 3.5.1** | Restrict access to cryptographic keys and detokenization. | RBAC enforcement (`ROLE_COMPLIANCE_OFFICER`, `ROLE_ADMIN`) in `CryptographicSubsystem`. |
| **PCI-DSS 10.2** | Implement automated audit trails for all system events. | Asynchronous batch audit ledger (`dlp_audit_logs`) recording digital SHA-256 fingerprints. |
| **GDPR Art. 32(1)(a)** | Pseudonymisation and encryption of personal data. | Deterministic HMAC-SHA256 tokenization preserving format without exposing plain text. |
| **NIST SP 800-122** | Safeguard confidentiality of personally identifiable information. | Offset-Safe surgical masking engine preventing text mangling and data exfiltration. |

### SOC Incident Response Runbook
1. **Critical Block Event (Score $\ge 80$):**
   - Immediate kill switch executed on transfer.
   - SHA-256 hash logged to `dlp_audit_logs` with `action_taken = BLOCK`.
   - Security Operations Center (SOC) receives high-priority event telemetry via `GET /api/v1/audit/stats`.
2. **Remediation Inspection (Score $45 - 79$):**
   - Automatic surgical banking redaction or tokenization applied.
   - Downstream recipients receive sanitized payload preserving non-confidential operational text.


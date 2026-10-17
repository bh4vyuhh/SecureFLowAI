# SecureFlow AI
AI-powered Enterprise Data Leakage Prevention (DLP) Platform

## 🏛️ Architecture Overview
SecureFlow AI is an enterprise-grade DLP platform designed to protect sensitive financial records, PII, and corporate communications across endpoints, cloud gateways, and file attachments:
- **Layer 1 & 2:** Clients & API Gateway (Web UI, Outlook/Desktop agent endpoints)
- **Layer 3:** AI Engine (RoBERTa PII Token-level NER & Medical PHI Scanner)
- **Layer 4:** Data & Cryptography Master Architecture (`crypto-enforcement`)
  - **Module 1:** PostgreSQL Data Vault & Legal Audit Ledger (`dlp_audit_logs`, `token_vault`, `security_policies`)
  - **Module 2:** Offset-Safe Text Masking Engine (Reverse-order replacement, standard banking masks)
  - **Module 3:** Cryptographic Subsystems (Deterministic HMAC-SHA256 Tokenization & AES-256-GCM Envelope Encryption)
  - **Module 4:** Dynamic Policy & Enforcement Router (Whitelist checks, risk brackets, sub-2ms in-memory cache)
  - **Module 5:** Non-Blocking Asynchronous Audit Pipeline (High-speed Producer-Consumer batching)

Detailed specifications: See [`LAYER4_ARCHITECTURE.md`](./LAYER4_ARCHITECTURE.md).

## Tech Stack
- **Backend:** Java 21 / 25, Spring Boot 3.5.4, Spring Data JPA, Spring Security
- **Security & Cryptography:** AES-256-GCM (12-byte random Nonces, 128-bit authentication tag), HMAC-SHA256, SHA-256 fingerprinting
- **Database:** PostgreSQL 17 (Data Vault, Audit Ledger, Token Vault)
- **Frontend:** React 19, Vite, Tailwind CSS, Lucide Icons
- **AI Service:** Python, FastAPI, Hugging Face Transformers
- **Containerization:** Docker & Docker Compose

## Quick Start

### 1. Start Database Vault (Docker)
```bash
docker compose up -d postgres
```

### 2. Run Backend (Spring Boot)
```bash
cd backend
mvn clean spring-boot:run
```

### 3. Run Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

### 4. Run Test Suite
```bash
cd backend
mvn clean test
```
*(All 25/25 Layer 4 unit and integration tests passing)*

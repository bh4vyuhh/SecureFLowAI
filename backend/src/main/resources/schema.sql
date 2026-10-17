-- =========================================================================
-- Layer 4: Data & Cryptography Master Architecture
-- Module 1: PostgreSQL Data Vault & Storage Architecture
-- Regulatory Compliance: PCI-DSS 4.0 (Req 3, 10), GDPR Art 32, NIST SP 800-122
-- =========================================================================

-- 1. Audit Log Table (dlp_audit_logs)
-- Permanent tamper-evident legal ledger recording every inspection
CREATE TABLE IF NOT EXISTS dlp_audit_logs (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    employee_id VARCHAR(120) NOT NULL,
    application VARCHAR(100) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    risk_score INTEGER NOT NULL CHECK (risk_score >= 0 AND risk_score <= 100),
    action_taken VARCHAR(32) NOT NULL,
    payload_hash VARCHAR(64) NOT NULL,
    matched_entities VARCHAR(500),
    execution_time_ms BIGINT,
    policy_id_applied VARCHAR(100),
    details TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON dlp_audit_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_employee_id ON dlp_audit_logs(employee_id);
CREATE INDEX IF NOT EXISTS idx_audit_action_taken ON dlp_audit_logs(action_taken);
CREATE INDEX IF NOT EXISTS idx_audit_payload_hash ON dlp_audit_logs(payload_hash);

-- 2. Secure Token Vault Table (token_vault)
-- Golden Rule: Never store plain-text customer data.
-- Real values are encrypted with AES-256-GCM and unique 12-byte Nonce.
CREATE TABLE IF NOT EXISTS token_vault (
    id UUID PRIMARY KEY,
    token_id VARCHAR(64) NOT NULL UNIQUE,
    encrypted_value TEXT NOT NULL,
    iv_nonce VARCHAR(64) NOT NULL,
    token_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_by VARCHAR(120) NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_token_id ON token_vault(token_id);
CREATE INDEX IF NOT EXISTS idx_token_type ON token_vault(token_type);
CREATE INDEX IF NOT EXISTS idx_token_created_at ON token_vault(created_at DESC);

-- 3. Security Policies Table (security_policies)
-- Dynamic policy rules allowing instant updates without redeployment
CREATE TABLE IF NOT EXISTS security_policies (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    block_threshold INTEGER NOT NULL DEFAULT 80,
    remediate_threshold INTEGER NOT NULL DEFAULT 45,
    allow_threshold INTEGER NOT NULL DEFAULT 0,
    whitelisted_domains TEXT NOT NULL,
    default_remediation_action VARCHAR(32) NOT NULL DEFAULT 'MASK',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

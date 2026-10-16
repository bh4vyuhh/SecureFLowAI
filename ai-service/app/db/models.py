"""
SecureFlow AI - Enterprise Database Models
================================================================================
File: ai-service/app/db/models.py

Defines forward-compatible database models for:
  - IncidentRecord: Non-repudiable zero-leak audit logging with JSONB telemetry
  - TokenVaultRecord: Reversible token-to-ciphertext mapping
  - DLPPolicyRecord: Versioned security policy definitions with threshold rules
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class IncidentRecord(Base):
    """
    Zero-Leak Incident Audit Log.
    Never stores raw plaintext customer data; stores payload_sha256 and entity counts.
    Supports forward-compatible JSONB telemetry (latencies, device fingerprint, metadata).
    """
    __tablename__ = "dlp_incidents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    
    # Client & Contextual Metadata
    client_id = Column(String(128), index=True, default="unknown-client")
    user_id = Column(String(128), index=True, default="anonymous")
    department = Column(String(64), index=True, default="general")
    destination_domain = Column(String(256), index=True, default="internal")
    source_action = Column(String(32), default="clipboard")  # clipboard, upload, prompt, email
    
    # Detection & Enforcement Attributes
    classification_tier = Column(String(32), index=True, default="SAFE")  # SAFE, CONFIDENTIAL, RESTRICTED
    risk_score = Column(Integer, default=0, index=True)
    enforcement_action = Column(String(32), default="ALLOW")  # ALLOW, MASK, BLOCK
    
    # Zero-Leak SHA-256 Hash of original inspected payload
    payload_sha256 = Column(String(64), index=True, nullable=False)
    
    # Cryptographic Tamperproof Hash Chaining (Objective 4: Effortless Regulatory Reporting)
    prev_hash = Column(String(64), default="GENESIS_BLOCK_0000000000000000000000000000000000000000000000000000")
    audit_hash = Column(String(64), index=True)
    
    # Regulatory Compliance Mapping (e.g. ["PCI-DSS-v4.0-Req3", "GDPR-Art32", "RBI-DLP-2023"])
    compliance_tags = Column(JSON, default=list)

    # Counts of entities detected (e.g. {"CREDIT_CARD": 2, "IBAN": 1})
    entity_counts = Column(JSON, default=dict)
    
    # Forward-compatible telemetry (processing latency ms, engine type, client OS, etc.)
    telemetry = Column(JSON, default=dict)
    
    # SOC Triage Status
    status = Column(String(32), default="OPEN", index=True)  # OPEN, REVIEWED, RESOLVED, FALSE_POSITIVE


class TokenVaultRecord(Base):
    """
    Reversible HMAC Token Vault.
    Stores AES-256-GCM envelope-encrypted ciphertext keyed by deterministic HMAC token.
    Includes key version ID for seamless cryptographic key rotation.
    """
    __tablename__ = "dlp_token_vault"

    token = Column(String(128), primary_key=True)  # TOK_CREDIT_CARD_...
    entity_type = Column(String(64), index=True, nullable=False)
    ciphertext = Column(Text, nullable=False)  # Base64 nonce + ciphertext + tag
    key_version = Column(String(16), default="v1", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DLPPolicyRecord(Base):
    """
    Dynamic Bank DLP Policy Configuration.
    Versioned to track policy iterations and audit trail over time.
    """
    __tablename__ = "dlp_policies"

    id = Column(String(64), primary_key=True, default="default-bank-policy")
    name = Column(String(128), nullable=False)
    version = Column(Integer, default=1, nullable=False)
    
    # Dynamic Risk Thresholds
    action_threshold_mask = Column(Integer, default=40)
    action_threshold_block = Column(Integer, default=70)
    
    # Whitelisted Destination Domains
    whitelisted_domains = Column(JSON, default=lambda: ["*.internal.bank.com", "api.internal.bank"])
    
    is_active = Column(Boolean, default=True, index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

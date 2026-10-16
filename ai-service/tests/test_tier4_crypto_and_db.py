"""
Tier 4 Tests - AES-256-GCM Crypto Vault, DB Audit Persistence & Detokenization
================================================================================
File: ai-service/tests/test_tier4_crypto_and_db.py
"""

import time
import pytest
from fastapi.testclient import TestClient
from app.crypto.vault import CryptoVault, get_crypto_vault
from app.db.session import init_db, SessionLocal
from app.db.models import IncidentRecord, TokenVaultRecord
from app.db.audit_writer import NonBlockingAuditWriter
from app.main import app

client = TestClient(app)


def test_crypto_vault_aes_gcm_encrypt_decrypt():
    vault = CryptoVault(key_version="v1")
    secret_card = "4532-8921-0043-9182"
    
    # 1. Encrypt
    ciphertext_b64 = vault.encrypt(secret_card)
    assert ciphertext_b64 != secret_card
    assert len(ciphertext_b64) > 30

    # 2. Decrypt
    decrypted = vault.decrypt(ciphertext_b64)
    assert decrypted == secret_card


def test_crypto_vault_token_generation_and_vaulting():
    vault = CryptoVault()
    entity_type = "CREDIT_CARD"
    card_number = "5500-0000-0000-0004"

    token, ciphertext, content_hash = vault.vault_token(entity_type, card_number)
    
    assert token.startswith("TOK_CREDIT_CARD_")
    assert vault.decrypt(ciphertext) == card_number
    assert len(content_hash) == 64  # SHA-256 hex length


@pytest.mark.anyio
async def test_non_blocking_audit_writer_async_batch():
    init_db()
    writer = NonBlockingAuditWriter(batch_size=10, flush_interval_secs=0.1)
    await writer.start()

    incident_id = f"test-inc-{int(time.time()*1000)}"
    incident_data = {
        "id": incident_id,
        "client_id": "test-client-daemon",
        "user_id": "analyst@bank.com",
        "department": "retail",
        "destination_domain": "api.openai.com",
        "source_action": "clipboard",
        "classification_tier": "RESTRICTED",
        "risk_score": 90,
        "enforcement_action": "BLOCK",
        "payload_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "entity_counts": {"CREDIT_CARD": 1},
        "telemetry": {"latency_ms": 8.5},
        "status": "OPEN"
    }

    vaulted_tokens = [{
        "token": f"TOK_CREDIT_CARD_{incident_id}",
        "entity_type": "CREDIT_CARD",
        "ciphertext": CryptoVault().encrypt("4532-8921-0043-9182"),
        "key_version": "v1"
    }]

    # Enqueue should return immediately without blocking
    await writer.enqueue_incident(incident_data, vaulted_tokens)

    # Wait briefly for background flush
    await writer._flush_all()
    await writer.stop()

    # Verify persisted in database
    db = SessionLocal()
    try:
        rec = db.query(IncidentRecord).filter(IncidentRecord.id == incident_id).first()
        assert rec is not None
        assert rec.enforcement_action == "BLOCK"
        assert rec.risk_score == 90
        assert rec.payload_sha256 == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

        vrec = db.query(TokenVaultRecord).filter(TokenVaultRecord.token == f"TOK_CREDIT_CARD_{incident_id}").first()
        assert vrec is not None
        assert vrec.entity_type == "CREDIT_CARD"
    finally:
        db.close()


def test_detokenize_api_endpoint():
    # Insert a vaulted token directly
    init_db()
    db = SessionLocal()
    vault = get_crypto_vault()
    token = "TOK_CREDIT_CARD_DETOK_TEST"
    raw_val = "4000-1234-5678-9010"
    ct = vault.encrypt(raw_val)

    try:
        rec = TokenVaultRecord(token=token, entity_type="CREDIT_CARD", ciphertext=ct, key_version="v1")
        db.merge(rec)
        db.commit()
    finally:
        db.close()

    # 1. Invalid key -> 403 Forbidden
    resp_bad = client.post("/api/v1/crypto/detokenize", json={
        "token": token,
        "authorization_key": "wrong-key"
    })
    assert resp_bad.status_code == 403

    # 2. Valid key -> 200 OK with plaintext
    resp_good = client.post("/api/v1/crypto/detokenize", json={
        "token": token,
        "authorization_key": "bank-soc-super-secret-key-2026"
    })
    assert resp_good.status_code == 200
    data = resp_good.json()
    assert data["plaintext_value"] == raw_val
    assert data["entity_type"] == "CREDIT_CARD"

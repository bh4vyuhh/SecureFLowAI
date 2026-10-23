"""
SecureFlow AI - Integration Tests for FastAPI Microservice Endpoints
================================================================================
File: ai-service/tests/test_endpoints.py
"""

import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "memory_usage_mb" in data
    assert "model_int8.onnx" in data["active_model"]


def test_classify_endpoint_safe():
    payload = {
        "text": "Hi team, please find attached the meeting minutes and room reservation for tomorrow."
    }
    response = client.post("/api/v1/dlp/classify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == "SAFE"
    assert data["confidence"] > 0.70
    assert data["latency_ms"] < 25.0


def test_classify_endpoint_confidential():
    payload = {
        "text": "Executive Treasury Memo: EBITDA margin projection of 24.2% with $42.5M in net income for Q4."
    }
    response = client.post("/api/v1/dlp/classify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == "CONFIDENTIAL"
    assert data["confidence"] > 0.70


def test_redact_endpoint_masking():
    payload = {
        "text": "Please process payment for John Doe using card 4530-8921-0043-9182 and SSN 010-71-6307.",
        "mode": "mask"
    }
    response = client.post("/api/v1/dlp/redact", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "[CARD_****9182]" in data["sanitized_text"]
    assert "[SSN_***-**-****]" in data["sanitized_text"]
    assert data["entity_count"] >= 2


def test_scan_endpoint_restricted_block():
    payload = {
        "text": "Wire transfer authorization: Card 4530892100439182, SSN 010-71-6307, IBAN GB82WEST12345698765432.",
        "mode": "mask"
    }
    response = client.post("/api/v1/dlp/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == "RESTRICTED"
    assert data["risk_score"] >= 80
    assert data["action"] == "BLOCK"
    assert "[CARD_****9182]" in data["sanitized_text"]


def test_scan_endpoint_file_upload():
    file_content = b"Confidential memo: Client Jane Doe SSN 010-71-6307 card 4530-8921-0043-9182"
    files = {
        "file": ("test_doc.txt", io.BytesIO(file_content), "text/plain")
    }
    data = {"mode": "mask"}
    response = client.post("/api/v1/dlp/scan", files=files, data=data)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["action"] == "BLOCK"
    assert "[CARD_****9182]" in res_data["sanitized_text"]


def test_redact_endpoint_tokenization():
    payload = {
        "text": "Payment for John Doe using card 4530-8921-0043-9182.",
        "mode": "tokenize"
    }
    response = client.post("/api/v1/dlp/redact", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "[TOKEN_" in data["sanitized_text"]
    assert "4530-8921-0043-9182" not in data["sanitized_text"]


def test_invalid_invoice_not_redacted():
    # 16-digit fake sequence failing Luhn must not be masked as a credit card
    payload = {
        "text": "Invoice ref 1234567890123456 and tracking 4532892100439183 for shipment.",
        "mode": "mask"
    }
    response = client.post("/api/v1/dlp/redact", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "1234567890123456" in data["sanitized_text"]
    assert "4532892100439183" in data["sanitized_text"]
    assert "[CARD_" not in data["sanitized_text"]


def test_long_document_sliding_window_escalation():
    # Page 1 & 2: 350 words of safe meeting agenda
    safe_page = "Our team scheduled an open quarterly review to discuss public conference dates and keynote speakers. " * 35
    # Page 3: Wire transfer data with sensitive IBAN and card
    leaked_page = " Wire transfer confirmation: Card 4530892100439182, SSN 010-71-6307, IBAN GB82WEST12345698765432."
    long_document = safe_page + leaked_page

    payload = {
        "text": long_document,
        "mode": "mask"
    }
    response = client.post("/api/v1/dlp/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Risk escalation should detect deep leak and classify as RESTRICTED + BLOCK
    assert data["tier"] == "RESTRICTED"
    assert data["action"] == "BLOCK"
    assert "[CARD_****9182]" in data["sanitized_text"]
    assert "[IBAN_GB****5432]" in data["sanitized_text"]


def test_benign_prompt_zero_entity_guard():
    # Conversational prompts and greetings must NEVER be blocked as confidential or restricted
    test_prompts = [
        "+ heloo how are you",
        "can you help me desing a simple css button",
        "How do I center a div in HTML and CSS?"
    ]
    for prompt in test_prompts:
        resp = client.post("/api/v1/dlp/scan", json={"text": prompt, "mode": "mask"})
        assert resp.status_code == 200
        res = resp.json()
        assert res["tier"] == "SAFE"
        assert res["action"] == "ALLOW"
        assert res["risk_score"] < 45
        assert res["threat_category"] == "BENIGN_BUSINESS_DATA"


def test_copilot_explainability_endpoints():
    # 1. Frameworks query
    r1 = client.post("/api/v1/soc/copilot/chat", json={"query": "What DLP compliance frameworks are enforced?"})
    assert r1.status_code == 200
    d1 = r1.json()
    assert "PCI-DSS" in d1["response"]
    assert "GDPR" in d1["response"]
    assert d1["reply"] is not None

    # 2. Cryptographic ledger query
    r2 = client.post("/api/v1/soc/copilot/chat", json={"query": "How does the SHA-256 tamperproof audit ledger work?"})
    assert r2.status_code == 200
    d2 = r2.json()
    assert "SHA-256" in d2["response"]
    assert d2["reply"] is not None


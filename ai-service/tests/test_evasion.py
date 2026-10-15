"""
SecureFlow AI - Tests for Adversarial Normalization & Anti-Evasion Hardening
================================================================================
File: ai-service/tests/test_evasion.py
"""

import pytest
import base64
from fastapi.testclient import TestClient
from app.main import app
from app.engine.normalizer import (
    strip_invisible_characters,
    normalize_homoglyphs,
    despace_digit_sequences,
    extract_and_decode_base64_payloads,
    normalize_adversarial_text
)

client = TestClient(app)


def test_zero_width_character_stripping():
    # Hidden zero-width spaces injected inside a card number
    evasive_text = "Card number is 4\u200B5\u200C3\u200D0\uFEFF8\u00AD92100439182."
    cleaned = strip_invisible_characters(evasive_text)
    assert "\u200b" not in cleaned
    assert "\u200c" not in cleaned
    assert "\ufeff" not in cleaned
    assert "4530892100439182" in cleaned


def test_homoglyph_normalization():
    # Russian/Cyrillic lookalike letters 'а', 'е', 'о', 'р'
    # "Customer" with Cyrillic 'о' and 'е'
    evasive_word = "Cust\u043Em\u0435r"
    normalized = normalize_homoglyphs(evasive_word)
    assert normalized == "Customer"


def test_despace_digit_sequences():
    # Spaced-out card number: "4 5 3 0   8 9 2 1   0 0 4 3   9 1 8 2"
    evasive_digits = "Please debit 4 5 3 0   8 9 2 1   0 0 4 3   9 1 8 2 for order."
    despaced = despace_digit_sequences(evasive_digits)
    assert "4530892100439182" in despaced


def test_base64_payload_extraction():
    # Base64 string of: "Restricted wire transfer card 4530892100439182"
    secret = "Restricted wire transfer card 4530892100439182"
    b64_str = base64.b64encode(secret.encode()).decode()
    carrier_text = f"Review standard config at payload {b64_str} and proceed."

    decoded = extract_and_decode_base64_payloads(carrier_text)
    assert len(decoded) >= 1
    assert "4530892100439182" in decoded[0]


def test_evasion_scan_endpoint_blocks_zero_width_attack():
    # Injected zero-width characters in credit card over REST API
    evasive_payload = {
        "text": "Transfer $50,000 to card 4\u200B5\u200C3\u200D0\uFEFF892100439182 immediately.",
        "mode": "mask"
    }
    response = client.post("/api/v1/dlp/scan", json=evasive_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "BLOCK"
    assert data["risk_score"] >= 80
    assert "[CARD_****9182]" in data["sanitized_text"]


def test_evasion_scan_endpoint_blocks_base64_leak():
    # Leaking card inside a base64 string
    secret = "Confidential payment auth for card 4530892100439182"
    b64_str = base64.b64encode(secret.encode()).decode()
    payload = {
        "text": f"System backup token: {b64_str}",
        "mode": "mask"
    }
    response = client.post("/api/v1/dlp/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "BLOCK"
    assert data["risk_score"] >= 80

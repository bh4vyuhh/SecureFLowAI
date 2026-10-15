"""
SecureFlow AI - Unit Tests for Span Conflict Resolution & Offset-Safe Redaction
================================================================================
File: ai-service/tests/test_redaction.py
"""

import re
from app.engine.resolver import resolve_entity_conflicts
from app.engine.redactor import redact_text, generate_hmac_token, generate_partial_mask


def test_span_conflict_resolution():
    """
    Simulates a conflict where spaCy flags index 10-18 as ORG, but regex flags
    index 10-26 as a verified CREDIT_CARD. The checksum rule must win.
    """
    conflicting_entities = [
        {"entity_type": "ORG", "start": 10, "end": 18, "value": "45328921", "confidence": 0.85},
        {"entity_type": "CREDIT_CARD", "start": 10, "end": 26, "value": "4532892100439182", "confidence": 1.0}
    ]
    resolved = resolve_entity_conflicts(conflicting_entities)
    assert len(resolved) == 1
    assert resolved[0]["entity_type"] == "CREDIT_CARD"
    assert resolved[0]["start"] == 10
    assert resolved[0]["end"] == 26


def test_redaction_offset_stability():
    """
    Tests that multiple entities in a single sentence are redacted without index drift,
    truncated characters, or misplaced masks.
    """
    text = "Account for Alice Smith with card 4532892100439182 and SSN 010-71-6307 located in New York."
    entities = [
        {"entity_type": "PERSON", "start": 12, "end": 23, "value": "Alice Smith", "confidence": 0.9},
        {"entity_type": "CREDIT_CARD", "start": 34, "end": 50, "value": "4532892100439182", "confidence": 1.0},
        {"entity_type": "US_SSN", "start": 59, "end": 70, "value": "010-71-6307", "confidence": 1.0},
        {"entity_type": "LOCATION", "start": 82, "end": 90, "value": "New York", "confidence": 0.9}
    ]

    sanitized, records = redact_text(text, entities, mode="mask")

    # Verify all expected masks are present
    assert "[PERSON_MASKED]" in sanitized
    assert "[CARD_****9182]" in sanitized
    assert "[SSN_***-**-****]" in sanitized
    assert "[LOCATION_MASKED]" in sanitized

    # Verify surrounding plaintext is strictly preserved
    assert sanitized.startswith("Account for [PERSON_MASKED] with card")
    assert "and SSN [SSN_***-**-****] located in [LOCATION_MASKED]." in sanitized


def test_tokenization_mode():
    """
    Tests deterministic reversible HMAC-SHA256 tokenization.
    """
    val = "4532892100439182"
    token1 = generate_hmac_token(val)
    token2 = generate_hmac_token(val)

    assert token1.startswith("[TOKEN_")
    assert token1.endswith("]")
    assert token1 == token2  # Deterministic for same value

    different_token = generate_hmac_token("9999888877776666")
    assert token1 != different_token

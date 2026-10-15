"""
SecureFlow AI - Unit Tests for Mathematical Checksum Rules
================================================================================
File: ai-service/tests/test_rules.py
"""

import pytest
from app.engine.rules import (
    validate_luhn,
    validate_iban,
    validate_aba_routing,
    validate_ssn,
    extract_rule_entities
)


# -----------------------------------------------------------------------------
# 1. Luhn Algorithm (Credit / Debit Cards) Tests
# -----------------------------------------------------------------------------
def test_luhn_valid_cards():
    # Valid Visa (Luhn pass, ends in 9182)
    assert validate_luhn("4530892100439182") is True
    # Valid Mastercard (Luhn pass)
    assert validate_luhn("5424 1801 2345 6789") is True
    # Valid Amex (15 digits)
    assert validate_luhn("378282246310005") is True


def test_luhn_invalid_invoices():
    # 16-digit fake sequence failing Luhn (e.g. invoice or tracking id)
    assert validate_luhn("4532892100439183") is False
    assert validate_luhn("1234567890123456") is False
    # Short sequences
    assert validate_luhn("12345678") is False


# -----------------------------------------------------------------------------
# 2. ISO 7064 MOD-97-10 (IBAN) Tests
# -----------------------------------------------------------------------------
def test_iban_valid():
    # Valid UK IBAN
    assert validate_iban("GB82 WEST 1234 5698 7654 32") is True
    # Valid German IBAN
    assert validate_iban("DE89370400440532013000") is True


def test_iban_invalid():
    # Corrupted check digits
    assert validate_iban("GB83 WEST 1234 5698 7654 32") is False
    assert validate_iban("DE00370400440532013000") is False
    assert validate_iban("NOTANIBAN123456") is False


# -----------------------------------------------------------------------------
# 3. Federal Reserve ABA Routing Tests
# -----------------------------------------------------------------------------
def test_aba_routing_valid():
    # Valid Fed routing number
    assert validate_aba_routing("021000021") is True  # Chase NY
    assert validate_aba_routing("121000358") is True  # Wells Fargo CA


def test_aba_routing_invalid():
    assert validate_aba_routing("021000022") is False
    assert validate_aba_routing("123456789") is False
    assert validate_aba_routing("12345") is False


# -----------------------------------------------------------------------------
# 4. US SSN Structural Tests
# -----------------------------------------------------------------------------
def test_ssn_valid():
    assert validate_ssn("010-71-6307") is True
    assert validate_ssn("123 45 6789") is True
    assert validate_ssn("789123456") is True


def test_ssn_invalid_prefixes():
    # Area 000, 666, 900+
    assert validate_ssn("000-45-6789") is False
    assert validate_ssn("666-45-6789") is False
    assert validate_ssn("950-45-6789") is False
    # Group 00
    assert validate_ssn("123-00-6789") is False
    # Serial 0000
    assert validate_ssn("123-45-0000") is False


# -----------------------------------------------------------------------------
# 5. Full Rule Entity Extractor Integration
# -----------------------------------------------------------------------------
def test_extract_rule_entities():
    dummy_key = "sk_" + "live_" + "FakeKeyForTesting12345678"
    text = (
        "Client Jane Doe transferred funds using Visa card 4530-8921-0043-9182, "
        "IBAN GB82WEST12345698765432, routing 021000021, and SSN 010-71-6307. "
        f"Also test Stripe token {dummy_key}."
    )
    entities = extract_rule_entities(text)
    types = [e["entity_type"] for e in entities]

    assert "CREDIT_CARD" in types
    assert "IBAN" in types
    assert "ABA_ROUTING" in types
    assert "US_SSN" in types
    assert "API_KEY" in types

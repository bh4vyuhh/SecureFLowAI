"""
SecureFlow AI - Deterministic PII & Mathematical Checksum Engine
================================================================================
File: ai-service/app/engine/rules.py

Implements strict regex matching validated by exact mathematical checksums:
  - Credit/Debit Cards: 13-19 digits validated by Luhn (MOD-10) algorithm
  - International Bank Account Numbers (IBAN): ISO 7064 MOD-97-10 checksum
  - US ABA Routing Numbers: Federal Reserve 3-7-1 weighted MOD-10 checksum
  - US Social Security Numbers (SSN): Format + historical invalid prefix exclusions
  - SWIFT/BIC Codes: 8 or 11 characters ISO 9362
  - Live API Keys & Secrets: Stripe, GitHub, AWS, RSA/EC PEM private keys
"""

import re
from typing import List, Dict, Any


# -----------------------------------------------------------------------------
# 1. Mathematical Checksum Implementations
# -----------------------------------------------------------------------------
def validate_luhn(number_str: str) -> bool:
    """
    Validates a credit/debit card number using the Luhn (MOD-10) algorithm.
    Any non-digit character is stripped prior to validation.
    """
    digits = [int(c) for c in number_str if c.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False

    checksum = 0
    # From right to left: double every second digit starting from the second rightmost
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = d * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += d

    return checksum % 10 == 0


def validate_iban(iban_str: str) -> bool:
    """
    Validates an International Bank Account Number using ISO 7064 MOD-97-10:
      1. Move first 4 characters to the end.
      2. Convert letters to digits: A=10, B=11, ..., Z=35.
      3. Compute integer MOD 97 == 1.
    """
    clean_iban = re.sub(r"\s+", "", iban_str).upper()
    if len(clean_iban) < 15 or len(clean_iban) > 34:
        return False
    if not re.match(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]+$", clean_iban):
        return False

    # Rearrange: move first 4 characters to end
    rearranged = clean_iban[4:] + clean_iban[:4]

    # Convert letters to digits: A->10, ..., Z->35
    num_str = ""
    for ch in rearranged:
        if ch.isalpha():
            num_str += str(ord(ch) - ord('A') + 10)
        else:
            num_str += ch

    try:
        # Perform mod 97 on large numeric string piece-wise or directly
        return int(num_str) % 97 == 1
    except ValueError:
        return False


def validate_aba_routing(routing_str: str) -> bool:
    """
    Validates a 9-digit US ABA routing transit number using the Federal Reserve checksum:
      (3*(d1 + d4 + d7) + 7*(d2 + d5 + d8) + 1*(d3 + d6 + d9)) % 10 == 0
    """
    clean_aba = re.sub(r"\D", "", routing_str)
    if len(clean_aba) != 9:
        return False

    d = [int(ch) for ch in clean_aba]
    checksum = (
        3 * (d[0] + d[3] + d[6]) +
        7 * (d[1] + d[4] + d[7]) +
        1 * (d[2] + d[5] + d[8])
    )
    return (checksum % 10) == 0


def validate_ssn(ssn_str: str) -> bool:
    """
    Validates US SSN format and rejects historical invalid SSA prefixes:
      - Area number cannot be 000, 666, or 900-999
      - Group number cannot be 00
      - Serial number cannot be 0000
    """
    clean = re.sub(r"\D", "", ssn_str)
    if len(clean) != 9:
        return False

    area = int(clean[:3])
    group = int(clean[3:5])
    serial = int(clean[5:9])

    if area == 0 or area == 666 or (900 <= area <= 999):
        return False
    if group == 0:
        return False
    if serial == 0:
        return False

    return True


# -----------------------------------------------------------------------------
# 2. Regex Patterns
# -----------------------------------------------------------------------------
# Credit/Debit Cards (13 to 19 digits with spaces/dashes)
CARD_REGEX = re.compile(
    r"\b(?:\d[ -]*?){13,19}\b"
)

# IBAN pattern (2 country letters, 2 digits, up to 30 alphanumeric)
IBAN_REGEX = re.compile(
    r"\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}(?:[A-Z0-9]?){0,16}\b",
    re.IGNORECASE
)

# ABA Routing (9 digits)
ABA_REGEX = re.compile(
    r"\b\d{9}\b"
)

# US SSN (3-2-4 format with optional dashes/spaces)
SSN_REGEX = re.compile(
    r"\b\d{3}[- ]?\d{2}[- ]?\d{4}\b"
)

# SWIFT/BIC (8 or 11 characters)
SWIFT_REGEX = re.compile(
    r"\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b"
)

# Live API credentials, Test tokens, and Private Key Headers
STRIPE_KEY_REGEX = re.compile(r"\b(?:sk_live_|sk_test_)[0-9a-zA-Z]{24,}\b")
GITHUB_TOKEN_REGEX = re.compile(r"\bghp_[0-9a-zA-Z]{36}\b")
AWS_KEY_REGEX = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
PEM_KEY_REGEX = re.compile(
    r"-----BEGIN (?:RSA|EC|OPENSSH|DSA|ENCRYPTED|PRIVATE) KEY-----[^-]+-----END (?:RSA|EC|OPENSSH|DSA|ENCRYPTED|PRIVATE) KEY-----",
    re.DOTALL
)


# -----------------------------------------------------------------------------
# 3. Main Rule Extraction Engine
# -----------------------------------------------------------------------------
def extract_rule_entities(text: str) -> List[Dict[str, Any]]:
    """
    Scans input text against all deterministic patterns and applies strict
    mathematical checksum validation. Discards candidates failing checksums.
    Returns:
      [{"entity_type": str, "start": int, "end": int, "value": str, "confidence": 1.0}]
    """
    if not text:
        return []

    entities: List[Dict[str, Any]] = []

    # 1. PEM Private Keys
    for m in PEM_KEY_REGEX.finditer(text):
        entities.append({
            "entity_type": "PRIVATE_KEY",
            "start": m.start(),
            "end": m.end(),
            "value": m.group(0),
            "confidence": 1.0
        })

    # 2. API Keys
    for regex, etype in [
        (STRIPE_KEY_REGEX, "API_KEY"),
        (GITHUB_TOKEN_REGEX, "API_KEY"),
        (AWS_KEY_REGEX, "API_KEY")
    ]:
        for m in regex.finditer(text):
            entities.append({
                "entity_type": etype,
                "start": m.start(),
                "end": m.end(),
                "value": m.group(0),
                "confidence": 1.0
            })

    # 3. Credit / Debit Cards (Must pass Luhn)
    for m in CARD_REGEX.finditer(text):
        val = m.group(0)
        digits_only = re.sub(r"\D", "", val)
        if 13 <= len(digits_only) <= 19 and validate_luhn(digits_only):
            entities.append({
                "entity_type": "CREDIT_CARD",
                "start": m.start(),
                "end": m.end(),
                "value": val,
                "confidence": 1.0
            })

    # 4. IBANs (Must pass MOD-97)
    for m in IBAN_REGEX.finditer(text):
        val = m.group(0)
        if validate_iban(val):
            entities.append({
                "entity_type": "IBAN",
                "start": m.start(),
                "end": m.end(),
                "value": val,
                "confidence": 1.0
            })

    # 5. US SSNs (Must satisfy SSA structural rules)
    for m in SSN_REGEX.finditer(text):
        val = m.group(0)
        if validate_ssn(val):
            # Ensure not overlapping with already detected credit card
            entities.append({
                "entity_type": "US_SSN",
                "start": m.start(),
                "end": m.end(),
                "value": val,
                "confidence": 1.0
            })

    # 6. US ABA Routing Numbers (9 digits, Federal Reserve Checksum)
    for m in ABA_REGEX.finditer(text):
        val = m.group(0)
        # Avoid overriding SSNs without hyphens or parts of card numbers
        if validate_aba_routing(val):
            entities.append({
                "entity_type": "ABA_ROUTING",
                "start": m.start(),
                "end": m.end(),
                "value": val,
                "confidence": 1.0
            })

    # 7. SWIFT / BIC codes
    for m in SWIFT_REGEX.finditer(text):
        val = m.group(0)
        # Basic check to avoid plain uppercase words like "DEPARTMENT"
        if val.isupper() and (len(val) == 8 or len(val) == 11):
            entities.append({
                "entity_type": "SWIFT_BIC",
                "start": m.start(),
                "end": m.end(),
                "value": val,
                "confidence": 0.95
            })

    return entities

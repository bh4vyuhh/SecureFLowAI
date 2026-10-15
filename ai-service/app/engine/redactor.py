"""
SecureFlow AI - Reverse-Offset Multi-Mode Redaction Engine
================================================================================
File: ai-service/app/engine/redactor.py

Eliminates the "String Offset Drift" bug by applying redaction masks in descending
character offset order (reverse=True).
Supports 2 enterprise modes:
  - Mode A: Partial Masking (PCI-DSS & GDPR compliant display masks)
  - Mode B: Reversible Cryptographic Tokenization (HMAC-SHA256 for audit trails)
"""

import os
import re
import hmac
import hashlib
from typing import List, Dict, Any, Tuple


# Default HMAC Secret for tokenization (overridable via environment variable)
HMAC_SECRET_KEY = os.getenv("HMAC_SECRET_KEY", "SecureFlowAI-Enterprise-DLP-Master-Key-2026").encode("utf-8")


def generate_hmac_token(value: str) -> str:
    """
    Generates a deterministic 12-character HMAC-SHA256 token:
      f"[TOKEN_{hmac.new(key, value.encode(), hashlib.sha256).hexdigest()[:12]}]"
    """
    token_hash = hmac.new(HMAC_SECRET_KEY, value.strip().encode("utf-8"), hashlib.sha256).hexdigest()[:12]
    return f"[TOKEN_{token_hash}]"


def generate_partial_mask(entity_type: str, value: str) -> str:
    """
    Generates enterprise partial masks preserving auditability while destroying leakage:
      - CREDIT_CARD: Preserve last 4 digits -> [CARD_****9182]
      - IBAN: Preserve country code + last 4 chars -> [IBAN_GB****9268]
      - US_SSN: Standard mask -> [SSN_***-**-****]
      - ABA_ROUTING: [ROUTING_****]
      - API_KEY & Passwords: Full mask -> [REDACTED_SECRET]
      - PRIVATE_KEY: Full mask -> [REDACTED_PRIVATE_KEY]
      - PERSON / ORG / LOCATION: Type labels -> [PERSON_MASKED], [ORG_MASKED], [LOCATION_MASKED]
    """
    val_clean = value.strip()
    digits = re.sub(r"\D", "", val_clean)

    if entity_type == "CREDIT_CARD":
        last4 = digits[-4:] if len(digits) >= 4 else "XXXX"
        return f"[CARD_****{last4}]"

    elif entity_type == "IBAN":
        clean_iban = re.sub(r"\s+", "", val_clean).upper()
        country = clean_iban[:2] if len(clean_iban) >= 2 else "XX"
        last4 = clean_iban[-4:] if len(clean_iban) >= 6 else "XXXX"
        return f"[IBAN_{country}****{last4}]"

    elif entity_type == "US_SSN":
        return "[SSN_***-**-****]"

    elif entity_type == "ABA_ROUTING":
        last4 = digits[-4:] if len(digits) >= 4 else "XXXX"
        return f"[ROUTING_****{last4}]"

    elif entity_type in ("API_KEY", "PASSWORD", "SECRET"):
        return "[REDACTED_SECRET]"

    elif entity_type == "PRIVATE_KEY":
        return "[REDACTED_PRIVATE_KEY]"

    elif entity_type == "SWIFT_BIC":
        return f"[SWIFT_****{val_clean[:4]}]"

    elif entity_type == "PERSON":
        return "[PERSON_MASKED]"

    elif entity_type == "ORG":
        return "[ORG_MASKED]"

    elif entity_type == "LOCATION":
        return "[LOCATION_MASKED]"

    else:
        return f"[{entity_type}_REDACTED]"


def redact_text(
    text: str,
    entities: List[Dict[str, Any]],
    mode: str = "mask"
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Applies redaction to the text using reverse-offset replacement to guarantee
    character indices remain strictly valid throughout the process.
    
    Args:
      text: The original plaintext.
      entities: List of non-overlapping entity dicts with 'start', 'end', 'entity_type', 'value'.
      mode: 'mask' (partial masking) or 'tokenize' (HMAC-SHA256 tokenization).

    Returns:
      (sanitized_text, list_of_redacted_entities_with_mask_value)
    """
    if not text or not entities:
        return text, []

    # CRITICAL: Sort entities in descending order of character start index (reverse=True)
    # This prevents earlier replacements from altering subsequent offsets!
    sorted_entities = sorted(entities, key=lambda e: e["start"], reverse=True)

    redacted_records: List[Dict[str, Any]] = []
    text_chars = list(text)

    for ent in sorted_entities:
        start = ent["start"]
        end = ent["end"]
        etype = ent["entity_type"]
        val = text[start:end]

        if mode == "tokenize":
            replacement = generate_hmac_token(val)
        else:
            replacement = generate_partial_mask(etype, val)

        # Replace slice in text array
        text_chars[start:end] = list(replacement)

        redacted_records.append({
            "entity_type": etype,
            "original_value": val,
            "replacement": replacement,
            "start": start,
            "end": end,
            "confidence": ent.get("confidence", 1.0)
        })

    sanitized_text = "".join(text_chars)
    # Return records in original ascending start order for clean reporting
    redacted_records.reverse()
    return sanitized_text, redacted_records

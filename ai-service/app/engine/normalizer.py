"""
SecureFlow AI - Adversarial Normalization & Anti-Evasion Engine
================================================================================
File: ai-service/app/engine/normalizer.py

Hardens the DLP inspection engine against common evasion vectors:
  1. Zero-Width & Invisible Unicode Characters (\u200B, \u200C, \u200D, \uFEFF, \u00AD, etc.)
  2. Homoglyph / Confusable Character Substitution (Cyrillic, Greek, Fullwidth)
  3. Spaced-Out & Punctuation-Interrupted Digit Sequences (e.g. "4 5 3 0 . 8 9 2 1")
  4. Base64-Encoded Payloads (e.g. encoded credentials or financial numbers)
"""

import re
import base64
import unicodedata
from typing import Tuple, List, Dict, Any

# Invisible & Zero-Width Unicode Characters
ZERO_WIDTH_CHARS = [
    "\u200b",  # Zero-width space
    "\u200c",  # Zero-width non-joiner
    "\u200d",  # Zero-width joiner
    "\ufeff",  # Zero-width no-break space (BOM)
    "\u00ad",  # Soft hyphen
    "\u2060",  # Word joiner
    "\u200e",  # Left-to-right mark
    "\u200f",  # Right-to-left mark
    "\u202a",  # Left-to-right embedding
    "\u202b",  # Right-to-left embedding
    "\u202c",  # Pop directional formatting
    "\u202d",  # Left-to-right override
    "\u202e",  # Right-to-left override
]
ZERO_WIDTH_PATTERN = re.compile("|".join(re.escape(c) for c in ZERO_WIDTH_CHARS))

# Common Cyrillic & Latin Lookalike Homoglyphs used in evasion
HOMOGLYPH_MAP = {
    # Lowercase
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x", "і": "i",
    "ј": "j", "ѕ": "s", "ԁ": "d", "ԛ": "q", "ԝ": "w",
    # Uppercase
    "А": "A", "В": "B", "Е": "E", "К": "K", "М": "H", "Н": "H", "О": "O", "Р": "P",
    "С": "C", "Т": "T", "Х": "X", "І": "I", "Ј": "J", "Ѕ": "S"
}
HOMOGLYPH_TRANSLATION = str.maketrans(HOMOGLYPH_MAP)

# Base64 pattern (minimum 16 characters = at least 12 decoded bytes)
BASE64_PATTERN = re.compile(r"(?:[A-Za-z0-9+/]{4}){4,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4})")



def strip_invisible_characters(text: str) -> str:
    """Removes all zero-width, non-printing, and directional override unicode characters."""
    if not text:
        return ""
    return ZERO_WIDTH_PATTERN.sub("", text)


def normalize_homoglyphs(text: str) -> str:
    """
    Normalizes fullwidth characters to standard ASCII and replaces common
    Cyrillic lookalike homoglyphs with standard Latin equivalents.
    """
    if not text:
        return ""
    # Unicode NFKD decomposition transforms fullwidth characters (e.g. ０-９) into standard ASCII
    normalized = unicodedata.normalize("NFKD", text)
    # Translate Cyrillic homoglyphs
    return normalized.translate(HOMOGLYPH_TRANSLATION)


def despace_digit_sequences(text: str) -> str:
    """
    Identifies digit sequences that have been deliberately spaced or punctuated to evade regex.
    Example: '4 5 3 0   8 9 2 1   0 0 4 3   9 1 8 2' -> '4530892100439182'
    Replaces spaced digit blocks of >= 9 digits with their consolidated equivalent.
    """
    if not text:
        return ""

    # Matches 9 to 19 single digits separated by spaces, dots, or underscores
    # e.g., "4 . 5 . 3 . 0" or "4 5 3 0 8 9 2 1"
    spaced_digits_pattern = re.compile(r"\b(?:\d[\s\._]+){8,18}\d\b")

    def _compact_match(match: re.Match) -> str:
        s = match.group(0)
        digits_only = re.sub(r"[\s\._]", "", s)
        if len(digits_only) >= 9:
            return digits_only
        return s

    return spaced_digits_pattern.sub(_compact_match, text)


def extract_and_decode_base64_payloads(text: str) -> List[str]:
    """
    Finds potential base64 strings, decodes valid ASCII/UTF-8 payloads,
    and returns decoded plaintext snippets.
    """
    if not text:
        return []

    decoded_payloads = []
    candidates = BASE64_PATTERN.findall(text)

    for cand in candidates:
        try:
            raw_bytes = base64.b64decode(cand, validate=True)
            # Check if decoded payload is printable text
            decoded_str = raw_bytes.decode("utf-8", errors="strict").strip()
            # Only consider if it has meaningful printable characters
            if len(decoded_str) >= 6 and all(c.isprintable() or c in "\r\n\t " for c in decoded_str):
                decoded_payloads.append(decoded_str)
        except Exception:
            continue

    return decoded_payloads


def normalize_adversarial_text(text: str) -> Tuple[str, List[str]]:
    """
    Full pipeline adversarial normalization:
      1. Strips zero-width invisible unicode.
      2. Normalizes homoglyphs & fullwidth unicode.
      3. Reconstructs spaced/punctuated digit sequences.
      4. Decodes base64 payload strings and appends them for deep inspection.
    Returns:
      (canonical_text, list_of_decoded_base64_payloads)
    """
    if not text:
        return "", []

    # 1. Strip invisible characters
    cleaned = strip_invisible_characters(text)

    # 2. Homoglyph normalization
    cleaned = normalize_homoglyphs(cleaned)

    # 3. Check for base64 encoded secrets
    b64_payloads = extract_and_decode_base64_payloads(cleaned)

    # 4. Despace digit sequences
    despaced = despace_digit_sequences(cleaned)

    return despaced, b64_payloads

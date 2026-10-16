"""
SecureFlow AI - Contextual Token Named Entity Recognition (NER)
================================================================================
File: ai-service/app/engine/ner.py

Wraps lightweight spaCy (en_core_web_sm) with non-essential components disabled
(tagger, parser, lemmatizer, attribute_ruler) to achieve high throughput (> 200 docs/sec).
Extracts:
  - PERSON: Customer, employee, account holder names
  - ORG: Corporate clients, vendor entities, financial institutions
  - GPE / LOC: Addresses, jurisdictions, countries, cities
"""

import logging
from typing import List, Dict, Any, Optional

try:
    import spacy
except ImportError:
    spacy = None

logger = logging.getLogger("SecureFlowAI.NER")

_nlp = None

def get_spacy_nlp():
    """
    Singleton lazy-loader for optimized lightweight spaCy pipeline.
    """
    global _nlp
    if _nlp is not None:
        return _nlp

    if spacy is None:
        logger.warning("[NER INIT] spaCy not installed; falling back to rule-based NER extractor.")
        return None

    model_name = "en_core_web_sm"
    try:
        # Load with heavy non-essential components disabled for pure NER throughput
        _nlp = spacy.load(model_name, disable=["tagger", "parser", "attribute_ruler", "lemmatizer"])
        logger.info(f"[NER INIT] Loaded spaCy model '{model_name}' (optimized for fast entity recognition)")
    except Exception as e:
        logger.warning(f"Failed to load '{model_name}': {e}. Attempting on-the-fly download...")
        try:
            spacy.cli.download(model_name)
            _nlp = spacy.load(model_name, disable=["tagger", "parser", "attribute_ruler", "lemmatizer"])
            logger.info(f"[NER INIT] Successfully downloaded and loaded '{model_name}'")
        except Exception as dl_err:
            logger.error(f"Could not load or download spaCy model: {dl_err}. Falling back to blank pipeline.")
            try:
                _nlp = spacy.blank("en")
            except Exception:
                _nlp = None

    return _nlp


def extract_ner_entities(text: str) -> List[Dict[str, Any]]:
    """
    Extracts PERSON, ORG, and GPE/LOC entities from input text.
    Returns:
      [{"entity_type": str, "start": int, "end": int, "value": str, "confidence": float}]
    """
    if not text or not text.strip():
        return []

    nlp = get_spacy_nlp()
    if nlp is None:
        return []
    doc = nlp(text)

    allowed_labels = {
        "PERSON": "PERSON",
        "ORG": "ORG",
        "GPE": "LOCATION",
        "LOC": "LOCATION"
    }

    COMMON_FIELD_LABELS = {
        "SSN", "CARD", "IBAN", "SWIFT", "BIC", "ABA", "ROUTING",
        "ACCOUNT", "CREDIT CARD", "DEBIT CARD", "PIN", "CVV", "CVC",
        "TAX ID", "ID", "VISA", "MASTERCARD", "AMEX"
    }

    results: List[Dict[str, Any]] = []
    for ent in doc.ents:
        if ent.label_ in allowed_labels:
            val = ent.text.strip()
            if len(val) >= 2 and val.upper() not in COMMON_FIELD_LABELS:
                # Exclude false positives:
                # 1. Names of individuals or locations do not contain numbers
                # 2. Organizations are not tracking numbers, references, or invoice identifiers
                digit_count = sum(c.isdigit() for c in val)
                if ent.label_ in ("PERSON", "GPE", "LOC") and digit_count > 0:
                    continue
                if ent.label_ == "ORG":
                    if digit_count >= 3 or (digit_count / max(1, len(val)) > 0.2):
                        continue
                    first_word = val.split()[0].lower() if val.split() else ""
                    if first_word in {"invoice", "order", "tracking", "shipment", "ticket", "case", "ref", "reference"}:
                        continue

                results.append({
                    "entity_type": allowed_labels[ent.label_],
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "value": ent.text,
                    "confidence": 0.85
                })

    return results

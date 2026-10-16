"""
SecureFlow AI - Hybrid Neural & Deterministic DLP Engine Adapter
================================================================================
File: ai-service/app/engine/hybrid_engine.py

Adapter B: Production Hybrid Engine implementing IDLPEngine.
Combines:
  1. Sliding-Window INT8 ONNX Transformer (Macro semantic intent)
  2. Pure Mathematical Checksums (Luhn, MOD-97, Fed ABA, US SSN)
  3. Contextual Token NER (Customer, Partner Institutions, Locations)
  4. Greedy Interval Conflict Resolver (Zero drift)
  5. Reverse-Offset Redaction (Masking & HMAC-SHA256 Tokenization)
"""

import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from .interfaces import IDLPEngine, DetectionResult, EntitySpan
from .classifier import SlidingWindowClassifier
from .rules import extract_rule_entities
from .ner import extract_ner_entities
from .resolver import resolve_entity_conflicts
from .redactor import redact_text
from .normalizer import normalize_adversarial_text


class HybridDLPEngine(IDLPEngine):
    """
    Enterprise-grade Hybrid Neural + Deterministic Engine.
    Delivers semantic document understanding paired with mathematical precision.
    """

    def __init__(self, models_dir: Optional[Path] = None, name: str = "Hybrid-ONNX-INT8-Engine"):
        self.name = name
        if models_dir is None:
            # Default to ../models
            current_dir = Path(__file__).resolve().parent
            ai_service_dir = current_dir.parent.parent
            models_dir = ai_service_dir / "models"
        self.models_dir = Path(models_dir)
        self.classifier = SlidingWindowClassifier(self.models_dir)

    def classify(self, text: str) -> Dict[str, Any]:
        normalized_text, _ = normalize_adversarial_text(text)
        return self.classifier.classify(normalized_text)

    def scan(self, text: str, mode: str = "mask", context: Optional[Dict[str, Any]] = None) -> DetectionResult:
        t0 = time.perf_counter()

        # 1. Adversarial Normalization
        normalized_text, b64_payloads = normalize_adversarial_text(text)
        inspection_text = normalized_text
        if b64_payloads:
            inspection_text = inspection_text + "\n" + "\n".join(b64_payloads)

        # 2. Sliding-Window Neural Classification
        cls_result = self.classifier.classify(inspection_text)
        tier = cls_result["tier"]
        confidence = cls_result["confidence"]

        # 3. Deterministic Rule Extraction
        rule_ents = extract_rule_entities(inspection_text)

        # 4. Contextual Token NER
        ner_ents = extract_ner_entities(inspection_text)

        # 5. Span Conflict Resolution (Priority: Rules > Credentials > NER)
        resolved_ents = resolve_entity_conflicts(rule_ents + ner_ents)

        # 6. Reverse-Offset Redaction
        sanitized, redacted_records = redact_text(normalized_text, resolved_ents, mode=mode)

        # 7. Unified Risk Decision
        critical_types = {"CREDIT_CARD", "PRIVATE_KEY", "API_KEY", "US_SSN"}
        has_critical = any(e["entity_type"] in critical_types for e in resolved_ents)
        financial_identifiers = {"IBAN", "ABA_ROUTING", "SWIFT_BIC"}
        has_financial = any(e["entity_type"] in financial_identifiers for e in resolved_ents)

        if tier == "RESTRICTED":
            base_score = 75 if (has_critical or has_financial) else 30
        elif tier == "CONFIDENTIAL":
            base_score = 50
        else:
            base_score = 10

        weights = {
            "CREDIT_CARD": 35, "PRIVATE_KEY": 40, "API_KEY": 30, "US_SSN": 30,
            "IBAN": 25, "ABA_ROUTING": 20, "SWIFT_BIC": 15,
            "PERSON": 3, "ORG": 3, "LOCATION": 2
        }
        entity_impact = sum(weights.get(e["entity_type"], 2) for e in resolved_ents)
        total_risk = min(100, base_score + entity_impact)

        # Policy Enforcement Decision:
        # BLOCK: If critical secrets exist (Cards, Keys, SSN) OR total risk >= 80
        # ENCRYPT / MASK: If total risk >= 45 OR financial identifiers detected
        # ALLOW: Normal documents without sensitive leaks
        if has_critical or total_risk >= 80:
            action = "BLOCK"
            total_risk = max(total_risk, 85)
        elif total_risk >= 45 or has_financial or tier == "CONFIDENTIAL":
            action = "ENCRYPT"
        else:
            action = "ALLOW"

        duration_ms = (time.perf_counter() - t0) * 1000.0

        entity_spans = [
            EntitySpan(
                entity_type=r["entity_type"],
                start=r["start"],
                end=r["end"],
                value=None,  # Zero-leak policy
                replacement=r["replacement"],
                confidence=r["confidence"]
            )
            for r in redacted_records
        ]

        return DetectionResult(
            tier=tier,
            risk_score=total_risk,
            action=action,
            entities=entity_spans,
            confidence=confidence,
            sanitized_text=sanitized,
            latency_ms=round(duration_ms, 2),
            engine_name=self.name,
            metadata={
                "probabilities": cls_result.get("probabilities", {}),
                "num_chunks": cls_result.get("num_chunks", 1),
                "entity_count": len(resolved_ents)
            }
        )

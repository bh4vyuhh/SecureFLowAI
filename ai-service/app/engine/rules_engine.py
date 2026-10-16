"""
SecureFlow AI - Rule-Based DLP Engine Adapter
================================================================================
File: ai-service/app/engine/rules_engine.py

Adapter A: Ultra-fast (< 2ms) deterministic baseline engine implementing IDLPEngine.
Uses mathematical checksums (Luhn, MOD-97, Fed ABA, US SSN) and regex without
requiring ONNX Runtime or neural network dependencies.
"""

import time
from typing import Dict, Any, Optional, List
from .interfaces import IDLPEngine, DetectionResult, EntitySpan
from .rules import extract_rule_entities
from .resolver import resolve_entity_conflicts
from .redactor import redact_text
from .normalizer import normalize_adversarial_text


class RuleBasedDLPEngine(IDLPEngine):
    """
    Fast, deterministic rule-based engine adapter.
    Ideal for low-resource environments, ultra-low latency routing, or fallback mode.
    """

    def __init__(self, name: str = "RuleBased-Engine-v1"):
        self.name = name

    def classify(self, text: str) -> Dict[str, Any]:
        t0 = time.perf_counter()
        normalized_text, _ = normalize_adversarial_text(text)
        rule_ents = extract_rule_entities(normalized_text)

        critical_types = {"CREDIT_CARD", "PRIVATE_KEY", "API_KEY", "US_SSN"}
        has_critical = any(e["entity_type"] in critical_types for e in rule_ents)
        has_any_pii = len(rule_ents) > 0

        if has_critical:
            tier = "RESTRICTED"
            confidence = 0.99
        elif has_any_pii:
            tier = "CONFIDENTIAL"
            confidence = 0.90
        else:
            tier = "SAFE"
            confidence = 0.85

        duration_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "tier": tier,
            "confidence": confidence,
            "probabilities": {
                "SAFE": 0.85 if tier == "SAFE" else 0.05,
                "CONFIDENTIAL": 0.90 if tier == "CONFIDENTIAL" else 0.05,
                "RESTRICTED": 0.99 if tier == "RESTRICTED" else 0.05
            },
            "num_chunks": 1,
            "latency_ms": round(duration_ms, 2)
        }

    def scan(self, text: str, mode: str = "mask", context: Optional[Dict[str, Any]] = None) -> DetectionResult:
        t0 = time.perf_counter()
        normalized_text, b64_payloads = normalize_adversarial_text(text)
        inspection_text = normalized_text
        if b64_payloads:
            inspection_text = inspection_text + "\n" + "\n".join(b64_payloads)

        # 1. Deterministic Rule Extraction
        rule_ents = extract_rule_entities(inspection_text)

        # 2. Span Conflict Resolution
        resolved_ents = resolve_entity_conflicts(rule_ents)

        # 3. Reverse-Offset Redaction
        sanitized, redacted_records = redact_text(normalized_text, resolved_ents, mode=mode)

        # 4. Risk Decision
        critical_types = {"CREDIT_CARD", "PRIVATE_KEY", "API_KEY", "US_SSN"}
        has_critical = any(e["entity_type"] in critical_types for e in resolved_ents)

        weights = {
            "CREDIT_CARD": 30, "PRIVATE_KEY": 35, "API_KEY": 25, "US_SSN": 25,
            "IBAN": 15, "ABA_ROUTING": 15, "SWIFT_BIC": 10
        }
        total_risk = min(100, sum(weights.get(e["entity_type"], 10) for e in resolved_ents))

        if has_critical or total_risk >= 80:
            tier = "RESTRICTED"
            action = "BLOCK"
            total_risk = max(total_risk, 80)
        elif total_risk >= 45:
            tier = "CONFIDENTIAL"
            action = "ENCRYPT"
        else:
            tier = "SAFE"
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
            confidence=0.99 if has_critical else 0.85,
            sanitized_text=sanitized,
            latency_ms=round(duration_ms, 2),
            engine_name=self.name,
            metadata={"rule_count": len(resolved_ents)}
        )

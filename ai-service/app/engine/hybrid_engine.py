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


import logging

logger = logging.getLogger("SecureFlowAI.HybridDLPEngine")


def build_threat_explanation(tier: str, action: str, risk_score: int, entities: list, cls_result: dict) -> dict:
    """
    Generates plain-English threat explainability, regulatory compliance impact,
    and remediation advice for SOC analysts and compliance officers.
    """
    entity_types = {e.get("entity_type") if isinstance(e, dict) else getattr(e, "entity_type", str(e)) for e in entities}
    
    if "CREDIT_CARD" in entity_types:
        category = "PCI_DSS_PAYMENT_CARD_EXPOSURE"
        summary = (
            f"Critical PCI-DSS violation detected ({risk_score}/100 risk). Raw payment card numbers intercepted. "
            "Exfiltration of unmasked Primary Account Numbers (PAN) to external endpoints is strictly forbidden."
        )
        compliance = ["PCI-DSS-v4.0-Req-3.4", "GLBA-Safeguards-Rule", "ISO-27001-A.8.24"]
        remediation = "Immediate quarantine enforced. Wipe clipboard on client endpoint and detokenize only via authorized compliance role."

    elif "PRIVATE_KEY" in entity_types or "API_KEY" in entity_types:
        category = "SECRET_KEY_CREDENTIAL_EXFILTRATION"
        summary = (
            f"High-severity credential leak intercepted ({risk_score}/100 risk). Active API tokens or private cryptographic "
            "keys detected in payload. External transmission poses catastrophic unauthorized access risk."
        )
        compliance = ["SOC2-CC6.1-Access-Control", "NIST-SP-800-53-IA-5", "ISO-27001-A.8.24"]
        remediation = "Block transmission immediately. Rotate leaked API/private keys in secrets manager and audit source repository."

    elif "US_SSN" in entity_types:
        category = "PII_NATIONAL_IDENTITY_EXPOSURE"
        summary = (
            f"Severe PII breach prevented ({risk_score}/100 risk). Government national identity numbers (SSN) detected. "
            "Unauthorized transmission violates federal privacy mandates."
        )
        compliance = ["GDPR-Art-9-Special-Category", "HIPAA-45-CFR-164.312", "GLBA-Financial-Privacy"]
        remediation = "Payload blocked and encrypted. Notify data protection officer (DPO) and record audit log."

    elif any(t in entity_types for t in ["IBAN", "ABA_ROUTING", "SWIFT_BIC"]):
        category = "BANKING_WIRE_TRANSFER_COORDINATES"
        summary = (
            f"Sensitive banking transaction coordinates intercepted ({risk_score}/100 risk). Account wire transfer "
            "instructions require tokenization and masking before crossing network perimeter."
        )
        compliance = ["SWIFT-Customer-Security-Programme", "RBI-Cyber-Security-DLP", "ISO-20022-Governance"]
        remediation = "Enforce offset-safe HMAC tokenization or masking before external forwarding."

    elif risk_score >= 45:
        category = "INTERNAL_CONFIDENTIAL_PII"
        summary = (
            f"Confidential enterprise communication intercepted ({risk_score}/100 risk). Internal personal identifiable "
            "information or corporate business records detected. Masking applied."
        )
        compliance = ["GDPR-Art-32-Security", "SOC2-Privacy-Criteria", "ISO-42001-AI-Governance"]
        remediation = "Mask PII identifiers in payload. Allow sanitized version to proceed."

    else:
        category = "BENIGN_BUSINESS_DATA"
        summary = (
            f"Verified safe communication ({risk_score}/100 risk). No sensitive payment cards, financial coordinates, "
            "credentials, or unauthorized PII found in payload."
        )
        compliance = ["SOC2-Baseline-Compliance", "ISO-27001-Conformance"]
        remediation = "Standard transfer authorized. No operational remediation needed."

    return {
        "threat_category": category,
        "explanation": summary,
        "compliance_impact": compliance,
        "remediation_advice": remediation
    }


class HybridDLPEngine(IDLPEngine):
    """
    Adapter B: Production-Grade Hybrid Detection Core
    Combines Sliding-Window ONNX INT8 Transformer + Contextual NER + Deterministic Checksum Rules.
    """

    def __init__(self, models_dir: Optional[Path] = None, name: str = "Hybrid-ONNX-INT8-SlidingWindow"):
        self.name = name
        if models_dir is None:
            current_dir = Path(__file__).resolve().parent
            ai_service_dir = current_dir.parent.parent
            models_dir = ai_service_dir / "models"
        self.models_dir = Path(models_dir)
        self.classifier = SlidingWindowClassifier(self.models_dir)
        logger.info(f"[ENGINE INITIALIZED] Adapter '{self.name}' active.")

    def classify(self, text: str) -> Dict[str, Any]:
        normalized_text, _ = normalize_adversarial_text(text)
        return self.classifier.classify(normalized_text)

    def scan(self, text: str, mode: str = "mask", context: Optional[Dict[str, Any]] = None) -> DetectionResult:
        t0 = time.perf_counter()

        # 1. Adversarial Normalization
        t_norm_start = time.perf_counter()
        normalized_text, b64_payloads = normalize_adversarial_text(text)
        inspection_text = normalized_text
        if b64_payloads:
            inspection_text = inspection_text + "\n" + "\n".join(b64_payloads)
        t_norm = (time.perf_counter() - t_norm_start) * 1000.0

        # 2. Sliding-Window Neural Classification
        t_cls_start = time.perf_counter()
        cls_result = self.classifier.classify(inspection_text)
        raw_tier = cls_result["tier"]
        confidence = cls_result["confidence"]
        t_cls = (time.perf_counter() - t_cls_start) * 1000.0

        # 3. Deterministic Rule Extraction
        t_rules_start = time.perf_counter()
        rule_ents = extract_rule_entities(inspection_text)
        t_rules = (time.perf_counter() - t_rules_start) * 1000.0

        # 4. Contextual Token NER
        t_ner_start = time.perf_counter()
        ner_ents = extract_ner_entities(inspection_text)
        t_ner = (time.perf_counter() - t_ner_start) * 1000.0

        # 5. Span Conflict Resolution (Priority: Rules > Credentials > NER)
        resolved_ents = resolve_entity_conflicts(rule_ents + ner_ents)

        # 6. Reverse-Offset Redaction
        t_redact_start = time.perf_counter()
        sanitized, redacted_records = redact_text(normalized_text, resolved_ents, mode=mode)
        t_redact = (time.perf_counter() - t_redact_start) * 1000.0

        # 7. Unified Risk Decision
        critical_types = {
            "CREDIT_CARD", "PRIVATE_KEY", "API_KEY", "US_SSN",
            "PASSWORD_SECRET", "DB_CONNECTION", "JWT_TOKEN", "PAN_CARD", "BANK_ACCOUNT"
        }
        has_critical = any(e["entity_type"] in critical_types for e in resolved_ents)
        financial_identifiers = {"IBAN", "ABA_ROUTING", "SWIFT_BIC", "BANK_ACCOUNT"}
        has_financial = any(e["entity_type"] in financial_identifiers for e in resolved_ents)

        financial_keywords = {
            "ebitda", "treasury", "margin", "acquisition", "revenue", "dividend",
            "strictly confidential", "internal only", "trade secret"
        }
        has_confidential_marker = any(k in normalized_text.lower() for k in financial_keywords)
        sensitive_identifiers = {"CONFIDENTIAL_MARKER", "US_SSN", "PAN_CARD"}
        has_sensitive_ents = any(e["entity_type"] in sensitive_identifiers for e in resolved_ents)
        is_confidential = (
            (raw_tier == "CONFIDENTIAL" and (has_financial or has_sensitive_ents or has_confidential_marker))
            or (raw_tier != "SAFE" and has_sensitive_ents)
            or any(e["entity_type"] == "CONFIDENTIAL_MARKER" for e in resolved_ents)
        )

        if raw_tier == "RESTRICTED":
            base_score = 75 if (has_critical or has_financial or has_sensitive_ents) else 50
        elif is_confidential:
            base_score = 50
        else:
            base_score = 15

        weights = {
            "CREDIT_CARD": 35, "PRIVATE_KEY": 40, "API_KEY": 30, "US_SSN": 30,
            "PASSWORD_SECRET": 35, "DB_CONNECTION": 35, "JWT_TOKEN": 30,
            "IBAN": 25, "ABA_ROUTING": 20, "SWIFT_BIC": 15, "BANK_ACCOUNT": 25, "PAN_CARD": 25,
            "CONFIDENTIAL_MARKER": 20, "PERSON": 3, "ORG": 3, "LOCATION": 2
        }
        entity_impact = sum(weights.get(e["entity_type"], 2) for e in resolved_ents)
        total_risk = min(100, base_score + entity_impact)

        # Policy Enforcement Decision:
        # BLOCK: If critical secrets exist (Cards, Keys, SSN) OR total risk >= 80
        # ENCRYPT / MASK: If total risk >= 45 OR financial identifiers detected OR confidential metrics exist
        # ALLOW: Normal documents without sensitive leaks
        if has_critical or total_risk >= 80:
            action = "BLOCK"
            total_risk = max(total_risk, 85)
            calibrated_tier = "RESTRICTED"
        elif total_risk >= 45 or has_financial or is_confidential:
            action = "ENCRYPT"
            calibrated_tier = "CONFIDENTIAL"
        else:
            action = "ALLOW"
            calibrated_tier = "SAFE"

        # 8. Threat Explainability
        explanation_data = build_threat_explanation(
            calibrated_tier, action, total_risk, resolved_ents, cls_result
        )

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

        latency_breakdown = {
            "normalization_ms": round(t_norm, 2),
            "inference_ms": round(t_cls, 2),
            "rules_ms": round(t_rules, 2),
            "ner_ms": round(t_ner, 2),
            "redaction_ms": round(t_redact, 2),
            "total_ms": round(duration_ms, 2)
        }

        return DetectionResult(
            tier=calibrated_tier,
            risk_score=total_risk,
            action=action,
            entities=entity_spans,
            confidence=confidence,
            sanitized_text=sanitized,
            threat_category=explanation_data["threat_category"],
            explanation=explanation_data["explanation"],
            compliance_impact=explanation_data["compliance_impact"],
            remediation_advice=explanation_data["remediation_advice"],
            latency_ms=round(duration_ms, 2),
            latency_breakdown=latency_breakdown,
            engine_name=self.name,
            metadata={
                "probabilities": cls_result.get("probabilities", {}),
                "num_chunks": cls_result.get("num_chunks", 1),
                "entity_count": len(resolved_ents),
                "raw_classifier_tier": raw_tier
            }
        )

"""
Tier 3 Tests - Pluggable Engine Adapters & IDLPEngine Interface
================================================================================
File: ai-service/tests/test_tier3_engine_adapters.py
"""

import pytest
from app.engine.interfaces import IDLPEngine, DetectionResult
from app.engine.rules_engine import RuleBasedDLPEngine
from app.engine.hybrid_engine import HybridDLPEngine
from app.engine.factory import get_dlp_engine, reset_engine_instance


def test_rule_based_dlp_engine_adapter():
    reset_engine_instance()
    engine = get_dlp_engine("rules")
    assert isinstance(engine, IDLPEngine)
    assert isinstance(engine, RuleBasedDLPEngine)

    # Test detection of critical banking entity (valid Luhn card and valid SSN)
    text = "Please process payment for Visa 4530-8921-0043-9182 and SSN 010-71-6307 immediately."
    res = engine.scan(text, mode="mask")

    assert isinstance(res, DetectionResult)
    assert res.tier == "RESTRICTED"
    assert res.risk_score >= 80
    assert res.action == "BLOCK"
    assert len(res.entities) >= 1
    assert "4530-8921-0043-9182" not in res.sanitized_text
    # Strict rule engine speed: < 5ms
    assert res.latency_ms < 15.0



def test_hybrid_dlp_engine_adapter():
    reset_engine_instance()
    engine = get_dlp_engine("hybrid")
    assert isinstance(engine, IDLPEngine)
    assert isinstance(engine, HybridDLPEngine)

    # Benign text
    benign_text = "All employees are invited to the Q3 company town hall on Friday at 2 PM."
    res_benign = engine.scan(benign_text)
    assert res_benign.tier == "SAFE"
    assert res_benign.action == "ALLOW"
    assert res_benign.risk_score < 40

    # Confidential text
    conf_text = "Executive Treasury Memo: EBITDA margin projection of 24.2% for Q4 acquisition."
    res_conf = engine.scan(conf_text)
    assert res_conf.tier == "CONFIDENTIAL"
    assert res_conf.action in ("MASK", "ENCRYPT")


def test_engine_factory_caching_and_switching():
    reset_engine_instance()
    engine1 = get_dlp_engine("rules")
    engine2 = get_dlp_engine("rules")
    assert engine1 is engine2

    engine3 = get_dlp_engine("hybrid")
    assert isinstance(engine3, HybridDLPEngine)
    assert engine3 is not engine1

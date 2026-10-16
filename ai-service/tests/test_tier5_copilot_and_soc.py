"""
Tier 5 Tests - SOC Platform, Analyst Copilot & Master Ingestion Contract
================================================================================
File: ai-service/tests/test_tier5_copilot_and_soc.py
"""

import pytest
from fastapi.testclient import TestClient
from app.copilot.agent import BankingCopilotAgent, get_copilot_agent
from app.main import app
from app.db.session import init_db

client = TestClient(app)


def test_copilot_explain_incident():
    copilot = get_copilot_agent()
    incident = {
        "id": "inc-999",
        "client_id": "desktop-agent-01",
        "user_id": "bob@bank.com",
        "department": "wealth_management",
        "destination_domain": "pastebin.com",
        "source_action": "clipboard",
        "classification_tier": "RESTRICTED",
        "risk_score": 95,
        "enforcement_action": "BLOCK",
        "entity_counts": {"CREDIT_CARD": 2, "US_SSN": 1}
    }
    explanation = copilot.explain_incident(incident)
    assert "bob@bank.com" in explanation
    assert "wealth_management" in explanation
    assert "pastebin.com" in explanation
    assert "BLOCK" in explanation
    assert "PCI-DSS" in explanation or "exposure" in explanation


def test_copilot_recommend_remediation():
    copilot = get_copilot_agent()

    # External domain with card -> BLOCK
    incident_ext = {
        "risk_score": 90,
        "destination_domain": "chatgpt.com",
        "entity_counts": {"CREDIT_CARD": 1}
    }
    rec_ext = copilot.recommend_remediation(incident_ext)
    assert rec_ext["action"] == "BLOCK"
    assert rec_ext["confidence"] >= 0.90

    # Internal bank domain -> MASK
    incident_int = {
        "risk_score": 85,
        "destination_domain": "internal.bank.com",
        "entity_counts": {"CREDIT_CARD": 1}
    }
    rec_int = copilot.recommend_remediation(incident_int)
    assert rec_int["action"] == "MASK"


def test_copilot_natural_language_to_sql():
    copilot = get_copilot_agent()
    res = copilot.query_incidents_nl("show all blocked incidents in retail banking")
    
    assert "sql_query" in res
    assert "enforcement_action = :action" in res["sql_query"]
    assert res["parameters"]["action"] == "BLOCK"
    assert "retail" in res["parameters"]["dept"]


def test_copilot_chat_endpoint():
    # Chat without context
    resp = client.post("/api/v1/soc/copilot/chat", json={
        "query": "find all high risk incidents sent to pastebin.com"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "sql_query" in data
    assert data["sql_query"] is not None


def test_soc_incidents_and_stats_endpoints():
    init_db()
    # Stats endpoint
    stats_resp = client.get("/api/v1/soc/stats")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert "total_scanned" in stats
    assert "blocked_count" in stats
    assert "avg_latency_ms" in stats

    # Incidents list endpoint
    inc_resp = client.get("/api/v1/soc/incidents?limit=10")
    assert inc_resp.status_code == 200
    assert isinstance(inc_resp.json(), list)


def test_master_dlp_scan_contract_endpoint():
    # 1. High risk payload with valid credit card
    req_body = {
        "client_id": "browser-ext-v3",
        "user_id": "alice@bank.com",
        "department": "treasury",
        "destination_domain": "api.openai.com",
        "source_action": "clipboard",
        "text": "Wire transfer for Visa 4530-8921-0043-9182 and SSN 010-71-6307 to offshore account.",
        "mode": "tokenize"
    }

    resp = client.post("/api/v1/scan/dlp", json=req_body)
    assert resp.status_code == 200
    data = resp.json()

    assert data["classification_tier"] == "RESTRICTED"
    assert data["risk_score"] >= 80
    assert data["enforcement_action"] == "BLOCK"
    assert len(data["payload_sha256"]) == 64
    assert "4530-8921-0043-9182" not in data["sanitized_text"]
    assert data["latency_ms"] < 25.0


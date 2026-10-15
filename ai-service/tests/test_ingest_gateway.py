"""
SecureFlow AI - Tests for Ingestion Gateway Endpoint (/api/v1/events/ingest)
================================================================================
File: ai-service/tests/test_ingest_gateway.py
"""

import pytest
import base64
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_ingest_chrome_extension_paste_blocked():
    event_payload = {
        "eventId": "ext-test-001",
        "timestamp": "2026-10-15T18:00:00Z",
        "source": "CHROME_EXTENSION",
        "eventType": "BROWSER_PASTE",
        "content": "Client payment authorization using card 4530-8921-0043-9182 and SSN 010-71-6307.",
        "fileName": "web_paste_chatgpt.com.txt",
        "metadata": {
            "url": "https://chatgpt.com",
            "hostname": "chatgpt.com",
            "targetField": "prompt-textarea"
        }
    }
    response = client.post("/api/v1/events/ingest", json=event_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["eventId"] == "ext-test-001"
    assert data["actionTaken"] == "BLOCK"
    assert data["riskScore"] >= 80
    assert data["tier"] == "RESTRICTED"
    assert "[CARD_****9182]" in data["sanitizedContent"]
    assert "CREDIT_CARD" in data["flags"]


def test_ingest_desktop_agent_safe_clipboard_allowed():
    event_payload = {
        "eventId": "desk-test-002",
        "timestamp": "2026-10-15T18:05:00Z",
        "source": "DESKTOP_AGENT",
        "eventType": "CLIPBOARD_COPY",
        "content": "Hello team, please find attached the public meeting minutes and room reservation for tomorrow.",
        "fileName": "clipboard_capture.txt",
        "metadata": {
            "sourceApp": "notepad.exe"
        }
    }
    response = client.post("/api/v1/events/ingest", json=event_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["eventId"] == "desk-test-002"
    assert data["actionTaken"] == "ALLOW"
    assert data["riskScore"] < 45
    assert data["tier"] == "SAFE"


def test_ingest_email_connector_confidential_encrypt():
    event_payload = {
        "eventId": "email-test-003",
        "timestamp": "2026-10-15T18:10:00Z",
        "source": "EMAIL_CONNECTOR",
        "eventType": "EMAIL_INBOUND",
        "content": "Executive Treasury Memo: EBITDA margin projection of 24.2% with $42.5M in net income for Q4.",
        "fileName": "sample_confidential.eml",
        "metadata": {
            "from": "cfo@bank.com",
            "to": "board@bank.com"
        }
    }
    response = client.post("/api/v1/events/ingest", json=event_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["eventId"] == "email-test-003"
    assert data["actionTaken"] in ("ENCRYPT", "BLOCK")
    assert data["riskScore"] >= 45
    assert data["tier"] == "CONFIDENTIAL"

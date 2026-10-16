"""
Tier 2 Tests - Event Dispatcher, WebSocket Hub & Multi-Format Zip Extractor
================================================================================
File: ai-service/tests/test_tier2_event_bus.py
"""

import io
import zipfile
import pytest
from unittest.mock import AsyncMock
from app.core.event_bus import EventDispatcher
from app.engine.extractor import extract_from_zip, extract_file_content


@pytest.mark.anyio
async def test_event_dispatcher_broadcast_and_cleanup():
    dispatcher = EventDispatcher()
    assert dispatcher.active_subscriber_count == 0

    # Create mock WebSockets
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    # ws2 will fail on send
    ws2.send_text.side_effect = ConnectionError("Client abruptly disconnected")

    await dispatcher.connect(ws1)
    await dispatcher.connect(ws2)
    assert dispatcher.active_subscriber_count == 2

    # Broadcast threat event
    event = {
        "type": "LIVE_THREAT_EVENT",
        "incident": {"id": "inc-001", "risk_score": 85, "enforcement_action": "BLOCK"}
    }
    await dispatcher.broadcast_threat(event)

    # ws1 received broadcast
    ws1.send_text.assert_called_once()
    # ws2 failed and was pruned
    assert dispatcher.active_subscriber_count == 1

    # Graceful disconnect
    await dispatcher.disconnect(ws1)
    assert dispatcher.active_subscriber_count == 0


def test_safe_zip_extractor_extracts_nested_files():
    # Build in-memory zip containing txt and csv files
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("confidential_memo.txt", "Q3 EBITDA was $45.2M for internal acquisition.")
        zf.writestr("customers.csv", "John Doe,4532-8921-0043-9182,New York")

    zip_bytes = zip_buffer.getvalue()
    extracted_text = extract_from_zip(zip_bytes)

    assert "confidential_memo.txt" in extracted_text
    assert "EBITDA was $45.2M" in extracted_text
    assert "4532-8921-0043-9182" in extracted_text

    # Also test dispatcher
    text, ext = extract_file_content(zip_bytes, "archive.zip")
    assert ext == "zip"
    assert "confidential_memo.txt" in text


def test_safe_zip_extractor_guards_against_excessive_files():
    # Create zip with 25 files (limit is 20)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for i in range(25):
            zf.writestr(f"file_{i}.txt", f"Sample content line {i}")

    zip_bytes = zip_buffer.getvalue()
    # Run with max_files=5
    extracted_text = extract_from_zip(zip_bytes, max_files=5)
    # Should only contain at most 5 files
    assert "file_0.txt" in extracted_text
    assert "file_4.txt" in extracted_text
    assert "file_10.txt" not in extracted_text

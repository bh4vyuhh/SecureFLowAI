"""
Tier 1 Tests - Client Circuit Breaker with Fail-Open / Fail-Closed
================================================================================
File: ai-service/tests/test_tier1_circuit_breaker.py
"""

import time
import pytest
from app.core.circuit_breaker import CircuitBreaker


def test_circuit_breaker_closed_state_success():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout_secs=1.0)
    assert cb.state == "CLOSED"
    assert cb.can_attempt() is True
    cb.record_success()
    assert cb.state == "CLOSED"
    assert cb.failure_count == 0


def test_circuit_breaker_trips_to_open_on_threshold():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout_secs=1.0, policy="FAIL_OPEN")
    
    # 2 failures -> still closed
    res1 = cb.record_failure({"id": "event-1"})
    assert res1["decision"] == "ALLOW"
    assert cb.state == "CLOSED"

    res2 = cb.record_failure({"id": "event-2"})
    assert res2["decision"] == "ALLOW"
    assert cb.state == "CLOSED"

    # 3rd failure -> trips to OPEN
    res3 = cb.record_failure({"id": "event-3"})
    assert cb.state == "OPEN"
    assert res3["decision"] == "ALLOW"
    assert res3["queued_locally"] is True
    assert cb.can_attempt() is False


def test_circuit_breaker_fail_closed_policy():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_secs=1.0, policy="FAIL_CLOSED")
    
    cb.record_failure({"id": "event-1"})
    res2 = cb.record_failure({"id": "event-2"})
    
    assert cb.state == "OPEN"
    assert res2["decision"] == "BLOCK"
    assert res2["reason"] == "GATEWAY_UNREACHABLE_FAIL_CLOSED"
    assert res2["queued_locally"] is False


def test_circuit_breaker_recovery_to_half_open_and_closed():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_secs=0.1, policy="FAIL_OPEN")
    
    cb.record_failure({"id": "event-1"})
    cb.record_failure({"id": "event-2"})
    assert cb.state == "OPEN"
    assert cb.can_attempt() is False

    # Wait for recovery timeout
    time.sleep(0.15)
    
    # can_attempt transitions to HALF_OPEN
    assert cb.can_attempt() is True
    assert cb.state == "HALF_OPEN"

    # Record 2 consecutive successes to close circuit
    cb.record_success()
    assert cb.state == "HALF_OPEN"
    cb.record_success()
    assert cb.state == "CLOSED"


def test_circuit_breaker_drain_deferred_queue():
    cb = CircuitBreaker(failure_threshold=1, policy="FAIL_OPEN")
    cb.record_failure({"data": "critical_tx_1"})
    cb.record_failure({"data": "critical_tx_2"})
    
    items = cb.drain_deferred_queue()
    assert len(items) == 2
    assert items[0]["payload"]["data"] == "critical_tx_1"
    assert items[1]["payload"]["data"] == "critical_tx_2"
    assert len(cb.local_deferred_queue) == 0

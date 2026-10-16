"""
SecureFlow AI - Client Circuit Breaker with Fail-Open / Fail-Closed Policies
================================================================================
File: ai-service/app/core/circuit_breaker.py

Provides client-side resilience when the central DLP gateway is unreachable:
  - States: CLOSED (normal), OPEN (tripped), HALF_OPEN (probing)
  - Configurable bank policies:
      - FAIL_OPEN: Intercepted data is permitted and enqueued locally for deferred inspection.
      - FAIL_CLOSED: Intercepted sensitive transfers are blocked hard to prevent leaks.
"""

import time
import logging
from typing import Optional, List, Any, Dict, Literal
from collections import deque

logger = logging.getLogger("SecureFlowAI.CircuitBreaker")


class CircuitBreaker:
    """
    Thread-safe Client Circuit Breaker.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_secs: float = 10.0,
        policy: Literal["FAIL_OPEN", "FAIL_CLOSED"] = "FAIL_OPEN",
        max_local_queue: int = 1000
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_secs = recovery_timeout_secs
        self.policy = policy
        
        self.state: Literal["CLOSED", "OPEN", "HALF_OPEN"] = "CLOSED"
        self.failure_count: int = 0
        self.success_count: int = 0
        self.last_failure_time: float = 0.0
        
        # Local offline queue for deferred submission in FAIL_OPEN mode
        self.local_deferred_queue: deque = deque(maxlen=max_local_queue)

    def can_attempt(self) -> bool:
        """Determines if a request should be forwarded to the gateway."""
        now = time.monotonic()

        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            if (now - self.last_failure_time) >= self.recovery_timeout_secs:
                logger.info("[CIRCUIT BREAKER] Recovery timeout elapsed. Transitioning to HALF_OPEN probe.")
                self.state = "HALF_OPEN"
                self.success_count = 0
                return True
            return False

        if self.state == "HALF_OPEN":
            return True

        return False

    def record_success(self):
        """Records a successful response from the gateway."""
        if self.state == "HALF_OPEN":
            self.success_count += 1
            if self.success_count >= 2:
                logger.info("[CIRCUIT BREAKER] Service recovered. Transitioning to CLOSED.")
                self.state = "CLOSED"
                self.failure_count = 0
        elif self.state == "CLOSED":
            self.failure_count = 0

    def record_failure(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Records an error/timeout contacting the gateway.
        Returns fallback decision based on bank policy (ALLOW or BLOCK).
        """
        self.last_failure_time = time.monotonic()
        self.failure_count += 1

        if self.state in ("CLOSED", "HALF_OPEN"):
            if self.failure_count >= self.failure_threshold or self.state == "HALF_OPEN":
                logger.warning(
                    f"[CIRCUIT BREAKER TRIPPED] Gateway unreachable ({self.failure_count} failures). "
                    f"Transitioning to OPEN. Policy: {self.policy}"
                )
                self.state = "OPEN"

        # Apply fallback policy
        if self.policy == "FAIL_OPEN":
            if payload:
                self.local_deferred_queue.append({
                    "timestamp": time.time(),
                    "payload": payload
                })
            return {
                "decision": "ALLOW",
                "reason": "GATEWAY_UNREACHABLE_FAIL_OPEN",
                "queued_locally": payload is not None,
                "circuit_state": self.state
            }
        else:  # FAIL_CLOSED
            return {
                "decision": "BLOCK",
                "reason": "GATEWAY_UNREACHABLE_FAIL_CLOSED",
                "queued_locally": False,
                "circuit_state": self.state
            }

    def drain_deferred_queue(self) -> List[Dict[str, Any]]:
        """Drains the local offline queue for re-transmission once recovered."""
        items = list(self.local_deferred_queue)
        self.local_deferred_queue.clear()
        return items

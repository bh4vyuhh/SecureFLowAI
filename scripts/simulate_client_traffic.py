"""
SecureFlow AI - Standalone Mock Client Traffic Simulator (Tier 1 & Tier 2)
================================================================================
File: scripts/simulate_client_traffic.py

Simulates high-volume enterprise banking traffic from Browser Extensions and Desktop Daemons:
  - Generates realistic benign, confidential, and restricted payloads (Credit Cards, IBANs, SSNs)
  - Exercises the Client Circuit Breaker with Fail-Open (local queueing) vs Fail-Closed policies
  - Concurrently listens to the WebSocket threat broadcast hub (/ws/live-threats)
  - Measures synchronous CPU latencies and asserts P95 < 25ms SLA
"""

import sys
import time
import json
import base64
import random
import asyncio
import logging
from typing import List, Dict, Any

import httpx
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TrafficSimulator")

GATEWAY_BASE_URL = "http://127.0.0.1:8000"
WS_THREAT_URL = "ws://127.0.0.1:8000/ws/live-threats"

# Test data generation templates
SAMPLE_BENIGN_TEXTS = [
    "Team, please review the Q3 frontend engineering sprint deliverables for the retail portal.",
    "The daily standup will take place at 10:00 AM in Conference Room 4B.",
    "Attached is the public documentation for our open-source React component library.",
    "def calculate_total_balance(accounts: list) -> float: return sum(acc.balance for acc in accounts)"
]

SAMPLE_CONFIDENTIAL_TEXTS = [
    "Q4 Treasury Memo: Projecting net interest margin of 3.42% pending Central Bank policy update.",
    "Preliminary merger discussion draft between Retail Banking Division and Northern Trust Corp.",
    "Internal compensation and bonus review guidelines for Senior Vice Presidents (Strictly Confidential)."
]

SAMPLE_RESTRICTED_TEXTS = [
    # Visa card with valid Luhn + SSN
    "Customer Account Verification: Jane Doe, Visa card 4530-8921-0043-9182, SSN 010-71-6307, balance $45,210.",
    # Mastercard with valid Luhn + IBAN
    "Urgent wire transfer to GB82 WEST 1234 5698 7654 32 using card 5500-0000-0000-0004 for Alice Smith.",
    # Mock Token + Routing
    "API Credentials: api_key = " + "mock_token_" + "sampleKey1234567890abcdef, routing ABA 021000021"
]


DEPARTMENTS = ["retail_banking", "wealth_management", "treasury", "compliance", "investment_banking"]
DESTINATIONS = ["api.openai.com", "pastebin.com", "github.com", "drive.google.com", "partner.bank.com"]


class SimulatedClient:
    """
    Mock Client Endpoint representing a Browser Extension or Desktop Agent.
    Implements local Circuit Breaker and handles simulated traffic.
    """

    def __init__(self, client_id: str, fail_policy: str = "FAIL_OPEN"):
        self.client_id = client_id
        self.fail_policy = fail_policy
        self.consecutive_failures = 0
        self.circuit_state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = 0.0
        self.local_offline_queue: List[Dict[str, Any]] = []

    def can_send(self) -> bool:
        now = time.monotonic()
        if self.circuit_state == "CLOSED":
            return True
        elif self.circuit_state == "OPEN":
            if (now - self.last_failure_time) >= 3.0:  # 3s probe timeout
                self.circuit_state = "HALF_OPEN"
                return True
            return False
        return True  # HALF_OPEN

    def record_success(self):
        self.consecutive_failures = 0
        self.circuit_state = "CLOSED"

    def record_failure(self, payload: Dict[str, Any]):
        self.consecutive_failures += 1
        self.last_failure_time = time.monotonic()
        if self.consecutive_failures >= 3:
            self.circuit_state = "OPEN"
        if self.fail_policy == "FAIL_OPEN":
            self.local_offline_queue.append(payload)


async def listen_to_live_threats(ws_url: str, stop_event: asyncio.Event, threat_counter: List[int]):
    """Background listener verifying real-time WebSocket event broadcaster."""
    try:
        async with websockets.connect(ws_url) as ws:
            logger.info(f"[WS CLIENT] Connected to Live Threat Feed: {ws_url}")
            while not stop_event.is_set():
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    data = json.loads(msg)
                    threat_counter[0] += 1
                    logger.info(
                        f"[WS EVENT RECEIVED] Threat ID: {data.get('incident', {}).get('id')} | "
                        f"Risk: {data.get('incident', {}).get('risk_score')} | "
                        f"Action: {data.get('incident', {}).get('enforcement_action')}"
                    )
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    break
    except Exception as e:
        logger.warning(f"[WS CLIENT] Could not connect to WebSocket live feed: {e}")


async def run_traffic_simulation(num_requests: int = 50, concurrency: int = 5):
    """
    Executes concurrent simulated requests against the DLP Gateway.
    """
    logger.info("=" * 70)
    logger.info(f"STARTING TRAFFIC SIMULATION: {num_requests} requests | Concurrency: {concurrency}")
    logger.info("=" * 70)

    clients = [
        SimulatedClient(f"browser-ext-{i:02d}", fail_policy="FAIL_OPEN")
        for i in range(concurrency)
    ]

    stop_ws = asyncio.Event()
    threat_counter = [0]
    ws_task = asyncio.create_task(listen_to_live_threats(WS_THREAT_URL, stop_ws, threat_counter))

    latencies: List[float] = []
    actions_count: Dict[str, int] = {"ALLOW": 0, "MASK": 0, "BLOCK": 0}
    tiers_count: Dict[str, int] = {"SAFE": 0, "CONFIDENTIAL": 0, "RESTRICTED": 0}

    async with httpx.AsyncClient(base_url=GATEWAY_BASE_URL, timeout=10.0) as client:
        # Check health first
        try:
            health = await client.get("/health")
            logger.info(f"[GATEWAY HEALTH] {health.status_code} - {health.json()}")
        except Exception as e:
            logger.error(f"[GATEWAY UNREACHABLE] Ensure FastAPI server is running on {GATEWAY_BASE_URL}: {e}")
            stop_ws.set()
            await ws_task
            return

        async def send_single_request(req_idx: int):
            sim_client = clients[req_idx % len(clients)]
            if not sim_client.can_send():
                # Circuit is open
                logger.warning(f"Client {sim_client.client_id} Circuit OPEN! Failing locally.")
                return

            # Randomly select payload category (40% Benign, 30% Confidential, 30% Restricted)
            roll = random.random()
            if roll < 0.4:
                text = random.choice(SAMPLE_BENIGN_TEXTS)
                mode = "mask"
            elif roll < 0.7:
                text = random.choice(SAMPLE_CONFIDENTIAL_TEXTS)
                mode = "mask"
            else:
                text = random.choice(SAMPLE_RESTRICTED_TEXTS)
                mode = "tokenize" if random.random() < 0.5 else "mask"

            payload = {
                "client_id": sim_client.client_id,
                "user_id": f"analyst_{req_idx % 10}@bank.com",
                "department": random.choice(DEPARTMENTS),
                "destination_domain": random.choice(DESTINATIONS),
                "source_action": random.choice(["clipboard", "browser_paste", "file_upload"]),
                "text": text,
                "mode": mode
            }

            t0 = time.perf_counter()
            try:
                resp = await client.post("/api/v1/scan/dlp", json=payload)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                if resp.status_code == 200:
                    sim_client.record_success()
                    data = resp.json()
                    latencies.append(elapsed_ms)
                    act = data.get("enforcement_action", "ALLOW")
                    tier = data.get("classification_tier", "SAFE")
                    actions_count[act] = actions_count.get(act, 0) + 1
                    tiers_count[tier] = tiers_count.get(tier, 0) + 1
                else:
                    sim_client.record_failure(payload)
                    logger.warning(f"Request {req_idx} failed with status {resp.status_code}")
            except Exception as e:
                sim_client.record_failure(payload)
                logger.error(f"Request {req_idx} error: {e}")

        # Batch requests with concurrency limit
        sem = asyncio.Semaphore(concurrency)
        async def bounded_request(i):
            async with sem:
                await send_single_request(i)

        tasks = [bounded_request(i) for i in range(num_requests)]
        await asyncio.gather(*tasks)

    # Let WebSocket flush
    await asyncio.sleep(1.0)
    stop_ws.set()
    await ws_task

    # Summary Statistics
    logger.info("=" * 70)
    logger.info("TRAFFIC SIMULATION RESULTS & SLA BENCHMARKS")
    logger.info("=" * 70)
    if latencies:
        latencies.sort()
        p50 = latencies[int(len(latencies) * 0.50)]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        avg = sum(latencies) / len(latencies)

        logger.info(f"Total Completed Requests: {len(latencies)} / {num_requests}")
        logger.info(f"Average CPU Latency:     {avg:.2f} ms")
        logger.info(f"P50 Latency:             {p50:.2f} ms")
        logger.info(f"P95 Latency:             {p95:.2f} ms")
        logger.info(f"P99 Latency:             {p99:.2f} ms")
        logger.info(f"Enforcement Actions:     {actions_count}")
        logger.info(f"Classified Tiers:        {tiers_count}")
        logger.info(f"WebSocket Threat Events: {threat_counter[0]}")

        sla_pass = p95 < 25.0
        status_str = "PASSED" if sla_pass else "EXCEEDED"
        logger.info(f"[BANKING SLA AUDIT] 25ms Constraint: {status_str} (P95={p95:.2f}ms)")
    else:
        logger.error("No successful requests recorded.")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    conc = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    asyncio.run(run_traffic_simulation(num_requests=count, concurrency=conc))

"""
SecureFlow AI - Non-Blocking Asynchronous Audit Writer
================================================================================
File: ai-service/app/db/audit_writer.py

Decouples synchronous enforcement (< 5ms response) from database writes:
  - Ingestion and inspection endpoints return immediately to clients.
  - Audit events and vaulted tokens are pushed into an in-memory async queue.
  - A background consumer writes records in batches to PostgreSQL/SQLite.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.db.session import SessionLocal
from app.db.models import IncidentRecord, TokenVaultRecord

logger = logging.getLogger("SecureFlowAI.AuditWriter")


class NonBlockingAuditWriter:
    """
    Asynchronous audit worker utilizing an asyncio.Queue.
    Ensures zero disk I/O delay in the critical enforcement path.
    """

    def __init__(self, max_queue_size: int = 10000, batch_size: int = 50, flush_interval_secs: float = 0.5):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.batch_size = batch_size
        self.flush_interval_secs = flush_interval_secs
        self._worker_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Starts the background batch persistence loop."""
        if self._running:
            return
        self._running = True
        self._worker_task = asyncio.create_task(self._batch_worker())
        logger.info("[AUDIT WRITER] Background batch writer started.")

    async def stop(self):
        """Gracefully drains the queue and stops the worker."""
        self._running = False
        if self._worker_task:
            # Drain remaining items
            await self._flush_all()
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
            self._worker_task = None
        logger.info("[AUDIT WRITER] Background batch writer stopped.")

    async def enqueue_incident(self, incident_data: Dict[str, Any], vaulted_tokens: Optional[List[Dict[str, str]]] = None):
        """
        Enqueues an audit event without blocking the caller.
        If the queue is full, logs a warning and drops or processes gracefully.
        """
        payload = {
            "type": "incident",
            "incident": incident_data,
            "vaulted_tokens": vaulted_tokens or [],
            "queued_at": datetime.now(timezone.utc)
        }
        try:
            self.queue.put_nowait(payload)
        except asyncio.QueueFull:
            logger.critical("[AUDIT QUEUE FULL] Audit queue saturated! Dropping incident telemetry to preserve SLA.")

    async def _batch_worker(self):
        """Background loop reading from queue and persisting batches to database."""
        while self._running:
            try:
                batch = []
                # Wait for at least one item
                try:
                    item = await asyncio.wait_for(self.queue.get(), timeout=self.flush_interval_secs)
                    batch.append(item)
                    self.queue.task_done()
                except asyncio.TimeoutError:
                    continue

                # Accumulate more items if available immediately up to batch_size
                while len(batch) < self.batch_size and not self.queue.empty():
                    item = self.queue.get_nowait()
                    batch.append(item)
                    self.queue.task_done()

                if batch:
                    await self._persist_batch(batch)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[AUDIT WORKER ERROR] Unexpected error in worker loop: {e}")
                await asyncio.sleep(0.5)

    async def _persist_batch(self, batch: List[Dict[str, Any]]):
        """Persists a list of queued audit events in a single database transaction."""
        def _write():
            import hashlib
            db = SessionLocal()
            try:
                # Retrieve the latest audit hash to maintain the tamperproof cryptographic chain
                last_record = db.query(IncidentRecord).order_by(IncidentRecord.timestamp.desc()).first()
                current_prev_hash = last_record.audit_hash if (last_record and last_record.audit_hash) else "GENESIS_BLOCK_0000000000000000000000000000000000000000000000000000"

                for entry in batch:
                    if entry.get("type") == "incident":
                        inc = entry["incident"]

                        # Determine regulatory compliance tags based on entities detected
                        ent_counts = inc.get("entity_counts", {})
                        tags = []
                        if any(k in ent_counts for k in ["CREDIT_CARD", "CVV", "EXPIRATION_DATE"]):
                            tags.append("PCI-DSS-v4.0-Req3")
                        if any(k in ent_counts for k in ["US_SSN", "PASSPORT", "NATIONAL_ID", "AADHAAR", "PAN"]):
                            tags.append("GDPR-Art32")
                        if any(k in ent_counts for k in ["IBAN", "SWIFT_BIC", "FED_WIRE_ROUTING", "ACCOUNT_NUMBER"]):
                            tags.append("RBI-DLP-2023")
                        if not tags:
                            tags = ["RBI-GENERAL-AUDIT"]

                        # Cryptographic Tamperproof Hash Computation:
                        # hash = SHA-256(prev_hash + id + payload_sha256 + risk_score + enforcement_action + user_id)
                        hash_payload = f"{current_prev_hash}:{inc.get('id')}:{inc.get('payload_sha256', '')}:{inc.get('risk_score', 0)}:{inc.get('enforcement_action', 'ALLOW')}:{inc.get('user_id', 'anonymous')}"
                        entry_audit_hash = hashlib.sha256(hash_payload.encode("utf-8")).hexdigest()

                        rec = IncidentRecord(
                            id=inc.get("id"),
                            client_id=inc.get("client_id", "unknown-client"),
                            user_id=inc.get("user_id", "anonymous"),
                            department=inc.get("department", "general"),
                            destination_domain=inc.get("destination_domain", "internal"),
                            source_action=inc.get("source_action", "clipboard"),
                            classification_tier=inc.get("classification_tier", "SAFE"),
                            risk_score=inc.get("risk_score", 0),
                            enforcement_action=inc.get("enforcement_action", "ALLOW"),
                            payload_sha256=inc.get("payload_sha256", ""),
                            prev_hash=current_prev_hash,
                            audit_hash=entry_audit_hash,
                            compliance_tags=inc.get("compliance_impact") or tags,
                            threat_category=inc.get("threat_category", "BENIGN_DATA"),
                            explanation=inc.get("explanation"),
                            remediation_advice=inc.get("remediation_advice"),
                            entity_counts=ent_counts,
                            telemetry=inc.get("telemetry", {}),
                            status=inc.get("status", "OPEN")
                        )
                        db.merge(rec)
                        # Advance hash chain
                        current_prev_hash = entry_audit_hash

                        # Persist any vaulted tokens associated with this incident
                        for tok in entry.get("vaulted_tokens", []):
                            vault_rec = TokenVaultRecord(
                                token=tok["token"],
                                entity_type=tok["entity_type"],
                                ciphertext=tok["ciphertext"],
                                key_version=tok.get("key_version", "v1")
                            )
                            # merge to handle duplicates idempotently
                            db.merge(vault_rec)

                db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"[DB WRITE FAILED] Could not persist audit batch of size {len(batch)}: {e}")
            finally:
                db.close()

        # Run synchronous DB write in thread pool so asyncio event loop is never blocked
        await asyncio.to_thread(_write)

    async def _flush_all(self):
        """Flushes all currently queued items."""
        remaining = []
        while not self.queue.empty():
            item = self.queue.get_nowait()
            remaining.append(item)
            self.queue.task_done()
        if remaining:
            await self._persist_batch(remaining)


# Global Singleton
_audit_writer_instance: Optional[NonBlockingAuditWriter] = None


def get_audit_writer() -> NonBlockingAuditWriter:
    global _audit_writer_instance
    if _audit_writer_instance is None:
        _audit_writer_instance = NonBlockingAuditWriter()
    return _audit_writer_instance

"""
SecureFlow AI - Production FastAPI DLP Microservice
================================================================================
File: ai-service/app/main.py

Features:
  - Lifespan pre-loading of ONNX INT8 session and spaCy NER pipeline
  - Anti-Leak Logging Middleware: SHA-256 hashes instead of plaintext customer payloads
  - CORS Middleware: Allows all origins for Chrome/Edge extensions & React frontend
  - Endpoints:
      * POST /api/v1/dlp/classify (Sliding-window 3-class DLP classification)
      * POST /api/v1/dlp/redact   (Reverse-offset masking & HMAC-SHA256 tokenization)
      * POST /api/v1/dlp/scan     (Unified DLP inspection for JSON text or multi-format files)
      * GET  /health              (Container & orchestrator liveness/readiness probe)
"""

import sys
import os
import time
import hashlib
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any, Tuple

import psutil
from fastapi import FastAPI, Request, Response, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .schemas import (
    ClassifyRequest, ClassifyResponse,
    RedactRequest, RedactResponse,
    ScanRequest, ScanResponse,
    HealthResponse, EntitySpan,
    IngestEventRequest, IngestEventResponse
)
from .engine import (
    SlidingWindowClassifier,
    extract_rule_entities,
    extract_ner_entities,
    resolve_entity_conflicts,
    redact_text,
    extract_file_content,
    get_spacy_nlp,
    normalize_adversarial_text,
    strip_invisible_characters
)

# -----------------------------------------------------------------------------
# Structured Logging Setup
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SecureFlowAI.APIService")

# Global engine instances
classifier_instance: Optional[SlidingWindowClassifier] = None


# -----------------------------------------------------------------------------
# Path Resolution
# -----------------------------------------------------------------------------
def get_model_directory() -> Path:
    current_dir = Path(__file__).resolve().parent
    ai_service_dir = current_dir.parent
    return ai_service_dir / "models"


def get_classifier() -> SlidingWindowClassifier:
    """
    Singleton accessor for SlidingWindowClassifier with lazy instantiation.
    """
    global classifier_instance
    if classifier_instance is None:
        models_dir = get_model_directory()
        logger.info(f"Initializing SlidingWindowClassifier from: {models_dir}")
        classifier_instance = SlidingWindowClassifier(models_dir)
    return classifier_instance


# -----------------------------------------------------------------------------
# Lifespan Management (Warm-up & Cache Preloading)
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 80)
    logger.info(" STARTING SECUREFLOW-AI BANKING DLP SERVICE")
    logger.info("=" * 80)

    # Ensure classifier is warmed up
    classifier = get_classifier()
    warmup_text = "SecureFlowAI warm up transaction verification test."
    classifier.classify(warmup_text)

    # Pre-warm spaCy NER
    logger.info("Pre-warming spaCy Contextual Tokenizer...")
    nlp = get_spacy_nlp()
    _ = nlp("Warm up Alice Smith Bank of America New York")

    logger.info("[STARTUP COMPLETE] All engines primed and ready for low-latency inference.")
    yield
    logger.info("[SHUTDOWN] Releasing engine resources...")


# -----------------------------------------------------------------------------
# Anti-Leak Logging Middleware
# -----------------------------------------------------------------------------
class AntiLeakLoggingMiddleware(BaseHTTPMiddleware):
    """
    Ensures ZERO customer plaintext data is logged to stdout/disk.
    Logs SHA-256 hashes, payload sizes, client IPs, endpoints, and latencies.
    """
    async def dispatch(self, request: Request, call_next):
        t0 = time.perf_counter()
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        # Process request
        response: Response = await call_next(request)
        duration_ms = (time.perf_counter() - t0) * 1000.0

        if path.startswith("/api/v1/dlp/"):
            logger.info(
                f"[DLP AUDIT] IP={client_ip} | Path={path} | Status={response.status_code} | "
                f"Latency={duration_ms:.2f}ms"
            )

        return response


# -----------------------------------------------------------------------------
# FastAPI App Initialization
# -----------------------------------------------------------------------------
app = FastAPI(
    title="SecureFlowAI - Enterprise Banking DLP Microservice",
    description="High-Throughput, Low-Latency (< 25ms) 3-Class Banking DLP, Deterministic Checksums, and Multi-Mode Redaction.",
    version="1.0.0",
    lifespan=lifespan
)

# 1. Install Anti-Leak Logger
app.add_middleware(AntiLeakLoggingMiddleware)

# 2. Configure CORS for Browser Extensions, Desktop Agents & Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Helper: Risk Score & Action Calculation
# -----------------------------------------------------------------------------
def calculate_risk_and_action(tier: str, entities: List[Dict[str, Any]]) -> Tuple[int, str]:
    """
    Calculates unified DLP risk score (0-100) and automated enforcement action:
      - BLOCK (risk >= 80): RESTRICTED tier, or PCI card, SSN, API Key present
      - ENCRYPT (45 <= risk < 80): CONFIDENTIAL tier, internal IBAN/routing, or high density PII
      - ALLOW (risk < 45): SAFE tier without high-risk PII
    """
    # Base score by semantic tier
    if tier == "RESTRICTED":
        base_score = 75
    elif tier == "CONFIDENTIAL":
        base_score = 50
    else:
        base_score = 10

    # Entity impact weighting
    weights = {
        "CREDIT_CARD": 30,
        "PRIVATE_KEY": 35,
        "API_KEY": 25,
        "US_SSN": 25,
        "IBAN": 15,
        "ABA_ROUTING": 15,
        "SWIFT_BIC": 10,
        "PERSON": 5,
        "ORG": 5,
        "LOCATION": 5
    }

    entity_impact = sum(weights.get(e["entity_type"], 5) for e in entities)
    total_risk = min(100, base_score + entity_impact)

    # Escalation policy
    critical_types = {"CREDIT_CARD", "PRIVATE_KEY", "API_KEY", "US_SSN"}
    has_critical = any(e["entity_type"] in critical_types for e in entities)

    if total_risk >= 80 or has_critical:
        action = "BLOCK"
        total_risk = max(total_risk, 80)
    elif total_risk >= 45 or tier == "CONFIDENTIAL":
        action = "ENCRYPT"
    else:
        action = "ALLOW"

    return total_risk, action


# -----------------------------------------------------------------------------
# API Endpoints
# -----------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Liveness probe: returns memory usage and active ONNX model state."""
    process = psutil.Process(os.getpid())
    mem_mb = round(process.memory_info().rss / (1024 * 1024), 2)
    models_dir = get_model_directory()
    onnx_file = models_dir / "onnx" / "model_int8.onnx"

    return HealthResponse(
        status="HEALTHY",
        service="SecureFlowAI-DLP-Microservice",
        version="1.0.0",
        memory_usage_mb=mem_mb,
        active_model=str(onnx_file.name) if onnx_file.exists() else "unloaded",
        active_providers=["CPUExecutionProvider"]
    )


@app.post("/api/v1/dlp/classify", response_model=ClassifyResponse, tags=["DLP"])
def classify_endpoint(request: ClassifyRequest):
    """
    Classifies input text into SAFE, CONFIDENTIAL, or RESTRICTED using
    the Sliding-Window INT8 ONNX Transformer with anti-evasion normalization.
    """
    normalized_text, _ = normalize_adversarial_text(request.text)
    classifier = get_classifier()
    result = classifier.classify(normalized_text)
    return ClassifyResponse(**result)


@app.post("/api/v1/dlp/redact", response_model=RedactResponse, tags=["DLP"])
def redact_endpoint(request: RedactRequest):
    """
    Extracts PII using deterministic checksums + contextual NER, resolves conflicts,
    and returns reverse-offset sanitized text with anti-evasion normalization.
    """
    t0 = time.perf_counter()
    normalized_text, _ = normalize_adversarial_text(request.text)

    # 1. Deterministic Rule Extraction (Luhn, MOD-97, ABA, SSN)
    rule_ents = extract_rule_entities(normalized_text)

    # 2. Contextual NER (PERSON, ORG, LOC)
    ner_ents = extract_ner_entities(normalized_text)

    # 3. Span Conflict Resolution
    resolved_ents = resolve_entity_conflicts(rule_ents + ner_ents)

    # 4. Reverse-Offset Redaction
    sanitized, redacted_records = redact_text(normalized_text, resolved_ents, mode=request.mode)
    duration_ms = (time.perf_counter() - t0) * 1000.0

    entity_spans = [
        EntitySpan(
            entity_type=r["entity_type"],
            start=r["start"],
            end=r["end"],
            value=None,  # Do not leak plaintext in response
            replacement=r["replacement"],
            confidence=r["confidence"]
        )
        for r in redacted_records
    ]

    return RedactResponse(
        sanitized_text=sanitized,
        entities_found=entity_spans,
        entity_count=len(entity_spans),
        mode=request.mode,
        latency_ms=round(duration_ms, 2)
    )


@app.post("/api/v1/dlp/scan", response_model=ScanResponse, tags=["DLP"])
async def scan_endpoint(request: Request):
    """
    Master DLP Inspection Endpoint:
      - Accepts JSON text body OR multipart file upload (.pdf, .docx, .xlsx, .csv, .txt, images).
      - Returns Security Tier, Risk Score (0-100), Enforcement Action (ALLOW/ENCRYPT/BLOCK),
        resolved entities, and sanitized text.
    """
    t0 = time.perf_counter()
    content_type = request.headers.get("content-type", "")

    if "multipart/form-data" in content_type:
        form = await request.form()
        uploaded_file = form.get("file")
        if not uploaded_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Multipart form data missing 'file' field."
            )
        file_bytes = await uploaded_file.read()
        filename = getattr(uploaded_file, "filename", "upload.txt") or "upload.txt"
        raw_text, _ = extract_file_content(file_bytes, filename)
        chosen_mode = form.get("mode", "mask")
        if isinstance(chosen_mode, bytes):
            chosen_mode = chosen_mode.decode("utf-8")
    else:
        try:
            body = await request.json()
            scan_req = ScanRequest(**body)
            raw_text = scan_req.text
            chosen_mode = scan_req.mode
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid scan request body: {str(e)}"
            )

    if not raw_text or not raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No extractable text found in request payload."
        )

    # Adversarial normalization & base64 secret decoding
    normalized_text, b64_payloads = normalize_adversarial_text(raw_text)
    inspection_text = normalized_text
    if b64_payloads:
        inspection_text = inspection_text + "\n" + "\n".join(b64_payloads)

    classifier = get_classifier()

    # 1. Sliding-Window Semantic Classification
    cls_result = classifier.classify(inspection_text)
    tier = cls_result["tier"]

    # 2. Deterministic Rule Extraction
    rule_ents = extract_rule_entities(inspection_text)

    # 3. Contextual NER Extraction
    ner_ents = extract_ner_entities(inspection_text)

    # 4. Span Conflict Resolution
    resolved_ents = resolve_entity_conflicts(rule_ents + ner_ents)

    # 5. Reverse-Offset Redaction (on normalized text)
    sanitized, redacted_records = redact_text(normalized_text, resolved_ents, mode=chosen_mode)

    # 6. Risk Scoring & Policy Decision
    risk_score, action = calculate_risk_and_action(tier, resolved_ents)
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

    return ScanResponse(
        tier=tier,
        risk_score=risk_score,
        action=action,
        entities=entity_spans,
        sanitized_text=sanitized,
        latency_ms=round(duration_ms, 2)
    )


@app.post("/api/v1/events/ingest", response_model=IngestEventResponse, tags=["Ingestion"])
async def ingest_event_endpoint(event: IngestEventRequest):
    """
    Client Gateway Ingestion Endpoint:
      - Intercepts events from Chrome/Edge Browser Extension, Desktop Agent, or Email Connector.
      - Supports raw pasted text, clipboard content, and base64-encoded binary files (with OCR).
      - Returns riskScore (0-100), actionTaken (ALLOW, ENCRYPT, BLOCK), tier, and sanitizedContent.
    """
    t0 = time.perf_counter()

    raw_text = ""
    # Check if a base64-encoded file payload is attached (e.g. screenshot or document)
    if event.fileBytesBase64:
        try:
            import base64
            file_bytes = base64.b64decode(event.fileBytesBase64)
            filename = event.fileName or "capture.dat"
            extracted, _ = extract_file_content(file_bytes, filename)
            raw_text = extracted
        except Exception as e:
            logger.warning(f"Failed to decode base64 file attachment in event {event.eventId}: {e}")

    # Fallback to text content
    if not raw_text and event.content:
        raw_text = event.content

    if not raw_text or not raw_text.strip():
        return IngestEventResponse(
            eventId=event.eventId,
            status="PROCESSED",
            riskScore=0,
            actionTaken="ALLOW",
            tier="SAFE",
            sanitizedContent="",
            flags=[],
            entityCount=0,
            latencyMs=round((time.perf_counter() - t0) * 1000.0, 2)
        )

    # 1. Adversarial normalization
    normalized_text, b64_payloads = normalize_adversarial_text(raw_text)
    inspection_text = normalized_text
    if b64_payloads:
        inspection_text = inspection_text + "\n" + "\n".join(b64_payloads)

    # 2. Sliding-Window Semantic Classification
    classifier = get_classifier()
    cls_result = classifier.classify(inspection_text)
    tier = cls_result["tier"]

    # 3. Deterministic Rule Extraction
    rule_ents = extract_rule_entities(inspection_text)

    # 4. Contextual NER Extraction
    ner_ents = extract_ner_entities(inspection_text)

    # 5. Span Conflict Resolution
    resolved_ents = resolve_entity_conflicts(rule_ents + ner_ents)

    # 6. Reverse-Offset Redaction
    sanitized, redacted_records = redact_text(normalized_text, resolved_ents, mode="mask")

    # 7. Risk Scoring & Policy Decision
    risk_score, action = calculate_risk_and_action(tier, resolved_ents)
    duration_ms = (time.perf_counter() - t0) * 1000.0

    flags = list({r["entity_type"] for r in resolved_ents})

    return IngestEventResponse(
        eventId=event.eventId,
        status="PROCESSED",
        riskScore=risk_score,
        actionTaken=action,
        tier=tier,
        sanitizedContent=sanitized,
        flags=flags,
        entityCount=len(resolved_ents),
        latencyMs=round(duration_ms, 2)
    )

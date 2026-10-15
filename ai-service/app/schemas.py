"""
SecureFlow AI - Pydantic v2 Strict Data Contracts
================================================================================
File: ai-service/app/schemas.py

Defines strictly typed request/response schemas:
  - ClassifyRequest / ClassifyResponse
  - RedactRequest / RedactResponse
  - ScanRequest / ScanResponse
  - HealthResponse
"""

from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Entity Span Schema
# -----------------------------------------------------------------------------
class EntitySpan(BaseModel):
    entity_type: str = Field(..., description="Detected entity type (CREDIT_CARD, IBAN, US_SSN, PERSON, etc.)")
    start: int = Field(..., description="Start character offset")
    end: int = Field(..., description="End character offset")
    value: Optional[str] = Field(None, description="Original raw detected string (omitted or masked in logs)")
    replacement: Optional[str] = Field(None, description="Redacted replacement token or mask")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")


# -----------------------------------------------------------------------------
# 1. Classification Endpoint Schemas
# -----------------------------------------------------------------------------
class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw text payload to classify")

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Executive Treasury Memo: EBITDA margin projection of 24.2% for Q4 acquisition."
            }
        }
    }


class ClassifyResponse(BaseModel):
    tier: Literal["SAFE", "CONFIDENTIAL", "RESTRICTED"] = Field(..., description="Predicted DLP security tier")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of top class")
    probabilities: Dict[str, float] = Field(..., description="Softmax probabilities across all 3 classes")
    num_chunks: int = Field(1, description="Number of sliding window chunks processed")
    latency_ms: float = Field(..., description="Inference execution time in milliseconds")


# -----------------------------------------------------------------------------
# 2. Redaction Endpoint Schemas
# -----------------------------------------------------------------------------
class RedactRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw text payload containing sensitive PII")
    mode: Literal["mask", "tokenize"] = Field("mask", description="Redaction mode: 'mask' (display mask) or 'tokenize' (reversible HMAC)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Customer John Doe with Visa card 4532-8921-0043-9182 and SSN 010-716-3079.",
                "mode": "mask"
            }
        }
    }


class RedactResponse(BaseModel):
    sanitized_text: str = Field(..., description="Masked or tokenized text output")
    entities_found: List[EntitySpan] = Field(default_factory=list, description="List of non-overlapping resolved entities")
    entity_count: int = Field(..., description="Total count of redacted entities")
    mode: str = Field(..., description="Redaction mode applied")
    latency_ms: float = Field(..., description="Redaction processing latency in milliseconds")


# -----------------------------------------------------------------------------
# 3. Master Scan Endpoint Schemas
# -----------------------------------------------------------------------------
class ScanRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text content to deeply inspect, classify, and redact")
    mode: Literal["mask", "tokenize"] = Field("mask", description="Redaction mode")

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Wire Transfer Authorization Form for Alice Smith, Account 4092-8819-2041, Visa 4532-8921-0043-9182."
            }
        }
    }


class ScanResponse(BaseModel):
    tier: Literal["SAFE", "CONFIDENTIAL", "RESTRICTED"] = Field(..., description="DLP Security Tier")
    risk_score: int = Field(..., ge=0, le=100, description="DLP Risk Score from 0 (benign) to 100 (critical leak)")
    action: Literal["ALLOW", "ENCRYPT", "BLOCK"] = Field(..., description="Automated DLP enforcement policy")
    entities: List[EntitySpan] = Field(default_factory=list, description="Extracted non-overlapping entities")
    sanitized_text: str = Field(..., description="Sanitized text with masked PII")
    latency_ms: float = Field(..., description="Total pipeline latency in milliseconds")


# -----------------------------------------------------------------------------
# 4. Service Health Schema
# -----------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: Literal["HEALTHY", "DEGRADED", "UNHEALTHY"] = Field("HEALTHY")
    service: str = Field("SecureFlowAI-DLP-Microservice")
    version: str = Field("1.0.0")
    memory_usage_mb: float = Field(..., description="Active RSS memory footprint in MB")
    active_model: str = Field(..., description="Name and path of active ONNX INT8 engine")
    active_providers: List[str] = Field(default_factory=list, description="Active execution providers")


# -----------------------------------------------------------------------------
# 5. Client Gateway Ingestion Schemas (Browser Extension / Desktop Agent / Email)
# -----------------------------------------------------------------------------
class IngestEventRequest(BaseModel):
    eventId: str = Field(..., description="Unique client-generated tracking event ID")
    timestamp: Optional[str] = Field(None, description="ISO8601 event timestamp")
    source: str = Field("GENERIC_CAPTURE", description="Source client: CHROME_EXTENSION, DESKTOP_AGENT, EMAIL_CONNECTOR")
    eventType: str = Field("DATA_TRANSFER", description="Event type: BROWSER_PASTE, CLIPBOARD_COPY, FILE_DETECTED, etc.")
    content: Optional[str] = Field(None, description="Raw text or decoded payload intercepted at endpoint")
    fileName: Optional[str] = Field(None, description="Name of intercepted file or virtual filename")
    fileBytesBase64: Optional[str] = Field(None, description="Optional Base64-encoded binary file payload (for OCR/files)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Client telemetry metadata")


class IngestEventResponse(BaseModel):
    eventId: str = Field(..., description="Client event ID mirrored back")
    status: str = Field("PROCESSED", description="Processing status")
    riskScore: int = Field(..., ge=0, le=100, description="DLP Risk Score (0-100)")
    actionTaken: Literal["ALLOW", "ENCRYPT", "BLOCK"] = Field(..., description="Automated DLP enforcement policy")
    tier: Literal["SAFE", "CONFIDENTIAL", "RESTRICTED"] = Field(..., description="Predicted document security tier")
    sanitizedContent: Optional[str] = Field(None, description="Masked/sanitized text safe for display or transmission")
    flags: List[str] = Field(default_factory=list, description="List of detected sensitive entity types")
    entityCount: int = Field(0, description="Total count of non-overlapping entities found")
    latencyMs: float = Field(..., description="Processing time in milliseconds")


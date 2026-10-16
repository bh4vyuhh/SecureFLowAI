"""
SecureFlow AI - Abstract DLP Engine Interface & Decoupled Contracts
================================================================================
File: ai-service/app/engine/interfaces.py

Defines the plug-and-play detection interface IDLPEngine and standardized
output schemas, allowing AI models or rule engines to be swapped or retrained
with zero modifications to the Gateway, Database, or Client tiers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class EntitySpan(BaseModel):
    entity_type: str = Field(..., description="Detected entity type (CREDIT_CARD, IBAN, US_SSN, PERSON, etc.)")
    start: int = Field(..., description="Start character offset in normalized text")
    end: int = Field(..., description="End character offset in normalized text")
    value: Optional[str] = Field(None, description="Original raw detected string (omitted in zero-leak logs)")
    replacement: Optional[str] = Field(None, description="Redacted replacement token or mask")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")


class DetectionResult(BaseModel):
    tier: Literal["SAFE", "CONFIDENTIAL", "RESTRICTED"] = Field(..., description="DLP Security Tier")
    risk_score: int = Field(..., ge=0, le=100, description="Risk Score from 0 (benign) to 100 (critical leak)")
    action: Literal["ALLOW", "ENCRYPT", "BLOCK"] = Field(..., description="Automated enforcement policy")
    entities: List[EntitySpan] = Field(default_factory=list, description="Extracted non-overlapping entities")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall classification confidence")
    sanitized_text: str = Field(..., description="Masked or tokenized text representation")
    latency_ms: float = Field(..., description="Total detection latency in milliseconds")
    engine_name: str = Field(..., description="Identifier of the active detection engine adapter")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Diagnostic telemetry attributes")


class IDLPEngine(ABC):
    """
    Abstract Detection Interface:
    Decouples central routing and storage tiers from the underlying AI detection engine.
    """

    @abstractmethod
    def scan(self, text: str, mode: str = "mask", context: Optional[Dict[str, Any]] = None) -> DetectionResult:
        """
        Executes unified DLP inspection: intent classification, entity detection,
        conflict resolution, reverse-offset redaction, and risk scoring.
        """
        pass

    @abstractmethod
    def classify(self, text: str) -> Dict[str, Any]:
        """
        Executes lightweight intent classification returning security tier and class probabilities.
        """
        pass

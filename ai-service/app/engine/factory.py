"""
SecureFlow AI - Engine Factory
================================================================================
File: ai-service/app/engine/factory.py

Factory provider for IDLPEngine instances:
  - Adapter A: "rules" -> RuleBasedDLPEngine (Deterministic, ultra-low latency < 2ms)
  - Adapter B: "hybrid" -> HybridDLPEngine (Rules + INT8 ONNX Transformer + Token NER)
"""

import os
import logging
from typing import Optional
from app.engine.interfaces import IDLPEngine
from app.engine.rules_engine import RuleBasedDLPEngine
from app.engine.hybrid_engine import HybridDLPEngine

logger = logging.getLogger("SecureFlowAI.EngineFactory")

_engine_instance: Optional[IDLPEngine] = None
_current_engine_type: Optional[str] = None


def get_dlp_engine(engine_type: Optional[str] = None) -> IDLPEngine:
    """
    Returns an IDLPEngine singleton based on configuration or explicit engine_type.
    Configuration priority:
      1. engine_type argument
      2. DLP_ENGINE_TYPE environment variable ('hybrid' or 'rules')
      3. Default fallback to 'hybrid'
    """
    global _engine_instance, _current_engine_type

    target_type = (engine_type or os.getenv("DLP_ENGINE_TYPE", "hybrid")).strip().lower()

    if _engine_instance is not None and _current_engine_type == target_type:
        return _engine_instance

    logger.info(f"[ENGINE FACTORY] Instantiating DLP Engine adapter: '{target_type}'")

    if target_type == "rules":
        _engine_instance = RuleBasedDLPEngine()
        _current_engine_type = "rules"
    elif target_type in ("hybrid", "onnx"):
        _engine_instance = HybridDLPEngine()
        _current_engine_type = "hybrid"
    else:
        logger.warning(f"Unknown engine type '{target_type}'; falling back to RuleBasedDLPEngine.")
        _engine_instance = RuleBasedDLPEngine()
        _current_engine_type = "rules"

    return _engine_instance


def reset_engine_instance():
    """For testing purposes to force re-instantiation."""
    global _engine_instance, _current_engine_type
    _engine_instance = None
    _current_engine_type = None

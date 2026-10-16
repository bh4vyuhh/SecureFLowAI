"""
SecureFlow AI - Analyst Copilot Interface Contract
================================================================================
File: ai-service/app/copilot/interfaces.py

Defines the abstract interface for the Conversational Analyst Copilot:
  - Incident Explainability: Translates detection logs into plain-English security summaries.
  - Remediation Advisor: Suggests whether to uphold blocks or whitelist destinations.
  - Natural Language Querying: Translates analyst queries into structured filters/SQL.
  - Provider Agnostic: Decoupled from specific LLM providers (Ollama, vLLM, OpenAI, Heuristic).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class ICopilotAgent(ABC):
    """
    Abstract interface for the SOC Analyst Copilot.
    """

    @abstractmethod
    def explain_incident(self, incident: Dict[str, Any]) -> str:
        """Translates technical detection telemetry into plain-English security analysis."""
        pass

    @abstractmethod
    def recommend_remediation(self, incident: Dict[str, Any], history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Recommends whether to uphold block, mask, whitelist, or flag false-positive.
        Returns dict with: 'action', 'confidence', 'rationale'.
        """
        pass

    @abstractmethod
    def query_incidents_nl(self, query: str) -> Dict[str, Any]:
        """
        Translates a natural language question into structured SQL and query parameters.
        Returns dict with: 'sql_query', 'parameters', 'intent_summary'.
        """
        pass

    @abstractmethod
    def chat(self, user_query: str, context_incident: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Master conversational assistant endpoint.
        Combines explanation, recommendations, or query execution.
        """
        pass

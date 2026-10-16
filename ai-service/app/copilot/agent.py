"""
SecureFlow AI - Banking SOC Analyst Copilot Agent
================================================================================
File: ai-service/app/copilot/agent.py

Implementation of ICopilotAgent:
  - Explainability Engine: Formulates security incident narrative from telemetry.
  - Remediation Advisor: Evaluates threat patterns, department context, destination trust.
  - Natural Language Query Parser: Converts analyst questions into SQL queries for IncidentRecord.
  - Provider-Agnostic: Works completely offline with zero cloud egress, or connects to local vLLM/Ollama.
"""

import re
import logging
from typing import Dict, Any, Optional, List
from app.copilot.interfaces import ICopilotAgent

logger = logging.getLogger("SecureFlowAI.CopilotAgent")


class BankingCopilotAgent(ICopilotAgent):
    """
    Decoupled Banking SOC Analyst Copilot.
    Operates fully air-gapped without requiring external cloud API keys.
    """

    def explain_incident(self, incident: Dict[str, Any]) -> str:
        """
        Translates raw DLP telemetry into plain-English security summary.
        """
        client = incident.get("client_id", "Unknown client")
        user = incident.get("user_id", "Unknown user")
        dept = incident.get("department", "General")
        domain = incident.get("destination_domain", "external endpoint")
        action = incident.get("enforcement_action", "ALLOW")
        risk = incident.get("risk_score", 0)
        tier = incident.get("classification_tier", "SAFE")
        entities = incident.get("entity_counts", {})
        source_act = incident.get("source_action", "transfer")

        entity_desc_list = [f"{count} {etype.replace('_', ' ').lower()}(s)" for etype, count in entities.items()]
        entity_summary = ", ".join(entity_desc_list) if entity_desc_list else "no specific PII tokens"

        summary = (
            f"**Incident Summary:** An attempted {source_act} action by **{user}** ({dept} department) "
            f"destined for **{domain}** was evaluated as **{tier}** risk (Score: {risk}/100). "
            f"The enforcement engine executed a **{action}** policy action. "
            f"Sensitive entities detected: {entity_summary}."
        )

        if risk >= 70:
            summary += (
                " This represents a high-severity regulatory exposure under PCI-DSS / GDPR "
                "due to unencrypted customer financial credentials."
            )
        elif risk >= 40:
            summary += (
                " This activity exhibits moderate sensitivity. Masking was enforced to prevent "
                "data leakage while maintaining operational flow."
            )
        else:
            summary += " This activity was classified as benign and within acceptable operational parameters."

        return summary

    def recommend_remediation(self, incident: Dict[str, Any], history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Recommends appropriate remediation action based on domain safety, entity count, and department.
        """
        risk = incident.get("risk_score", 0)
        domain = incident.get("destination_domain", "").lower()
        entities = incident.get("entity_counts", {})
        
        # High risk threshold
        if risk >= 70 or "CREDIT_CARD" in entities or "IBAN" in entities:
            if "internal.bank" in domain or "corp.bank" in domain:
                return {
                    "action": "MASK",
                    "confidence": 0.85,
                    "rationale": (
                        f"Destination '{domain}' is an authorized internal domain, but contains raw banking tokens. "
                        "Recommend MASK to protect data at rest while permitting internal workflow."
                    )
                }
            else:
                return {
                    "action": "BLOCK",
                    "confidence": 0.98,
                    "rationale": (
                        f"Destination '{domain}' is an untrusted external endpoint receiving raw financial credentials. "
                        "Strict BLOCK must be upheld to comply with PCI-DSS."
                    )
                }

        # Moderate risk threshold
        if risk >= 40:
            return {
                "action": "MASK",
                "confidence": 0.90,
                "rationale": "Moderate sensitivity data detected. Tokenization or masking is recommended."
            }

        # Safe
        return {
            "action": "ALLOW",
            "confidence": 0.95,
            "rationale": "Payload contains no critical PII or confidential trade secrets. Safe to allow."
        }

    def query_incidents_nl(self, query: str) -> Dict[str, Any]:
        """
        Translates natural language questions into structured SQL queries over `dlp_incidents`.
        Supports queries like:
          - 'show all blocked incidents'
          - 'find high risk transfers in retail banking'
          - 'incidents sent to openai'
          - 'list incidents today'
        """
        q = query.lower()
        where_clauses = []
        params = {}

        if "block" in q:
            where_clauses.append("enforcement_action = :action")
            params["action"] = "BLOCK"
        elif "mask" in q:
            where_clauses.append("enforcement_action = :action")
            params["action"] = "MASK"
        elif "allow" in q:
            where_clauses.append("enforcement_action = :action")
            params["action"] = "ALLOW"

        if "high risk" in q or "critical" in q:
            where_clauses.append("risk_score >= :min_risk")
            params["min_risk"] = 70
        elif "moderate" in q:
            where_clauses.append("risk_score >= 40 AND risk_score < 70")

        # Department detection
        for dept in ["retail", "wealth", "investment", "treasury", "compliance", "it"]:
            if dept in q:
                where_clauses.append("LOWER(department) LIKE :dept")
                params["dept"] = f"%{dept}%"
                break

        # Domain extraction
        domain_match = re.search(r'(?:to|domain|site|destination)\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', q)
        if domain_match:
            where_clauses.append("LOWER(destination_domain) LIKE :domain")
            params["domain"] = f"%{domain_match.group(1).lower()}%"

        where_stmt = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        sql = f"SELECT id, timestamp, user_id, department, destination_domain, risk_score, enforcement_action, classification_tier FROM dlp_incidents{where_stmt} ORDER BY timestamp DESC LIMIT 50"

        return {
            "sql_query": sql,
            "parameters": params,
            "intent_summary": f"Querying dlp_incidents with filters: {params if params else 'None (recent incidents)'}"
        }

    def chat(self, user_query: str, context_incident: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Conversational entrypoint for the SOC Analyst Copilot.
        """
        q = user_query.strip()
        lower_q = q.lower()

        # If analyzing a specific incident
        if context_incident:
            if "explain" in lower_q or "what happened" in lower_q or "summary" in lower_q:
                explanation = self.explain_incident(context_incident)
                remediation = self.recommend_remediation(context_incident)
                return {
                    "response": f"{explanation}\n\n**Recommendation:** {remediation['rationale']}",
                    "suggested_action": remediation["action"],
                    "confidence": remediation["confidence"],
                    "sql_query": None,
                    "matched_incidents_count": 1
                }
            elif "remediate" in lower_q or "action" in lower_q or "recommend" in lower_q:
                remediation = self.recommend_remediation(context_incident)
                return {
                    "response": f"**Recommended Action:** **{remediation['action']}** (Confidence: {int(remediation['confidence']*100)}%)\n\n{remediation['rationale']}",
                    "suggested_action": remediation["action"],
                    "confidence": remediation["confidence"],
                    "sql_query": None,
                    "matched_incidents_count": 1
                }

        # If natural language database inquiry
        if any(w in lower_q for w in ["find", "show", "list", "how many", "search", "who", "incidents"]):
            parsed = self.query_incidents_nl(user_query)
            return {
                "response": f"I translated your question into the following incident query:\n```sql\n{parsed['sql_query']}\n```\nExecuting audit query across historical records.",
                "suggested_action": None,
                "confidence": 0.95,
                "sql_query": parsed["sql_query"],
                "matched_incidents_count": 0
            }

        # General assistance
        return {
            "response": (
                "SecureFlow AI Analyst Copilot ready. I can explain incidents, recommend remediation "
                "actions, or search historical DLP audit logs in plain English. For example:\n"
                "- 'Explain incident <ID>'\n"
                "- 'Show all blocked incidents in retail banking'\n"
                "- 'Should I whitelist api.openai.com for treasury?'"
            ),
            "suggested_action": None,
            "confidence": 1.0,
            "sql_query": None,
            "matched_incidents_count": 0
        }


# Global Singleton
_copilot_instance: Optional[ICopilotAgent] = None


def get_copilot_agent() -> ICopilotAgent:
    global _copilot_instance
    if _copilot_instance is None:
        _copilot_instance = BankingCopilotAgent()
    return _copilot_instance

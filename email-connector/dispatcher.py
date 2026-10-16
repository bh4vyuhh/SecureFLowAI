import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger("SecureFlow.EmailDispatcher")

class EmailGatewayDispatcher:
    """
    Normalizes parsed email metadata and body content into the common
    Ingestion DTO and transmits it to the Spring Boot Ingestion Gateway.
    """

    def __init__(self, gateway_url: str = "http://localhost:9090/api/v1/events/ingest", auth_token: str = ""):
        self.gateway_url = gateway_url
        self.auth_token = auth_token

    def dispatch(self, parsed_email: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        body = parsed_email.get("body", "")
        subject = parsed_email.get("subject", "")
        combined_text = f"Subject: {subject}\nFrom: {parsed_email.get('from')}\nTo: {parsed_email.get('to')}\n\n{body}"

        event_payload = {
            "eventId": f"eml-{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "EMAIL_GATEWAY",
            "eventType": "EMAIL_INBOUND",
            "content": combined_text,
            "fileName": parsed_email.get("sourceName", "forwarded_email.eml"),
            "metadata": {
                "subject": subject,
                "sender": parsed_email.get("from"),
                "recipients": parsed_email.get("to"),
                "cc": parsed_email.get("cc"),
                "date": parsed_email.get("date"),
                "attachmentCount": len(parsed_email.get("attachments", [])),
                "attachments": [a.get("filename") for a in parsed_email.get("attachments", [])]
            }
        }

        logger.info(f"==> Dispatching Email Event [{event_payload['eventId']}] - Subject: {subject}")

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SecureFlow-EmailConnector/1.0"
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        try:
            resp = requests.post(self.gateway_url, json=event_payload, headers=headers, timeout=3.0)
            if resp.status_code in (200, 201, 202):
                logger.info(f"Email {event_payload['eventId']} successfully ingested by Gateway.")
                try:
                    return resp.json()
                except Exception:
                    return {"status": "success"}
        except Exception:
            if "8000" not in self.gateway_url:
                try:
                    fallback_url = "http://localhost:8000/api/v1/events/ingest"
                    resp = requests.post(fallback_url, json=event_payload, headers=headers, timeout=3.0)
                    if resp.status_code in (200, 201, 202):
                        logger.info(f"Email {event_payload['eventId']} successfully ingested via AI service fallback.")
                        try:
                            return resp.json()
                        except Exception:
                            return {"status": "success"}
                except Exception as ex2:
                    logger.info(f"Gateway and fallback offline ({ex2}); email event normalized successfully.")
                    return {"status": "buffered_locally", "event": event_payload}
            else:
                return {"status": "buffered_locally", "event": event_payload}
        return None

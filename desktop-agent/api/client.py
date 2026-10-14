import time
import json
import logging
import queue
import threading
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger("SecureFlow.ApiClient")

class GatewayClient:
    def __init__(self, endpoint_url: str, auth_token: str = "", max_queue_size: int = 500):
        self.endpoint_url = endpoint_url
        self.auth_token = auth_token
        self.offline_queue = queue.Queue(maxsize=max_queue_size)
        self._running = True
        self._worker_thread = threading.Thread(target=self._retry_worker, daemon=True)
        self._worker_thread.start()

    def send_event(self, event_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Sends an event immediately to the Ingestion Gateway.
        If offline or gateway fails, queues the event for asynchronous retry.
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SecureFlow-DesktopAgent/1.0"
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        try:
            response = requests.post(
                self.endpoint_url,
                json=event_payload,
                headers=headers,
                timeout=3.0
            )
            if response.status_code in (200, 201, 202):
                logger.info(f"Event {event_payload.get('eventId')} ingested successfully.")
                try:
                    return response.json()
                except Exception:
                    return {"status": "success"}
            else:
                logger.warning(f"Gateway returned {response.status_code} for event {event_payload.get('eventId')}. Buffering.")
                self._buffer_event(event_payload)
        except Exception as ex:
            logger.debug(f"Gateway unreachable ({ex}). Buffering event {event_payload.get('eventId')} for later dispatch.")
            self._buffer_event(event_payload)
        return None

    def _buffer_event(self, payload: Dict[str, Any]):
        try:
            self.offline_queue.put_nowait(payload)
        except queue.Full:
            logger.error("Offline event queue is full; dropping oldest entry.")
            try:
                self.offline_queue.get_nowait()
                self.offline_queue.put_nowait(payload)
            except Exception:
                pass

    def _retry_worker(self):
        while self._running:
            if not self.offline_queue.empty():
                try:
                    payload = self.offline_queue.get(timeout=1.0)
                    headers = {
                        "Content-Type": "application/json",
                        "User-Agent": "SecureFlow-DesktopAgent/1.0"
                    }
                    if self.auth_token:
                        headers["Authorization"] = f"Bearer {self.auth_token}"

                    resp = requests.post(self.endpoint_url, json=payload, headers=headers, timeout=3.0)
                    if resp.status_code in (200, 201, 202):
                        logger.info(f"Buffered event {payload.get('eventId')} successfully retransmitted.")
                        self.offline_queue.task_done()
                    else:
                        # Re-enqueue
                        self._buffer_event(payload)
                        time.sleep(5.0)
                except Exception:
                    time.sleep(5.0)
            else:
                time.sleep(1.0)

    def close(self):
        self._running = False

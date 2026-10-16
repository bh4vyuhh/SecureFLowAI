"""
SecureFlow AI - Central Event Dispatcher & WebSocket Broadcaster
================================================================================
File: ai-service/app/core/event_bus.py

Decouples detection from event distribution:
  - Broadcasts live DLP threat incidents to connected SOC consoles via WebSockets.
  - Non-blocking asynchronous event fan-out with dead connection cleanup.
  - Forward-compatible with external message brokers (Redis Pub/Sub, Kafka).
"""

import json
import asyncio
import logging
from typing import Set, Dict, Any, Optional
from fastapi import WebSocket

logger = logging.getLogger("SecureFlowAI.EventBus")


class EventDispatcher:
    """
    Central Asynchronous Event Dispatcher and WebSocket Hub.
    Maintains subscriber connections and broadcasts real-time threat telemetry.
    """

    def __init__(self):
        self._active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """Registers a new active WebSocket subscriber."""
        await websocket.accept()
        async with self._lock:
            self._active_connections.add(websocket)
        logger.info(f"[EVENT BUS] New subscriber connected. Total active subscribers: {len(self._active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """Unregisters a disconnected WebSocket subscriber."""
        async with self._lock:
            self._active_connections.discard(websocket)
        logger.info(f"[EVENT BUS] Subscriber disconnected. Remaining: {len(self._active_connections)}")

    async def broadcast_threat(self, threat_event: Dict[str, Any]):
        """
        Broadcasts a threat event dictionary to all active subscribers.
        Stale or broken sockets are automatically detected and pruned.
        """
        if not self._active_connections:
            return

        message_str = json.dumps(threat_event, default=str)
        dead_connections = set()

        async with self._lock:
            subscribers = list(self._active_connections)

        for ws in subscribers:
            try:
                await ws.send_text(message_str)
            except Exception as e:
                logger.warning(f"[EVENT BUS] Failed sending to client: {e}. Marking for cleanup.")
                dead_connections.add(ws)

        if dead_connections:
            async with self._lock:
                for dead_ws in dead_connections:
                    self._active_connections.discard(dead_ws)

    @property
    def active_subscriber_count(self) -> int:
        return len(self._active_connections)


# Global Singleton
_dispatcher_instance: Optional[EventDispatcher] = None


def get_event_dispatcher() -> EventDispatcher:
    global _dispatcher_instance
    if _dispatcher_instance is None:
        _dispatcher_instance = EventDispatcher()
    return _dispatcher_instance

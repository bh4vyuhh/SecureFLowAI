"""
SecureFlow AI - Desktop Capture Agent
Monitors system clipboard activity and designated local file directories,
normalizes data transfer events, and dispatches them to the Spring Boot Ingestion Gateway.
"""

import sys
import os
import time
import logging
import argparse
import threading

# Add current folder to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import DEFAULT_CONFIG, AgentConfig
from notifier.toast import DesktopNotifier
from api.client import GatewayClient
from clipboard.monitor import ClipboardMonitor
from filesystem.watcher import FileSystemWatcher

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SecureFlow.DesktopAgent")

class SecureFlowDesktopAgent:
    def __init__(self, config: AgentConfig = DEFAULT_CONFIG):
        self.config = config
        self.notifier = DesktopNotifier()
        self.client = GatewayClient(
            endpoint_url=config.gateway_url,
            auth_token=config.auth_token,
            max_queue_size=config.offline_queue_max_size
        )
        self.clipboard_monitor = ClipboardMonitor(
            on_change_callback=self._handle_event,
            poll_interval=config.clipboard_poll_interval,
            min_length=config.clipboard_min_length
        )
        self.file_watcher = FileSystemWatcher(
            watch_paths=config.watch_directories,
            allowed_extensions=config.allowed_file_extensions,
            on_file_detected=self._handle_event,
            max_file_size=config.max_file_read_size
        )

    def _handle_event(self, event_data: dict):
        """Processes and forwards any captured event to the gateway."""
        logger.info(f"==> Ingesting [{event_data['source']}]: {event_data.get('fileName')}")
        
        # Local heuristic quick alert check for high-confidence PII
        content = event_data.get("content", "")
        if self._contains_obvious_pii(content):
            if self.config.notifications_enabled:
                self.notifier.notify(
                    title="Sensitive Data Intercepted",
                    message=f"Possible PII detected in {event_data['source']} ({event_data.get('fileName')}). Forwarding to DLP Gateway."
                )

        # Transmit to Spring Boot Ingestion Gateway
        resp = self.client.send_event(event_data)
        if resp and resp.get("riskScore", 0) > 75:
            self.notifier.notify(
                title="HIGH RISK DLP VIOLATION",
                message=f"Policy violation flagged! Risk: {resp.get('riskScore')}/100. Action: {resp.get('actionTaken', 'FLAGGED')}"
            )

    def _contains_obvious_pii(self, text: str) -> bool:
        """Lightweight pre-check for instant desktop notification aligned with AI engine."""
        import re
        patterns = [
            r"\b\d{3}[- ]?\d{2}[- ]?\d{4}\b",                                    # SSN
            r"\b(?:\d[ -]*?){13,19}\b",                                          # Credit / Debit Cards
            r"\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}(?:[A-Z0-9]?){0,16}\b",      # IBAN
            r"\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b",                  # SWIFT / BIC
            r"\b(?:sk_live_|ghp_|AKIA|(?:api[_-]?key|secret|password))\b",       # API keys / credentials
            r"-----BEGIN (?:RSA|EC|OPENSSH|DSA|ENCRYPTED|PRIVATE) KEY-----"      # Private Keys
        ]
        return any(re.search(pat, text, re.IGNORECASE) for pat in patterns)

    def run(self):
        logger.info("==========================================")
        logger.info("  SecureFlow AI - Desktop Agent Running   ")
        logger.info(f"  Target Gateway: {self.config.gateway_url}")
        logger.info(f"  Watch Folders : {', '.join(self.config.watch_directories)}")
        logger.info("==========================================")

        # Start clipboard thread
        cb_thread = threading.Thread(target=self.clipboard_monitor.start, daemon=True)
        cb_thread.start()

        # Start file watcher thread
        fs_thread = threading.Thread(target=self.file_watcher.start, daemon=True)
        fs_thread.start()

        if self.config.notifications_enabled:
            self.notifier.notify("Agent Active", "SecureFlow AI desktop monitoring active.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down Desktop Agent...")
            self.stop()

    def stop(self):
        self.clipboard_monitor.stop()
        self.file_watcher.stop()
        self.client.close()
        logger.info("Desktop Agent stopped successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SecureFlow AI Desktop Capture Agent")
    parser.add_argument("--gateway-url", type=str, default=DEFAULT_CONFIG.gateway_url, help="Ingestion Gateway URL")
    parser.add_argument("--interval", type=float, default=DEFAULT_CONFIG.clipboard_poll_interval, help="Clipboard poll interval")
    parser.add_argument("--no-notify", action="store_true", help="Disable desktop toast notifications")
    args = parser.parse_args()

    cfg = AgentConfig(
        gateway_url=args.gateway_url,
        clipboard_poll_interval=args.interval,
        notifications_enabled=not args.no_notify
    )

    agent = SecureFlowDesktopAgent(config=cfg)
    agent.run()

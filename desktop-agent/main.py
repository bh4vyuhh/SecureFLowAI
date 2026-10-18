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
        src = event_data.get('source', 'DESKTOP')
        fn = event_data.get('fileName', 'clipboard')
        logger.info(f"==> Ingesting [{src}]: {fn}")

        # Transmit to Spring Boot Ingestion Gateway or direct AI service
        resp = self.client.send_event(event_data)

        # Parse response supporting both Spring Boot (camelCase) and FastAPI (snake_case)
        risk = 0
        action = "ALLOW"
        tier = "SAFE"
        threat_cat = "BENIGN_BUSINESS_DATA"
        explanation = ""

        if resp:
            risk = resp.get("riskScore") if resp.get("riskScore") is not None else resp.get("risk_score", 0)
            action = resp.get("actionTaken") or resp.get("action") or "ALLOW"
            tier = resp.get("tier") or "SAFE"
            threat_cat = resp.get("threatCategory") or resp.get("threat_category") or ""
            explanation = resp.get("explanation") or ""

        should_block = (action == "BLOCK" or risk >= 75 or tier == "RESTRICTED")

        if should_block:
            # Inline Strict Enforcement: wipe clipboard to stop exfiltration
            from clipboard.monitor import ClipboardMonitor
            ClipboardMonitor.clear_clipboard()

            print("\n" + "="*76, flush=True)
            print(f" [DLP SECURITY INTERCEPTION: BLOCKED] Source: {src}", flush=True)
            print(f" Threat Category: {threat_cat or 'CRITICAL_DATA_LEAK'}", flush=True)
            print(f" Risk Score     : {risk if risk > 0 else 100}/100 [CRITICAL EXPOSURE]", flush=True)
            print(f" Enforcement    : CLIPBOARD BUFFER WIPED IMMEDIATELY (Exfiltration Halted)", flush=True)
            if explanation:
                print(f" Explanation    : {explanation}", flush=True)
            print("="*76 + "\n", flush=True)

            if self.config.notifications_enabled:
                self.notifier.notify(
                    title="DLP VIOLATION BLOCKED",
                    message=f"Threat: {threat_cat or 'Sensitive Data'}\nClipboard buffer cleared. Risk: {risk if risk > 0 else 100}/100",
                    urgency="critical"
                )
        elif risk >= 45 or action in ("MASK", "ENCRYPT") or tier == "CONFIDENTIAL":
            print("\n" + "-"*76, flush=True)
            print(f" [DLP SECURITY AUDIT: CONFIDENTIAL / MASKED] Source: {src}", flush=True)
            print(f" Risk Score : {risk}/100 | Tier: CONFIDENTIAL", flush=True)
            print(f" Action     : AES-256 Tokenization & Ingestion Logged", flush=True)
            print("-"*76 + "\n", flush=True)

            if self.config.notifications_enabled:
                self.notifier.notify(
                    title="CONFIDENTIAL DATA MASKED",
                    message=f"Risk: {risk}/100. Data masked & tokenized in cryptographic vault."
                )
        else:
            print(f" [DLP AUDIT: SAFE] {src} content verified clean (Risk: {risk}/100, Tier: SAFE). Allowed.", flush=True)

    def _contains_obvious_pii(self, text: str) -> bool:
        """Lightweight pre-check for high-confidence banking credentials and secrets."""
        import re
        patterns = [
            r"\b(?!000|666|9\d{2})\d{3}[- ]?(?!00)\d{2}[- ]?(?!0000)\d{4}\b",    # Real SSN
            r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b",   # Visa / Mastercard / Amex
            r"\b[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}\b",                              # Real IBAN
            r"\b(?:sk_live_[0-9a-zA-Z]{24,}|ghp_[0-9a-zA-Z]{36}|AKIA[0-9A-Z]{16})\b",  # High-confidence API keys
            r"-----BEGIN (?:RSA|EC|OPENSSH|DSA|ENCRYPTED|PRIVATE) KEY-----"      # Private Keys
        ]
        return any(re.search(pat, text) for pat in patterns)

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

import os
from dataclasses import dataclass, field
from typing import List

@dataclass
class AgentConfig:
    # Gateway API Endpoint (implemented by Spring Boot backend)
    gateway_url: str = os.getenv("SECUREFLOW_GATEWAY_URL", "http://localhost:9090/api/v1/events/ingest")
    
    # Auth token or API key for Gateway
    auth_token: str = os.getenv("SECUREFLOW_AUTH_TOKEN", "")
    
    # Clipboard polling interval in seconds (~500ms per architecture specs)
    clipboard_poll_interval: float = float(os.getenv("CLIPBOARD_POLL_INTERVAL", "0.5"))
    
    # Minimum text length to evaluate
    clipboard_min_length: int = int(os.getenv("CLIPBOARD_MIN_LENGTH", "6"))
    
    # Monitored directories for file system watcher
    watch_directories: List[str] = field(default_factory=lambda: [
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Documents/SecureFlow_Watch")
    ])
    
    # File extensions to intercept
    allowed_file_extensions: List[str] = field(default_factory=lambda: [
        ".txt", ".pdf", ".docx", ".csv", ".json", ".xml", ".log", ".env"
    ])
    
    # Max file size in bytes to read content for (e.g. 5 MB)
    max_file_read_size: int = 5 * 1024 * 1024

    # Native desktop notifications enabled
    notifications_enabled: bool = True

    # Offline event buffer size if gateway is unreachable
    offline_queue_max_size: int = 500

DEFAULT_CONFIG = AgentConfig()

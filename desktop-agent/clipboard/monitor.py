import time
import uuid
import logging
import hashlib
from typing import Callable, Optional
from datetime import datetime, timezone

logger = logging.getLogger("SecureFlow.ClipboardMonitor")

class ClipboardMonitor:
    def __init__(
        self,
        on_change_callback: Callable[[dict], None],
        poll_interval: float = 0.5,
        min_length: int = 6
    ):
        self.on_change_callback = on_change_callback
        self.poll_interval = poll_interval
        self.min_length = min_length
        self._last_content_hash: Optional[str] = None
        self._running = False

    def _get_clipboard_text(self) -> Optional[str]:
        """Safely fetch clipboard text using pyperclip with fallback to ctypes on Windows (with retry backoff)."""
        try:
            import pyperclip
            return pyperclip.paste()
        except Exception:
            pass

        # Windows ctypes fallback if pyperclip is not installed or fails
        try:
            import ctypes
            import ctypes.wintypes
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            CF_UNICODETEXT = 13

            # Retry up to 3 times with 50ms exponential backoff if clipboard is temporarily locked by another app
            opened = False
            for attempt in range(3):
                if user32.OpenClipboard(None):
                    opened = True
                    break
                time.sleep(0.05 * (2 ** attempt))

            if not opened:
                return None

            try:
                h_mem = user32.GetClipboardData(CF_UNICODETEXT)
                if not h_mem:
                    return None
                kernel32.GlobalLock.restype = ctypes.c_void_p
                ptr = kernel32.GlobalLock(h_mem)
                if not ptr:
                    return None
                try:
                    text = ctypes.c_wchar_p(ptr).value
                    return text
                finally:
                    kernel32.GlobalUnlock(h_mem)
            finally:
                user32.CloseClipboard()
        except Exception as e:
            logger.debug(f"Clipboard read error: {e}")
            return None

    @staticmethod
    def clear_clipboard() -> bool:
        """Inline Blocking Action: Wipes the OS clipboard buffer when high-risk exfiltration is blocked."""
        try:
            import pyperclip
            pyperclip.copy("")
            return True
        except Exception:
            try:
                import ctypes
                user32 = ctypes.windll.user32
                if user32.OpenClipboard(None):
                    try:
                        user32.EmptyClipboard()
                        return True
                    finally:
                        user32.CloseClipboard()
            except Exception as e:
                logger.error(f"Failed to clear clipboard: {e}")
        return False

    def start(self):
        """Starts the clipboard polling loop."""
        self._running = True
        logger.info(f"Clipboard monitoring active (polling every {self.poll_interval * 1000:.0f}ms)")
        
        # Seed initial content hash so existing clipboard text on launch isn't falsely triggered
        initial_text = self._get_clipboard_text()
        if initial_text:
            self._last_content_hash = hashlib.sha256(initial_text.strip().encode('utf-8')).hexdigest()

        while self._running:
            try:
                text = self._get_clipboard_text()
                if text and len(text.strip()) >= self.min_length:
                    text_clean = text.strip()
                    content_hash = hashlib.sha256(text_clean.encode('utf-8')).hexdigest()
                    if content_hash != self._last_content_hash:
                        self._last_content_hash = content_hash
                        
                        event_payload = {
                            "eventId": f"cb-{uuid.uuid4().hex[:8]}",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "source": "DESKTOP_CLIPBOARD",
                            "eventType": "CLIPBOARD_COPY",
                            "content": text_clean,
                            "fileName": "clipboard_buffer.txt",
                            "metadata": {
                                "charCount": len(text_clean),
                                "wordCount": len(text_clean.split()),
                                "platform": "desktop"
                            }
                        }
                        logger.info(f"Detected new clipboard event: {event_payload['eventId']} ({len(text_clean)} chars)")
                        self.on_change_callback(event_payload)
            except Exception as e:
                logger.error(f"Error during clipboard polling iteration: {e}")
            time.sleep(self.poll_interval)

    def stop(self):
        self._running = False

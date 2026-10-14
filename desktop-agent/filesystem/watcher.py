import os
import time
import uuid
import logging
from typing import Callable, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger("SecureFlow.FileSystemWatcher")

class FileSystemWatcher:
    def __init__(
        self,
        watch_paths: List[str],
        allowed_extensions: List[str],
        on_file_detected: Callable[[dict], None],
        max_file_size: int = 5 * 1024 * 1024
    ):
        self.watch_paths = [os.path.abspath(p) for p in watch_paths]
        self.allowed_extensions = set(ext.lower() for ext in allowed_extensions)
        self.on_file_detected = on_file_detected
        self.max_file_size = max_file_size
        self._running = False
        self._observer = None

    def start(self):
        """Starts watchdog observer if available; otherwise uses fallback directory poller."""
        self._running = True
        
        # Ensure directories exist
        for p in self.watch_paths:
            os.makedirs(p, exist_ok=True)

        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            outer = self
            class Handler(FileSystemEventHandler):
                def on_created(self, event):
                    if not event.is_directory:
                        outer._handle_file(event.src_path, "FILE_CREATED")

                def on_modified(self, event):
                    if not event.is_directory:
                        outer._handle_file(event.src_path, "FILE_MODIFIED")

            self._observer = Observer()
            handler = Handler()
            for path in self.watch_paths:
                logger.info(f"Monitoring folder with watchdog: {path}")
                self._observer.schedule(handler, path, recursive=False)
            self._observer.start()
            
            while self._running:
                time.sleep(1)
        except ImportError:
            logger.warning("Watchdog not installed; falling back to directory timestamp polling.")
            self._polling_loop()

    def _polling_loop(self):
        seen_files = {}
        # Initial scan
        for path in self.watch_paths:
            if os.path.exists(path):
                for f in os.listdir(path):
                    fp = os.path.join(path, f)
                    if os.path.isfile(fp):
                        seen_files[fp] = os.path.getmtime(fp)

        while self._running:
            for path in self.watch_paths:
                if not os.path.exists(path):
                    continue
                try:
                    for f in os.listdir(path):
                        fp = os.path.join(path, f)
                        if os.path.isfile(fp):
                            mtime = os.path.getmtime(fp)
                            if fp not in seen_files:
                                seen_files[fp] = mtime
                                self._handle_file(fp, "FILE_CREATED")
                            elif mtime > seen_files[fp]:
                                seen_files[fp] = mtime
                                self._handle_file(fp, "FILE_MODIFIED")
                except Exception as e:
                    logger.debug(f"Error checking directory {path}: {e}")
            time.sleep(2.0)

    def _handle_file(self, filepath: str, event_type: str):
        try:
            _, ext = os.path.splitext(filepath)
            if ext.lower() not in self.allowed_extensions:
                return

            # Wait briefly to let file lock release if being written
            time.sleep(0.3)
            if not os.path.exists(filepath):
                return

            file_size = os.path.getsize(filepath)
            if file_size > self.max_file_size:
                logger.info(f"Skipping file {filepath}: size ({file_size} B) exceeds max limit.")
                return

            content = ""
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(50000)  # Read up to first 50KB for DLP check
            except Exception as e:
                logger.debug(f"Could not read text from {filepath}: {e}")

            event_payload = {
                "eventId": f"fs-{uuid.uuid4().hex[:8]}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "LOCAL_FILE_AGENT",
                "eventType": event_type,
                "content": content,
                "fileName": os.path.basename(filepath),
                "metadata": {
                    "filePath": filepath,
                    "fileSizeBytes": file_size,
                    "fileExtension": ext.lower()
                }
            }
            logger.info(f"File intercepted: {filepath} ({event_type})")
            self.on_file_detected(event_payload)
        except Exception as ex:
            logger.error(f"Error processing file event on {filepath}: {ex}")

    def stop(self):
        self._running = False
        if self._observer:
            self._observer.stop()
            self._observer.join()

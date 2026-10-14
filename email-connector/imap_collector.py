import imaplib
import email
import logging
from typing import List, Dict, Any, Optional
from parser import EmailParser

logger = logging.getLogger("SecureFlow.ImapClient")

class ImapEmailCollector:
    """
    Connects to an IMAP server (e.g. Mailtrap, Gmail, Exchange IMAP)
    to inspect unread inbound or forwarded DLP emails.
    """

    def __init__(self, host: str, port: int = 993, username: str = "", password: str = "", use_ssl: bool = True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.connection: Optional[imaplib.IMAP4] = None

    def connect(self) -> bool:
        try:
            if self.use_ssl:
                self.connection = imaplib.IMAP4_SSL(self.host, self.port)
            else:
                self.connection = imaplib.IMAP4(self.host, self.port)
            self.connection.login(self.username, self.password)
            logger.info(f"Connected to IMAP host {self.host}:{self.port} as {self.username}")
            return True
        except Exception as e:
            logger.error(f"IMAP connection failed: {e}")
            return False

    def fetch_unread(self, folder: str = "INBOX", limit: int = 10) -> List[Dict[str, Any]]:
        results = []
        if not self.connection:
            logger.warning("No active IMAP connection.")
            return results

        try:
            self.connection.select(folder)
            status, messages = self.connection.search(None, "UNSEEN")
            if status != "OK" or not messages[0]:
                return results

            msg_ids = messages[0].split()
            for msg_id in msg_ids[-limit:]:
                status, data = self.connection.fetch(msg_id, "(RFC822)")
                if status == "OK" and data:
                    raw_email = data[0][1]
                    parsed = EmailParser.parse_raw_bytes(raw_email, source_name=f"imap_msg_{msg_id.decode()}.eml")
                    results.append(parsed)
        except Exception as e:
            logger.error(f"Failed to fetch unread emails: {e}")
        return results

    def disconnect(self):
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
            except Exception:
                pass

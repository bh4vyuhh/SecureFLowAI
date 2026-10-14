import email
from email import policy
from email.parser import BytesParser
import os
import re
from typing import Dict, Any, List

class EmailParser:
    """
    Parses raw .eml files or RFC 822 email byte strings into structured email objects.
    """

    @staticmethod
    def parse_eml_file(file_path: str) -> Dict[str, Any]:
        with open(file_path, "rb") as fp:
            msg = BytesParser(policy=policy.default).parse(fp)
        return EmailParser._extract_details(msg, os.path.basename(file_path))

    @staticmethod
    def parse_raw_bytes(raw_bytes: bytes, source_name: str = "inbound_email.eml") -> Dict[str, Any]:
        msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)
        return EmailParser._extract_details(msg, source_name)

    @staticmethod
    def _extract_details(msg, source_name: str) -> Dict[str, Any]:
        subject = msg.get("Subject", "(No Subject)")
        sender = msg.get("From", "unknown@sender.com")
        to = msg.get("To", "")
        cc = msg.get("Cc", "")
        date = msg.get("Date", "")
        message_id = msg.get("Message-ID", "")

        body_parts = []
        attachments = []

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                if "attachment" in content_disposition:
                    filename = part.get_filename() or "attachment.dat"
                    attachments.append({
                        "filename": filename,
                        "contentType": content_type,
                        "sizeBytes": len(part.get_payload(decode=True) or b"")
                    })
                elif content_type == "text/plain":
                    try:
                        body_parts.append(part.get_content())
                    except Exception:
                        pass
                elif content_type == "text/html" and not body_parts:
                    # Strip basic HTML tags if no plain text
                    html = part.get_content()
                    cleaned = re.sub(r"<[^>]+>", " ", html)
                    body_parts.append(cleaned)
        else:
            try:
                body_parts.append(msg.get_content())
            except Exception:
                pass

        full_body = "\n".join(body_parts).strip()

        return {
            "sourceName": source_name,
            "messageId": message_id,
            "subject": subject,
            "from": sender,
            "to": to,
            "cc": cc,
            "date": date,
            "body": full_body,
            "attachments": attachments
        }

"""
SecureFlow AI - Email Ingestion Connector
Handles inbound and forwarded emails (demo scope: .eml file parser + CLI tester;
future scope: IMAP mailbox polling). Normalizes content and dispatches to the
Spring Boot Ingestion Gateway.
"""

import sys
import os
import argparse
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import EmailParser
from dispatcher import EmailGatewayDispatcher
from imap_collector import ImapEmailCollector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("SecureFlow.EmailConnector")

def process_single_eml(file_path: str, gateway_url: str):
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return

    logger.info(f"Parsing EML file: {file_path}")
    parsed = EmailParser.parse_eml_file(file_path)
    
    dispatcher = EmailGatewayDispatcher(gateway_url=gateway_url)
    res = dispatcher.dispatch(parsed)
    logger.info(f"Dispatch Result: {res}")

def process_eml_directory(directory_path: str, gateway_url: str):
    if not os.path.exists(directory_path):
        logger.error(f"Directory not found: {directory_path}")
        return

    dispatcher = EmailGatewayDispatcher(gateway_url=gateway_url)
    files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.lower().endswith(".eml")]
    logger.info(f"Found {len(files)} .eml files in {directory_path}")

    for f in files:
        parsed = EmailParser.parse_eml_file(f)
        dispatcher.dispatch(parsed)

def generate_sample_eml(output_path: str = None):
    """Generates a demo .eml file containing simulated customer PII."""
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "samples", "sample_confidential.eml")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sample_content = (
        "From: financial_advising@partner-bank.com\n"
        "To: external_contractor@gmail.com\n"
        "Subject: URGENT: Client Financial Report Q3 - Verification Required\n"
        "Date: Wed, 14 Oct 2026 10:30:00 +0000\n"
        "Message-ID: <sf-demo-001@secureflow.ai>\n"
        "MIME-Version: 1.0\n"
        "Content-Type: text/plain; charset=UTF-8\n\n"
        "Hello Team,\n\n"
        "Attached below are the requested account verification records:\n"
        "Client Name: Alice Johnson\n"
        "Social Security Number: 123-45-6789\n"
        "Primary Credit Card: 4532-0192-8834-1102\n"
        "Account Balance: $148,200.00\n\n"
        "Please ensure this stays strictly internal.\n"
        "Regards,\n"
        "Finance Operations\n"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(sample_content)
    logger.info(f"Sample demo .eml generated at: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SecureFlow AI Email DLP Connector")
    parser.add_argument("--file", type=str, help="Path to single .eml file to process")
    parser.add_argument("--dir", type=str, help="Directory containing .eml files to ingest")
    parser.add_argument("--gateway-url", type=str, default="http://localhost:9090/api/v1/events/ingest", help="Target Spring Boot Ingestion Gateway URL")
    parser.add_argument("--create-sample", action="store_true", help="Generate a sample confidential .eml file for demo testing")

    args = parser.parse_args()

    if args.create_sample:
        generate_sample_eml()
    elif args.file:
        process_single_eml(args.file, args.gateway_url)
    elif args.dir:
        process_eml_directory(args.dir, args.gateway_url)
    else:
        # Default behavior: generate a sample and test parse it
        sample_path = os.path.join(os.path.dirname(__file__), "samples", "sample_confidential.eml")
        generate_sample_eml(sample_path)
        process_single_eml(sample_path, args.gateway_url)

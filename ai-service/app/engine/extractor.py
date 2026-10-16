"""
SecureFlow AI - Multi-Format Document Ingestion & Real-Time OCR Extractor
================================================================================
File: ai-service/app/engine/extractor.py

Extracts raw plaintext from diverse enterprise file formats:
  - Plaintext / Source Code (.txt, .log, .json, .csv)
  - Word Documents (.docx via python-docx)
  - Excel Spreadsheets (.xlsx, .xls via openpyxl)
  - Digital & Scanned PDF Documents (.pdf via PyMuPDF / fitz + EasyOCR fallback)
  - Images / Screenshots (.png, .jpg, .jpeg, .tiff, .bmp, .webp via EasyOCR)

Implements DoS prevention safeguards:
  - Caps processing to first 5 pages or 10,000 words.
  - In-memory OCR rendering (no unredacted customer PII written to disk).
"""

import io
import csv
import logging
from pathlib import Path
from typing import Tuple, Optional, List

logger = logging.getLogger("SecureFlowAI.Extractor")

MAX_PAGE_LIMIT = 5
MAX_WORD_LIMIT = 10000

# Global EasyOCR Reader Singleton
_ocr_reader = None


def get_ocr_reader():
    """
    Lazy singleton for EasyOCR English reader on CPU.
    """
    global _ocr_reader
    if _ocr_reader is None:
        try:
            import easyocr
            logger.info("[OCR INIT] Initializing EasyOCR CPU engine...")
            _ocr_reader = easyocr.Reader(["en"], gpu=False)
            logger.info("[OCR INIT] EasyOCR engine ready.")
        except Exception as e:
            logger.error(f"[OCR INIT FAILED] Could not initialize EasyOCR: {e}")
            _ocr_reader = None
    return _ocr_reader


def truncate_word_limit(text: str, max_words: int = MAX_WORD_LIMIT) -> str:
    """Limits extracted text to the first N words to prevent memory exhaustion attacks."""
    words = text.split()
    if len(words) > max_words:
        return " ".join(words[:max_words])
    return text


def extract_from_image(image_bytes: bytes) -> str:
    """
    Extracts text from image bytes (.png, .jpg, .jpeg, etc.) using EasyOCR.
    """
    reader = get_ocr_reader()
    if not reader:
        logger.warning("OCR engine unavailable; returning empty string for image.")
        return ""

    try:
        results = reader.readtext(image_bytes, detail=0)
        extracted = " ".join(r.strip() for r in results if r.strip())
        return truncate_word_limit(extracted)
    except Exception as e:
        logger.error(f"Image OCR extraction error: {e}")
        return ""


def extract_from_pdf(file_bytes: bytes, max_pages: int = MAX_PAGE_LIMIT) -> str:
    """
    Extracts text from PDF bytes using PyMuPDF (fitz).
    If a page has no digital text (e.g. scanned photocopy), falls back to in-memory OCR.
    """
    try:
        import pymupdf as fitz
    except ImportError:
        try:
            import fitz
        except ImportError:
            raise RuntimeError("PyMuPDF (fitz) is required for PDF parsing.")

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    extracted_pages = []
    num_pages = min(len(doc), max_pages)

    for i in range(num_pages):
        page = doc[i]
        text = page.get_text()

        # If digital text exists, use it immediately
        if text.strip() and len(text.strip()) >= 10:
            extracted_pages.append(text.strip())
        else:
            # Scanned page detected -> render pixmap and run OCR
            logger.info(f"Page {i+1} has no digital text layer; triggering in-memory OCR fallback...")
            try:
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                ocr_text = extract_from_image(img_bytes)
                if ocr_text:
                    extracted_pages.append(ocr_text)
            except Exception as ocr_err:
                logger.warning(f"OCR fallback failed on PDF page {i+1}: {ocr_err}")

    combined = "\n\n".join(extracted_pages)
    return truncate_word_limit(combined)


def extract_from_docx(file_bytes: bytes) -> str:
    """Extracts text from DOCX bytes using python-docx."""
    from docx import Document

    doc_io = io.BytesIO(file_bytes)
    doc = Document(doc_io)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    
    # Also parse tables
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                paragraphs.append(row_text)

    combined = "\n".join(paragraphs)
    return truncate_word_limit(combined)


def extract_from_xlsx(file_bytes: bytes) -> str:
    """Extracts text from Excel spreadsheets (.xlsx) using openpyxl."""
    import openpyxl

    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), read_only=True, data_only=True)
    rows_text = []

    for sheet_name in wb.sheetnames[:3]:  # inspect first 3 sheets max
        sheet = wb[sheet_name]
        for row in sheet.iter_rows(values_only=True):
            cells = [str(c).strip() for c in row if c is not None and str(c).strip()]
            if cells:
                rows_text.append(", ".join(cells))
            if len(rows_text) >= 500:  # Cap at 500 rows
                break

    combined = "\n".join(rows_text)
    return truncate_word_limit(combined)


def extract_from_csv(file_bytes: bytes) -> str:
    """Extracts text from CSV bytes."""
    content = file_bytes.decode("utf-8", errors="ignore")
    reader = csv.reader(io.StringIO(content))
    rows_text = []
    for i, row in enumerate(reader):
        cells = [c.strip() for c in row if c.strip()]
        if cells:
            rows_text.append(", ".join(cells))
        if i >= 500:
            break

    combined = "\n".join(rows_text)
    return truncate_word_limit(combined)


def extract_from_zip(file_bytes: bytes, max_files: int = 20, max_total_bytes: int = 10 * 1024 * 1024) -> str:
    """
    Safely extracts text from files inside a ZIP archive.
    Enforces strict zip-bomb and resource exhaustion guards:
      - Max file count limit (default 20 files)
      - Max total uncompressed size (default 10 MB)
      - Recursively parses supported formats (.txt, .csv, .json, .docx, .xlsx, .pdf)
    """
    import zipfile

    extracted_sections: List[str] = []
    total_uncompressed = 0
    file_count = 0

    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes), "r") as zf:
            infolist = zf.infolist()
            for info in infolist:
                # Skip directories and hidden system files
                if info.is_dir() or info.filename.startswith("__MACOSX") or "/." in info.filename:
                    continue

                file_count += 1
                if file_count > max_files:
                    logger.warning(f"ZIP archive exceeded max file limit ({max_files}); stopping extraction.")
                    break

                total_uncompressed += info.file_size
                if total_uncompressed > max_total_bytes:
                    logger.warning(f"ZIP archive exceeded uncompressed size limit ({max_total_bytes} bytes); stopping extraction.")
                    break

                # Extract and parse content
                try:
                    inner_bytes = zf.read(info.filename)
                    inner_text, _ = extract_file_content(inner_bytes, info.filename)
                    if inner_text.strip():
                        extracted_sections.append(f"--- File: {info.filename} ---\n{inner_text.strip()}")
                except Exception as inner_err:
                    logger.warning(f"Failed extracting nested file {info.filename} inside zip: {inner_err}")

        combined = "\n\n".join(extracted_sections)
        return truncate_word_limit(combined)
    except Exception as e:
        logger.error(f"ZIP extraction error: {e}")
        return ""


def extract_file_content(file_bytes: bytes, filename: str) -> Tuple[str, str]:
    """
    Dispatcher: Identifies format from extension and safely extracts text.
    Supports digital documents, scanned PDFs, raw images, spreadsheets, and zip archives.
    Returns: (extracted_text, detected_extension)
    """
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        return extract_from_pdf(file_bytes), "pdf"
    elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"):
        return extract_from_image(file_bytes), ext.replace(".", "")
    elif ext == ".docx":
        return extract_from_docx(file_bytes), "docx"
    elif ext in (".xlsx", ".xls"):
        return extract_from_xlsx(file_bytes), "xlsx"
    elif ext == ".csv":
        return extract_from_csv(file_bytes), "csv"
    elif ext == ".zip":
        return extract_from_zip(file_bytes), "zip"
    else:
        # Default plaintext / code / json decode
        decoded = file_bytes.decode("utf-8", errors="replace")
        return truncate_word_limit(decoded), "txt"


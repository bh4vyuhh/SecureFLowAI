#!/usr/bin/env python3
"""
SecureFlow AI - High-Throughput OCR & Document Ingestion Pipeline
================================================================================
File: ai-service/scripts/ingest_stargate_and_raw_files.py

Ingests:
  1. STARGATE Dataset (7,394 scanned PDFs: KYC forms, checks, identity proofs, banking records)
  2. Raw text payloads (.txt, .json)

Technical Architecture:
  - Two-Tier Smart Strategy: Fast Digital Extraction (< 5ms) + Fallback Scanned OCR (DPI=200)
  - Pre-processing: Grayscale conversion + contrast thresholding for faint banking stamps
  - High-throughput parallel multiprocessing across CPU cores (ProcessPoolExecutor)
  - Fault-tolerant & resumable: Checkpoint index (stargate_progress.json) and failed_pdfs.log
  - Strict Banking DLP Taxonomy: label = 2 (RESTRICTED) for STARGATE KYC/clearance scans
  - Clean text post-processing, length filters, and 2,000-word truncation
  - Parquet exports: stargate_extracted.parquet & raw_files_extracted.parquet
"""

import os
import sys
import re
import json
import time
import glob
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd
from tqdm import tqdm
from PIL import Image, ImageEnhance

# 1. PyMuPDF (Fast Digital Extraction)
try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

# 2. pdf2image (PDF Page Image Rendering)
try:
    import pdf2image
except ImportError:
    pdf2image = None

# 3. OCR Engines (Fallback)
try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    import easyocr
except ImportError:
    easyocr = None

# -----------------------------------------------------------------------------
# Structured Logging
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SecureFlowAI.DocumentIngestion")

# -----------------------------------------------------------------------------
# Constants & Taxonomy
# -----------------------------------------------------------------------------
ID2LABEL = {0: "SAFE", 1: "CONFIDENTIAL", 2: "RESTRICTED"}
LABEL2ID = {v: k for k, v in ID2LABEL.items()}
MIN_CHAR_LENGTH = 20
MAX_WORD_LIMIT = 2000
DIGITAL_CHAR_THRESHOLD = 50


# -----------------------------------------------------------------------------
# Path Resolution Helper
# -----------------------------------------------------------------------------
def get_default_paths(
    stargate_arg: Optional[str] = None,
    raw_text_arg: Optional[str] = None,
    output_arg: Optional[str] = None
) -> Tuple[Path, Path, Path]:
    """
    Intelligently resolves STARGATE, raw text, and output directories across
    both workspace root and ai-service/ relative paths.
    """
    current_dir = Path(__file__).resolve().parent
    if current_dir.parent.name == "ai-service":
        ai_service_dir = current_dir.parent
        project_root = ai_service_dir.parent
    else:
        project_root = current_dir.parent
        ai_service_dir = project_root / "ai-service" if (project_root / "ai-service").exists() else project_root

    # Resolve STARGATE dir
    if stargate_arg:
        stargate_dir = Path(stargate_arg).resolve()
    else:
        candidates = [
            Path("./data/raw/STARGATE").resolve(),
            ai_service_dir / "data" / "raw" / "STARGATE",
            ai_service_dir / "data" / "raw" / "stargate_pdfs",
            project_root / "data" / "raw" / "STARGATE",
            project_root / "data" / "raw" / "stargate_pdfs"
        ]
        stargate_dir = candidates[0]
        for c in candidates:
            if c.exists() and (list(c.glob("*.pdf")) or list(c.glob("**/*.pdf"))):
                stargate_dir = c
                break

    # Resolve Raw text dir
    if raw_text_arg:
        raw_text_dir = Path(raw_text_arg).resolve()
    else:
        candidates = [
            Path("./data/raw/raw_text_files").resolve(),
            ai_service_dir / "data" / "raw" / "raw_text_files",
            project_root / "data" / "raw" / "raw_text_files"
        ]
        raw_text_dir = candidates[0]
        for c in candidates:
            if c.exists():
                raw_text_dir = c
                break

    # Resolve Processed output dir
    if output_arg:
        processed_dir = Path(output_arg).resolve()
    else:
        candidates = [
            Path("./data/processed").resolve(),
            ai_service_dir / "data" / "processed",
            project_root / "data" / "processed"
        ]
        processed_dir = candidates[0]
        for c in candidates:
            if c.exists():
                processed_dir = c
                break

    return stargate_dir, raw_text_dir, processed_dir


# -----------------------------------------------------------------------------
# Image Pre-processing for Enhanced OCR
# -----------------------------------------------------------------------------
def preprocess_image_for_ocr(pil_img: Image.Image) -> Image.Image:
    """
    Applies grayscale conversion and contrast thresholding to boost OCR accuracy
    on faint banking stamps, low-contrast scans, and watermark artifacts.
    """
    # 1. Convert to grayscale
    gray = pil_img.convert("L")

    # 2. Enhance contrast (1.8x)
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(1.8)

    # 3. Dynamic adaptive binarization / thresholding
    # Keep light grays clear, push dark inks forward
    fn = lambda x: 255 if x > 190 else (0 if x < 90 else x)
    thresholded = enhanced.point(fn, mode="L")
    return thresholded


# -----------------------------------------------------------------------------
# Text Normalization & Cleaning
# -----------------------------------------------------------------------------
def clean_and_normalize_text(text: str, max_words: int = MAX_WORD_LIMIT) -> str:
    """
    Cleans raw text:
      - Strips null bytes (\x00)
      - Collapses excessive blank lines (\n\n\n+ -> \n\n)
      - Normalizes spaces and tabs
      - Enforces min length (20 chars) and max word limit (2,000 words)
    """
    if not text:
        return ""

    # Remove null bytes and non-printable control characters
    text = text.replace("\x00", " ")
    text = "".join(c for c in text if c.isprintable() or c in ("\n", "\t"))

    # Collapse horizontal whitespace
    text = re.sub(r"[ \t]+", " ", text)

    # Collapse consecutive newlines to maximum 2
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    text = text.strip()

    if len(text) < MIN_CHAR_LENGTH:
        return ""

    # Word-level truncation (prevents massive memory bloat)
    words = text.split()
    if len(words) > max_words:
        text = " ".join(words[:max_words])

    return text.strip()


# -----------------------------------------------------------------------------
# Worker Process Initializer & OCR Fallback
# -----------------------------------------------------------------------------
_worker_reader = None

def get_easyocr_reader():
    """Lazy per-process initialization of CPU EasyOCR reader."""
    global _worker_reader
    if _worker_reader is None and easyocr is not None:
        try:
            _worker_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        except Exception:
            _worker_reader = False
    return _worker_reader if _worker_reader is not False else None


def render_page_to_image(page, doc_path: Path, page_idx: int, dpi: int = 200) -> Optional[Image.Image]:
    """
    Renders a PDF page to a PIL Image using PyMuPDF pixmap (ultra-fast C rasterization)
    with seamless fallback to pdf2image if pixmap fails.
    """
    try:
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return img
    except Exception:
        pass

    if pdf2image is not None:
        try:
            images = pdf2image.convert_from_path(
                str(doc_path),
                first_page=page_idx + 1,
                last_page=page_idx + 1,
                dpi=dpi
            )
            if images:
                return images[0]
        except Exception:
            pass

    return None


def extract_single_pdf(
    pdf_path_str: str,
    max_pages: int = 5,
    tesseract_cmd: Optional[str] = None
) -> Dict[str, Any]:
    """
    Two-Tier Smart Extraction for a single PDF:
      Tier 1: Fast Digital Extraction via PyMuPDF (fitz) [< 5ms per page]
      Tier 2: Fallback Scanned OCR (pytesseract or easyocr) on preprocessed images
    """
    pdf_path = Path(pdf_path_str)
    file_id = pdf_path.stem
    result = {
        "id": file_id,
        "source": "STARGATE",
        "file_path": str(pdf_path),
        "text": "",
        "label": 2,  # RESTRICTED for STARGATE KYC/Clearance documents
        "extraction_method": "failed",
        "word_count": 0,
        "error": None
    }

    if fitz is None:
        result["error"] = "PyMuPDF (fitz) is not installed."
        return result

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        result["error"] = f"Corrupted or password-protected PDF: {e}"
        return result

    num_pages = len(doc)
    pages_to_process = min(num_pages, max_pages)

    # -------------------------------------------------------------------------
    # Tier 1: Fast Digital Extraction
    # -------------------------------------------------------------------------
    digital_text_parts = []
    for page_idx in range(pages_to_process):
        try:
            page = doc[page_idx]
            txt = page.get_text()
            if txt and len(txt.strip()) > 0:
                digital_text_parts.append(txt.strip())
        except Exception:
            continue

    combined_digital_text = "\n\n".join(digital_text_parts)
    cleaned_digital = clean_and_normalize_text(combined_digital_text)

    # If digital text is found (> 50 characters), return instantly (< 5ms)
    if len(cleaned_digital) > DIGITAL_CHAR_THRESHOLD:
        doc.close()
        result["text"] = cleaned_digital
        result["extraction_method"] = "digital"
        result["word_count"] = len(cleaned_digital.split())
        return result

    # -------------------------------------------------------------------------
    # Tier 2: Fallback Scanned OCR
    # -------------------------------------------------------------------------
    ocr_text_parts = []
    for page_idx in range(pages_to_process):
        try:
            page = doc[page_idx]
            img = render_page_to_image(page, pdf_path, page_idx, dpi=200)
            if img is None:
                continue

            # Image enhancement for faint stamps & low contrast
            preprocessed_img = preprocess_image_for_ocr(img)

            page_ocr_text = ""

            # Attempt 2A: Tesseract OCR if binary available
            if pytesseract is not None:
                if tesseract_cmd:
                    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
                try:
                    page_ocr_text = pytesseract.image_to_string(preprocessed_img, lang="eng")
                except Exception:
                    page_ocr_text = ""

            # Attempt 2B: EasyOCR fallback if Tesseract unavailable or returned blank
            if not page_ocr_text or len(page_ocr_text.strip()) < 10:
                reader = get_easyocr_reader()
                if reader is not None:
                    try:
                        img_np = np.array(preprocessed_img)
                        ocr_lines = reader.readtext(img_np, detail=0)
                        page_ocr_text = " ".join(ocr_lines)
                    except Exception:
                        page_ocr_text = ""

            if page_ocr_text and len(page_ocr_text.strip()) > 0:
                ocr_text_parts.append(page_ocr_text.strip())

        except Exception:
            continue

    doc.close()

    combined_ocr_text = "\n\n".join(ocr_text_parts)
    cleaned_ocr = clean_and_normalize_text(combined_ocr_text)

    if len(cleaned_ocr) >= MIN_CHAR_LENGTH:
        result["text"] = cleaned_ocr
        result["extraction_method"] = "ocr"
        result["word_count"] = len(cleaned_ocr.split())
    else:
        result["error"] = "Insufficient text extracted after digital check and OCR fallback."

    return result


# -----------------------------------------------------------------------------
# Raw Text & JSON Ingestion
# -----------------------------------------------------------------------------
def ingest_raw_text_files(raw_text_dir: Path) -> List[Dict[str, Any]]:
    """
    Ingests and normalizes raw .txt and .json files.
    Cleans text: removes null bytes, excessive blank lines, and standard artifacts.
    """
    records = []
    if not raw_text_dir.exists():
        logger.info(f"Raw text directory does not exist yet: {raw_text_dir}. Skipping.")
        return records

    candidate_files = list(raw_text_dir.glob("**/*.*"))
    target_files = [f for f in candidate_files if f.suffix.lower() in (".txt", ".json", ".csv")]
    logger.info(f"Discovered {len(target_files)} raw text/json files in {raw_text_dir}...")

    for f in target_files:
        try:
            content = ""
            if f.suffix.lower() == ".txt":
                # UTF-8 with ISO-8859 fallback
                try:
                    content = f.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    content = f.read_text(encoding="iso-8859-1", errors="ignore")

            elif f.suffix.lower() == ".json":
                try:
                    with open(f, "r", encoding="utf-8") as jf:
                        data = json.load(jf)
                    if isinstance(data, list):
                        content = "\n".join([str(item) for item in data])
                    elif isinstance(data, dict):
                        content = json.dumps(data, indent=2)
                except Exception:
                    continue

            cleaned = clean_and_normalize_text(content)
            if len(cleaned) >= MIN_CHAR_LENGTH:
                # Default label: 0 (SAFE) or heuristic check
                label = 0
                lower_c = cleaned.lower()
                if any(k in lower_c for k in ["confidential", "strategy", "forecast", "board meeting", "internal audit"]):
                    label = 1
                elif any(k in lower_c for k in ["ssn", "passport", "credit card", "iban", "kyc", "edd", "tax id"]):
                    label = 2

                records.append({
                    "id": f.stem,
                    "source": f"raw_text_{f.suffix[1:]}",
                    "text": cleaned,
                    "label": label,
                    "extraction_method": "text_file",
                    "word_count": len(cleaned.split())
                })
        except Exception as e:
            logger.warning(f"Error reading raw file {f}: {e}")

    logger.info(f"Successfully parsed {len(records)} raw text records.")
    return records


# -----------------------------------------------------------------------------
# Resumable Checkpoint Tracker
# -----------------------------------------------------------------------------
class StargateProgressTracker:
    def __init__(self, checkpoint_file: Path):
        self.checkpoint_file = checkpoint_file
        self.processed_ids = set()
        self.load()

    def load(self):
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.processed_ids = set(data.get("processed_ids", []))
                logger.info(f"[RESUME CACHE] Loaded {len(self.processed_ids)} already processed PDF IDs.")
            except Exception as e:
                logger.warning(f"Could not load checkpoint file: {e}")

    def save(self):
        try:
            with open(self.checkpoint_file, "w", encoding="utf-8") as f:
                json.dump({"processed_ids": list(self.processed_ids)}, f)
        except Exception as e:
            logger.warning(f"Failed to save checkpoint index: {e}")

    def mark_processed(self, file_id: str):
        self.processed_ids.add(file_id)

    def is_processed(self, file_id: str) -> bool:
        return file_id in self.processed_ids


# -----------------------------------------------------------------------------
# Main Ingestion Orchestrator
# -----------------------------------------------------------------------------
def run_ingestion_pipeline(args: argparse.Namespace):
    stargate_dir, raw_text_dir, processed_dir = get_default_paths(
        stargate_arg=args.stargate_dir,
        raw_text_arg=args.raw_text_dir,
        output_arg=args.output_dir
    )
    processed_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_file = processed_dir / "stargate_progress.json"
    failed_log_path = processed_dir / "failed_pdfs.log"
    stargate_output_parquet = processed_dir / "stargate_extracted.parquet"
    raw_output_parquet = processed_dir / "raw_files_extracted.parquet"

    logger.info("=" * 80)
    logger.info(" SECUREFLOW AI: HIGH-THROUGHPUT DOCUMENT INGESTION & OCR PIPELINE")
    logger.info("=" * 80)
    logger.info(f"STARGATE Source:       {stargate_dir}")
    logger.info(f"Raw Text Source:       {raw_text_dir}")
    logger.info(f"Processed Output:      {processed_dir}")
    logger.info(f"Max Pages per Doc:     {args.max_pages}")
    logger.info(f"Worker Processes:      {args.workers}")
    logger.info("=" * 80)

    # 1. Discover STARGATE PDFs
    if not stargate_dir.exists():
        logger.error(f"STARGATE directory does not exist: {stargate_dir}")
        return

    pdf_files = sorted(list(stargate_dir.glob("*.pdf")) or list(stargate_dir.glob("**/*.pdf")))
    total_discovered = len(pdf_files)
    logger.info(f"Discovered {total_discovered:,} total PDFs in STARGATE directory.")

    if args.sample_limit and args.sample_limit < total_discovered:
        logger.info(f"Subsampling to --sample_limit={args.sample_limit} PDFs for testing/verification.")
        pdf_files = pdf_files[:args.sample_limit]

    # 2. Checkpoint Tracker
    tracker = StargateProgressTracker(checkpoint_file)
    pending_pdfs = [p for p in pdf_files if not tracker.is_processed(p.stem)]
    already_done_count = len(pdf_files) - len(pending_pdfs)
    logger.info(f"Pending to process: {len(pending_pdfs):,} ({already_done_count:,} already completed in cache).")

    # Load existing parquet records if resuming
    existing_records = []
    if stargate_output_parquet.exists() and already_done_count > 0:
        try:
            existing_df = pd.read_parquet(stargate_output_parquet)
            existing_records = existing_df.to_dict("records")
            logger.info(f"Loaded {len(existing_records)} existing records from {stargate_output_parquet.name}")
        except Exception as e:
            logger.warning(f"Could not load existing parquet: {e}")

    # 3. Parallel PDF Extraction Execution
    successful_records = list(existing_records)
    failed_records = []
    digital_count = sum(1 for r in existing_records if r.get("extraction_method") == "digital")
    ocr_count = sum(1 for r in existing_records if r.get("extraction_method") == "ocr")

    t_start = time.time()

    if pending_pdfs:
        logger.info(f"Processing {len(pending_pdfs):,} PDFs with {args.workers} workers...")
        pbar = tqdm(
            total=len(pending_pdfs),
            desc="STARGATE Extraction",
            unit="doc",
            dynamic_ncols=True
        )

        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            future_to_pdf = {
                executor.submit(
                    extract_single_pdf,
                    str(pdf),
                    args.max_pages,
                    args.tesseract_cmd
                ): pdf
                for pdf in pending_pdfs
            }

            save_interval = 50
            processed_since_save = 0

            for future in as_completed(future_to_pdf):
                pdf_path = future_to_pdf[future]
                pbar.update(1)
                try:
                    res = future.result()
                    if res["text"]:
                        successful_records.append({
                            "id": res["id"],
                            "source": res["source"],
                            "text": res["text"],
                            "label": res["label"],
                            "extraction_method": res["extraction_method"]
                        })
                        if res["extraction_method"] == "digital":
                            digital_count += 1
                        else:
                            ocr_count += 1
                        tracker.mark_processed(res["id"])
                    else:
                        failed_records.append(f"{pdf_path.name}: {res.get('error', 'No text extracted')}")
                except Exception as e:
                    failed_records.append(f"{pdf_path.name}: Exception: {e}")

                pbar.set_postfix({
                    "Digital": digital_count,
                    "OCR": ocr_count,
                    "Failed": len(failed_records)
                })

                processed_since_save += 1
                if processed_since_save >= save_interval:
                    tracker.save()
                    processed_since_save = 0

        pbar.close()
        tracker.save()

    # Log failures to failed_pdfs.log
    if failed_records:
        with open(failed_log_path, "a", encoding="utf-8") as fl:
            for item in failed_records:
                fl.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {item}\n")
        logger.info(f"Logged {len(failed_records)} failed PDF entries to: {failed_log_path}")

    # 4. Export STARGATE Parquet
    if successful_records:
        stargate_df = pd.DataFrame(successful_records)
        cols = ["id", "source", "text", "label", "extraction_method"]
        for c in cols:
            if c not in stargate_df.columns:
                stargate_df[c] = None

        stargate_df[cols].to_parquet(stargate_output_parquet, index=False)
        logger.info(f"[SUCCESS] Exported {len(stargate_df):,} STARGATE records to: {stargate_output_parquet}")

    # 5. Ingest Raw Text Files
    logger.info("Processing raw text and json directory...")
    raw_records = ingest_raw_text_files(raw_text_dir)
    if raw_records:
        raw_df = pd.DataFrame(raw_records)
        cols = ["id", "source", "text", "label", "extraction_method"]
        raw_df[cols].to_parquet(raw_output_parquet, index=False)
        logger.info(f"[SUCCESS] Exported {len(raw_df):,} raw text records to: {raw_output_parquet}")

    # 6. Final Summary Report
    elapsed = time.time() - t_start
    total_success = len(successful_records)
    total_failed = len(failed_records)
    digital_pct = (digital_count / total_success * 100) if total_success > 0 else 0.0
    ocr_pct = (ocr_count / total_success * 100) if total_success > 0 else 0.0

    avg_words = 0
    if successful_records:
        avg_words = sum(len(str(r["text"]).split()) for r in successful_records) / len(successful_records)

    logger.info("=" * 80)
    logger.info(" STARGATE & DOCUMENT INGESTION SUMMARY REPORT")
    logger.info("=" * 80)
    logger.info(f"  Total Processed Successfully:   {total_success:,}")
    logger.info(f"  Total Failed / Corrupted PDFs:  {total_failed:,}")
    logger.info(f"  Digital Fast Extraction:        {digital_count:,} ({digital_pct:.1f}%)")
    logger.info(f"  Fallback Scanned OCR:           {ocr_count:,} ({ocr_pct:.1f}%)")
    logger.info(f"  Average Words Extracted / Doc:  {avg_words:.1f} words")
    logger.info(f"  Pipeline Execution Time:        {elapsed:.2f}s ({elapsed / 60:.1f} mins)")
    if stargate_output_parquet.exists():
        logger.info(f"  Output STARGATE Parquet:        {stargate_output_parquet} ({stargate_output_parquet.stat().st_size / 1024:.1f} KB)")
    if raw_output_parquet.exists():
        logger.info(f"  Output Raw Files Parquet:       {raw_output_parquet} ({raw_output_parquet.stat().st_size / 1024:.1f} KB)")
    logger.info("=" * 80)


# -----------------------------------------------------------------------------
# CLI Parser
# -----------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SecureFlow AI - High-Throughput OCR & Document Ingestion Pipeline"
    )
    parser.add_argument(
        "--stargate_dir",
        type=str,
        default="./data/raw/STARGATE",
        help="Path to directory containing STARGATE PDFs (default: ./data/raw/STARGATE)"
    )
    parser.add_argument(
        "--raw_text_dir",
        type=str,
        default="./data/raw/raw_text_files",
        help="Path to directory containing raw .txt and .json files (default: ./data/raw/raw_text_files)"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./data/processed",
        help="Destination directory for processed parquet files (default: ./data/processed)"
    )
    parser.add_argument(
        "--max_pages",
        type=int,
        default=5,
        help="Max pages per PDF to inspect (default: 5)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=min(os.cpu_count() or 4, 8),
        help="Number of multiprocessing workers (default: min(cpu_count, 8))"
    )
    parser.add_argument(
        "--sample_limit",
        type=int,
        default=None,
        help="Limit number of PDFs to process (for rapid testing/verification)"
    )
    parser.add_argument(
        "--tesseract_cmd",
        type=str,
        default=None,
        help="Optional path to tesseract.exe binary if installed"
    )
    return parser.parse_args()


if __name__ == "__main__":
    cli_args = parse_args()
    run_ingestion_pipeline(cli_args)

"""
SecureFlow AI - Tests for Real-Time In-Memory OCR Extraction
================================================================================
File: ai-service/tests/test_ocr.py
"""

import io
import pytest
from PIL import Image, ImageDraw
import pymupdf as fitz
from app.engine.extractor import extract_from_image, extract_file_content, extract_from_pdf


def create_synthetic_text_image(text: str) -> bytes:
    """Renders a simple synthetic black-on-white image in memory."""
    img = Image.new("RGB", (600, 120), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 45), text, fill=(0, 0, 0))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_ocr_extracts_from_image_bytes():
    card_text = "CARD 4530-8921-0043-9182"
    img_bytes = create_synthetic_text_image(card_text)

    extracted_text, file_type = extract_file_content(img_bytes, "card_photo.png")
    assert file_type == "png"
    assert "4530" in extracted_text
    assert "9182" in extracted_text


def test_ocr_pdf_scanned_page_fallback():
    # Create a PDF document that has ONLY an image (zero digital text layer)
    img_bytes = create_synthetic_text_image("WIRE TRANSFER 4530-8921-0043-9182")
    
    doc = fitz.open()
    page = doc.new_page(width=600, height=120)
    rect = fitz.Rect(0, 0, 600, 120)
    page.insert_image(rect, stream=img_bytes)
    
    pdf_bytes = doc.tobytes()
    doc.close()

    # PyMuPDF page.get_text() will return empty string because it's a pure image
    extracted = extract_from_pdf(pdf_bytes)
    assert "4530" in extracted
    assert "9182" in extracted

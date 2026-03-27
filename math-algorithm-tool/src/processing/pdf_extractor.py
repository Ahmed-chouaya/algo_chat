"""
PDF text extraction module.

Provides functions to extract text from PDF files using PyMuPDF (fitz).
Handles both text-based and image-only PDFs.
"""
from typing import Optional

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None


def extract_text_from_pdf(path: str) -> str:
    """
    Extract all text content from a PDF file.
    
    Args:
        path: Path to the PDF file
        
    Returns:
        Extracted text content from all pages
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        ValueError: If the file is not a valid PDF or has no extractable text
    """
    if not PYMUPDF_AVAILABLE:
        raise ImportError("PyMuPDF (fitz) is required for PDF extraction. Install with: pip install pymupdf")
    
    try:
        doc = fitz.open(path)
    except Exception as e:
        if "not a valid PDF" in str(e).lower() or "empty" in str(e).lower():
            raise ValueError(f"Invalid or corrupted PDF file: {path}") from e
        raise FileNotFoundError(f"PDF file not found: {path}") from e
    
    if doc.page_count == 0:
        doc.close()
        raise ValueError(f"PDF has no pages: {path}")
    
    text_parts = []
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text = page.get_text()
        if text.strip():
            text_parts.append(text)
    
    doc.close()
    
    if not text_parts:
        raise ValueError(f"PDF contains no extractable text (possibly image-only): {path}")
    
    return "\n\n".join(text_parts)


def has_text_pages(path: str) -> bool:
    """
    Check if any page in a PDF has extractable text.
    
    Args:
        path: Path to the PDF file
        
    Returns:
        True if at least one page has extractable text, False otherwise
    """
    if not PYMUPDF_AVAILABLE:
        return False
    
    try:
        doc = fitz.open(path)
    except Exception:
        return False
    
    if doc.page_count == 0:
        doc.close()
        return False
    
    has_text = False
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text = page.get_text()
        if text.strip():
            has_text = True
            break
    
    doc.close()
    return has_text


def get_page_count(path: str) -> int:
    """
    Get the number of pages in a PDF.
    
    Args:
        path: Path to the PDF file
        
    Returns:
        Number of pages in the PDF
    """
    if not PYMUPDF_AVAILABLE:
        return 0
    
    try:
        doc = fitz.open(path)
        count = doc.page_count
        doc.close()
        return count
    except Exception:
        return 0

"""
File processor module for handling file imports.

Provides functions to:
- Detect file format from extension
- Read text files (.txt, .md)
- Import PDF files with text extraction
- Unified import interface
"""
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from src.processing.pdf_extractor import extract_text_from_pdf, has_text_pages


class SupportedFormat(Enum):
    """Supported file formats for algorithm import."""
    PDF = "pdf"
    TXT = "txt"
    MD = "md"


@dataclass
class ImportResult:
    """Result of importing a file."""
    success: bool
    format: SupportedFormat
    content: str
    file_path: str
    error: Optional[str] = None


def detect_format(path: str) -> SupportedFormat:
    """
    Detect the file format from the file extension.
    
    Args:
        path: Path to the file
        
    Returns:
        SupportedFormat enum value
        
    Raises:
        ValueError: If the file extension is not supported
    """
    ext = os.path.splitext(path)[1].lower().lstrip('.')
    
    if ext == 'pdf':
        return SupportedFormat.PDF
    elif ext == 'txt':
        return SupportedFormat.TXT
    elif ext in ('md', 'markdown'):
        return SupportedFormat.MD
    else:
        raise ValueError(f"Unsupported file format: .{ext}")


def read_file(path: str) -> str:
    """
    Read a file and return its content.
    
    Automatically detects format and uses appropriate reader.
    
    Args:
        path: Path to the file
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If format is unsupported or PDF has no text
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    file_format = detect_format(path)
    
    if file_format == SupportedFormat.PDF:
        # Check if PDF has text before extracting
        if not has_text_pages(path):
            raise ValueError(f"PDF has no extractable text (image-only): {path}")
        return extract_text_from_pdf(path)
    
    elif file_format in (SupportedFormat.TXT, SupportedFormat.MD):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    else:
        raise ValueError(f"Unsupported format: {file_format.value}")


def import_file(path: str) -> ImportResult:
    """
    Import a file and return structured result.
    
    Unified entry point for file import that handles all formats
    and returns a structured result.
    
    Args:
        path: Path to the file to import
        
    Returns:
        ImportResult with success status, format, and content
    """
    try:
        file_format = detect_format(path)
        content = read_file(path)
        
        return ImportResult(
            success=True,
            format=file_format,
            content=content,
            file_path=path,
            error=None
        )
    except FileNotFoundError as e:
        return ImportResult(
            success=False,
            format=detect_format(path) if os.path.exists(path) else SupportedFormat.PDF,
            content="",
            file_path=path,
            error=str(e)
        )
    except ValueError as e:
        return ImportResult(
            success=False,
            format=SupportedFormat.PDF if path.lower().endswith('.pdf') else SupportedFormat.TXT,
            content="",
            file_path=path,
            error=str(e)
        )
    except Exception as e:
        return ImportResult(
            success=False,
            format=SupportedFormat.PDF if path.lower().endswith('.pdf') else SupportedFormat.TXT,
            content="",
            file_path=path,
            error=f"Unexpected error: {str(e)}"
        )

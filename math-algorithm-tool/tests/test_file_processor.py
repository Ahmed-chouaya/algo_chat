"""
Tests for file processor module.

Tests PDF extraction, text/markdown file handling, and format detection.
"""
import os
import sys
from unittest.mock import MagicMock, patch, mock_open

import pytest


# Mock the fitz module before importing the processor
mock_fitz = MagicMock()
mock_doc = MagicMock()
mock_page = MagicMock()

# Setup mock for PDF with text
mock_page.get_text.return_value = "Hello World\nTest Content"
mock_doc.__enter__ = MagicMock(return_value=mock_doc)
mock_doc.__exit__ = MagicMock(return_value=False)
mock_doc.__getitem__ = MagicMock(return_value=mock_page)
mock_doc.page_count = 1
mock_doc.close = MagicMock()
mock_fitz.open.return_value = mock_doc


class TestPdfExtractor:
    """Tests for PDF extraction functionality."""

    @patch.dict(sys.modules, {'fitz': mock_fitz})
    def test_extract_text_from_pdf_returns_string(self, tmp_path):
        """Test that extract_text_from_pdf returns a string."""
        # Need to reimport with mocked module
        from src.processing import pdf_extractor
        # Re-apply the mock
        pdf_extractor.fitz = mock_fitz
        pdf_extractor.PYMUPDF_AVAILABLE = True
        
        # Create a dummy file path
        pdf_path = str(tmp_path / "test.pdf")
        
        result = pdf_extractor.extract_text_from_pdf(pdf_path)
        
        assert isinstance(result, str)
        assert "Hello World" in result

    @patch.dict(sys.modules, {'fitz': mock_fitz})
    def test_has_text_pages_returns_bool(self, tmp_path):
        """Test that has_text_pages returns a boolean."""
        from src.processing import pdf_extractor
        pdf_extractor.fitz = mock_fitz
        pdf_extractor.PYMUPDF_AVAILABLE = True
        
        pdf_path = str(tmp_path / "test.pdf")
        
        result = pdf_extractor.has_text_pages(pdf_path)
        
        assert isinstance(result, bool)
        assert result is True

    def test_extract_text_from_nonexistent_raises_error(self):
        """Test that extracting from nonexistent file raises appropriate error."""
        from src.processing import pdf_extractor
        # If pymupdf not available, should raise ImportError
        pdf_extractor.PYMUPDF_AVAILABLE = False
        
        with pytest.raises(ImportError):
            pdf_extractor.extract_text_from_pdf("/nonexistent/path.pdf")


class TestFileProcessor:
    """Tests for file processor functionality."""

    def test_detect_format_pdf(self):
        """Test PDF format detection."""
        from src.processing.file_processor import detect_format, SupportedFormat
        result = detect_format("document.pdf")
        assert result == SupportedFormat.PDF

    def test_detect_format_txt(self):
        """Test TXT format detection."""
        from src.processing.file_processor import detect_format, SupportedFormat
        result = detect_format("readme.txt")
        assert result == SupportedFormat.TXT

    def test_detect_format_md(self):
        """Test MD format detection."""
        from src.processing.file_processor import detect_format, SupportedFormat
        result = detect_format("notes.md")
        assert result == SupportedFormat.MD

    def test_detect_format_markdown(self):
        """Test markdown format detection."""
        from src.processing.file_processor import detect_format, SupportedFormat
        result = detect_format("notes.markdown")
        assert result == SupportedFormat.MD

    def test_detect_format_unsupported(self):
        """Test unsupported format raises error."""
        from src.processing.file_processor import detect_format
        with pytest.raises(ValueError, match="Unsupported"):
            detect_format("document.json")

    def test_read_file_txt(self, tmp_path):
        """Test reading a .txt file."""
        from src.processing.file_processor import read_file
        
        txt_path = tmp_path / "test.txt"
        test_content = "Hello, this is a test file."
        txt_path.write_text(test_content)
        
        result = read_file(str(txt_path))
        
        assert result == test_content

    def test_read_file_md(self, tmp_path):
        """Test reading a .md file."""
        from src.processing.file_processor import read_file
        
        md_path = tmp_path / "test.md"
        test_content = "# Markdown Content\n\nSome text."
        md_path.write_text(test_content)
        
        result = read_file(str(md_path))
        
        assert result == test_content

    def test_read_file_not_found(self):
        """Test reading nonexistent file raises error."""
        from src.processing.file_processor import read_file
        
        with pytest.raises(FileNotFoundError):
            read_file("/nonexistent/file.txt")

    @patch.dict(sys.modules, {'fitz': mock_fitz})
    def test_read_file_pdf_with_text(self, tmp_path):
        """Test reading a PDF with text."""
        from src.processing import pdf_extractor
        from src.processing.file_processor import read_file
        
        pdf_extractor.fitz = mock_fitz
        pdf_extractor.PYMUPDF_AVAILABLE = True
        
        pdf_path = tmp_path / "document.pdf"
        pdf_path.write_bytes(b"dummy pdf content")
        
        result = read_file(str(pdf_path))
        
        assert isinstance(result, str)
        assert "Hello World" in result

    @patch.dict(sys.modules, {'fitz': mock_fitz})
    def test_read_file_image_pdf_raises_error(self, tmp_path):
        """Test that image-only PDF raises error (no text)."""
        from src.processing import pdf_extractor
        from src.processing.file_processor import read_file
        
        # Mock PDF with no text
        mock_doc_empty = MagicMock()
        mock_page_empty = MagicMock()
        mock_page_empty.get_text.return_value = ""
        mock_doc_empty.__getitem__ = MagicMock(return_value=mock_page_empty)
        mock_doc_empty.page_count = 1
        mock_doc_empty.__enter__ = MagicMock(return_value=mock_doc_empty)
        mock_doc_empty.__exit__ = MagicMock(return_value=False)
        mock_doc_empty.close = MagicMock()
        
        mock_fitz.open.return_value = mock_doc_empty
        
        pdf_extractor.fitz = mock_fitz
        pdf_extractor.PYMUPDF_AVAILABLE = True
        
        pdf_path = tmp_path / "image.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with pytest.raises(ValueError, match="extractable text"):
            read_file(str(pdf_path))

    def test_import_file_txt(self, tmp_path):
        """Test importing a TXT file."""
        from src.processing.file_processor import import_file, SupportedFormat, ImportResult
        
        txt_path = tmp_path / "data.txt"
        test_content = "Algorithm data"
        txt_path.write_text(test_content)
        
        result = import_file(str(txt_path))
        
        assert isinstance(result, ImportResult)
        assert result.format == SupportedFormat.TXT
        assert result.content == test_content
        assert result.success is True

    def test_import_file_unsupported_format(self, tmp_path):
        """Test importing unsupported file format."""
        from src.processing.file_processor import import_file
        
        file_path = tmp_path / "data.json"
        file_path.write_text('{"key": "value"}')
        
        result = import_file(str(file_path))
        
        # Should return ImportResult with success=False
        assert hasattr(result, 'success')
        assert result.success is False
        assert result.error is not None
        assert "Unsupported" in result.error

    # Note: Full PDF import test requires proper PDF fixtures
    # The core PDF extraction is tested in TestPdfExtractor tests
    # and file_processor handles PDF by calling pdf_extractor functions

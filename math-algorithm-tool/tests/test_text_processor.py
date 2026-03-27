"""
Tests for text processor module.

Tests the text processing pipeline for handling plain text and mixed content.
"""
import pytest
from src.processing.text_processor import (
    clean_text,
    split_into_sections,
    process_text_input,
    ProcessedInput,
    Section
)


class TestCleanText:
    """Test clean_text function."""

    def test_remove_code_blocks(self):
        """Test that code blocks are removed."""
        text = "Some text\n```python\ndef foo():\n    pass\n```\nMore text"
        result = clean_text(text)
        
        assert "```python" not in result
        assert "def foo():" not in result
        assert "Some text" in result
        assert "More text" in result

    def test_remove_inline_code(self):
        """Test that inline code is removed."""
        text = "Use `print()` function"
        result = clean_text(text)
        
        assert "`" not in result
        assert "print" not in result

    def test_normalize_whitespace(self):
        """Test that multiple newlines are normalized."""
        text = "Line 1\n\n\n\nLine 2"
        result = clean_text(text)
        
        assert result.count('\n\n') == 1

    def test_empty_string(self):
        """Test empty input returns empty."""
        assert clean_text("") == ""

    def test_only_whitespace(self):
        """Test whitespace-only input returns empty."""
        assert clean_text("   \n\t\n   ") == ""


class TestSplitIntoSections:
    """Test split_into_sections function."""

    def test_split_by_markdown_headers(self):
        """Test splitting by markdown headers."""
        text = "# Introduction\nSome intro text\n\n# Algorithm\nThe algorithm steps\n\n# Conclusion"
        result = split_into_sections(text)
        
        assert len(result) == 3
        assert result[0].title == "Introduction"
        assert result[1].title == "Algorithm"
        assert result[2].title == "Conclusion"

    def test_split_by_numbered_sections(self):
        """Test splitting by numbered sections."""
        text = "1. First step\nContent here\n\n2. Second step\nMore content"
        result = split_into_sections(text)
        
        assert len(result) == 2

    def test_no_headers_creates_single_section(self):
        """Test plain text without headers creates single section."""
        text = "Just some plain text without any headers"
        result = split_into_sections(text)
        
        assert len(result) == 1
        assert result[0].content == text

    def test_empty_input(self):
        """Test empty input returns empty list."""
        assert split_into_sections("") == []


class TestProcessTextInput:
    """Test process_text_input main function."""

    def test_basic_processing(self):
        """Test basic text processing pipeline."""
        text = "Calculate the sum of x and y"
        result = process_text_input(text)
        
        assert isinstance(result, ProcessedInput)
        assert result.original_text == text
        assert result.cleaned_text == "Calculate the sum of x and y"
        assert isinstance(result.latex_expressions, list)
        assert len(result.sections) >= 1

    def test_extracts_latex(self):
        """Test that LaTeX is extracted from mixed content."""
        text = "The equation is $x^2 + y^2 = z^2$ and more text"
        result = process_text_input(text)
        
        assert result.has_latex()
        assert result.get_latex_count() >= 1

    def test_empty_input(self):
        """Test empty input returns empty ProcessedInput."""
        result = process_text_input("")
        
        assert result.original_text == ""
        assert result.cleaned_text == ""
        assert result.latex_expressions == []
        assert result.sections == []

    def test_mixed_content_with_sections(self):
        """Test mixed content with headers extracts latex and sections."""
        text = """# Algorithm

Given $n$ elements, compute their sum.

## Step 1
Initialize sum to 0

## Step 2
For each element $a_i$, add to sum
"""
        result = process_text_input(text)
        
        assert result.has_latex()
        assert len(result.sections) >= 2  # At least Algorithm + steps

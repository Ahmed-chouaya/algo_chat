"""
Text processor module for handling plain text and mixed content input.

This module provides:
- process_text_input: Main entry point for processing raw text
- clean_text: Strip code blocks, normalize whitespace
- split_into_sections: Split by headers or logical sections

Works with latex_parser to extract LaTeX expressions from mixed content.
"""
import re
from dataclasses import dataclass, field
from typing import Optional

from src.processing.latex_parser import extract_latex_expressions, is_valid_latex


@dataclass
class Section:
    """Represents a logical section of text."""
    title: Optional[str] = None
    content: str = ""
    start_line: int = 0
    end_line: int = 0


@dataclass
class ProcessedInput:
    """Result of processing algorithm input text."""
    original_text: str
    cleaned_text: str
    latex_expressions: list = field(default_factory=list)
    sections: list = field(default_factory=list)
    
    def has_latex(self) -> bool:
        """Check if any LaTeX was extracted."""
        return len(self.latex_expressions) > 0
    
    def get_latex_count(self) -> int:
        """Get count of LaTeX expressions found."""
        return len(self.latex_expressions)


def clean_text(text: str) -> str:
    """
    Clean text by removing code blocks and normalizing whitespace.
    
    Args:
        text: Raw input text
        
    Returns:
        Cleaned text with code blocks removed and whitespace normalized
    """
    if not text:
        return ""
    
    # Remove code blocks (```...```)
    # Matches triple-backtick code blocks with optional language
    text = re.sub(r'```[\s\S]*?```', '', text)
    
    # Remove inline code (`...`)
    text = re.sub(r'`[^`]+`', '', text)
    
    # Normalize multiple newlines to double newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    
    # Remove completely empty lines at start/end
    text = '\n'.join(lines)
    text = text.strip()
    
    return text


def split_into_sections(text: str) -> list[Section]:
    """
    Split text into logical sections based on headers or structure.
    
    Uses common header patterns:
    - Markdown headers (#, ##, ###)
    - Numbered sections (1., 2., 2.1)
    - All-caps lines (often used for section titles)
    
    Args:
        text: Cleaned text to split
        
    Returns:
        List of Section objects
    """
    if not text:
        return []
    
    lines = text.split('\n')
    sections = []
    current_section = Section(content="", start_line=0)
    
    # Patterns for detecting section headers
    markdown_header = re.compile(r'^(#{1,6})\s+(.+)$')
    numbered_header = re.compile(r'^(\d+\.)+\s+(.+)$')
    all_caps_header = re.compile(r'^([A-Z][A-Z\s]+)$')
    
    for i, line in enumerate(lines):
        # Check for header patterns
        md_match = markdown_header.match(line)
        num_match = numbered_header.match(line)
        caps_match = all_caps_header.match(line)
        
        if md_match or num_match or caps_match:
            # Save current section if it has content
            if current_section.content.strip():
                current_section.end_line = i - 1
                sections.append(current_section)
            
            # Start new section
            title = md_match.group(2) if md_match else (num_match.group(0) if num_match else line)
            current_section = Section(title=title, content="", start_line=i)
        else:
            # Add to current section
            if current_section.content:
                current_section.content += '\n' + line
            else:
                current_section.content = line
    
    # Don't forget the last section
    if current_section.content.strip() or current_section.title:
        current_section.end_line = len(lines) - 1
        sections.append(current_section)
    
    # If no sections were found, create a single section with all content
    if not sections:
        sections.append(Section(title=None, content=text, start_line=0, end_line=len(lines) - 1))
    
    return sections


def process_text_input(raw_text: str) -> ProcessedInput:
    """
    Main entry point for processing algorithm text input.
    
    Processes text in stages:
    1. Clean: remove code blocks, normalize whitespace
    2. Extract: find LaTeX expressions using latex_parser
    3. Split: identify logical sections
    
    Args:
        raw_text: Raw text input from user
        
    Returns:
        ProcessedInput with cleaned text, extracted LaTeX, and sections
    """
    if not raw_text:
        return ProcessedInput(
            original_text="",
            cleaned_text="",
            latex_expressions=[],
            sections=[]
        )
    
    # Stage 1: Clean the text
    cleaned = clean_text(raw_text)
    
    # Stage 2: Extract LaTeX expressions
    latex_exprs = extract_latex_expressions(cleaned)
    
    # Stage 3: Split into sections
    sections = split_into_sections(cleaned)
    
    return ProcessedInput(
        original_text=raw_text,
        cleaned_text=cleaned,
        latex_expressions=latex_exprs,
        sections=sections
    )

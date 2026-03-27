"""
LaTeX parser module for extracting and parsing LaTeX mathematical expressions.

This module provides functions to:
- Extract LaTeX expressions from text ($...$ and $$...$$ delimiters)
- Parse LaTeX to SymPy expressions
- Validate LaTeX expressions

Uses SymPy's built-in LaTeX parser for mathematical expressions.
"""
import re
from typing import Any, Optional

# Workaround for antlr4 version check in sympy 1.14
# SymPy requires exactly version 4.11 but nixpkgs may have 4.13+
import importlib.metadata
_original_version = importlib.metadata.version

def _patched_version(package: str):
    """Patch antlr4 version to satisfy sympy's check."""
    if package == 'antlr4-python3-runtime':
        return '4.11'
    return _original_version(package)

importlib.metadata.version = _patched_version

try:
    from sympy.parsing.latex import parse_latex
    from sympy import Symbol, Rational, Matrix
    from sympy.core.expr import Expr
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    # Fallback types for when sympy isn't available
    parse_latex = None
    
    class Expr:
        """Fallback Expr class."""
        pass


def extract_latex_expressions(text: str) -> list[tuple[str, Optional[Expr]]]:
    """
    Extract all LaTeX expressions from text.
    
    Finds all LaTeX expressions in $...$ (inline) and $$...$$ (display) delimiters
    and attempts to parse them to SymPy expressions.
    
    Args:
        text: Input text containing LaTeX expressions
        
    Returns:
        List of tuples: (latex_string, parsed_sympy_expr)
        The parsed_sympy_expr is None if parsing fails
    """
    if not text:
        return []
    
    results = []
    
    # Match inline math: $...$
    inline_pattern = r'\$([^\$]+)\$'
    # Match display math: $$...$$
    display_pattern = r'\$\$([^\$]+)\$\$'
    
    # Find all matches
    inline_matches = re.findall(inline_pattern, text)
    display_matches = re.findall(display_pattern, text)
    
    # Process inline matches
    for latex_expr in inline_matches:
        parsed = parse_latex_to_sympy(latex_expr)
        results.append((latex_expr, parsed))
    
    # Process display matches
    for latex_expr in display_matches:
        parsed = parse_latex_to_sympy(latex_expr)
        results.append((latex_expr, parsed))
    
    return results


def parse_latex_to_sympy(latex_str: str) -> Optional[Expr]:
    """
    Parse a single LaTeX string to a SymPy expression.
    
    Args:
        latex_str: LaTeX string (without delimiters)
        
    Returns:
        SymPy expression, or None if parsing fails
    """
    if not latex_str or not SYMPY_AVAILABLE:
        return None
    
    try:
        # Try to parse as LaTeX
        result = parse_latex(latex_str)
        return result
    except Exception as e:
        # Return None on parse failure - don't crash
        return None


def is_valid_latex(latex_str: str) -> bool:
    """
    Validate a LaTeX string without attempting full parsing.
    
    Does basic syntax validation - checks for balanced braces and
    common LaTeX command structure.
    
    Args:
        latex_str: LaTeX string to validate
        
    Returns:
        True if the LaTeX appears valid, False otherwise
    """
    if not latex_str:
        return False
    
    # Check balanced braces
    if latex_str.count('{') != latex_str.count('}'):
        return False
    
    # Check for common LaTeX commands (must start with backslash)
    # Allow expressions that start with letters (simple variables)
    # or with backslash (LaTeX commands)
    if latex_str.strip() and not latex_str.strip()[0].isalnum() and latex_str.strip()[0] != '\\':
        # Could be a number or operator - check basic validity
        pass
    
    # Try to parse - if it fails, it's not valid
    if SYMPY_AVAILABLE:
        try:
            parse_latex(latex_str)
            return True
        except Exception:
            return False
    
    # If sympy not available, do basic validation
    # Must contain at least some valid-looking LaTeX
    return bool(latex_str.strip())


# Convenience function for testing - check if sympy is available
def is_sympy_available() -> bool:
    """Check if SymPy is available for parsing."""
    return SYMPY_AVAILABLE

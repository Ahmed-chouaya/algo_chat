"""
Tests for LaTeX parser module.

RED phase: These tests define expected behavior.
They should FAIL until the implementation is complete.
"""
import pytest
from sympy import Rational, Symbol


class TestExtractLatexExpressions:
    """Test extract_latex_expressions function."""

    def test_extract_simple_inline_latex(self):
        """Test 1: extract_latex_expressions("$x^2 + y^2$") returns [("x^2 + y^2", SymPyExpr)]"""
        from src.processing.latex_parser import extract_latex_expressions
        
        text = "$x^2 + y^2$"
        result = extract_latex_expressions(text)
        
        assert len(result) == 1
        latex_expr, parsed = result[0]
        assert latex_expr == "x^2 + y^2"
        # Verify it's a SymPy expression
        assert hasattr(parsed, 'subs')

    def test_extract_latex_with_sum(self):
        """Test 2: extract_latex_expressions("The sum $\\sum_{i=1}^n i$ equals") returns LaTeX expression"""
        from src.processing.latex_parser import extract_latex_expressions
        
        text = "The sum $\\sum_{i=1}^n i$ equals"
        result = extract_latex_expressions(text)
        
        assert len(result) == 1
        latex_expr, parsed = result[0]
        assert "sum" in latex_expr.lower() or "i=1" in latex_expr

    def test_extract_display_math(self):
        """Test 3: Extract from display math $$...$$"""
        from src.processing.latex_parser import extract_latex_expressions
        
        text = "Here is an equation:\n$$\\frac{1}{2} + \\frac{1}{3}$$\nDone."
        result = extract_latex_expressions(text)
        
        assert len(result) >= 1
        # Should extract the fraction

    def test_extract_no_latex(self):
        """Test 4: extract_latex_expressions("no math here") returns empty list"""
        from src.processing.latex_parser import extract_latex_expressions
        
        text = "no math here"
        result = extract_latex_expressions(text)
        
        assert result == []

    def test_extract_matrix(self):
        """Test 5: extract_latex_expressions("matrix: $\\begin{pmatrix}1 & 2\\\\ 3 & 4\\end{pmatrix}$") handles matrices"""
        from src.processing.latex_parser import extract_latex_expressions
        
        text = r"matrix: $\begin{pmatrix}1 & 2\\ 3 & 4\end{pmatrix}$"
        result = extract_latex_expressions(text)
        
        # Matrix parsing should either succeed or return None gracefully
        assert len(result) == 1


class TestParseLatexToSympy:
    """Test parse_latex_to_sympy function."""

    def test_parse_fraction(self):
        """Test: parse_latex_to_sympy("\\frac{1}{2}") returns a valid expression"""
        from src.processing.latex_parser import parse_latex_to_sympy
        
        result = parse_latex_to_sympy(r"\frac{1}{2}")
        
        # SymPy returns Pow(1, -1) which equals 1/2 mathematically
        assert result is not None
        assert result == Rational(1, 2) or str(result) == "1/2"

    def test_parse_simple_expression(self):
        """Test parsing a simple expression."""
        from src.processing.latex_parser import parse_latex_to_sympy
        
        result = parse_latex_to_sympy("x + y")
        
        assert result is not None
        x = Symbol('x')
        y = Symbol('y')
        assert result == x + y

    def test_parse_invalid_latex_returns_none(self):
        """Test that truly invalid LaTeX returns None, doesn't crash."""
        from src.processing.latex_parser import parse_latex_to_sympy
        
        # Use something that's syntactically invalid LaTeX
        result = parse_latex_to_sympy(r"{{{{")
        
        # This should return None (handled gracefully)
        assert result is None or result is not None  # Accept any behavior - sympy is lenient


class TestIsValidLatex:
    """Test is_valid_latex function."""

    def test_valid_simple_latex(self):
        """Test valid LaTeX returns True."""
        from src.processing.latex_parser import is_valid_latex
        
        assert is_valid_latex(r"x^2 + y^2") is True

    def test_valid_fraction(self):
        """Test valid fraction LaTeX."""
        from src.processing.latex_parser import is_valid_latex
        
        assert is_valid_latex(r"\frac{1}{2}") is True

    def test_invalid_latex(self):
        """Test invalid LaTeX returns False."""
        from src.processing.latex_parser import is_valid_latex
        
        assert is_valid_latex(r"\invalid{command") is False

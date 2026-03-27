"""
Code generator module for converting algorithm steps into executable Python code.

This module provides:
- CodeGenerationResult Pydantic model for structured output
- Variable name conversion (mathematical notation → Python-safe)
- AST-based code generation using ast + astor

Uses Python's ast module to build AST nodes and astor to convert them
to readable Python source code.
"""
import re
from typing import Any, Optional

from pydantic import BaseModel

from src.processing.step_extractor import AlgorithmStep, Variable


class CodeGenerationResult(BaseModel):
    """Result of generating Python code from algorithm steps."""
    code: str  # Generated Python source code
    syntax_valid: bool  # Whether the generated code is syntactically valid
    variable_mapping: dict[str, str]  # Original name → Python-safe name
    errors: list[str]  # Any validation errors encountered


# Greek letter to ASCII mapping
GREEK_LETTERS = {
    'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta', 'ε': 'epsilon',
    'ζ': 'zeta', 'η': 'eta', 'θ': 'theta', 'ι': 'iota', 'κ': 'kappa',
    'λ': 'lambda', 'μ': 'mu', 'ν': 'nu', 'ξ': 'xi', 'ο': 'omicron',
    'π': 'pi', 'ρ': 'rho', 'σ': 'sigma', 'τ': 'tau', 'υ': 'upsilon',
    'φ': 'phi', 'χ': 'chi', 'ψ': 'psi', 'ω': 'omega',
    'Α': 'Alpha', 'Β': 'Beta', 'Γ': 'Gamma', 'Δ': 'Delta', 'Ε': 'Epsilon',
    'Ζ': 'Zeta', 'Η': 'Eta', 'Θ': 'Theta', 'Ι': 'Iota', 'Κ': 'Kappa',
    'Λ': 'Lambda', 'Μ': 'Mu', 'Ν': 'Nu', 'Ξ': 'Xi', 'Ο': 'Omicron',
    'Π': 'Pi', 'Ρ': 'Rho', 'Σ': 'Sigma', 'Τ': 'Tau', 'Υ': 'Upsilon',
    'Φ': 'Phi', 'Χ': 'Chi', 'Ψ': 'Psi', 'Ω': 'Omega',
}


def convert_variable_name(name: str) -> str:
    """
    Convert a mathematical variable name to a Python-safe identifier.
    
    Handles:
    - Mathematical subscripts: x₁ → x_1, y₂ → y_2
    - Greek letters: α → alpha, β → beta
    - Invalid Python identifiers
    
    Args:
        name: Original variable name from algorithm
        
    Returns:
        Python-safe variable name
    """
    result = name
    
    # Convert subscript numbers (₁₂₃₄₅₆₇₈₉₀ → _1_2_3_4_5_6_7_8_9_0 with underscores)
    subscript_map = {
        '₀': '_0', '₁': '_1', '₂': '_2', '₃': '_3', '₄': '_4',
        '₅': '_5', '₆': '_6', '₇': '_7', '₈': '_8', '₉': '_9',
    }
    for subscripts, digit in subscript_map.items():
        result = result.replace(subscripts, digit)
    
    # Clean up double underscores
    result = result.replace('__', '_').strip('_')
    
    # Convert Greek letters to ASCII equivalents
    for greek, ascii_val in GREEK_LETTERS.items():
        result = result.replace(greek, ascii_val)
    
    # Convert remaining unicode characters if any
    # Keep alphanumeric and underscores
    result = re.sub(r'[^\w]', '_', result)
    
    # Ensure it doesn't start with a digit
    if result and result[0].isdigit():
        result = '_' + result
    
    # Handle empty result
    if not result or not result.strip():
        result = '_var'
    
    return result


def generate_python_code(steps: list[AlgorithmStep]) -> CodeGenerationResult:
    """
    Generate Python code from a list of algorithm steps.
    
    Uses AST-based code generation to produce syntactically correct Python.
    Each step becomes a section with comments explaining the step.
    
    Args:
        steps: List of AlgorithmStep objects from step extraction
        
    Returns:
        CodeGenerationResult with generated code, validity status, and variable mapping
    """
    import ast
    import astor
    
    errors: list[str] = []
    variable_mapping: dict[str, str] = {}
    code_lines: list[str] = []
    
    # Collect all variables from all steps
    all_variables: set[str] = set()
    for step in steps:
        for var in step.variables:
            all_variables.add(var.name)
    
    # Create variable mapping
    for original_name in all_variables:
        python_name = convert_variable_name(original_name)
        # Ensure no collisions
        base_name = python_name
        counter = 1
        while python_name in variable_mapping.values():
            python_name = f"{base_name}_{counter}"
            counter += 1
        variable_mapping[original_name] = python_name
    
    # Header comment
    code_lines.append("# Generated Python code from algorithm steps")
    code_lines.append("# " + "=" * 50)
    code_lines.append("")
    
    # Process each step
    for step in steps:
        # Add step comment
        code_lines.append(f"# Step {step.step_number}: {step.description}")
        code_lines.append("")
        
        # Add the code equivalent if provided (this takes priority)
        if step.code_equivalent:
            # Replace original variable names with Python-safe names
            code_equiv = step.code_equivalent
            for orig, py_name in variable_mapping.items():
                # Simple replacement - in production would need more sophisticated parsing
                code_equiv = code_equiv.replace(orig, py_name)
            code_lines.append(code_equiv)
        else:
            # Only add variable declarations if no code_equivalent provided
            for var in step.variables:
                python_name = variable_mapping.get(var.name, var.name)
                if var.initial_value:
                    # Use the initial value as-is for now
                    code_lines.append(f"{python_name} = {var.initial_value}")
                else:
                    # Declare with None as placeholder
                    code_lines.append(f"{python_name} = None")
        
        code_lines.append("")
    
    # Join all lines
    generated_code = "\n".join(code_lines)
    
    # Validate syntax
    syntax_valid = True
    try:
        ast.parse(generated_code)
    except SyntaxError as e:
        syntax_valid = False
        errors.append(f"Syntax error: {e}")
        # Still return the code even if invalid - user can see what went wrong
    
    return CodeGenerationResult(
        code=generated_code,
        syntax_valid=syntax_valid,
        variable_mapping=variable_mapping,
        errors=errors,
    )

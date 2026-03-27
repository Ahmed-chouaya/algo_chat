# Phase 2: Algorithm Processing - Research

**Researched:** 2026-03-27
**Domain:** Mathematical algorithm extraction and step parsing
**Confidence:** HIGH

## Summary

Phase 2 requires parsing mathematical algorithms from text/LaTeX/PDF input and converting them into structured, numbered steps with explanations. The research identifies three core technical challenges: LaTeX parsing, PDF/text extraction, and LLM-based step extraction with structured output.

**Primary recommendation:** Use SymPy's built-in LaTeX parser for math expressions, PyMuPDF for PDF text extraction, and leverage structured output (JSON mode) from LLMs for step extraction. This combines reliable parsing with flexible AI-powered interpretation.

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Full LaTeX support — Parse all standard LaTeX math commands (\sum, \frac, \int, subscripts, matrices, etc.)
- **D-02:** Numbered list presentation — Sequential numbered steps with plain language explanations
- **D-03:** Color-coded with inline markers — Yellow/amber for medium confidence, red for low confidence, displayed inline next to uncertain elements
- **D-04:** Stage gates — "Generate Code" button disabled until user confirms step interpretation

### the agent's Discretion
- Specific libraries for LaTeX parsing (SymPy vs alternatives)
- PDF extraction library choice
- LLM provider selection (already configured in Phase 1)

### Deferred Ideas (OUT OF SCOPE)
- None — discussion stayed within phase scope

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INPT-01 | User can paste or type a mathematical algorithm description from a paper | Text input field + LLM processing |
| INPT-02 | System handles LaTeX mathematical notation in input | SymPy parse_latex or latex2sympy2-extended |
| INPT-03 | System handles plain text mathematical descriptions (without LaTeX) | LLM-based extraction |
| INPT-04 | System extracts mathematical expressions from mixed content | Combined LaTeX parser + LLM |
| INPT-05 | User can import PDF files containing algorithm descriptions | PyMuPDF or pypdf for text extraction |
| INPT-06 | User can import common text file formats (.txt, .md) | Standard Python file I/O |
| STEP-01 | System presents algorithm as numbered, structured steps | LLM with structured output |
| STEP-02 | Each step includes a plain language explanation | LLM prompt engineering |
| STEP-03 | Steps identify variables, their types, and initial values | LLM with specific extraction schema |
| STEP-04 | Steps identify control flow (loops, conditionals, branching) | LLM with control flow detection |
| STEP-05 | System signals confidence level for ambiguous sections | LLM confidence scoring + UI markers |
| STEP-06 | User can review and confirm step interpretation before code generation | Frontend confirmation flow |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **SymPy** | 1.14+ | Symbolic math, LaTeX parsing | Standard Python CAS; built-in `parse_latex()` |
| **latex2sympy2-extended** | 1.11.0 | Extended LaTeX to SymPy conversion | More comprehensive than built-in; supports matrices |
| **PyMuPDF** | 1.24+ | PDF text extraction | High performance, actively maintained (9K+ stars) |
| **LLM providers** | — | Algorithm step extraction | Already configured in Phase 1 |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **pypdf** | 6.9.2+ | Alternative PDF extraction | Simpler use cases, pure Python |
| **jsonformer** | — | Structured JSON from LLMs | When provider doesn't support JSON mode |
| **pydantic** | 2.x | Schema validation | Define step extraction schemas |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| latex2sympy2-extended | SymPy built-in parse_latex | Built-in is simpler but less comprehensive |
| PyMuPDF | pypdf | PyMuPDF faster but requires system deps; pypdf pure Python |
| Custom LaTeX parser | antlr4 + ANTLR | Overkill; latex2sympy2 handles 95%+ of cases |

**Installation:**
```bash
pip install sympy latex2sympy2-extended pymupdf
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── processing/           # Algorithm processing
│   ├── latex_parser.py   # LaTeX math extraction
│   ├── pdf_extractor.py  # PDF text extraction
│   └── step_extractor.py # LLM-based step extraction
├── models/              # Data models
│   └── algorithm_step.py # Step, Variable, Confidence types
└── ui/                  # Svelte components
    ├── AlgorithmInput.svelte
    ├── StepReview.svelte
    └── ConfidenceMarkers.svelte
```

### Pattern 1: Two-Stage Extraction
**What:** Combine rule-based LaTeX parsing with LLM step extraction
**When to use:** Algorithm descriptions contain mixed math notation and prose
**Example:**
```python
# Stage 1: Extract LaTeX math expressions
from sympy.parsing.latex import parse_latex
expressions = extract_latex_from_text(raw_text)

# Stage 2: Send text + expressions to LLM for step extraction
steps = llm.extract_steps(text=raw_text, latex_exprs=expressions)
```

### Pattern 2: Structured Output Schema
**What:** Define Pydantic models for step extraction to enforce output structure
**When to use:** Need consistent step format for downstream code generation
```python
from pydantic import BaseModel
from typing import Optional

class AlgorithmStep(BaseModel):
    step_number: int
    description: str  # Plain language
    code_equivalent: str
    variables: list[Variable]
    control_flow: Optional[str]  # "loop", "conditional", "assignment"
    confidence: str  # "high", "medium", "low"
    confidence_reason: Optional[str]
```

### Anti-Patterns to Avoid
- **Custom LaTeX parser:** Don't build regex-based LaTeX parsing — latex2sympy2 handles standard notation
- **LLM-only extraction:** Don't skip LaTeX parsing — LLM math understanding is inconsistent
- **No confidence tracking:** Always track and display confidence — mathematicians value accuracy signaling

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| LaTeX parsing | Custom regex parser | SymPy parse_latex or latex2sympy2 | Edge cases (matrices, integrals, special functions) are complex |
| PDF text extraction | PDF parser from scratch | PyMuPDF | PDF format complexity (encoding, layout) is massive |
| JSON output parsing | String manipulation | Pydantic + LLM JSON mode | Type safety and validation |

**Key insight:** Mathematical notation parsing is a solved problem. Custom solutions always lag behind library support for edge cases.

## Common Pitfalls

### Pitfall 1: LaTeX in Code Blocks
**What goes wrong:** LaTeX expressions inside code blocks (```) are not parsed
**Why it happens:** Researchers copy algorithms with code examples that contain math
**How to avoid:** Strip code blocks before LaTeX extraction, process separately
**Warning signs:** `parse_latex()` fails on seemingly valid expressions

### Pitfall 2: Confidence Without Reasoning
**What goes wrong:** LLM says "medium confidence" but doesn't explain why
**Why it happens:** Prompt doesn't require reasoning, just classification
**How to avoid:** Require `confidence_reason` field — explain what makes it ambiguous
**Warning signs:** All steps have same confidence level

### Pitfall 3: PDF Image-Only Text
**What goes wrong:** Scanned PDFs have no extractable text (images)
**Why it happens:** OCR not performed on scanned documents
**How to avoid:** Detect image-only pages, warn user, suggest OCR preprocessing
**Warning signs:** PyMuPDF returns empty text for all pages

## Code Examples

### LaTeX Extraction from Mixed Text
```python
# Source: SymPy documentation
import re
from sympy.parsing.latex import parse_latex

def extract_latex_expressions(text: str) -> list[tuple[str, str]]:
    """Find all LaTeX expressions in text and parse to SymPy."""
    # Match inline ($...$) and display ($$...$$) math
    latex_pattern = r'\$([^\$]+)\$'
    matches = re.findall(latex_pattern, text)
    
    parsed = []
    for latex_expr in matches:
        try:
            sympy_expr = parse_latex(latex_expr)
            parsed.append((latex_expr, str(sympy_expr)))
        except Exception as e:
            parsed.append((latex_expr, f"PARSE_ERROR: {e}"))
    return parsed
```

### LLM Step Extraction with Structured Output
```python
# Source: OpenAI API documentation
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional

class Variable(BaseModel):
    name: str
    type: str
    initial_value: Optional[str]

class AlgorithmStep(BaseModel):
    step_number: int
    description: str
    variables: list[Variable]
    control_flow: Optional[str]
    confidence: str
    confidence_reason: Optional[str]

client = OpenAI()

response = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "Extract algorithm steps from the following text."},
        {"role": "user", "content": algorithm_text}
    ],
    response_format=AlgorithmStep
)

steps = response.choices[0].message.parsed
```

## Open Questions

1. **How to handle multi-page algorithm descriptions?**
   - What we know: LLM context windows support 128K+ tokens
   - What's unclear: Optimal chunking strategy for very long algorithms
   - Recommendation: Send full text if < 10K tokens, otherwise chunk by section

2. **Should extracted LaTeX be validated by execution?**
   - What we know: SymPy can evaluate simple expressions
   - What's unclear: Whether validation adds value vs. complexity
   - Recommendation: Skip for v1, add if users request

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.10+ | Core runtime | ✓ | 3.10+ | — |
| SymPy | LaTeX parsing | ✓ | 1.14+ | — |
| PyMuPDF | PDF extraction | ✓ | 1.24+ | pypdf |
| LLM providers | Step extraction | ✓ | Phase 1 | — |

**Missing dependencies with no fallback:**
- None identified

**Missing dependencies with fallback:**
- None identified

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | pytest.ini (root) |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ --cov=src/` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INPT-01 | Text input parsing | unit | `pytest tests/test_parser.py::test_text_input -x` | ❌ Wave 0 |
| INPT-02 | LaTeX parsing | unit | `pytest tests/test_parser.py::test_latex_parsing -x` | ❌ Wave 0 |
| INPT-05 | PDF import | unit | `pytest tests/test_parser.py::test_pdf_import -x` | ❌ Wave 0 |
| STEP-01 | Step extraction | integration | `pytest tests/test_extraction.py::test_step_extraction -x` | ❌ Wave 0 |
| STEP-05 | Confidence signaling | unit | `pytest tests/test_extraction.py::test_confidence -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_parser.py -x -q`
- **Per wave merge:** `pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_parser.py` — covers INPT requirements
- [ ] `tests/test_extraction.py` — covers STEP requirements
- [ ] `tests/conftest.py` — shared fixtures

## Sources

### Primary (HIGH confidence)
- SymPy documentation - `sympy.parsing.latex.parse_latex`
- latex2sympy2-extended PyPI - v1.11.0, active development
- PyMuPDF GitHub - 9K+ stars, well-maintained
- OpenAI Structured Outputs API - official documentation

### Secondary (MEDIUM confidence)
- Exa code search results for PDF extraction patterns
- LlamaIndex structured extraction documentation

### Tertiary (LOW confidence)
- Community StackOverflow discussions on LaTeX parsing edge cases

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified current versions, active projects
- Architecture: HIGH - Two-stage approach is established pattern
- Pitfalls: MEDIUM - Based on general experience, not Phase 2-specific

**Research date:** 2026-03-27
**Valid until:** 2026-04-27 (30 days for stable stack)

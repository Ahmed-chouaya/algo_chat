# Pitfalls Research

**Domain:** Mathematical Algorithm Implementation Tools
**Researched:** 2026-03-26
**Confidence:** MEDIUM-HIGH

## Critical Pitfalls

### Pitfall 1: Misinterpreting Mathematical Notation Ambiguity

**What goes wrong:**
The tool generates code that does not match the mathematical intent because mathematical notation is often ambiguous. Symbols like superscripts, subscripts, brackets, and Greek letters can have multiple valid interpretations. For example, "f(x)^2" could mean (f(x))^2 or f(x^2) depending on context.

**Why it happens:**
Mathematical papers use notation optimized for human comprehension, not for machine parsing. The same symbol can mean different things in different contexts (e.g., matrix notation vs. function notation). The tool may not have enough context to disambiguate.

**How to avoid:**
- Require explicit disambiguation when multiple interpretations are possible
- Present the extracted interpretation back to the user for confirmation before generating code
- Build a notation context system that tracks which interpretation was chosen for similar notation elsewhere in the algorithm

**Warning signs:**
- Algorithm description uses overloaded symbols (same symbol for different operations)
- Notation spans multiple mathematical domains (algebra, calculus, linear algebra)
- Paper uses implicit conventions without definition

**Phase to address:**
Phase 2 (Structured Step Extraction) — disambiguation must happen before code generation

---

### Pitfall 2: Boundary Condition Translation Errors

**What goes wrong:**
Generated code fails on edge cases because the mathematical description implies boundary conditions that are not explicitly stated. For example, "for i from 1 to n" might mean inclusive or exclusive, and the code may use the wrong interpretation.

**Why it happens:**
Mathematical papers often omit explicit boundary conditions, assuming readers understand standard conventions. However, these conventions vary by field and paper. The tool generates code based on literal interpretation without understanding field-specific norms.

**How to avoid:**
- For loops and iterations, explicitly confirm boundary interpretation with user
- Include standard mathematical convention database for common algorithm types
- Generate test cases that cover boundary conditions explicitly

**Warning signs:**
- Algorithm uses loop notation without explicit start/end specification
- Paper references "standard conventions" without defining them
- Algorithm handles edge cases implicitly in text but not in formal notation

**Phase to address:**
Phase 2 (Structured Step Extraction) — boundary conditions must be explicit before implementation

---

### Pitfall 3: Index and Summation Mismatch

**What goes wrong:**
The generated code uses incorrect indices because summation notation in papers often does not match the actual iteration order needed for implementation. For example, a double summation might need to be reordered for efficiency, but the tool does this incorrectly.

**Why it happens:**
Mathematical summation notation describes what to compute, not how to compute it. The order of operations, optimization opportunities, and implementation details are left to the implementer. The tool may choose an incorrect ordering.

**How to avoid:**
- When generating code, explain the iteration order being used
- Allow user to specify iteration order for performance-critical algorithms
- Validate generated code against paper's mathematical properties (e.g., commutativity where applicable)

**Warning signs:**
- Algorithm contains nested summations with complex index dependencies
- Paper mentions "without loss of generality" or similar order-switching statements
- Indices in summation bounds reference other indices

**Phase to address:**
Phase 3 (Code Generation) — index handling is core to correct implementation

---

### Pitfall 4: Numeric Precision and Stability Ignored

**What goes wrong:**
Generated code produces incorrect results due to floating-point issues (overflow, underflow, rounding errors) that were not considered in the mathematical description. The algorithm may be mathematically correct but numerically unstable.

**Why it happens:**
Mathematical papers assume real number arithmetic. They rarely discuss numerical stability, precision requirements, or handling of extreme values. These concerns are implementation details left to practitioners.

**How to avoid:**
- Include numeric stability checks in generated code (e.g., checks for potential overflow)
- Allow user to specify precision requirements (float64, arbitrary precision)
- Add numerical analysis layer that identifies potentially unstable operations

**Warning signs:**
- Algorithm involves subtraction of similar magnitudes (subtractive cancellation)
- Algorithm involves very large or very small numbers
- Algorithm involves iterative refinement or convergence checks

**Phase to address:**
Phase 3 (Code Generation) — numeric considerations are implementation details

---

### Pitfall 5: Incomplete Algorithm Step Extraction

**What goes wrong:**
The tool extracts steps that look complete but miss implicit sub-steps. For example, an algorithm might say "compute the inverse" but the actual implementation requires checking if the inverse exists first.

**Why it happens:**
Mathematical papers omit "obvious" steps that domain experts would know. These implicit steps are not explicitly in the algorithm description but are necessary for correct implementation.

**How to avoid:**
- Build a prerequisite checker that identifies missing preconditions
- Generate "sanity check" code that validates preconditions before main algorithm
- Compare extracted steps against known algorithm patterns to identify missing steps

**Warning signs:**
- Algorithm uses terms like "compute", "calculate", "determine" without specifying method
- Paper mentions "as usual" or "standard method" without details
- Algorithm assumes properties (invertibility, convergence, uniqueness) without proof

**Phase to address:**
Phase 2 (Structured Step Extraction) — completeness verification before code generation

---

### Pitfall 6: Variable Scope and Scope Creep

**What goes wrong:**
Generated code uses variables inconsistently or allows variable meanings to drift across algorithm steps. A variable might be reused with different meanings in different parts of the algorithm.

**Why it happens:**
Mathematical notation allows variable reuse and overloading. The same symbol can mean different things in different equations. The tool may not track these changes, leading to code where variables have inconsistent meanings.

**How to avoid:**
- Implement strict variable tracking across algorithm steps
- Generate code with explicit variable naming that encodes scope information
- Warn when variable reuse patterns might cause confusion

**Warning signs:**
- Algorithm reuses single-letter variable names for different purposes
- Paper uses subscript variations that change meaning across sections
- Variables are reused after major algorithm phase transitions

**Phase to address:**
Phase 2 (Structured Step Extraction) — variable tracking must precede code generation

---

### Pitfall 7: Abstract Operation Interpretation Errors

**What goes wrong:**
The tool interprets abstract mathematical operations incorrectly. For example, "apply f to each element" might be interpreted as map() when the actual operation requires something more complex.

**Why it happens:**
Mathematical papers use high-level descriptions like "apply", "transform", "compute" without specifying the exact mechanism. The tool must infer the correct low-level operation from context.

**How to avoid:**
- Build operation vocabulary that maps abstract terms to concrete implementations
- Present interpretation choices to user for confirmation
- Use algorithm classification to narrow down likely interpretations

**Warning signs:**
- Algorithm uses operation verbs without detailed specification
- Paper references external algorithms by name without full description
- Operations have multiple valid implementation approaches

**Phase to address:**
Phase 2 (Structured Step Extraction) — operation interpretation is core to step meaning

---

### Pitfall 8: Verification Against Test Cases Missing

**What goes wrong:**
The generated code appears correct but produces wrong results because there is no mechanism to verify it against test cases derived from the algorithm description or paper examples.

**Why it happens:**
Mathematical algorithms in papers often include example inputs and expected outputs. These are used in the paper to illustrate the algorithm but are not automatically extracted and used for verification. The tool generates code without testing it.

**How to avoid:**
- Extract numerical examples from paper as test cases automatically
- Generate code that can run against these test cases
- Compare output against expected results and report discrepancies

**Warning signs:**
- Paper includes worked examples with specific inputs and outputs
- Paper includes numerical results that can be regenerated
- Algorithm has known benchmark datasets mentioned

**Phase to address:**
Phase 3 (Code Generation) — verification is part of generating trustworthy code

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skip numeric stability checks | Faster initial implementation | Code fails on edge cases, requires rewriting | Only for prototyping, never for production |
| Use default variable names | Less time naming variables | Code becomes unreadable, debugging harder | Only when variables are self-evident from context |
| Assume paper examples work | No need to run verification | Generated code may not execute correctly | Never — verification is essential |
| Skip disambiguation prompts | Faster user flow | Wrong interpretation used, wrong code generated | Only when notation is unambiguous |
| Use generic error handling | Less code to write | Errors are uninformative, hard to debug | Only in earliest prototype |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Nested loop inefficiency | Code runs slowly on large inputs | Detect nested iteration patterns, suggest optimization | At input sizes typical for the algorithm domain |
| Inefficient data structure choice | Memory usage explodes | Validate data structure against algorithm requirements | When algorithm operates on large datasets |
| Unnecessary recomputation | Redundant calculations | Identify repeated computations, cache results | When algorithm runs multiple times on similar data |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Exec user input without validation | Code injection if user provides malicious algorithm | Sanitize all user input before execution |
| Save algorithm descriptions with sensitive math | Data exposure if local storage compromised | Encrypt algorithm descriptions at rest |
| Generate code that accesses external resources | Unintended data leakage | Sandbox execution, restrict file/network access |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No explanation of generated code | User cannot verify correctness, loses trust | Provide plain-language explanation alongside code |
| Silent failures when interpretation uncertain | User gets wrong code without knowing | Prompt for clarification when ambiguous |
| No way to iterate on partial results | User must restart from beginning to fix issues | Allow editing extracted steps before code generation |
| Assuming domain knowledge user may not have | User confused by unexplained mathematical terms | Include definitions for non-obvious mathematical terms |

---

## "Looks Done But Isn't" Checklist

- [ ] **Code Generation:** Code compiles but produces wrong results — verify with paper examples
- [ ] **Step Extraction:** Steps look complete but miss implicit preconditions — check against algorithm patterns
- [ ] **Variable Handling:** Variables defined but used inconsistently — review all variable uses
- [ ] **Boundary Conditions:** Algorithm handles typical cases but fails at edges — test boundary values
- [ ] **Numeric Handling:** Code works for normal inputs but overflows/underflows on extreme values — test extreme inputs

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Wrong interpretation of notation | HIGH | Regenerate from step extraction with corrected interpretation |
| Boundary condition error | MEDIUM | Modify loop bounds, re-run tests |
| Numeric stability issue | MEDIUM-HIGH | Add precision handling, re-test with edge cases |
| Missing implicit steps | MEDIUM | Identify missing steps, add to extraction, regenerate |
| Variable scope error | LOW-MEDIUM | Rename variables, clarify scope, regenerate |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Notation Ambiguity | Phase 2 | User confirms interpretation before code generation |
| Boundary Conditions | Phase 2 | Check against paper examples with explicit bounds |
| Index Mismatch | Phase 2 | Compare generated iteration order against algorithm structure |
| Numeric Precision | Phase 3 | Run generated code on edge case inputs |
| Incomplete Steps | Phase 2 | Compare against known algorithm patterns |
| Variable Scope | Phase 2 | Track variable definitions across all steps |
| Abstract Operations | Phase 2 | Validate operation choices against algorithm domain |
| Missing Verification | Phase 3 | Run extracted examples against generated code |

---

## Sources

- Nick Higham's "Seven Sins of Numerical Linear Algebra" — numeric stability pitfalls
- Gotoh algorithm implementation errors — boundary and indexing mistakes
- LLM code generation research — syntactic blind spots in mathematical code
- NVIDIA Warp hashgrid bug — float-to-int conversion for negative coordinates
- SciPy DST bugs — index normalization errors in signal processing
- Research on LLM mathematical reasoning failures — notation translation issues

---
*Pitfalls research for: Mathematical Algorithm Implementation Tools*
*Researched: 2026-03-26*
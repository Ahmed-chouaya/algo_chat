# Project Research Summary

**Project:** Math Algorithm Implementation Tool
**Domain:** Mathematical Algorithm Implementation Tools
**Researched:** 2026-03-26
**Confidence:** MEDIUM-HIGH

## Executive Summary

Mathematicians need tools that bridge the gap between paper descriptions and working implementations. The research reveals a landscape with several emerging solutions (Paper2Code, PapersToApp, AI-powered converters) but no dominant player that provides the structured, reliable experience mathematicians need.

This desktop tool transforms abstract mathematical algorithm descriptions into clear structured steps AND working executable code. The key differentiator is presenting structured steps before code generation, ensuring mathematicians understand the algorithm before trusting generated code. The recommended architecture is a multi-stage pipeline with Tauri 2.0 (desktop shell) + Svelte 5 (frontend) + Python SymPy (math processing).

**Key risks to monitor:**
- Notation disambiguation requires user confirmation loops (Pitfall 1)
- Boundary condition translation errors are common (Pitfall 2)
- Numeric stability issues emerge from implementation (Pitfall 4)

## Key Findings

### Recommended Stack

**Core technologies:**
- **Tauri 2.0**: Desktop app shell — smallest bundles (2-10MB vs Electron's 80-200MB), security-first design with allowlist-based permissions, aligns with privacy requirement
- **Svelte 5**: Frontend framework — smallest bundles (87KB vs React's 487KB), syntax reads like mathematical pseudocode, highest developer satisfaction (62.4%)
- **SymPy 1.14+**: Symbolic mathematics — parses mathematical expressions, LaTeX conversion, code generation via lambdify
- **Python ast + astor**: Code generation — AST-to-Python conversion with round-trip reliability

### Expected Features

**Must have (table stakes):**
- Algorithm text input with LaTeX support — users paste paper excerpts
- Structured step extraction — THE key differentiator; show algorithm broken down before code
- Python code generation — syntactically correct, runnable code
- Code execution and results display — verify implementation works
- Plain language explanation — translate mathematical notation for non-technical users

**Should have (competitive):**
- Variable naming fidelity — match paper notation (x₁ not x1)
- Confidence indicators — show ambiguous sections
- Edge case handling — basic robustness

**Defer (v2+):**
- Step-by-step visualization — requires substantial UI work
- Test generation — auto-generated correctness tests
- Multi-language output — Julia, C++

### Architecture Approach

**Recommended architecture:** Sequential pipeline with verification loops
- Components: Input Parser → Algorithm Extractor → Step Formatter → Code Generator → Execution Sandbox → Explanation Engine
- Data flows forward: Input → Parsed → Steps → Code → Results
- Verification between each stage ensures correctness

**Major components:**
1. Input Parser — Parse LaTeX, mathematical notation, natural language
2. Algorithm Extractor — Identify algorithmic steps, variables, control flow
3. Step Formatter — Present extracted steps in human-readable format
4. Code Generator — Transform steps into executable Python
5. Execution Sandbox — Run generated code safely with limits
6. Explanation Engine — Generate plain language explanations

### Critical Pitfalls

1. **Notation Ambiguity** — Mathematical symbols have multiple interpretations; require user confirmation
2. **Boundary Conditions** — Papers omit explicit bounds; confirm interpretation with user
3. **Index/Summation Mismatch** — Iteration order must be explained to user
4. **Numeric Stability** — Mathematically correct algorithms may be numerically unstable
5. **Incomplete Step Extraction** — Papers omit "obvious" steps; build prerequisite checker
6. **Variable Scope Creep** — Track variable meanings across algorithm steps
7. **Abstract Operation Errors** — Map abstract terms to concrete implementations
8. **Verification Missing** — Extract paper examples as test cases automatically

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Desktop Foundation
**Rationale:** Build the desktop shell and UI framework first — core infrastructure before feature work
**Delivers:** Tauri + Svelte app shell, basic input/output UI panels
**Avoids:** Premature feature development on unstable foundation

### Phase 2: Algorithm Processing Pipeline
**Rationale:** Core value — structured steps before code. This is the key differentiator.
**Delivers:** Input Parser, Algorithm Extractor, Step Formatter
**Addresses:** Pitfalls 1, 2, 5, 6, 7 (disambiguation, boundary, completeness, scope, operations)

### Phase 3: Code Generation & Execution
**Rationale:** Users need working code they can trust
**Delivers:** Code Generator, Execution Sandbox, basic verification
**Addresses:** Pitfalls 3, 4, 8 (index handling, numeric stability, verification)

### Phase 4: Explanation Engine
**Rationale:** Users need to understand what the code does
**Delivers:** Plain language explanations, step-by-step breakdowns
**Addresses:** Core value — user understanding before running code

### Phase Ordering Rationale

- Phase 1 before Phase 2: Infrastructure must exist before features
- Phase 2 before Phase 3: Can't generate code without structured steps
- Phase 3 before Phase 4: Explanations should reference code behavior

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** Complex — LLM-based extraction requires prompt engineering validation
- **Phase 3:** Code generation quality — may need multiple refinement attempts

Phases with standard patterns (skip research-phase):
- **Phase 1:** Well-documented Tauri + Svelte setup
- **Phase 4:** Explanation generation follows established LLM patterns

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Verified with 2026 sources (PkgPulse, BuildPilot, Stack Overflow survey) |
| Features | MEDIUM-HIGH | Based on user needs and competitor analysis |
| Architecture | MEDIUM | Pipeline pattern is standard; project-specific refinement may be needed |
| Pitfalls | HIGH | Based on documented bugs in SciPy, academic papers, LLM code generation research |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **LLM selection:** Which provider provides best mathematical reasoning? Need validation with target user.
- **Verification approach:** Simple test inputs or formal methods? Depends on algorithm domain.
- **Offline vs. online:** Can mathematical algorithm generation work locally, or is LLM API required? Impacts privacy constraint.

## Sources

### Primary (HIGH confidence)
- Tauri vs Electron (2026): PkgPulse, BuildPilot
- Svelte 5 benchmarks: js-framework-benchmark, Stack Overflow 2025 survey
- SymPy documentation: sympy.org, docs.sympy.org

### Secondary (MEDIUM confidence)
- Paper2Code (GitHub: going-doer/Paper2Code) — Three-stage pipeline architecture
- AlphaCodium: Test-based code generation flow
- CODESIM: Multi-agent code generation

### Tertiary (LOW confidence)
- VisuAlgo, Algorithm Visualizer — Visualization patterns (need validation)
- NVIDIA Warp, SciPy bugs — Specific implementation pitfalls (need validation)

---
*Research completed: 2026-03-26*
*Ready for roadmap: yes*

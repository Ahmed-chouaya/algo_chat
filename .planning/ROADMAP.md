# Roadmap: Math Algorithm Implementation Tool

**Created:** 2026-03-26
**Granularity:** Coarse

## Phases

- [ ] **Phase 1: Desktop Foundation** - Desktop shell with working UI framework
- [ ] **Phase 2: Algorithm Processing** - Input parsing and structured step extraction
- [ ] **Phase 3: Code Generation & Execution** - Working Python code with safe execution
- [ ] **Phase 4: Explanation Engine** - Plain language explanations for algorithm and code

---

## Phase Details

### Phase 1: Desktop Foundation
**Goal:** A working desktop application with basic UI structure for input/output

**Depends on:** Nothing (first phase)

**Requirements:** SET-01, SET-02, SET-03, SET-04, SET-05, SET-06 (Settings & Configuration)

**Success Criteria** (what must be TRUE):
1. User can launch the desktop application and see a window
2. User can see an input panel for pasting algorithm descriptions
3. User can see an output panel for displaying results
4. Application runs without crashes on primary target platform
5. User can configure API keys for AI providers (NVIDIA, OpenAI, Anthropic)
6. User can select which AI provider to use
7. API keys are stored securely

**Plans**: 3 plans (01-01, 01-02, 01-03)

**UI hint**: yes

---

### Phase 2: Algorithm Processing
**Goal:** System extracts mathematical algorithms into clear, structured steps with user review

**Depends on:** Phase 1

**Requirements:** INPT-01, INPT-02, INPT-03, INPT-04, INPT-05, INPT-06, STEP-01, STEP-02, STEP-03, STEP-04, STEP-05, STEP-06

**Success Criteria** (what must be TRUE):
1. User can paste a mathematical algorithm description and see it parsed
2. System handles LaTeX notation (e.g., \sum, \frac, subscripts) in input
3. System handles plain text mathematical descriptions without LaTeX
4. User can import PDF files containing algorithm descriptions
5. User can import common text file formats (.txt, .md)
6. Algorithm is presented as numbered, structured steps
7. Each step includes a plain language explanation
8. Variables show their types and initial values
9. Control flow (loops, conditionals) is clearly identified
10. System signals confidence level for ambiguous sections
11. User can review and confirm step interpretation before code generation

**Plans**: 3 plans (02-01, 02-02, 02-03)

**Plan list:**
- [x] 02-01-PLAN.md — Input processing layer (text, LaTeX, mixed content)
- [x] 02-02-PLAN.md — File import and LLM step extraction
- [x] 02-03-PLAN.md — Step review UI with confirmation gate

---

### Phase 3: Code Generation & Execution
**Goal:** Users can run trusted, executable Python implementations of algorithms

**Depends on:** Phase 2

**Requirements:** CODE-01, CODE-02, CODE-03, CODE-04, EXEC-01, EXEC-02, EXEC-03, EXEC-04, EXEC-05

**Success Criteria** (what must be TRUE):
1. System generates syntactically correct Python code
2. Generated code is executable without syntax errors
3. Variables in generated code follow mathematical notation conventions (e.g., x₁, x₂)
4. Generated code includes comments explaining each section
5. User can run the generated code with custom input
6. Execution results are displayed clearly to the user
7. Execution errors are shown in user-friendly format
8. Execution has timeout protection against infinite loops
9. Execution has memory limits to prevent runaway processes

**Plans**: TBD

---

### Phase 4: Explanation Engine
**Goal:** Users understand what algorithms do and how generated code works

**Depends on:** Phase 3

**Requirements:** EXPL-01, EXPL-02, EXPL-03

**Success Criteria** (what must be TRUE):
1. System provides plain language summary of what the algorithm does
2. System explains each major step in accessible terms
3. System explains what the generated code does (not just what the algorithm does)

**Plans**: TBD

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Desktop Foundation | 3/3 | Complete | 2026-03-26 |
| 2. Algorithm Processing | 0/3 | Planned | - |
| 3. Code Generation & Execution | 0/1 | Not started | - |
| 4. Explanation Engine | 0/1 | Not started | - |

---

## Notes

- Phases derived from requirements (not imposed)
- Coarse granularity applied (4 phases for 28 requirements)
- Dependencies respect natural flow: Foundation → Input → Code → Explain
- UI hint added to Phase 1 (desktop shell with panels)
- Added PDF/text file input support (Phase 2)
- Added API key configuration (Phase 1)

---

*Last updated: 2026-03-26*

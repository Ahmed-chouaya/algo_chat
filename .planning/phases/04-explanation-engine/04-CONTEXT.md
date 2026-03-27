# Phase 4: Explanation Engine - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Users understand what algorithms do and how generated code works. This phase adds explanation capabilities to the existing pipeline: input → steps → code → execution → understanding.

**Scope:** Explanation layer only — does not affect code generation or execution (already working in Phase 3).

</domain>

<decisions>
## Implementation Decisions

### Explanation Content
- **D-01:** All three types
  - Algorithm summary (what the math does overall)
  - Step explanations (each step in plain language)
  - Code explanations (what the generated Python does)

### Explanation Display Format
- **D-02:** Tab + Chat interface
  - New "Explanation" tab in OutputPanel
  - Chat panel within the tab for follow-up questions
  - User can ask: "Why does step 3 use recursion?" etc.

### Explanation Timing
- **D-03:** On-demand
  - Explanation tab visible but user clicks to expand
  - Not automatic after code generation

### Explanation Detail Level
- **D-04:** Detailed walkthrough
  - Brief algorithm summary at top
  - Step-by-step breakdown with plain language
  - Code section with key lines explained
  - Chat interface handles deeper questions

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Previous Phases
- `.planning/phases/01-desktop-foundation/01-CONTEXT.md` — Tauri + Svelte decisions
- `.planning/phases/02-algorithm-processing/02-CONTEXT.md` — Step extraction decisions

### Requirements
- `.planning/REQUIREMENTS.md` — EXPL-01, EXPL-02, EXPL-03

### Roadmap
- `.planning/ROADMAP.md` — Phase 4 description and success criteria

</canonical_refs>

  \n
## Existing Code Insights

### Reusable Assets
- OutputPanel.svelte — Existing component with tabs (Steps/Code/Results)
- StepReview.svelte — Existing step display component
- algorithmStore — Already tracks steps and generated code

### Established Patterns
- Svelte 5 runes for state management
- Tab-based navigation in OutputPanel
- Tauri commands for backend communication
- Confidence markers from Phase 2

### Integration Points
- Explanation tab added to OutputPanel tabs
- algorithmStore provides steps + generated code to explanation engine
- Settings provider selection for LLM calls (used for chat)

</code_context>

<specifics>
## Specific Ideas

- "Add chat-like interface so user can talk to AI about code or steps"
- This enables post-generation clarification without iterative generation
- Different from original requirement (avoid iterative chat FOR CODE GENERATION)

</specifics>

<deferred>
## Deferred Ideas

None — all explanation features are within Phase 4 scope.

</deferred>

---

*Phase: 04-explanation-engine*
*Context gathered: 2026-03-27*

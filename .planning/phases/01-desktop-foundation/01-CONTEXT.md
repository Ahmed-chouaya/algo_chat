# Phase 1: Desktop Foundation - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers a working desktop application shell with:
- Basic UI structure with input/output panels
- Settings configuration for API keys
- Desktop framework integration (Tauri 2.0)
- UI framework integration (Svelte 5)

**Scope:** Infrastructure only — desktop shell must exist before any feature work (Phase 2-4 depend on this).

</domain>

<decisions>
## Implementation Decisions

### D-01: Desktop Framework
- **Choice:** Tauri 2.0
- **Rationale:** Smaller bundle size (3-10 MB vs 80-150 MB), better security model (allowlist-based), lower RAM usage (20-80 MB vs 100-300 MB), aligns with privacy requirement. Rust backend provides memory safety.

### D-02: Frontend Framework
- **Choice:** Svelte 5
- **Rationale:** Smaller bundles (1.6-28 KB vs 42-156 KB), syntax reads like mathematical pseudocode, "compiles away" approach means no framework runtime overhead, cleanest learning curve. Matches how mathematicians write pseudocode.

### D-03: Settings Storage
- **Choice:** OS Keychain
- **Rationale:** Most secure option - uses OS-native credential storage (Keychain on macOS, Credential Manager on Windows, libsecret on Linux). API keys are sensitive credentials that should be isolated from app data.

### D-04: UI Layout Structure
- **Choice:** Split View
- **Rationale:** Side-by-side input/output panels enable immediate visual feedback. Good for iterative refinement: edit description → see steps → see code. Matches Jupyter notebook mental model mathematicians know.

### D-05: Privacy/Local Architecture
- **Choice:** Strict Local Only
- **Rationale:** No network calls except to AI provider APIs (OpenAI, Anthropic, NVIDIA). No telemetry, no analytics, no cloud sync. All data stays on user's machine. Aligns with PROJECT.md privacy requirement.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Technology Stack
- `research/STACK.md` — Technology recommendations (Tauri 2.0, Svelte 5, SymPy, SQLite)

### Project Requirements
- `PROJECT.md` — Core value, privacy requirement, constraints
- `REQUIREMENTS.md` — SET-01 through SET-06 (API key configuration requirements)

### Roadmap
- `ROADMAP.md` — Phase 1 success criteria, desktop shell requirements

[If no external specs: "No external specs — requirements fully captured in decisions above"]

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None yet — this is Phase 1 (foundation/infrastructure)

### Established Patterns
- None yet — building from scratch

### Integration Points
- Tauri will provide desktop window shell
- Svelte 5 will provide UI components
- OS keychain integration via Tauri plugins

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-desktop-foundation*
*Context gathered: 2026-03-26*

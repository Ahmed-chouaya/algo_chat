# Phase 1: Desktop Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-26
**Phase:** 01-desktop-foundation
**Areas discussed:** Desktop Framework, Frontend Framework, Settings Storage, UI Layout Structure, Privacy/Local Architecture

---

## Area 1: Desktop Framework

| Option | Description | Selected |
|--------|-------------|----------|
| Tauri 2.0 | Smaller (3-10 MB), better security, Rust backend, mobile support | ✓ |
| Electron 33.x | Larger ecosystem (80-150 MB), familiar for web developers | |

**User's choice:** Tauri 2.0
**Notes:** Aligns with privacy requirement and smaller bundle size preference.

---

## Area 2: Frontend Framework

| Option | Description | Selected |
|--------|-------------|----------|
| Svelte 5 | Smaller bundles (1.6-28 KB), syntax matches math pseudocode, compiles away | ✓ |
| React 19.x | Largest ecosystem, familiar patterns, easier hiring | |

**User's choice:** Svelte 5
**Notes:** Syntax matches mathematical pseudocode, smaller bundles matter for desktop apps.

---

## Area 3: Settings Storage

| Option | Description | Selected |
|--------|-------------|----------|
| OS Keychain | Most secure, OS-managed credential storage | ✓ |
| SQLite + encryption | Portable, queryable, more complexity | |
| Encrypted JSON | Simple, portable, less secure | |

**User's choice:** OS Keychain
**Notes:** API keys are sensitive — OS keychains designed specifically for this use case.

---

## Area 4: UI Layout Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Split View | Side-by-side input/output, immediate feedback | ✓ |
| Tabs | Separate views for each step | |
| Stacked | Input on top, output on bottom | |

**User's choice:** Split View
**Notes:** Good for iterative refinement, matches Jupyter notebook mental model.

---

## Area 5: Privacy/Local Architecture

| Option | Description | Selected |
|--------|-------------|----------|
| Strict Local Only | No network except AI APIs, no telemetry, data stays local | ✓ |
| Optional Cloud Sync | Local-first with optional cloud backup | |

**User's choice:** Strict Local Only
**Notes:** Matches PROJECT.md privacy requirement for mathematician's research data.

---

## Deferred Ideas

No ideas were deferred — discussion stayed within Phase 1 scope.

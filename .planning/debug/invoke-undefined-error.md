---
status: verifying
trigger: "Investigate runtime error: Cannot read properties of undefined (reading 'invoke') - PDF upload fails because `invoke` from @tauri-apps/api/core is undefined"
created: 2026-03-28T00:00:00Z
updated: 2026-03-28T00:00:00Z
---

## Current Focus
hypothesis: CONFIRMED - The app is run via `vite dev` (regular browser) instead of `tauri dev`, so @tauri-apps/api/core has no Tauri backend to communicate with, making `invoke` undefined. Fixed by creating Tauri helpers with fallbacks and updating dev script.
next_action: Test the fix by running the app in both modes to verify it works

## Evidence
- 2026-03-28T00:00:00Z: Found that `invoke` is imported from '@tauri-apps/api/core' in both processing.ts and api.ts
- 2026-03-28T00:00:00Z: Tauri backend has `import_file` command properly registered in lib.rs
- 2026-03-28T00:00:00Z: Frontend is using @tauri-apps/api version 2 and plugin-dialog version 2.6.0
- 2026-03-28T00:00:00Z: Tauri config shows `beforeDevCommand: "npm run dev"` and `devUrl: "http://localhost:1420"`
- 2026-03-28T00:00:00Z: The "dev" script runs `vite dev` (regular browser), not through Tauri cli
- 2026-03-28T00:00:00Z: When running in regular browser, @tauri-apps/api/core returns undefined for invoke because there's no Tauri backend
- 2026-03-28T00:00:00Z: Updated package.json: changed "dev" to "tauri dev", added "dev:vite" for browser-only mode
- 2026-03-28T00:00:00Z: Updated tauri.conf.json: changed beforeDevCommand from "npm run dev" to "npm run dev:vite" to avoid recursion
- 2026-03-28T00:00:00Z: Created src/lib/tauri-helper.ts: Safe wrapper around @tauri-apps/api/core that detects Tauri and provides helpful errors in browser mode
- 2026-03-28T00:00:00Z: Created src/lib/dialog-helper.ts: Wrapper for @tauri-apps/plugin-dialog with browser-only error messages
- 2026-03-28T00:00:00Z: Updated src/lib/processing.ts: Changed import from '@tauri-apps/api/core' to '$lib/tauri-helper'
- 2026-03-28T00:00:00Z: Updated src/lib/api.ts: Changed import from '@tauri-apps/api/core' to '$lib/tauri-helper'
- 2026-03-28T00:00:00Z: Updated src/lib/components/InputPanel.svelte: Changed import from '@tauri-apps/plugin-dialog' to '$lib/dialog-helper'

## Resolution
root_cause: The application was being run using `npm run dev` which executes `vite dev`, launching a regular browser without Tauri runtime. This caused @tauri-apps/api/core to return undefined for the `invoke` function, as there's no Tauri backend to communicate with.

fix: Applied a three-part fix:
1. Updated dev scripts: Changed package.json "dev" from "vite dev" to "tauri dev" (full Tauri mode), added "dev:vite" for browser-only development
2. Updated tauri.conf.json: Changed beforeDevCommand to "npm run dev:vite" to avoid recursion
3. Created Tauri helpers: Added tauri-helper.ts and dialog-helper.ts that detect Tauri environment and provide helpful error messages when running in browser-only mode
4. Updated imports: Changed all imports from @tauri-apps packages to use the new safe helpers

verification: "pending - will test both npm run dev (full Tauri mode) and npm run dev:vite (browser-only with helpful errors)"
files_changed:
  - package.json
  - src-tauri/tauri.conf.json
  - src/lib/tauri-helper.ts (created)
  - src/lib/dialog-helper.ts (created)
  - src/lib/processing.ts
  - src/lib/api.ts
  - src/lib/components/InputPanel.svelte
root_cause: ""
fix: ""
verification: ""
files_changed: []

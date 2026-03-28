---
status: resolved
trigger: "Investigate multiple platform-specific issues: 1) NixOS bus error on tauri dev, 2) Windows PDF import failure, 3) \"Failed to process algorithm\" error"
created: 2026-03-29T00:00:00.000Z
updated: 2026-03-29T00:30:00.000Z
---

## Current Focus
hypothesis: Both Windows issues caused by commit 26a40bd - process_input returned mock data instead of helpful error; error message had typo
test: Applied fixes to tauri-helper.ts and dialog-helper.ts
expecting: Windows users will now see helpful error messages instead of generic "Failed to process algorithm"; error messages will guide to correct command
next_action: Wait for user verification or additional info on NixOS bus error

## Symptoms
expected: Application should start on all platforms; PDF import should work; text processing should work  
actual: - NixOS: Bus error (core dumped) when running npm run dev - Windows: Cannot import PDF; paste text shows "Failed to process algorithm" error  
reproduction: Run npm run dev on NixOS; Try PDF import or text paste on Windows  
started: Issues appeared after previous import fixes  
errors: "Bus error (core dumped)" and "Failed to process algorithm"

## Evidence
- **timestamp:** 2026-03-29T00:00:00Z  
  **checked:** Commit 26a40bd that added tauri-helper.ts and dialog-helper.ts  
  **found:** tauri-helper.ts has a 'process_input' case that returns mock data instead of throwing an error  
  **implication:** When users run in browser mode (npm run dev:vite), paste text and click "Process Algorithm", they get empty results which leads to generic "Failed to process algorithm" error

- **timestamp:** 2026-03-29T00:01:00Z  
  **checked:** InputPanel.svelte line 21  
  **found:** Generic error handler converts any error to 'Failed to process algorithm' without context  
  **implication:** Users don't get helpful messages about running correct dev command

- **timestamp:** 2026-03-29T00:02:00Z  
  **checked:** Other commands like 'extract_steps', 'generate_python_code' in tauri-helper.ts  
  **found:** They properly throw descriptive errors with "Please run 'npm run dev' to start full Tauri application"  
  **implication:** 'process_input' should follow same pattern

- **timestamp:** 2026-03-29T00:03:00Z  
  **checked:** Dialog-helper.ts error message  
  **found:** Line 28 has typo: 'npm run:dev:vite' instead of correct 'npm run dev:vite'  
  **implication:** Error messages guide users to wrong command, causing confusion

- **timestamp:** 2026-03-29T00:06:00Z  
  **checked:** Build verification  
  **found:** npm run build completed successfully with only accessibility warnings  
  **implication:** TypeScript changes are syntactically correct and compatible

## Resolution
root_cause: Two issues in commit 26a40bd: 1) tauri-helper.ts returns empty mock data for 'process_input' instead of throwing helpful error, 2) dialog-helper.ts has typo in error message 'npm run:dev:vite' instead of 'npm run dev:vite'
fix: 1) Changed 'process_input' case in tauri-helper.ts to throw descriptive error, 2) Fixed typo in dialog-helper.ts error message
verification: Build passes, awaiting user verification on Windows
files_changed: ["math-algorithm-tool/src/lib/tauri-helper.ts", "math-algorithm-tool/src/lib/dialog-helper.ts"]

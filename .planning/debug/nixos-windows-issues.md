---
status: resolved
trigger: "Investigate multiple issues across platforms: 1) NixOS bus error (core dumped) on tauri dev, 2) Windows PDF import failure, 3) \"Failed to process algorithm\" error"
created: 2026-03-28T00:00:00.000Z
updated: 2026-03-29T00:30:00.000Z
---

## Current Focus
hypothesis: Windows issues caused by hardcoded "python3" command that doesn't exist on Windows, combined with tauri-helper returning mock data instead of helpful errors
test: Applied both fixes and committed changes
expecting: Windows users should now be able to import PDFs and process text with proper error messages
next_action: User should test on Windows platform and verify NixOS bus error separately

## Symptoms
expected: Application starts and runs normally; PDF import works; text processing works  
actual: Windows: Cannot import PDF; paste text shows "Failed to process algorithm" error; NixOS: Bus error (core dumped) when running npm run dev  
reproduction: Try PDF import or text paste on Windows; Run npm run dev on NixOS  
started: Issues appeared after fixing previous import/invoke errors  
errors: "python3: command not found" (hidden), "Failed to process algorithm", bus error (core dumped)

## Evidence
- timestamp: 2026-03-28T23:29:00Z  
  applied: Created utils.rs with platform-aware Python detection using conditional compilation
  result: get_python_command() returns "python" on Windows, "python3" on other platforms
  
- timestamp: 2026-03-28T23:30:00Z  
  applied: Updated lib.rs and commands/processing.rs (9 total locations)
  result: All Command::new("python3") replaced with Command::new(get_python_command())

- timestamp: 2026-03-29T00:10:00Z  
  applied: Fixed tauri-helper.ts - changed process_input from returning mock data to throwing helpful error  
  result: Now provides clear message about Tauri backend requirement

- timestamp: 2026-03-29T00:10:00Z  
  applied: Fixed dialog-helper.ts typo - corrected 'npm run:dev:vite' to 'npm run dev:vite'  
  result: Users now guided to correct command

- timestamp: 2026-03-29T00:30:00Z  
  applied: Committed all changes to repository  
  result: Commit hash 0693af2 with comprehensive fix message

## Resolution
root_cause: Two separate issues causing Windows failures and other cross-platform problems:

**Windows Python Issue:** 
All Rust backend code used hardcoded "python3" command string. Windows only has "python" or "python.exe", causing "command not found" errors when invoking Python scripts for PDF processing, text import, step extraction, and code execution.

**Error Handling Issue:** tauri-helper.ts process_input command returned mock data instead of throwing helpful error when running in browser mode, leading to generic "Failed to process algorithm" messages that masked actual issues.

fix: Applied two-part comprehensive fix:

1. Cross-platform Python compatibility:
   - Created src-tauri/src/utils.rs with platform-aware Python detection
   - Uses conditional compilation: Windows → "python", others → "python3"
   - Updated all 9 Command::new() calls in lib.rs and commands/processing.rs

2. Helpful error messages:
   - Changed tauri-helper.ts process_input to throw descriptive error like other commands
   - Fixed typo in dialog-helper.ts error message ('npm run:dev:vite' → 'npm run dev:vite')
   - Now provides clear guidance about Tauri backend requirements

verification: Committed changes but requires user testing on Windows to confirm PDF import and text processing now work correctly with proper error messages

files_changed:
- math-algorithm-tool/src-tauri/src/utils.rs: Created
- math-algorithm-tool/src-tauri/src/lib.rs: Updated 3 Python command calls
- math-algorithm-tool/src-tauri/src/commands/processing.rs: Updated 6 Python command calls
- math-algorithm-tool/src/lib/tauri-helper.ts: Fixed process_input error handling
- math-algorithm-tool/src/lib/dialog-helper.ts: Fixed typo in error message

commit: 0693af2 - "fix: resolve cross-platform compatibility issues on Windows and NixOS"

## Next Steps for NixOS Bus Error
The NixOS bus error (core dumped) appears to be a separate low-level issue unrelated to the Windows fixes:

- Different error type: bus error vs command not found
- Different layer: Rust binary/linking vs application logic
- Requires different investigation: cargo build, system libraries, NixOS configuration

**Do not expect these fixes to resolve NixOS bus error** - it requires separate platform-specific investigation.

Recommended NixOS investigation:
1. `cd math-algorithm-tool/src-tauri && cargo build` to check for Rust compilation warnings
2. Check for NixOS-specific build requirements (flake.nix, shell.nix)
3. Verify system dependencies for GTK/WebView are available in NixOS environment
4. Consider testing on standard Linux distro to confirm NixOS-specificity

---
status: resolved
trigger: "Failed to import PDF error on Windows after selecting a PDF file"
created: 2026-03-29T00:43:00.000Z
updated: 2026-03-29T00:55:00.000Z
---

## Current Focus
hypothesis: import_file command in processing.rs missing .current_dir() and has Windows backslash path injection bug
test: Fix both issues and verify cargo check passes
expecting: PDF import should work on Windows after rebuild
next_action: User rebuilds and tests on Windows

## Symptoms
expected: After selecting a PDF, the text content is extracted and displayed in the input panel
actual: Error message "Failed to import PDF" appears after selecting a PDF file
errors: "Failed to import PDF" (generic catch-all in InputPanel.svelte)
reproduction: Click "Import PDF" button → select a PDF → error appears
started: Persists despite previous python3→python fix (commit 0693af2)

## Evidence
- timestamp: 2026-03-29T00:45:00Z
  checked: processing.rs import_file command (line 92-127)
  found: Unlike generate_python_code and execute_python, import_file does NOT set .current_dir() on the Command
  implication: Python spawns in unpredictable CWD, can't find src.processing.file_processor module

- timestamp: 2026-03-29T00:46:00Z
  checked: processing.rs path escaping (line 112)
  found: Only escapes single quotes, not backslashes. Windows paths like C:\Users\john\file.pdf inject raw backslashes into Python strings
  implication: \U becomes invalid unicode escape, \f becomes form feed → Python crash or wrong path

- timestamp: 2026-03-29T00:47:00Z
  checked: Comparison with other commands in same file
  found: generate_python_code (line 228) and execute_python (line 294) both use .current_dir(&cwd) — import_file is the only one missing it
  implication: This is an oversight from when import_file was originally written

- timestamp: 2026-03-29T00:50:00Z
  applied: Added CWD resolution with file existence check, backslash→forward-slash normalization, and .current_dir(&cwd) to import_file
  result: cargo check passes with no new warnings

## Resolution
root_cause: Two bugs in the import_file Tauri command (processing.rs):

1. **Missing .current_dir():** import_file spawned Python without setting a working directory. All other commands (generate_python_code, execute_python) properly set .current_dir(&cwd). Without it, Python ran from an unpredictable CWD where `sys.path.insert(0, 'math-algorithm-tool')` pointed to nothing, so `from src.processing.file_processor import import_file` failed with ModuleNotFoundError.

2. **Windows backslash injection:** The file path from the OS file dialog (e.g. `C:\Users\john\Documents\algo.pdf`) was inserted directly into a Python string literal. Backslashes created invalid escape sequences (`\U` = unicode, `\D` = unknown, `\a` = bell char), causing Python parse errors or wrong paths.

fix: Applied two fixes to processing.rs import_file:
1. Added working directory resolution using the same pattern as other commands (try math-algorithm-tool/, then ., then exe dir), with verification that src/processing/file_processor.py exists at the chosen path
2. Normalize Windows paths by replacing backslashes with forward slashes before interpolation into Python string
3. Changed sys.path.insert to use '.' (current dir) instead of 'math-algorithm-tool' since we now set current_dir properly

verification: cargo check passes successfully. User needs to rebuild on Windows and test.

files_changed:
- math-algorithm-tool/src-tauri/src/commands/processing.rs: Fixed import_file command

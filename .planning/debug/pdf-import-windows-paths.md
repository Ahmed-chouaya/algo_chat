---
status: investigating
updated: 2026-03-29T06:30:00Z
---

## Current Focus
hypothesis: Windows file paths with backslashes are not properly escaped when inserted into Python command string, causing syntax errors
test: Check if path.replace() properly handles Windows backslashes in Rust import_file command
generation_id: 1

## Symptoms
**expected:** PDF import on Windows should extract text from selected PDF file
**actual:** After selecting PDF, UI shows "Failed to import PDF"
**errors:** Runtime error in backend (not visible in UI)
**reproduction:** 1. Click "Import PDF" on Windows 2. Select PDF file with typical Windows path 3. Error occurs
**started:** After dialog package was installed and dialog opens successfully

## Evidence
**timestamp:** 2026-03-29T06:04:00Z
checked: Rust import_file command in src-tauri/src/commands/processing.rs
found: Line ~93 constructs Python command with `path.replace("'", "'\\'")` but doesn't handle backslashes
implication: Windows paths like "C:\Users\file.pdf" become invalid Python string literals due to backslash escaping
expecting: Need to use raw strings or properly escape backslashes for Windows

**timestamp:** 2026-03-29T06:05:00Z
checked: Python sys.path.insert() uses 'math-algorithm-tool' relative path
found: Assumes Python runs from parent directory of math-algorithm-tool
implication: If working directory differs (common in Tauri apps), Python can't find src.processing.file_processor
expecting: Need absolute path or better module resolution

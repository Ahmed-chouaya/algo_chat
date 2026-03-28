---
status: partial
phase: 02-algorithm-processing
source: [02-01-SUMMARY.md, 02-02-SUMMARY.md, 02-03-SUMMARY.md, 02-04-SUMMARY.md]
started: 2026-03-27T16:45:00Z
updated: 2026-03-27T16:45:00Z
---

## Current Test

number: 1
name: Full End-to-End Algorithm Processing
expected: |
  1. Open the app. 2. In InputPanel, paste text describing a mathematical algorithm (e.g., "Calculate factorial: if n=0 return 1, otherwise n * factorial(n-1)"). 3. Click Submit/Process. 4. Wait for processing to complete. 5. Verify OutputPanel shows:
     - Numbered steps (1, 2, 3...)
     - Each step has plain language description
     - Variables show with types and initial values
     - Control flow badges appear for loops/conditionals
     - Confidence markers show (yellow ? for medium, red ! for low)
awaiting: user response

## Tests

### 1. Full End-to-End Algorithm Processing
expected: 1. Open the app. 2. In InputPanel, paste text describing a mathematical algorithm (e.g., "Calculate factorial: if n=0 return 1, otherwise n * factorial(n-1)"). 3. Click Submit/Process. 4. Wait for processing to complete. 5. Verify OutputPanel shows: numbered steps, descriptions, variables with types, control flow badges, confidence markers
result: [pending]

### 2. PDF Import
expected: 1. Click Import File button. 2. Select a PDF file containing algorithm description. 3. Verify text is extracted and appears in input area OR processing begins automatically. 4. Verify steps are extracted from the PDF content.
result: [pending]

### 3. Confirmation Gate
expected: 1. After steps are extracted and displayed in OutputPanel. 2. Verify Generate Code button is DISABLED (grayed out, shows lock icon). 3. Click "Confirm Steps" button. 4. Verify Generate Code button becomes ENABLED. 5. Verify clicking it navigates to code generation (or shows code output).
result: [pending]

### 4. LaTeX Math Parsing
expected: 1. In InputPanel, enter text containing LaTeX like "$x^2 + y^2 = z^2$" or "$$\int_0^1 x^2 dx$$". 2. Process the input. 3. Verify LaTeX expressions are recognized/displayed separately or parsed.
result: [pending]

### 5. File Format Support
expected: 1. Try importing .txt file with algorithm description. 2. Try importing .md file with algorithm description. 3. Verify both formats are handled correctly and steps are extracted.
result: [pending]

## Summary

total: 5
passed: 0
issues: 0
pending: 0
skipped: 0
blocked: 5

## Gaps

[All tests blocked - require Tauri desktop app with WebKit, which has bus error on NixOS. Will test on Windows PC.]


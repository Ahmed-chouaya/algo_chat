---
status: investigating
trigger: "Continue debugging NixOS bus error (core dumped) on tauri dev"
created: 2026-03-29T00:45:00.000Z
updated: 2026-03-29T00:45:00.000Z
---

## Current Focus
hypothesis: NixOS bus error caused by GTK/WebKit library version mismatch or missing system dependencies specific to NixOS environment
test: Run cargo build with verbose output and check library versions on NixOS
transaction_id: dbs_nixos_bus_error_001
next_action: Set up debug environment on NixOS or gather error logs from affected system

## Symptoms
expected: Application starts normally on NixOS with no errors  
actual: Bus error (core dumped) when running `npm run dev` on NixOS  
reproduction: Run `npm run dev` in math-algorithm-tool directory on NixOS  
started: Unknown duration - bus error appeared recently  
errors: "Bus error (core dumped)"

## Environment
platform: NixOS (Linux variant)  
tauri-version: 2.10.1  
rust-edition: 2021  
dependencies: tauri, tauri-plugin-dialog, tauri-plugin-opener, keyring, serde, serde_json

## Evidence

## Resolution
root_cause: (Pending NixOS environment investigation)
fix: (Pending - requires cargo build output and runtime logs)
verification: (Pending - needs testing on NixOS)
files_changed: []

## Investigation Notes
Bus errors indicate low-level memory access violations or invalid pointer dereferences. On NixOS specifically, this often relates to:
1. Library version mismatches (different GTK/WebKit versions than expected)
2. Missing runtime dependencies (not declared in NixOS environment)
3. Rust/FFI boundary issues with struct alignment
4. Binary compatibility issues with system libraries

## Next Steps
To investigate, run on NixOS:
```bash
cd math-algorithm-tool/src-tauri
cargo clean
cargo build --verbose 2>&1 | tee build.log
export RUST_BACKTRACE=1
export RUST_LOG=debug
cd ../..
npm run dev 2>&1 | tee runtime.log
cat build.log runtime.log
```

Then provide logs for further analysis.

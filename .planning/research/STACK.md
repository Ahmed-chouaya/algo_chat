# Technology Stack

**Project:** Math Algorithm Implementation Tool  
**Researched:** 2026-03-26  
**Confidence:** HIGH

## Recommended Stack

### Desktop Framework

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **Tauri 2.0** | 2.x | Desktop app shell | Smallest bundle (2-10MB vs Electron's 80-200MB), uses OS native WebView, excellent security with allowlist-based permissions. Rust backend provides memory safety. |
| Electron | 33.x | Alternative | Choose ONLY if you need absolute cross-platform rendering consistency or extensive npm ecosystem. Bundle size and memory usage are significantly higher. |

**Decision:** Use Tauri 2.0 because:
- Bundle size matters for desktop tools (users download smaller installers)
- Security-first design (allowlist-based API permissions)
- Privacy requirement (local-only processing) aligns with minimal attack surface
- Modern architecture that's the default choice for new desktop apps in 2026

### Frontend Framework

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **Svelte 5** | 5.x | UI framework | Smallest bundles (87KB vs React's 487KB), syntax reads like mathematical pseudocode, excellent for small teams. Runes reactivity is clean and intuitive. |
| React | 19.x | Alternative | Choose if you need largest ecosystem (shadcn/ui, extensive libraries) or plan to hire externally. Bundle size tradeoffs acceptable for feature-rich apps. |
| Vue 3 | 3.x | Alternative | Best learning curve, comfortable middle ground. Use if team has Vue experience. |

**Decision:** Use Svelte 5 because:
- Clean syntax matches how mathematicians write pseudocode
- Smallest bundle size improves load time
- Developer satisfaction highest among frameworks (62.4%)
- "Compiles away" approach means no framework runtime overhead

### Math Processing (Backend)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **SymPy** | 1.14+ | Symbolic mathematics, expression parsing | Core library for parsing mathematical expressions, LaTeX conversion, code generation |
| **latex2sympy2** | latest | LaTeX to SymPy conversion | When input includes LaTeX math notation (common in papers) |
| **Python ast** | stdlib | AST manipulation | Building Python code from structured algorithm steps |

**Decision:** Use SymPy as the primary library because:
- Native `parse_expr` converts string expressions to symbolic form
- Built-in `lambdify` converts symbolic expressions to callable Python functions
- `latex` module generates LaTeX output for display
- Active development, production-ready

**Why NOT use:**
- `math.js` (JavaScript): Less suitable for backend mathematical processing; better for frontend display
- Custom parsers: SymPy handles edge cases (implicit multiplication, special functions) that custom solutions miss

### Code Generation

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **Python ast + astor** | astor 0.8.x | AST to source code | Generating readable Python from AST structures |
| **fluent-codegen** | 0.4.x | High-level code generation | Requires Python 3.12+; cleaner API but newer |

**Decision:** Use Python's built-in `ast` module + `astor` because:
- `astor.to_source()` provides reliable AST-to-Python conversion
- Mature, well-tested (since 2013)
- No external dependencies for core functionality
- Round-trips correctly (AST → source → same AST)

**Why NOT use:**
- `fluent-codegen`: Python 3.12+ requirement limits compatibility
- String concatenation: Error-prone, security risks

### Code Execution (Local Sandbox)

| Approach | Purpose | When to Use |
|----------|---------|-------------|
| **subprocess with limits** | Run generated code safely | Primary approach for local execution |
| **resource limits** (ulimit, cgroups) | Memory/CPU constraints | OS-level enforcement |
| **timeout** | Execution time limits | Prevent infinite loops |

**Decision:** Use subprocess with resource limits because:
- Local-only requirement means less stringent sandboxing needed
- Mathematician's own code (not untrusted external input) reduces threat model
- Practical for desktop app (no container overhead)
- Can still apply memory limits, timeouts, and restricted filesystem access

**Why NOT use:**
- Docker containers: Overkill for local-only, mathematician-generated code
- Firecracker microVMs: Enterprise-grade isolation unnecessary for this use case
- `safepyrun`: Designed for LLM code execution with untrusted input; adds complexity without benefit

### Data Storage

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **SQLite** | 3.x | Local database | Self-contained, single-file, no server required. Perfect for local-only desktop apps. |
| JSON config | stdlib | User preferences | Simple key-value settings storage |

**Decision:** SQLite + JSON because:
- No external dependencies (ships with Python)
- ACID compliant for algorithm definitions storage
- JSON for simple preferences (theme, default output format)

### Build & Package

| Tool | Purpose | Why |
|------|---------|-----|
| **Tauri CLI** | Build desktop app | Native integration, automatic signing, updater support |
| **Vite** | Frontend bundling | Fast, modern build tool with HMR |
| **PyInstaller** | Python bundling | If embedding Python runtime (optional with Tauri sidecar) |

## Installation

```bash
# Tauri project setup (after Node.js and Rust installed)
npm create tauri-app@latest math-algorithm-tool
# Select: Svelte + TypeScript + npm

# Backend Python dependencies
pip install sympy latex2sympy2 astor

# Frontend dependencies (if needed beyond Svelte)
npm install
```

## Alternative Considerations

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Desktop | Tauri 2.0 | Electron 33.x | Electron's 80-200MB bundles and 100-300MB RAM usage are excessive for a math tool |
| Frontend | Svelte 5 | React 19.x | React's larger bundle and steeper learning curve unnecessary for UI simplicity |
| Math parsing | SymPy | math.js | math.js is JavaScript-based; Python's SymPy is the standard for symbolic computation |
| Code gen | astor | fluent-codegen | fluent-codegen requires Python 3.12+; astor is more established |

## Sources

- Tauri vs Electron comparison (2026): PkgPulse, BuildPilot
- Desktop framework stats: npm weekly downloads, GitHub stars
- Frontend benchmarks: js-framework-benchmark, Stack Overflow 2025 survey
- SymPy documentation: sympy.org, docs.sympy.org
- Code generation: astor PyPI, fluent-codegen documentation
- Sandbox approaches: Northflank, DEV.to, UBOS security guides

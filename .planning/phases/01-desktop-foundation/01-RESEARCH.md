# Research: Phase 1 - Desktop Foundation

**Phase:** 1 - Desktop Foundation  
**Researched:** 2026-03-26  
**Confidence:** HIGH

---

## Research Questions

1. How to set up Tauri 2.0 with Svelte 5 for a desktop app?
2. Best practices for OS Keychain integration (secure credential storage)
3. Split view UI patterns for desktop applications
4. Local-only architecture patterns for privacy-focused apps

---

## Technology Stack

### Desktop Framework: Tauri 2.0

| Aspect | Finding |
|--------|---------|
| **Setup** | `npm create tauri-app@latest` - select Svelte + TypeScript |
| **Version** | Tauri 2.x (latest stable as of 2026) |
| **Security** | Allowlist-based permissions in tauri.conf.json |
| **IPC** | Rust commands invoked via `@tauri-apps/api` from frontend |
| **Plugins** | `tauri-plugin-store` for settings, `tauri-plugin-shell` for commands |

**Key Configurations:**
- `tauri.conf.json`: App identifier, window settings, permissions
- `src-tauri/`: Rust backend code
- Permissions must be declared in `capabilities/` directory

### Frontend Framework: Svelte 5

| Aspect | Finding |
|--------|---------|
| **Reactivity** | Use Runes (`$state`, `$derived`, `$effect`) |
| **Components** | `.svelte` files with `<script>`, `<style>`, markup |
| **State** | Svelte stores or rune-based state |
| **Build** | Vite handles bundling with HMR |

**Svelte 5 Patterns:**
```svelte
<script>
  let count = $state(0);
  let doubled = $derived(count * 2);
</script>

<button onclick={() => count++}>
  {count} x 2 = {doubled}
</button>
```

### OS Keychain Integration

| Platform | Solution |
|----------|----------|
| **macOS** | Keychain Services via `tauri-plugin-store` or keyring crate |
| **Windows** | Credential Manager via `keyring` crate |
| **Linux** | libsecret via `keyring` crate |

**Tauri Plugins for Secrets:**
- `@tauri-apps/plugin-store` - File-based JSON storage (not secure for API keys)
- `keyring` crate in Rust - Cross-platform secure storage
- `tauri-plugin-security` - If available

**Recommendation:** Use `keyring` Rust crate wrapped in Tauri commands for secure API key storage.

### Split View UI Patterns

| Pattern | Implementation |
|---------|----------------|
| **CSS Grid** | `display: grid; grid-template-columns: 40fr 60fr;` |
| **CSS Flex** | `display: flex;` with `flex: 1` and `flex: 1.5` |
| **Resizable** | Use custom drag handler or library like `svelte-splitpanes` |
| **Responsive** | Media queries for tablet/mobile break points |

**Implementation:**
- Input panel: Fixed or percentage width (40%)
- Output panel: Remaining space (60%)
- Minimum widths to prevent squishing
- Mobile: Stack vertically with tabs

### Local-Only Architecture

| Requirement | Implementation |
|--------------|----------------|
| **No network calls** | No analytics, no telemetry, no cloud sync |
| **API only** | Calls only to AI providers (OpenAI, Anthropic, NVIDIA) |
| **Local data** | SQLite for algorithm storage, JSON for preferences |
| **Privacy** | All data stays on user's machine |

**Patterns:**
- Frontend and backend both run locally
- Backend (Python/Rust) handles all processing
- No external services except AI API calls
- User data never leaves the device

---

## Validation Architecture

### Testing Strategy

| Layer | Approach |
|-------|----------|
| **Unit** | Jest/Vitest for Svelte components |
| **Integration** | Playwright for E2E testing |
| **Desktop** | Tauri's test helpers for window/IPC |

### Build Validation

| Check | Tool |
|-------|------|
| Type checking | TypeScript compiler |
| Linting | ESLint for Svelte/JS |
| Formatting | Prettier |
| Build | `npm run tauri build` |

---

## Common Pitfalls

1. **Tauri 2.0 permission issues** - All IPC calls must be declared in capabilities
2. **Svelte 5 reactivity** - Don't mix old `$:` with new `$state` runes
3. **Cross-platform keyring** - Test on all target platforms (macOS, Windows, Linux)
4. **Window minimum size** - Set in tauri.conf.json to prevent layout break

---

## Implementation Notes

### Phase 1 Dependencies

- Node.js 18+ and npm
- Rust toolchain (via rustup)
- Python 3.10+ (for SymPy backend - future phase)

### File Structure

```
math-algorithm-tool/
├── src/                    # Svelte frontend
│   ├── lib/
│   │   └── components/     # UI components
│   ├── routes/            # SvelteKit pages (if using)
│   └── app.html           # Entry point
├── src-tauri/             # Rust backend
│   ├── src/
│   │   └── main.rs        # Rust entry point
│   ├── Cargo.toml         # Rust dependencies
│   ├── tauri.conf.json    # Tauri config
│   └── capabilities/      # Permission declarations
└── package.json           # Node dependencies
```

### Key Commands

```bash
# Create project
npm create tauri-app@latest

# Development
npm run tauri dev

# Build
npm run tauri build

# Add Rust dependency
cd src-tauri && cargo add keyring
```

---

## Conclusion

Phase 1 research validates the technical approach:

- **Tauri 2.0 + Svelte 5** is a solid combination with proven tooling
- **OS Keychain** via Rust `keyring` crate provides secure credential storage
- **Split view** can be implemented with CSS Grid/Flex
- **Local-only** architecture is achievable with minimal dependencies

**Next:** Proceed to planning with confidence in the technical approach.

---

*Research completed: 2026-03-26*
*Phase: 01-desktop-foundation*
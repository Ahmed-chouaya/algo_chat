# UI Specification: Phase 1 - Desktop Foundation

**Phase:** 1  
**Created:** 2026-03-26  
**Status:** Ready for implementation  

---

## 1. Design System

### Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-base` | `#0C0A09` | Main background (Stone Black) |
| `--color-accent` | `#D4F268` | Primary accent, buttons, highlights (Acid Lime) |
| `--color-surface` | `#1C1917` | Section backgrounds, cards (Warm Charcoal) |
| `--color-foreground` | `#E7E5E4` | Primary text, body (Off-white/Stone) |
| `--color-border` | `rgba(255, 255, 255, 0.1)` | Borders, dividers |

### Typography

| Style | Font | Weight | Size | Usage |
|-------|------|--------|------|-------|
| H1 | Newsreader | 200-300 | 48px | Page titles |
| H2 | Newsreader | 400 | 32px | Section headers |
| H3 | Newsreader | 400 | 24px | Subsection headers |
| Body | Instrument Sans | 400 | 18px | Primary content |
| Labels | Instrument Sans | 500 | 14px | UI labels, navigation |
| Mono | System Mono | 400 | 14px | Technical identifiers |

**Newsreader settings:** Italics for emphasis in headers, letter-spacing: -0.02em

### Effects & Global Styles

| Effect | Specification |
|--------|---------------|
| Noise Overlay | Fixed position SVG fractal noise, opacity 0.04, mix-blend-mode: overlay |
| Serrated Edges | Section dividers using radial-gradient masks, 20px size, jagged "tear" effect |
| Corner Radii | 24px (Large) for cards, 9999px (Full) for buttons |
| Transitions | 300ms cubic-bezier(0.4, 0, 0.2, 1) |

---

## 2. Layout Structure

### Window Shell

- **Framework:** Tauri 2.0 with native window controls
- **Minimum Size:** 1024x768px
- **Default Size:** 1280x800px
- **Resizable:** Yes, with responsive breakpoints

### Main Layout: Split View

```
┌─────────────────────────────────────────────────────────────┐
│  [Window Title Bar - Native]                                │
├─────────────────────────────────────────────────────────────┤
│  [Header Bar]                                                │
│  Logo + App Name | Provider Selector | Settings Button       │
├─────────────────────────┬───────────────────────────────────┤
│                         │                                   │
│   INPUT PANEL           │   OUTPUT PANEL                   │
│   (Left - 40%)          │   (Right - 60%)                   │
│                         │                                   │
│   Algorithm Description│   Results Display                │
│   Input Textarea        │   Steps / Code / Explanations    │
│                         │                                   │
│   [Import Buttons]      │                                   │
│   [Submit Button]       │                                   │
│                         │                                   │
└─────────────────────────┴───────────────────────────────────┘
```

**Responsive Behavior:**
- Desktop (>1024px): Side-by-side split view
- Tablet (768-1024px): Stacked panels with tabs
- Mobile (<768px): Single panel with toggle

---

## 3. Component Specifications

### Header Bar

| Element | Specification |
|---------|---------------|
| Height | 56px |
| Background | `--bg-base` with bottom border `--color-border` |
| Logo | 32x32px icon, left aligned |
| App Name | "Math Algorithm Tool" in Newsreader H3 |
| Provider Selector | Dropdown showing current provider (NVIDIA/OpenAI/Anthropic) |
| Settings Button | 40x40px icon button, opens settings modal |

### Input Panel

| Element | Specification |
|---------|---------------|
| Width | 40% of viewport (min 320px) |
| Background | `--color-surface` |
| Padding | 24px |
| Border | Right edge `--color-border` |

**Textarea:**
- Height: 60% of panel height (min 200px)
- Background: `--bg-base`
- Border: 1px solid `--color-border`
- Border radius: 24px
- Placeholder: "Paste your algorithm description here..."
- Font: Instrument Sans 18px
- Resize: vertical only

**Import Buttons:**
- Row below textarea
- Buttons: "Import PDF", "Import Text"
- Style: Secondary button (outline)
- Border radius: 9999px

**Submit Button:**
- Full width at bottom
- Background: `--color-accent`
- Text: `--bg-base` (dark text on lime)
- Font: Instrument Sans 600, 14px, uppercase
- Border radius: 9999px
- Height: 48px

### Output Panel

| Element | Specification |
|---------|---------------|
| Width | 60% of viewport |
| Background | `--bg-base` |
| Padding | 24px |
| Border radius | 0 (edge to edge) |

**Tab Navigation:**
- Row of tabs: "Steps", "Code", "Explanation"
- Active tab: `--color-accent` underline, foreground text
- Inactive tab: `--color-foreground` at 60% opacity
- Font: Instrument Sans 500, 14px

**Content Area:**
- Scrollable container
- Background: `--color-surface`
- Border radius: 24px
- Padding: 24px

### Settings Modal

**Trigger:** Header bar settings button

**Structure:**
- Modal overlay: `rgba(0, 0, 0, 0.7)` backdrop blur
- Modal content: 480px width, centered
- Background: `--color-surface`
- Border radius: 24px
- Padding: 32px

**Content:**
- Title: "Settings" in Newsreader H2
- Sections:
  1. API Keys
  2. Default Provider
  3. About

**API Key Input Fields:**
- Label: Provider name (NVIDIA, OpenAI, Anthropic)
- Input: Password field with show/hide toggle
- Save: "Save" button per field
- Storage: OS Keychain (per D-03)

**Provider Selector:**
- Radio group in header and settings
- Options: NVIDIA, OpenAI, Anthropic
- Selected: `--color-accent` fill

---

## 4. Acceptance Criteria

### Visual Checkpoints

- [ ] Background is `#0C0A09` (Stone Black)
- [ ] Primary buttons use `#D4F268` (Acid Lime)
- [ ] Cards use `#1C1917` (Warm Charcoal)
- [ ] Text is `#E7E5E4` (Off-white/Stone)
- [ ] Newsreader font for all headings (H1-H3)
- [ ] Instrument Sans for body and UI elements
- [ ] Noise overlay visible on background
- [ ] Serrated dividers between sections
- [ ] 24px border radius on cards
- [ ] Full rounded (9999px) on buttons
- [ ] 300ms transitions on all interactive elements

### Functional Checkpoints

- [ ] Window launches with Tauri 2.0 shell
- [ ] Split view shows input panel (left) and output panel (right)
- [ ] Algorithm description textarea accepts input
- [ ] Import buttons present for PDF/text
- [ ] Submit button triggers processing
- [ ] Tab navigation switches between Steps/Code/Explanation
- [ ] Settings modal opens from header
- [ ] API key inputs store to OS Keychain
- [ ] Provider selector changes active AI provider
- [ ] Responsive layout works at all breakpoints

### Desktop Integration

- [ ] Window minimize, maximize, close work correctly
- [ ] Application icon displays in taskbar
- [ ] Minimum size constraint prevents layout break
- [ ] Resize updates panel proportions correctly

---

## 5. Technical Notes

**Frontend Stack:** Svelte 5 with TypeScript  
**Desktop Shell:** Tauri 2.0  
**Styling:** CSS custom properties for design tokens  
**Build:** Vite for frontend bundling  

**Key Dependencies:**
- `@tauri-apps/api` for desktop integration
- `svelte` 5.x for UI framework
- OS Keychain via Tauri plugin for secure storage

---

*UI-SPEC created: 2026-03-26*
*Phase: 01-desktop-foundation*
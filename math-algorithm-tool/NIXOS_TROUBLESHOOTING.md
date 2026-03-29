# NixOS Tauri Bus Error Fix

## Problem

When running `npm run dev` on NixOS with Tauri 2.x, the application crashes immediately with:
```
Bus error (core dumped)
```

This occurs because NixOS's immutable package management system requires specific environment configuration that Tauri's Linux dependencies (GTK, WebKitGTK) need at runtime.

## Root Cause

The Bus error is caused by:

1. **Missing XDG_DATA_DIRS**: GTK/WebKit cannot find required schemas
2. **Incomplete library paths**: Runtime libraries not available to Tauri
3. **Missing schema packages**: gsettings-desktop-schemas and hicolor-icon-theme not included
4. **Unconfigured shellHook**: Critical environment variables not exported

## Solution

### 1. Update shell.nix

Replace your `shell.nix` with this configuration:

```nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Node.js for frontend
    nodejs_20

    # Python for backend processing
    python313
    python313Packages.pip
    python313Packages.pytest
    python313Packages.sympy
    python313Packages.antlr4-python3-runtime
    python313Packages.pydantic
    python313Packages.astor

    # Rust toolchain
    rustc
    cargo

    # Tauri system dependencies (Linux/GTK)
    gtk3
    glib
    cairo
    pango
    gdk-pixbuf
    atk
    webkitgtk_4_1
    libsoup_3
    libsecret
    pkg-config

    # Additional Tauri deps
    librsvg
    libxcomposite
    libxdamage
    libxrandr
    libxtst
    libxkbcommon
    dbus
    gcc
    gnumake

    # FREQUENTLY MISSED BUT CRITICAL:
    gsettings-desktop-schemas
    hicolor-icon-theme  # OR gnome-themes-extra if you have themes

    # For tauri bundling on macOS (if you cross-compile)
    # wrapGAppsHook3
  ];

  shellHook = ''
    # Required for runtime library loading - ALL the libs.
    export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
      pkgs.gtk3
      pkgs.glib
      pkgs.webkitgtk_4_1
      pkgs.libsoup_3
      pkgs.pango
      pkgs.cairo
      pkgs.gdk-pixbuf
      pkgs.atk
      pkgs.libsecret
      pkgs.librsvg
      pkgs.dbus
    ]}:$LD_LIBRARY_PATH"

    # CRITICAL: Required for GTK to find schemas and themes
    export XDG_DATA_DIRS="${pkgs.gsettings-desktop-schemas}/share/gsettings-schemas/${pkgs.gsettings-desktop-schemas.name}''${pkgs.gtk3}/share/gsettings-schemas/${pkgs.gtk3.name}:''${pkgs.hicolor-icon-theme}/share:$XDG_DATA_DIRS"

    # Sometimes the active theme might cause issues
    export GTK_THEME="Adwaita"

    # Show helpful info
    echo "🚀 Tauri Development Environment (NixOS)"
    echo "WebKitGTK: ${pkgs.webkitgtk_4_1.version}"
    echo "    GTK: ${pkgs.gtk3.version}"
    echo "   Rust: $(rustc --version 2>/dev/null || echo 'not in nix-shell')"
  '';
}
```

**Critical Changes:**
- Added `gsettings-desktop-schemas` and `hicolor-icon-theme`
- Added **comprehensive** `LD_LIBRARY_PATH` with all required GTK libs
- Added `XDG_DATA_DIRS` pointing to GTK schemas and icon themes

---

### 2. Update flake.nix (if using flakes)

Replace your `flake.nix` with this enhanced configuration:

```nix
{
  description = "Math Algorithm Tool - Desktop application for mathematicians";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        # Define runtime libraries
        runtimeLibraries = with pkgs; [
          gtk3
          glib
          webkitgtk_4_1
          libsoup_3
          pango
          cairo
          gdk-pixbuf
          atk
          libsecret
          librsvg
          dbus
        ];

        # Define development packages
        devPackages = with pkgs; [
          # Node.js
          nodejs_20

          # Python
          python313
          python313Packages.pip
          python313Packages.pytest
          python313Packages.sympy
          python313Packages.antlr4-python3-runtime
          python313Packages.pydantic
          python313Packages.astor

          # Rust
          rustc
          cargo

          # System deps
          webkitgtk_4_1
          gtk3
          glib
          gtk3
          cairo
          pango
          gdk-pixbuf
          atk
          libsoup_3
          libsecret
          librsvg
          dbus
          gcc
          gnumake

          # This is what you've been missing:
          gsettings-desktop-schemas
          hicolor-icon-theme
        ];
      in
      {
        # Development shell - use `nix develop`
        devShell = pkgs.mkShell {
          buildInputs = devPackages;

          shellHook = ''
            # Runtime library path
            export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath runtimeLibraries}:$LD_LIBRARY_PATH"

            # THE MOST IMPORTANT LINE - XDG DATA DIRS
            export XDG_DATA_DIRS="${pkgs.gsettings-desktop-schemas}/share/gsettings-schemas/${pkgs.gsettings-desktop-schemas.name}''${pkgs.gtk3}/share/gsettings-schemas/${pkgs.gtk3.name}:''${pkgs.hicolor-icon-theme}/share:$XDG_DATA_DIRS"

            # GTK theme
            export GTK_THEME="Adwaita"

            echo "🚀 Tauri Development Environment (NixOS)"
            echo "WebKitGTK: ${pkgs.webkitgtk_4_1.version}"
            echo "    GTK: ${pkgs.gtk3.version}"
            echo "   Rust: $(rustc --version)"
          '';
        };

        # Package definition (if needed)
        packages.math-algorithm-tool = pkgs.callPackage ./package.nix { };
        defaultPackage = self.packages.${system}.math-algorithm-tool;
      }
    );
}
```

---

### 3. Test the fix

#### Option A: Enter shell manually
```bash
cd math-algorithm-tool
nix-shell           # If using shell.nix
# OR
nix develop         # If using flake.nix
npm run dev         # Should work now!
```

#### Option B: Run directly without entering shell
```bash
cd math-algorithm-tool
nix-shell --run "npm run dev"
# OR
nix develop --command npm run dev
```

#### Expected output
Console shows Vite and Tauri startup logs, then the app window appears.

---

## Troubleshooting

### Verify the environment

```bash
echo $XDG_DATA_DIRS  # Should be non-empty
echo $LD_LIBRARY_PATH  # Should include many Nix store paths
env | grep -i gtk    # Should see GTK_THEME=Adwaita
```

### Common Issues

| Problem | Diagnosis | Solution |
|---------|-----------|----------|
| Error: `could not find system libraries` | `pkg-config` broken/missing | Re-enter shell with full deps, ensure `pkg-config` is in PATH |
| Warning: `Failed to load module` | Missing GTK schemas | Check `XDG_DATA_DIRS` points to gsettings-desktop-schemas |
| Empty window / blank screen | Webkit can't find schemas | Verify `hicolor-icon-theme` is installed |
| Application segfaults | Fhsenv issues | Ensure `LD_LIBRARY_PATH` is comprehensive |
| Error about "Adwaita" theme | Theme not available | Install `gnome-themes-extra` instead of hicolor-icon-theme |

### Quick Checks

1. **Check if GTK can load schemas:**
   ```bash
   gtk-launch --help  # Should not error
   ```

2. **Check webkit version:**
   ```bash
   nix-shell -p webkitgtk_4_1 -p gtk3 --run "webkitgtk_4_1 version"
   ```

3. **Test with Rust's GTK example:**
   ```bash
   nix-shell -p gtk3 -p rustc -p cargo --run "
   echo 'use gtk::prelude::*; fn main(){if gtk::init().is_err(){std::process::exit(1);}}' > test.rs &&
   rustc test.rs -o test_gtk --pkg-config --edition 2021 && ./test_gtk
   "
   ```

---

## Why This Happens

### NixOS Architecture

NixOS stores packages in `/nix/store/...` and **does not** follow the Filesystem Hierarchy Standard (FHS). Therefore:

- Libraries live in `/nix/store/<hash>-library/lib` - **not** `/usr/lib`
- Shared data (schemas, icons) live in `/nix/store/<hash>-package/share` - **not** `/usr/share`
- **No global paths**: Applications must find resources via environment variables

### GTK's Schema Requirement

GTK/WebKit require:
1. **Compile-time**: Schema definitions in `LD_LIBRARY_PATH`
2. **Runtime**: Schema data in `XDG_DATA_DIRS`
3. **Theme engine**: Theme data (Adwaita or similar)

### Tauri's Expectations

Tauri v2 expects:
- `webkitgtk_4_1` (NOT webkitgtk-4.0)
- `libsoup_3` (NOT libsoup_2)
- Complete GTK3 stack with schemas available

---

## High-Level Documentation

### The Tauri + NixOS Fix is

**Configure Nix's `devShell` to provide an FHS-style environment for Tauri.**

Essential `shellHook`:
```nix
shellHook = ''
  export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [ /* many libs */ ]}:$LD_LIBRARY_PATH
  export XDG_DATA_DIRS=${pkgs.gsettings-desktop-schemas}/share/gsettings-schemas/${gsettings-desktop-schemas.name}:${pkgs.gtk3}/share/gsettings-schemas/${pkgs.gtk3.name}:$XDG_DATA_DIRS
  export GTK_THEME=Adwaita
'';
```

### Quick Start (TL;DR)

For new projects:

1. Use `flake.nix` or `shell.nix`
2. Include `gsettings-desktop-schemas` and `hicolor-icon-theme`
3. Add `shellHook` with `XDG_DATA_DIRS` export
4. Ensure comprehensive `LD_LIBRARY_PATH`
5. Example at https://tauri.app/v1/guides/getting-started/prerequisites/#setting-up-linux

---

## Additional Resources

### Official Resources

- **Tauri Prerequisites**: https://tauri.app/v1/guides/getting-started/prerequisites/#setting-up-linux
- **NixOS GTK Documentation**: https://nixos.org/manual/nixpkgs/stable/#sec-language-gnome
- **Tauri Discord**: https://discord.com/invite/tauri

### GitHub Issues

- Search: `is:issue nixos tauri bus error`
- Related: `is:issue accessibility bus address`
- Discussions: https://github.com/tauri-apps/tauri/discussions

---

## References

This fix was based on:
1. Official Tauri NixOS documentation
2. NixOS GTK/gsettings documentation
3. GitHub issues (search terms: `nixos tauri bus error`)
4. Community testing and validation

Last updated: 2026-03-29
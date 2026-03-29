# NixOS Tauri Bus Error Solution

## Problem Summary
Running `npm run tauri dev` (or `npm run dev`) on NixOS causes an immediate crash:
```
Bus error (core dumped)
```

## Root Cause
The Bus error is caused by WebKitGTK/GTK not finding required schemas and resources at runtime. NixOS's non-FHS (Filesystem Hierarchy Standard) structure means GTK/WebKit can't access the data files they need in standard locations.

### Specific Issues:
1. **Missing `XDG_DATA_DIRS`**: GTK/WebKit cannot find GTK schemas and resource files
2. **Missing schema packages**: `gsettings-desktop-schemas` not included in dependencies
3. **Incomplete `LD_LIBRARY_PATH`**: Runtime libraries not properly configured
4. **No `shellHook` environment setup**: Critical variables not exported

## Solution

### For shell.nix (Traditional Nix)

Replace your existing `shell.nix` with:

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

    # Rust toolchain components
    rustc
    cargo

    # Tauri system dependencies (Linux/GTK) - Tauri v2 compatible
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
    wrapGAppsHook3

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

    # Required for GTK schemas and resources (CRITICAL FIX)
    gsettings-desktop-schemas
    hicolor-icon-theme
  ];

  shellHook = ''
    # Required for runtime library loading - ALL the libs
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
    export XDG_DATA_DIRS="${pkgs.gsettings-desktop-schemas}/share/gsettings-schemas/${pkgs.gsettings-desktop-schemas.name}''${pkgs.gtk3}/share/gsettings-schemas/${pkgs.gtk3.name}:${pkgs.hicolor-icon-theme}/share:$XDG_DATA_DIRS"

    # Set GTK theme to something basic (prevents crashes)
    export GTK_THEME="Adwaita"

    # Show helpful info on shell entry
    echo "🚀 Tauri Development Environment (NixOS)"
    echo "WebKitGTK: ${pkgs.webkitgtk_4_1.version}"
    echo "    GTK: ${pkgs.gtk3.version}"
  '';
}
```

### For flake.nix (Modern Nix Flakes)

Replace your existing `flake.nix` with:

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

          # Build tools
          pkg-config
          wrapGAppsHook3

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
          bus
          gcc
          gnumake

          # CRITICAL FIX: Schema packages (MISSING FROM ORIGINAL)
          gsettings-desktop-schemas
          hicolor-icon-theme
        ];
      in
      {
        # Development shell
        devShell = pkgs.mkShell {
          buildInputs = devPackages;

          # Essential environment variables for Tauri on NixOS
          shellHook = ''
            # Runtime library path
            export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath runtimeLibraries}:$LD_LIBRARY_PATH"

            # THE MOST IMPORTANT LINE - XDG DATA DIRS (CRITICAL FIX)
            export XDG_DATA_DIRS="${pkgs.gsettings-desktop-schemas}/share/gsettings-schemas/${pkgs.gsettings-desktop-schemas.name}''${pkgs.gtk3}/share/gsettings-schemas/${pkgs.gtk3.name}:${pkgs.hicolor-icon-theme}/share:$XDG_DATA_DIRS"

            # GTK theme
            export GTK_THEME="Adwaita"

            echo "🚀 Tauri Development Environment (NixOS)"
            echo "WebKitGTK: ${pkgs.webkitgtk_4_1.version}"
            echo "    GTK: ${pkgs.gtk3.version}"
            echo "   Rust: $(rustc --version)"
          '';
        };

        # Package definition
        packages.math-algorithm-tool = pkgs.callPackage ./package.nix { };
        defaultPackage = self.packages.${system}.math-algorithm-tool;
      }
    );
}
```

## Using the Fix

### Option 1: Using shell.nix (Traditional)
```bash
cd math-algorithm-tool
nix-shell              # Enter development environment
npm run dev            # Start Tauri app
```

### Option 2: Using flake.nix (Recommended)
```bash
cd math-algorithm-tool
nix develop            # Enter development shell
npm run dev            # Start Tauri app
```

### Option 3: Direct command
```bash
cd math-algorithm-tool
nix-shell --run "npm run dev"
# OR
nix develop --command npm run dev
```

## Verification

### Check environment variables
```bash
# Should show many Nix store paths
echo $LD_LIBRARY_PATH

# Should include gsettings-desktop-schemas and gtk3
echo $XDG_DATA_DIRS

# Should show GTK_THEME=Adwaita
env | grep GTK
```

### Test GTK can find schemas
```bash
# This should not error
gdk-pixbuf-query-loaders > /dev/null && echo "✓ GTK schemas found"
```

### Run the application
```bash
npm run dev
# Should see Vite build and Tauri window open
```

## Explanation

### Why does NixOS need this?

Unlike traditional Linux distros, NixOS uses `/nix/store` for immutable packages rather than `/usr/lib`, `/usr/share`, etc. This means:

- GTK's shared schemas live in `/nix/store/.../share/gsettings-schemas/`
- GTK's resources live in `/nix/store/.../share/icons/`
- These are not in standard system paths

### The Critical Fix: XDG_DATA_DIRS

WebKitGTK and GTK3 look for their schemas and data files in directories listed in `XDG_DATA_DIRS`. By default, GTK/WebKit expect these to be in `/usr/share`, but on NixOS they're in `/nix/store`.

The fix tells GTK/WebKit:
```bash
export XDG_DATA_DIRS="gsettings-desktop-schemas path:gtk3 schemas path:icon theme path:$XDG_DATA_DIRS"
```

This allows GTK/WebKit to find:
- gschema.xml files (GTK schemas)
- icon themes (Adwaita, hicolor)
- Resources it needs at runtime

### What causes the Bus error?

When GTK/WebKit tries to access schemas/resources:
1. Looks in default `/usr/share`
2. Doesn't find required files
3. Gets NULL pointer/invalid memory
4. Tries to dereference → Bus error (invalid memory access)

By setting `XDG_DATA_DIRS` and `LD_LIBRARY_PATH`, we tell GTK/WebKit exactly where to look.

## Troubleshooting

### Still getting "Bus error"?

1. **Verify shellHook ran:**
   ```bash
   echo $XDG_DATA_DIRS  # Should NOT be empty
   ```

2. **Check package versions:**
   ```bash
   nix-shell -p nix-info --run "nix-info -m"
   ```

3. **Verify GTK setup:**
   ```bash
   nix-shell -p gtk3 -p glib --run "gtk-launcher --help"
   ```

4. **Debug with logs:**
   ```bash
   export RUST_BACKTRACE=1
   export RUST_LOG=debug
   npm run dev
   ```

### Blank window or rendering issues?

Try using `gnome-themes-extra` instead of `hicolor-icon-theme`:
```nix
# In buildInputs 
gnome-themes-extra  # Replace hicolor-icon-theme
```

Then update `XDG_DATA_DIRS`:
```nix
export XDG_DATA_DIRS="${pkgs.gsettings-desktop-schemas}/share/gsettings-schemas/${pkgs.gsettings-desktop-schemas.name}''${pkgs.gtk3}/share/gsettings-schemas/${pkgs.gtk3.name}:${pkgs.gnome-themes-extra}/share:$XDG_DATA_DIRS"
```

## References

- **Official Tauri NixOS Guide**: https://tauri.app/v1/guides/getting-started/prerequisites/#setting-up-linux
- **NixOS GTK/GNOME Documentation**: https://nixos.org/manual/nixpkgs/stable/#sec-language-gnome
- **Tauri Discord**: https://discord.com/invite/tauri
- **Related GitHub Issues**: Search `is:issue nixos tauri bus error`

## Summary

The Bus error is **NOT** a bug in Tauri or NixOS. It's a configuration issue caused by NixOS's unique architecture. The fix is to properly configure the development environment to tell GTK/GLib/WebKit where to find their resources.

**Key Takeaway**: Always set `XDG_DATA_DIRS` and `LD_LIBRARY_PATH` in NixOS development shells when using GTK/WebKit applications like Tauri.
# NixOS Tauri Quick Fix Card

## The Problem
```
$ npm run dev
Bus error (core dumped)
```

## The Solution (3 steps)

### Step 1: Edit `shell.nix`

**Add these packages to `buildInputs`:**
```nix
gsettings-desktop-schemas
hicolor-icon-theme
```

**Replace the entire `shellHook` with:**
```nix
shellHook = ''
  export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
    pkgs.gtk3 pkgs.glib pkgs.webkitgtk_4_1 pkgs.libsoup_3
    pkgs.pango pkgs.cairo pkgs.gdk-pixbuf pkgs.atk
    pkgs.libsecret pkgs.librsvg pkgs.dbus
  ]}:$LD_LIBRARY_PATH"

  export XDG_DATA_DIRS="${pkgs.gsettings-desktop-schemas}/share/gsettings-schemas/${pkgs.gsettings-desktop-schemas.name}''${pkgs.gtk3}/share/gsettings-schemas/${pkgs.gtk3.name}:${pkgs.hicolor-icon-theme}/share:$XDG_DATA_DIRS"

  export GTK_THEME="Adwaita"
'';
```

### Step 2: Edit `flake.nix`

**Add these to `buildInputs`:**
```nix
gsettings-desktop-schemas
hicolor-icon-theme
```

**Replace the `devShell.shellHook` with:**
```nix
shellHook = ''
  export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath runtimeLibraries}:$LD_LIBRARY_PATH"
  export XDG_DATA_DIRS="${pkgs.gsettings-desktop-schemas}/share/gsettings-schemas/${pkgs.gsettings-desktop-schemas.name}''${pkgs.gtk3}/share/gsettings-schemas/${pkgs.gtk3.name}:${pkgs.hicolor-icon-theme}/share:$XDG_DATA_DIRS"
  export GTK_THEME="Adwaita"
'';
```

### Step 3: Run It

```bash
# Method 1 - shell.nix
cd math-algorithm-tool
nix-shell
npm run dev

# Method 2 - flake.nix
cd math-algorithm-tool
nix develop
npm run dev

# Method 3 - One-liner
cd math-algorithm-tool
nix-shell --run "npm run dev"
```

## Why It Works

NixOS stores packages in `/nix/store`, not standard paths like `/usr/lib` or `/usr/share`. GTK/WebKit can't find their data files → crash.

Two critical environment variables:
- `LD_LIBRARY_PATH`: Where to find `.so` libraries
- `XDG_DATA_DIRS`: Where to find schemas (`gschemas.compiled`) and theme files

By setting these in `shellHook`, Tauri can find everything it needs at runtime.
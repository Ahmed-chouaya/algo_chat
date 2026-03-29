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

    # Required for GTK/webkitgtk schemas on NixOS
    # Fixes "Bus error (core dumped)" by providing missing schemas
    gsettings-desktop-schemas
    hicolor-icon-theme
  ];

  # Required for sandbox issues on NixOS
  LD_LIBRARY_PATH = "${pkgs.lib.makeLibraryPath [
    pkgs.gtk3
  ]}:$LD_LIBRARY_PATH";

  # Required environment variables for GTK/webkit
  GDK_SCALE = "1";
  GDK_DPI_SCALE = "1";

  # NixOS fix: Set XDG_DATA_DIRS so WebKitGTK can find schemas
  # Prevents "Bus error (core dumped)" on NixOS
  shellHook = ''
    export XDG_DATA_DIRS="${pkgs.gsettings-desktop-schemas}/share/gsettings-schemas/${pkgs.gsettings-desktop-schemas.name}:${pkgs.hicolor-icon-theme}/share/icons''${XDG_DATA_DIRS:+:$XDG_DATA_DIRS}"
    echo "[NixOS Tauri Fix] XDG_DATA_DIRS configured for WebKitGTK"
  '';
}
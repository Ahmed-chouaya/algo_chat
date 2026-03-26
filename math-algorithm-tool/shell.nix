{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Node.js for frontend
    nodejs_20

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
    wrapGAppsHook3

    # Additional Tauri deps
    librsvg
    xorg.libXcomposite
    xorg.libXdamage
    xorg.libXrandr
    xorg.libXtst
    libxkbcommon
    dbus
    gcc
    gnumake
  ];

  # Required environment variables for GTK/webkit
  GDK_SCALE = "1";
  GDK_DPI_SCALE = "1";
}
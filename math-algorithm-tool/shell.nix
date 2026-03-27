{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Node.js for frontend
    nodejs_20

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
  ];

  # Required environment variables for GTK/webkit
  GDK_SCALE = "1";
  GDK_DPI_SCALE = "1";
}
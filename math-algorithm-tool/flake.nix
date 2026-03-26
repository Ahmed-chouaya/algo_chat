{
  description = "Math Algorithm Tool - Desktop application for mathematicians";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ ];
        };
      in
      {
        packages.math-algorithm-tool = pkgs.callPackage ./package.nix { };

        defaultPackage = self.packages.${system}.math-algorithm-tool;

        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            nodejs_20
            rustc
            cargo

            # Tauri system dependencies
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
            librsvg
            libxkbcommon
            dbus
            xorg.libXcomposite
            xorg.libXdamage
            xorg.libXrandr
            xorg.libXtst
            gcc
            gnumake
          ];

          GDK_SCALE = "1";
          GDK_DPI_SCALE = "1";
        };
      }
    );
}
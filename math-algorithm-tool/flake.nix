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
      in
      {
        packages.math-algorithm-tool = pkgs.callPackage ./package.nix { };

        defaultPackage = self.packages.${system}.math-algorithm-tool;

        devShell = import ./shell.nix { inherit pkgs; };
      }
    );
}
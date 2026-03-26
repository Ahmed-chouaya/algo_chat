{ lib
, stdenv
, autoPatchelfHook
, wrapGAppsHook3
, pkg-config
, nodejs_20
, rustPlatform
, cargo
, rustc
, glib
, gtk3
, cairo
, pango
, gdk-pixbuf
, atk
, webkitgtk_4_1
, libsoup_3
, libsecret
, librsvg
, libxkbcommon
, dbus
, xorg
, gcc
, gnumake
, makeWrapper
}:

let
  pname = "math-algorithm-tool";
  version = "0.1.0";
in
rustPlatform.buildRustPackage {
  inherit pname version;

  src = ./.;

  cargoLock.lockFile = ./src-tauri/Cargo.lock;

  nativeBuildInputs = [
    autoPatchelfHook
    wrapGAppsHook3
    pkg-config
    nodejs_20
    makeWrapper
  ];

  buildInputs = [
    gcc
    gnumake
    glib
    gtk3
    cairo
    pango
    gdk-pixbuf
    atk
    webkitgtk_4_1
    libsoup_3
    libsecret
    librsvg
    libxkbcommon
    dbus
    xorg.libXcomposite
    xorg.libXdamage
    xorg.libXrandr
    xorg.libXtst
  ];

  buildPhase = ''
    export HOME=$TMPDIR
    npm run build
    npm run tauri build -- --bundles none
  '';

  installPhase = ''
    mkdir -p $out/bin
    mkdir -p $out/share/${pname}
    cp src-tauri/target/release/math-algorithm-tool $out/bin/
    cp -r build/* $out/share/${pname}/

    wrapProgram $out/bin/math-algorithm-tool \
      --prefix XDG_DATA_DIRS "$out/share:$XDG_DATA_DIRS"
  '';

  postFixup = ''
    patchelf --set-rpath "${lib.makeLibraryPath buildInputs}" $out/bin/math-algorithm-tool
  '';

  meta = with lib; {
    description = "Desktop tool for mathematicians to convert algorithm descriptions into executable implementations";
    homepage = "https://github.com/milgraph/algo";
    license = lib.licenses.mit;
    platforms = lib.platforms.linux;
  };
}
{ lib
, stdenv
, autoPatchelfHook
, wrapGAppsHook3
, pkg-config
, nodejs_20
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
, libxcomposite
, libxdamage
, libxrandr
, libxtst
, gcc
, gnumake
, makeWrapper
}:

let
  pname = "math-algorithm-tool";
  version = "0.1.0";
in
stdenv.mkDerivation {
  inherit pname version;

  src = ./.;

  nativeBuildInputs = [
    autoPatchelfHook
    wrapGAppsHook3
    pkg-config
    nodejs_20
    makeWrapper
    gcc
    gnumake
  ];

  buildInputs = [
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
    libxcomposite
    libxdamage
    libxrandr
    libxtst
  ];

  configurePhase = ''
    export HOME=$TMPDIR
    npm install
  '';

  buildPhase = ''
    export HOME=$TMPDIR
    export PATH="$HOME/.cargo/bin:$PATH"

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

  meta = with lib; {
    description = "Desktop tool for mathematicians to convert algorithm descriptions into executable implementations";
    homepage = "https://github.com/milgraph/algo";
    license = lib.licenses.mit;
    platforms = lib.platforms.linux;
  };
}
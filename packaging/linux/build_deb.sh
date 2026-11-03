#!/usr/bin/env bash
# Build dist/guess-a-sketch_<version>_amd64.deb (self-contained PyInstaller bundle).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
VERSION="$(python3 packaging/version_info.py)"
PKG=guess-a-sketch
BUILD="$ROOT/build/linux"
STAGE="$BUILD/${PKG}_${VERSION}_amd64"
rm -rf "$BUILD" && mkdir -p "$BUILD" dist

python3 -m PyInstaller --noconfirm --clean --onedir --windowed \
  --name "$PKG" --distpath "$BUILD/dist" --workpath "$BUILD/work" --specpath "$BUILD" \
  --add-data "$ROOT/assets:assets" --exclude-module numpy --exclude-module tkinter \
  main.py

mkdir -p "$STAGE/DEBIAN" "$STAGE/opt" "$STAGE/usr/bin" "$STAGE/usr/share/applications"
cp -r "$BUILD/dist/$PKG" "$STAGE/opt/$PKG"
ln -s "/opt/$PKG/$PKG" "$STAGE/usr/bin/$PKG"
for s in 48 64 128 256 512; do
  d="$STAGE/usr/share/icons/hicolor/${s}x${s}/apps"; mkdir -p "$d"
  cp "assets/icons/icon-$s.png" "$d/$PKG.png"
done
mkdir -p "$STAGE/usr/share/doc/$PKG"
cp LICENSE "$STAGE/usr/share/doc/$PKG/copyright"

cat > "$STAGE/usr/share/applications/$PKG.desktop" <<DESK
[Desktop Entry]
Type=Application
Name=Guess-A-Sketch
Comment=Spell the word before the sketch is finished
Exec=/usr/bin/$PKG
Icon=$PKG
Terminal=false
Categories=Game;Education;KidsGame;
Keywords=spelling;hangman;words;kids;
DESK

SIZE=$(du -sk "$STAGE/opt" | cut -f1)
cat > "$STAGE/DEBIAN/control" <<CTRL
Package: $PKG
Version: $VERSION
Section: games
Priority: optional
Architecture: amd64
Installed-Size: $SIZE
Depends: libc6 (>= 2.31)
Maintainer: Shawn Rapaz <info@shoukugames.org>
Homepage: https://shoukugames.org/
Description: Guess-A-Sketch - a drawing-based spelling game for kids
 A hangman-style spelling game. Every wrong letter sketches more of the
 mystery object; spell the word before the drawing is finished.
 Unlimited levels, three difficulty settings and a parent progress report.
CTRL
cat > "$STAGE/DEBIAN/postinst" <<'POST'
#!/bin/sh
set -e
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database -q || true
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -q -t /usr/share/icons/hicolor || true
exit 0
POST
cp "$STAGE/DEBIAN/postinst" "$STAGE/DEBIAN/postrm"
chmod 755 "$STAGE/DEBIAN/postinst" "$STAGE/DEBIAN/postrm"
find "$STAGE" -type d -exec chmod 755 {} +

dpkg-deb --root-owner-group --build "$STAGE" "dist/${PKG}_${VERSION}_amd64.deb"
echo "Built dist/${PKG}_${VERSION}_amd64.deb"

#!/usr/bin/env bash
# Build dist/GuessASketch-<version>-win64.exe using Windows Python under Wine.
# One-time setup of the Wine prefix is done by setup_wine.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export WINEPREFIX="${WINEPREFIX:-$HOME/.cache/gas-build/wine}" WINEDEBUG=-all
VERSION="$(python3 packaging/version_info.py)"
NAME="GuessASketch-${VERSION}-win64"
BUILD="build/windows"
rm -rf "$BUILD" && mkdir -p "$BUILD" dist
python3 packaging/version_info.py --winfile "$BUILD/version_info.txt"

wine 'C:\Python311\python.exe' -m PyInstaller --noconfirm --clean --onefile --windowed \
  --name "$NAME" --distpath "$BUILD\\dist" --workpath "$BUILD\\work" --specpath "$BUILD" \
  --icon "$ROOT/assets/icons/icon.ico" --version-file "$ROOT/$BUILD/version_info.txt" \
  --add-data "$ROOT/assets;assets" --exclude-module numpy --exclude-module tkinter \
  main.py </dev/null

cp "$BUILD/dist/$NAME.exe" "dist/$NAME.exe"
echo "Built dist/$NAME.exe"

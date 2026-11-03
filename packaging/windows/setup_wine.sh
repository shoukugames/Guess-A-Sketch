#!/usr/bin/env bash
# One-time: create a Wine prefix with Windows Python 3.11 + pygame + PyInstaller.
set -euo pipefail
export WINEPREFIX="${WINEPREFIX:-$HOME/.cache/gas-build/wine}" WINEDEBUG=-all
CACHE="$(dirname "$WINEPREFIX")"
mkdir -p "$CACHE" && cd "$CACHE"
wineboot -i >/dev/null 2>&1 || true
if [ ! -f "$WINEPREFIX/drive_c/Python311/python.exe" ]; then
  curl -sSL -o python.nupkg https://www.nuget.org/api/v2/package/python/3.11.9
  rm -rf pyzip && mkdir pyzip && (cd pyzip && python3 -m zipfile -e ../python.nupkg .)
  mkdir -p "$WINEPREFIX/drive_c/Python311" && cp -r pyzip/tools/* "$WINEPREFIX/drive_c/Python311/"
fi
wine 'C:\Python311\python.exe' -m ensurepip </dev/null
wine 'C:\Python311\python.exe' -m pip install --no-warn-script-location pygame==2.6.1 pyinstaller==6.20.0 </dev/null

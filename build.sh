#!/usr/bin/env bash
# Build all release packages into dist/.
set -euo pipefail
cd "$(dirname "$0")"
bash packaging/linux/build_deb.sh
bash packaging/windows/build_exe.sh
ls -lh dist/

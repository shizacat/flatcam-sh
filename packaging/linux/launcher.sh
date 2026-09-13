#!/usr/bin/env bash
# Launcher inside the Linux package — relocates the packed conda env on first run.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
ENV="$ROOT/env"
SRC="$ROOT/src"
LOG_DIR="${HOME}/.FlatCAM"
LOG_FILE="$LOG_DIR/launch.log"

mkdir -p "$LOG_DIR"
exec >>"$LOG_FILE" 2>&1
echo "=== $(date '+%Y-%m-%d %H:%M:%S') FlatCAM launch ==="

export PATH="$ENV/bin:$PATH"
export CONDA_PREFIX="$ENV"

if [[ -x "$ENV/bin/conda-unpack" ]]; then
  "$ENV/bin/conda-unpack" || true
fi

if [[ -f "$SRC/FlatCAM.py" ]]; then
  ENTRY="$SRC/FlatCAM.py"
elif [[ -f "$SRC/flatcam.py" ]]; then
  ENTRY="$SRC/flatcam.py"
else
  echo "FlatCAM entry script not found in $SRC" >&2
  exit 1
fi

cd "$SRC"
exec "$ENV/bin/python" "$ENTRY" "$@"

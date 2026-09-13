#!/bin/bash
# Launcher inside FlatCAM.app — relocates the packed conda env on first run.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV="$ROOT/Resources/env"
SRC="$ROOT/Resources/src"
LOG_DIR="${HOME}/Library/Logs/FlatCAM"
LOG_FILE="$LOG_DIR/flatcam.log"

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
  echo "FlatCAM entry script not found in $SRC"
  osascript -e "display alert \"FlatCAM\" message \"Entry script not found. See log: $LOG_FILE\""
  exit 1
fi

cd "$SRC"
"$ENV/bin/python" "$ENTRY" "$@"
status=$?
if [[ $status -ne 0 ]]; then
  echo "FlatCAM exited with status $status"
  osascript -e "display alert \"FlatCAM failed to start\" message \"See log: $LOG_FILE\""
  exit "$status"
fi

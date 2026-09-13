#!/bin/bash
# Launcher inside FlatCAM.app — relocates the packed conda env on first run.
# Do not use `set -e`: a failing python would then skip the user-visible alert.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV="$ROOT/Resources/env"
SRC="$ROOT/Resources/src"
LOG_DIR="${HOME}/Library/Logs/FlatCAM"
LOG_FILE="$LOG_DIR/flatcam.log"
UNPACK_MARK="$ENV/.conda-unpack-done"

mkdir -p "$LOG_DIR"

alert() {
  /usr/bin/osascript -e "display alert \"FlatCAM\" message \"$1\"" >/dev/null 2>&1 || true
}

exec >>"$LOG_FILE" 2>&1
echo "=== $(date '+%Y-%m-%d %H:%M:%S') FlatCAM launch ==="
echo "bundle=$ROOT"
echo "ENV=$ENV"

if [[ ! -d "$ENV" ]]; then
  echo "Packed env missing: $ENV"
  alert "This copy of FlatCAM is incomplete. Install from the DMG by dragging FlatCAM.app to Applications."
  exit 1
fi

if [[ ! -w "$ENV" ]]; then
  echo "Env is not writable; likely launched from a read-only DMG."
  alert "Copy FlatCAM.app to Applications and run it from there. It cannot start from the read-only disk image."
  exit 1
fi

export PATH="$ENV/bin:$PATH"
export CONDA_PREFIX="$ENV"

for plugins in "$ENV/lib/qt6/plugins" "$ENV/plugins"; do
  if [[ -d "$plugins" ]]; then
    export QT_PLUGIN_PATH="$plugins${QT_PLUGIN_PATH:+:$QT_PLUGIN_PATH}"
  fi
done
if [[ -d "$ENV/lib/qt6/plugins/platforms" ]]; then
  export QT_QPA_PLATFORM_PLUGIN_PATH="$ENV/lib/qt6/plugins/platforms"
fi

if [[ -x "$ENV/bin/conda-unpack" && ! -f "$UNPACK_MARK" ]]; then
  echo "Running conda-unpack"
  if ! "$ENV/bin/conda-unpack"; then
    echo "conda-unpack failed"
    alert "Could not prepare the Python environment. Copy FlatCAM.app to Applications and try again. Log: $LOG_FILE"
    exit 1
  fi
  touch "$UNPACK_MARK"
fi

if [[ -f "$SRC/FlatCAM.py" ]]; then
  ENTRY="$SRC/FlatCAM.py"
elif [[ -f "$SRC/flatcam.py" ]]; then
  ENTRY="$SRC/flatcam.py"
else
  echo "FlatCAM entry script not found in $SRC"
  alert "Entry script not found. See log: $LOG_FILE"
  exit 1
fi

if [[ ! -x "$ENV/bin/python" ]]; then
  echo "Python missing: $ENV/bin/python"
  alert "Python is missing in the app bundle. See log: $LOG_FILE"
  exit 1
fi

cd "$SRC"
"$ENV/bin/python" "$ENTRY" "$@"
status=$?
if [[ $status -ne 0 ]]; then
  echo "FlatCAM exited with status $status"
  alert "FlatCAM failed to start. See log: $LOG_FILE"
  exit "$status"
fi

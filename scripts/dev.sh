#!/usr/bin/env bash
# Launch FlatCAM in developer mode.
# Requires an activated mamba env: mamba activate flatcam
#
#   ./scripts/dev.sh [args...]

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAUNCH="${ROOT}/scripts/dev_launch.py"

if ! command -v python >/dev/null 2>&1; then
    printf 'error: python not found. Run first: mamba activate flatcam\n' >&2
    exit 1
fi

if [[ ! -f "${LAUNCH}" ]]; then
    printf 'error: missing %s\n' "${LAUNCH}" >&2
    exit 1
fi

export PYTHONUNBUFFERED=1
export PYTHONFAULTHANDLER=1
export FLATCAM_DEV=1

exec python -u -X faulthandler "${LAUNCH}" "$@"

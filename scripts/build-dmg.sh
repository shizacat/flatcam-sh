#!/usr/bin/env bash
# Compatibility wrapper for the former macOS-only DMG script.
exec "$(cd "$(dirname "$0")" && pwd)/build.sh" macos "$@"

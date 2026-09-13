#!/usr/bin/env bash
# Build a relocatable FlatCAM package from this repository.
#
# Layout is shared across platforms: conda-pack the environment, copy sources,
# then wrap them in a platform-specific installer (DMG / tar.gz / zip).
#
# Usage:
#   ./scripts/build.sh              # auto-detect the host OS
#   ./scripts/build.sh macos
#   ./scripts/build.sh linux
#   ./scripts/build.sh windows
#
# Tools: git (optional, for version), micromamba/mamba, conda-pack.
# macOS extras: sips, iconutil, hdiutil; create-dmg is optional.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="${BUILD_DIR:-$ROOT/build}"
mkdir -p "$BUILD_DIR"

APP_NAME="${APP_NAME:-FlatCAM}"
MAMBA="${MAMBA:-$BUILD_DIR/bin/micromamba}"
ENV_PREFIX="${ENV_PREFIX:-$BUILD_DIR/env}"
PACK_TAR="$BUILD_DIR/env.tar.gz"
DIST_DIR="$BUILD_DIR/dist"

if [[ "${OSTYPE:-}" == msys* || "${OSTYPE:-}" == cygwin* || "${OSTYPE:-}" == mingw* ]]; then
  export MSYS_NO_PATHCONV=1
  export MSYS2_ARG_CONV_EXCL="*"
fi

log() { printf '==> %s\n' "$*" >&2; }

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command not found: $1" >&2
    exit 1
  fi
}

detect_os() {
  local sys
  sys="$(uname -s 2>/dev/null || echo unknown)"
  case "$sys" in
    Darwin) echo macos ;;
    Linux) echo linux ;;
    MINGW*|MSYS*|CYGWIN*|Windows_NT) echo windows ;;
    *)
      echo "Unsupported OS: $sys" >&2
      exit 1
      ;;
  esac
}

detect_arch() {
  local machine
  machine="$(uname -m 2>/dev/null || echo unknown)"
  case "$machine" in
    arm64|aarch64) echo arm64 ;;
    x86_64|amd64|AMD64) echo x86_64 ;;
    *)
      echo "Unsupported arch: $machine" >&2
      exit 1
      ;;
  esac
}

native_path() {
  if command -v cygpath >/dev/null 2>&1; then
    cygpath -w "$1"
  else
    printf '%s\n' "$1"
  fi
}

unix_path() {
  if command -v cygpath >/dev/null 2>&1; then
    cygpath -u "$1"
  else
    printf '%s\n' "$1"
  fi
}

default_version() {
  local tag=""
  if [[ -n "${GITHUB_REF:-}" && "$GITHUB_REF" == refs/tags/* ]]; then
    tag="${GITHUB_REF_NAME:-${GITHUB_REF#refs/tags/}}"
  elif git -C "$ROOT" describe --tags --exact-match >/dev/null 2>&1; then
    tag="$(git -C "$ROOT" describe --tags --exact-match)"
  fi
  if [[ -n "$tag" ]]; then
    printf '%s\n' "${tag#v}"
    return
  fi
  printf '%s\n' "dev"
}

TARGET_OS="${1:-${TARGET_OS:-$(detect_os)}}"
ARCH="$(detect_arch)"
APP_VERSION="${APP_VERSION:-$(default_version)}"
APP_VERSION="${APP_VERSION#v}"
APP_SRC_DIR=""
ARTIFACT=""

case "$TARGET_OS" in
  macos|linux|windows) ;;
  *)
    echo "Usage: $0 [macos|linux|windows]" >&2
    exit 1
    ;;
esac

HOST_OS="$(detect_os)"
if [[ "$TARGET_OS" != "$HOST_OS" ]]; then
  echo "Cannot cross-compile: host is $HOST_OS, target is $TARGET_OS" >&2
  exit 1
fi

# Layout differs between upstream (sources at repo root) and this fork (source/).
resolve_app_src() {
  local candidate
  for candidate in "$ROOT/source" "$ROOT"; do
    if [[ -f "$candidate/FlatCAM.py" || -f "$candidate/flatcam.py" ]]; then
      APP_SRC_DIR="$candidate"
      log "App sources in $APP_SRC_DIR"
      return
    fi
  done
  echo "FlatCAM entry script not found under $ROOT" >&2
  exit 1
}

apply_patches() {
  local patches_dir="$ROOT/packaging/patches"
  if [[ ! -d "$patches_dir" ]]; then
    return
  fi
  shopt -s nullglob
  local patch
  for patch in "$patches_dir"/*.patch; do
    log "Apply $(basename "$patch")"
    patch -d "$ROOT" -p1 --forward < "$patch"
  done
  shopt -u nullglob
}

micromamba_platform() {
  case "$TARGET_OS-$ARCH" in
    macos-arm64) echo osx-arm64 ;;
    macos-x86_64) echo osx-64 ;;
    linux-arm64) echo linux-aarch64 ;;
    linux-x86_64) echo linux-64 ;;
    windows-x86_64) echo win-64 ;;
    *)
      echo "No micromamba build for $TARGET_OS-$ARCH" >&2
      exit 1
      ;;
  esac
}

ensure_micromamba() {
  if [[ -x "$MAMBA" ]] || command -v "$MAMBA" >/dev/null 2>&1; then
    return
  fi

  mkdir -p "$BUILD_DIR/bin"
  local platform
  platform="$(micromamba_platform)"
  log "Bootstrap micromamba ($platform) into $MAMBA"

  if [[ "$TARGET_OS" == windows ]]; then
    curl -Ls "https://micro.mamba.pm/api/micromamba/${platform}/latest" \
      | tar -xj -C "$BUILD_DIR" Library/bin/micromamba.exe
    MAMBA="$BUILD_DIR/Library/bin/micromamba.exe"
  else
    curl -Ls "https://micro.mamba.pm/api/micromamba/${platform}/latest" \
      | tar -xj -C "$BUILD_DIR" bin/micromamba
    MAMBA="$BUILD_DIR/bin/micromamba"
  fi
  chmod +x "$MAMBA"
}

find_environment_yml() {
  local candidate
  for candidate in "$ROOT/environment.yml" "$APP_SRC_DIR/environment.yml"; do
    if [[ -f "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return
    fi
  done
  echo "Missing environment.yml under $ROOT" >&2
  exit 1
}

create_env() {
  if [[ "${SKIP_ENV_CREATE:-}" == 1 ]]; then
    ENV_PREFIX="${ENV_PREFIX:-${CONDA_PREFIX:-}}"
    if [[ -n "$ENV_PREFIX" ]]; then
      ENV_PREFIX="$(unix_path "$ENV_PREFIX")"
    fi
    if [[ -z "$ENV_PREFIX" || ! -d "$ENV_PREFIX" ]]; then
      echo "SKIP_ENV_CREATE=1 requires ENV_PREFIX or an activated conda env" >&2
      exit 1
    fi
    log "Reuse conda env at $ENV_PREFIX"
    return
  fi

  local yml
  yml="$(find_environment_yml)"
  log "Create conda env at $ENV_PREFIX from $yml"
  rm -rf "$ENV_PREFIX"
  "$MAMBA" create -y -p "$(native_path "$ENV_PREFIX")" -f "$(native_path "$yml")" python=3.11
}

env_python() {
  if [[ -x "$ENV_PREFIX/python.exe" ]]; then
    printf '%s\n' "$ENV_PREFIX/python.exe"
  elif [[ -x "$ENV_PREFIX/bin/python" ]]; then
    printf '%s\n' "$ENV_PREFIX/bin/python"
  else
    echo "Python not found in $ENV_PREFIX" >&2
    exit 1
  fi
}

ensure_conda_pack() {
  local py
  py="$(env_python)"
  if ! "$py" -c "import conda_pack" >/dev/null 2>&1; then
    log "Install conda-pack"
    "$py" -m pip install conda-pack
  fi
}

pack_env() {
  local py
  py="$(env_python)"
  log "conda-pack → $PACK_TAR"
  rm -f "$PACK_TAR"
  "$py" -m conda_pack \
    -p "$(native_path "$ENV_PREFIX")" \
    -o "$(native_path "$PACK_TAR")" \
    --ignore-missing-files
}

copy_tree() {
  local src="$1"
  local dest="$2"
  mkdir -p "$dest"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete \
      --exclude '.git/' \
      --exclude '__pycache__/' \
      --exclude '*.pyc' \
      "$src/" "$dest/"
    return
  fi
  (cd "$src" && tar -cf - --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' .) \
    | (cd "$dest" && tar -xf -)
}

copy_sources_to() {
  copy_tree "$APP_SRC_DIR" "$1"
}

# App icon: Evo ships PNG/ICO, not .icns. Build .icns from the 256px PNG.
make_icns() {
  local src="$APP_SRC_DIR/assets/resources/flatcam_icon256.png"
  local icns_path="$1"
  if [[ ! -f "$src" ]]; then
    echo "Missing app icon source: $src" >&2
    exit 1
  fi
  need_cmd sips
  need_cmd iconutil

  local iconset="$BUILD_DIR/AppIcon.iconset"
  log "Build $icns_path from $(basename "$src")"
  rm -rf "$iconset"
  mkdir -p "$iconset"

  sips -z 16 16 "$src" --out "$iconset/icon_16x16.png" >/dev/null
  sips -z 32 32 "$src" --out "$iconset/icon_16x16@2x.png" >/dev/null
  sips -z 32 32 "$src" --out "$iconset/icon_32x32.png" >/dev/null
  sips -z 64 64 "$src" --out "$iconset/icon_32x32@2x.png" >/dev/null
  sips -z 128 128 "$src" --out "$iconset/icon_128x128.png" >/dev/null
  sips -z 256 256 "$src" --out "$iconset/icon_128x128@2x.png" >/dev/null
  sips -z 256 256 "$src" --out "$iconset/icon_256x256.png" >/dev/null
  sips -z 512 512 "$src" --out "$iconset/icon_256x256@2x.png" >/dev/null
  sips -z 512 512 "$src" --out "$iconset/icon_512x512.png" >/dev/null
  sips -z 1024 1024 "$src" --out "$iconset/icon_512x512@2x.png" >/dev/null

  iconutil -c icns "$iconset" -o "$icns_path"
  rm -rf "$iconset"
}

write_plist() {
  local dest="$1"
  sed "s/@APP_VERSION@/${APP_VERSION}/g" "$ROOT/packaging/macos/Info.plist" > "$dest"
}

package_macos() {
  local app_dir="$BUILD_DIR/${APP_NAME}.app"
  local staging="$BUILD_DIR/staging"
  local icns_path="$BUILD_DIR/AppIcon.icns"
  ARTIFACT="$BUILD_DIR/${APP_NAME}-${APP_VERSION}-macos-${ARCH}.dmg"

  pack_env
  log "Assemble $app_dir"
  rm -rf "$app_dir"
  mkdir -p "$app_dir/Contents/MacOS" \
           "$app_dir/Contents/Resources/env" \
           "$app_dir/Contents/Resources/src"

  tar -xzf "$PACK_TAR" -C "$app_dir/Contents/Resources/env"
  copy_sources_to "$app_dir/Contents/Resources/src"
  make_icns "$icns_path"
  cp "$icns_path" "$app_dir/Contents/Resources/AppIcon.icns"
  write_plist "$app_dir/Contents/Info.plist"
  cp "$ROOT/packaging/macos/launcher.sh" "$app_dir/Contents/MacOS/FlatCAM"
  chmod 755 "$app_dir/Contents/MacOS/FlatCAM"

  mkdir -p "$staging"
  rm -rf "${staging:?}/"*
  cp -R "$app_dir" "$staging/"
  rm -f "$ARTIFACT"

  if [[ -z "${CI:-}" ]] && command -v create-dmg >/dev/null 2>&1; then
    log "create-dmg → $ARTIFACT"
    create-dmg \
      --volname "$APP_NAME" \
      --volicon "$icns_path" \
      --window-pos 200 120 \
      --window-size 600 400 \
      --icon-size 100 \
      --icon "${APP_NAME}.app" 150 190 \
      --hide-extension "${APP_NAME}.app" \
      --app-drop-link 450 190 \
      "$ARTIFACT" \
      "$staging" || true
    if [[ ! -f "$ARTIFACT" ]]; then
      echo "create-dmg did not produce $ARTIFACT, falling back to hdiutil" >&2
      ln -sf /Applications "$staging/Applications"
      hdiutil create -volname "$APP_NAME" -srcfolder "$staging" -ov -format UDZO "$ARTIFACT"
    fi
  else
    log "hdiutil → $ARTIFACT"
    need_cmd hdiutil
    ln -sf /Applications "$staging/Applications"
    hdiutil create -volname "$APP_NAME" -srcfolder "$staging" -ov -format UDZO "$ARTIFACT"
  fi
}

package_linux() {
  local dist="$DIST_DIR/${APP_NAME}"
  ARTIFACT="$BUILD_DIR/${APP_NAME}-${APP_VERSION}-linux-${ARCH}.tar.gz"

  pack_env
  log "Assemble $dist"
  rm -rf "$dist"
  mkdir -p "$dist/env" "$dist/src"
  tar -xzf "$PACK_TAR" -C "$dist/env"
  copy_sources_to "$dist/src"
  cp "$ROOT/packaging/linux/launcher.sh" "$dist/${APP_NAME}"
  chmod 755 "$dist/${APP_NAME}"
  if [[ -f "$APP_SRC_DIR/assets/resources/flatcam_icon256.png" ]]; then
    cp "$APP_SRC_DIR/assets/resources/flatcam_icon256.png" "$dist/${APP_NAME}.png"
  fi

  rm -f "$ARTIFACT"
  log "tar → $ARTIFACT"
  tar -czf "$ARTIFACT" -C "$DIST_DIR" "$APP_NAME"
}

package_windows() {
  local dist="$DIST_DIR/${APP_NAME}"
  ARTIFACT="$BUILD_DIR/${APP_NAME}-${APP_VERSION}-windows-${ARCH}.zip"

  pack_env
  log "Assemble $dist"
  rm -rf "$dist"
  mkdir -p "$dist/env" "$dist/src"
  tar -xzf "$PACK_TAR" -C "$dist/env"
  copy_sources_to "$dist/src"
  cp "$ROOT/packaging/windows/launcher.bat" "$dist/${APP_NAME}.bat"
  if [[ -f "$APP_SRC_DIR/assets/resources/flatcam_icon256.ico" ]]; then
    cp "$APP_SRC_DIR/assets/resources/flatcam_icon256.ico" "$dist/${APP_NAME}.ico"
  fi

  rm -f "$ARTIFACT"
  log "zip → $ARTIFACT"
  if command -v powershell.exe >/dev/null 2>&1; then
    powershell.exe -NoProfile -Command \
      "Compress-Archive -Path '$(native_path "$dist")' -DestinationPath '$(native_path "$ARTIFACT")' -Force"
  elif command -v zip >/dev/null 2>&1; then
    (cd "$DIST_DIR" && zip -r "$ARTIFACT" "$APP_NAME")
  else
    tar -a -cf "$ARTIFACT" -C "$DIST_DIR" "$APP_NAME"
  fi
}

log "Target $TARGET_OS-$ARCH version $APP_VERSION"
resolve_app_src
apply_patches
if [[ "${SKIP_ENV_CREATE:-}" != 1 ]]; then
  ensure_micromamba
fi
create_env
ensure_conda_pack

case "$TARGET_OS" in
  macos) package_macos ;;
  linux) package_linux ;;
  windows) package_windows ;;
esac

log "Done: $ARTIFACT"

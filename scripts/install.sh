#!/usr/bin/env bash
# ALEAPP one-line installer: installs the latest GitHub release for this machine.
#
#   curl -fsSL https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/install.sh | bash -s -- --help
#
# What it does per platform:
#   Debian/Ubuntu  -> the release .deb (sudo dpkg -i)
#   Fedora/RHEL/SUSE -> the release .rpm (sudo rpm/dnf install)
#   Arch/CachyOS   -> aleapp-git from the AUR (yay/paru), else the AppImage
#   other Linux    -> the release AppImage into ~/.local/bin (+ .desktop entry)
#   macOS          -> downloads the release .dmg and opens it
#
# Every download is checked against the release's SHA256SUMS.txt before it is
# used. Nothing is run as root except the package-manager install itself.
set -euo pipefail

REPO='abrignoni/ALEAPP'
APP='ALEAPP'
BIN='aleapp'
TAG=''           # empty = latest release
FROM_SOURCE=0
UNINSTALL=0
DRY_RUN=0
ASSUME_YES=0
PREFIX="${HOME}/.local"

log() { printf '%s\n' "$*"; }
run() {
  if [ "$DRY_RUN" -eq 1 ]; then printf '+ %s\n' "$*"; else "$@"; fi
}

usage() {
  cat <<EOF
Usage: install.sh [options]

Installs the latest ALEAPP release for this machine (see above for the
per-platform mapping). All downloads are verified against SHA256SUMS.txt.

Options:
  --tag TAG       install a specific release tag (e.g. --tag v2026.5.0)
  --from-source   install from git source instead of a release asset
  --prefix DIR    install location for AppImage/source installs (default: $HOME/.local)
  --uninstall     remove an AppImage/source install at --prefix (package-manager
                  installs are removed with your package manager instead)
  --dry-run       print what would be done without doing it
  -y, --yes       assume yes for prompts
  -h, --help      show this help and exit
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --tag) TAG="${2:?--tag needs a value}"; shift 2 ;;
    --from-source) FROM_SOURCE=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -y|--yes) ASSUME_YES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) log "install.sh: unknown option: $1 (see --help)"; exit 1 ;;
  esac
done

need() {
  command -v "$1" >/dev/null 2>&1 || { log "install.sh: need '$1' on PATH"; exit 1; }
}

confirm() {
  if [ "$ASSUME_YES" -eq 1 ] || [ "$DRY_RUN" -eq 1 ]; then return 0; fi
  printf '%s [y/N] ' "$1"
  read -r answer
  [ "$answer" = 'y' ] || [ "$answer" = 'Y' ]
}

# Familiy of https://github.com/cli/cli's extension installer: prefer python3's
# json over jq, which installers cannot assume.
resolve_tag() {
  if [ -n "$TAG" ]; then printf '%s' "$TAG"; return; fi
  need curl
  need python3
  curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" |
    python3 -c 'import json,sys; print(json.load(sys.stdin)["tag_name"])'
}

release_arch() {
  # Release assets are named ALEAPP-<version>-linux-<arch>: x64 or arm64,
  # matching release.yml's lower-cased RUNNER_ARCH.
  case "$(uname -m)" in
    x86_64|amd64) printf 'x64' ;;
    aarch64|arm64) printf 'arm64' ;;
    *) log "install.sh: unsupported architecture: $(uname -m)"; exit 1 ;;
  esac
}

download_verified() {
  # download_verified <tag> <asset> <destdir>: fetch asset + SHA256SUMS.txt,
  # verify, and print the asset path.
  local tag="$1" asset="$2" destdir="$3"
  need curl
  mkdir -p "$destdir"
  local sums="$destdir/SHA256SUMS.txt"
  curl -fsSL -o "$destdir/$asset" "https://github.com/${REPO}/releases/download/${tag}/${asset}"
  curl -fsSL -o "$sums" "https://github.com/${REPO}/releases/download/${tag}/SHA256SUMS.txt"
  ( cd "$destdir" && grep -F " $asset" SHA256SUMS.txt | sha256sum -c - ) ||
    { log "install.sh: checksum mismatch for $asset"; exit 1; }
  printf '%s/%s' "$destdir" "$asset"
}

uninstall_local() {
  local target="$PREFIX/bin/$BIN" desktop="$HOME/.local/share/applications/$BIN.desktop"
  log "Removing $target${desktop:+, $desktop} (if present)..."
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '+ rm -f %s %s %s\n' "$target" "$target.AppImage" "$desktop"
    return
  fi
  rm -f "$target" "$target.AppImage" "$desktop"
  log 'Done. (A .deb/.rpm install is removed with: sudo dpkg -r aleapp / sudo rpm -e aleapp)'
}

install_appimage() {
  local tag="$1" rarch="$2" tmpdir="$3"
  local asset="${APP}-${tag#v}-linux-${rarch}.AppImage"
  local file
  file=$(download_verified "$tag" "$asset" "$tmpdir")
  local dest="$PREFIX/bin/$BIN"
  log "Installing $asset to $dest ..."
  run mkdir -p "$PREFIX/bin"
  run cp "$file" "$dest"
  run chmod +x "$dest"
  if [ "$(uname -s)" = 'Linux' ]; then
    local desktop="$HOME/.local/share/applications/$BIN.desktop"
    log "Writing $desktop ..."
    if [ "$DRY_RUN" -eq 0 ]; then
      mkdir -p "$(dirname "$desktop")"
      cat > "$desktop" <<EOF2
[Desktop Entry]
Type=Application
Name=$APP
Comment=Android Logs, Events, and Protobuf Parser
Exec=$dest
Icon=$BIN
Terminal=false
Categories=Utility;
EOF2
    else
      printf '+ write %s\n' "$desktop"
    fi
    log "If the AppImage does not start (no FUSE), run it with: $dest --appimage-extract-and-run"
  fi
  log "Installed. Try: $dest --help"
}

install_from_source() {
  need git
  need python3
  local dest="$PREFIX/share/aleapp"
  log "Installing ALEAPP from source into $dest ..."
  if [ -d "$dest/.git" ]; then
    run git -C "$dest" pull --ff-only
  else
    run git clone --depth 1 "https://github.com/${REPO}.git" "$dest"
  fi
  run python3 "$dest/admin/scripts/install_requirements.py"
  local wrapper="$PREFIX/bin/$BIN"
  log "Writing wrapper $wrapper ..."
  if [ "$DRY_RUN" -eq 0 ]; then
    mkdir -p "$PREFIX/bin"
    cat > "$wrapper" <<EOF2
#!/usr/bin/env sh
exec python3 "$dest/aleapp.py" "\$@"
EOF2
    chmod +x "$wrapper"
  else
    printf '+ write %s\n' "$wrapper"
  fi
  log "Installed. Try: $wrapper --help"
  case ":$PATH:" in
    *":$PREFIX/bin:"*) ;;
    *) log "Note: $PREFIX/bin is not on PATH; add it to use '$BIN' directly." ;;
  esac
}

main() {
  if [ "$UNINSTALL" -eq 1 ]; then uninstall_local; exit 0; fi
  if [ "$FROM_SOURCE" -eq 1 ]; then install_from_source; exit 0; fi

  local os rarch tag tmpdir
  os="$(uname -s)"
  tmpdir="$(mktemp -d "${TMPDIR:-/tmp}/aleapp-install.XXXXXX")"
  trap 'rm -rf "$tmpdir"' EXIT

  if [ "$os" = 'Darwin' ]; then
    rarch="$(release_arch)"
    tag="$(resolve_tag)"
    # Asset names mirror release.yml: ALEAPP-<version>-macos-<arch>.dmg.
    local dmg="ALEAPP-${tag#v}-macos-${rarch}.dmg"
    local file
    file=$(download_verified "$tag" "$dmg" "$tmpdir")
    log "Downloaded $file (verified). Opening it for a drag-install to Applications..."
    run open "$file"
    exit 0
  fi

  if [ "$os" != 'Linux' ]; then
    log "install.sh: unsupported OS: $os (Linux and macOS only)"
    exit 1
  fi

  rarch="$(release_arch)"
  tag="$(resolve_tag)"
  log "Latest release: $tag ($rarch)"

  if [ -r /etc/os-release ]; then
    # shellcheck disable=SC1091
    . /etc/os-release
  fi
  local distro="${ID:-unknown}"

  case "$distro" in
    ubuntu|debian|linuxmint|pop|raspbian)
      need sudo
      local asset="ALEAPP-${tag#v}-linux-${rarch}.deb"
      local file
      file=$(download_verified "$tag" "$asset" "$tmpdir")
      log "Installing $asset with dpkg ..."
      if confirm "Run: sudo dpkg -i $file?"; then
        run sudo dpkg -i "$file"
        log "Installed. Try: $BIN --help"
      else
        log "Aborted. The verified .deb is at $file"
      fi
      ;;
    fedora|rhel|centos|almalinux|rocky|ol|opensuse*|sles)
      need sudo
      local asset="ALEAPP-${tag#v}-linux-${rarch}.rpm"
      local file
      file=$(download_verified "$tag" "$asset" "$tmpdir")
      log "Installing $asset ..."
      if confirm "Run the package-manager install for $file?"; then
        if command -v dnf >/dev/null 2>&1; then
          run sudo dnf install -y "$file"
        else
          run sudo rpm -Uvh "$file"
        fi
        log "Installed. Try: $BIN --help"
      else
        log "Aborted. The verified .rpm is at $file"
      fi
      ;;
    arch|cachyos|manjaro|endeavouros)
      if command -v yay >/dev/null 2>&1 || command -v paru >/dev/null 2>&1; then
        local helper='yay'
        command -v yay >/dev/null 2>&1 || helper='paru'
        log "Arch-based distro detected: installing aleapp-git from the AUR with $helper ..."
        run "$helper" -S aleapp-git
      else
        log "Arch-based distro without an AUR helper; falling back to the AppImage."
        log "Tip: install yay or paru, then run: yay -S aleapp-git"
        install_appimage "$tag" "$rarch" "$tmpdir"
      fi
      ;;
    *)
      install_appimage "$tag" "$rarch" "$tmpdir"
      ;;
  esac
}

main

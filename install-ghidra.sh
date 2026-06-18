#!/usr/bin/env bash
#
# install-ghidra.sh - Install Ghidra and launch it on Ubuntu 26.04 (and nearby releases).
# Windows: use install-ghidra.ps1 / install-ghidra.bat (see GHIDRA.md)
# Installer version: 1.1.1
#
# What it does (in order):
#   0. Pre-flight        verify Ubuntu/arch, sudo, network
#   1. System packages   OpenJDK 21, unzip, GUI libraries, optional Xvfb
#   2. Download          fetch the official PUBLIC release zip from GitHub
#   3. Install           extract under ~/.local/share/ghidra and wire up launchers
#   4. Launch            run ./ghidraRun (GUI) or under Xvfb when requested
#
# USAGE
#   ./install-ghidra.sh                     # install (if needed) and launch GUI
#   ./install-ghidra.sh --install-only      # install only, do not launch
#   ./install-ghidra.sh --run-only          # launch an existing install
#   ./install-ghidra.sh --version 12.1.2    # pin a specific Ghidra release
#   ./install-ghidra.sh --xvfb              # launch under a virtual framebuffer
#   ./install-ghidra.sh --force             # re-download and reinstall
#   ./install-ghidra.sh --help
#
# Note: Ghidra does not require Gradle. If apt update fails because of a stale
# third-party PPA (e.g. ppa:cwchien/gradle on Ubuntu 26.04), this script will
# disable the broken source automatically and retry.
#
# Safe to re-run - skips work that is already done unless --force is passed.
#

if [ -z "${BASH_VERSION:-}" ]; then exec bash "$0" "$@"; fi
set -euo pipefail

# ----- Color + helpers -----
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
    CYAN=$'\033[96m'; GREEN=$'\033[92m'; YELLOW=$'\033[93m'
    RED=$'\033[91m'; DIM=$'\033[90m'; BOLD=$'\033[1m'; RESET=$'\033[0m'
else
    CYAN=''; GREEN=''; YELLOW=''; RED=''; DIM=''; BOLD=''; RESET=''
fi

ok()      { printf "  ${GREEN}[OK]${RESET}   %s\n"   "$1"; }
warn()    { printf "  ${YELLOW}[WARN]${RESET} %s\n" "$1"; }
fail()    { printf "  ${RED}[FAIL]${RESET} %s\n"   "$1" >&2; exit 1; }
info()    { printf "  ${CYAN}[INFO]${RESET} %s\n"  "$1"; }
banner()  { printf "\n${BOLD}${CYAN}[[ %s ]]${RESET}\n" "$1"; }
step()    { printf "${DIM}    ▶ %s${RESET}\n" "$1"; }

# Disable apt source entries that fail on the current Ubuntu release (common after
# distro upgrades when third-party PPAs lag behind, e.g. ppa:cwchien/gradle on 26.04).
disable_broken_apt_sources() {
    local log_file="$1"
    local repo_line url_key source_file disabled_any=false

    while IFS= read -r repo_line; do
        [[ -n "$repo_line" ]] || continue
        url_key="$(sed -E 's|^https?://||; s|/ubuntu.*||; s|[[:space:]].*||' <<<"$repo_line")"
        if [[ -z "$url_key" ]]; then
            continue
        fi

        while IFS= read -r source_file; do
            [[ -n "$source_file" ]] || continue
            warn "Disabling unsupported apt source: $source_file"
            warn "  ($repo_line)"
            sudo mv "$source_file" "${source_file}.disabled"
            disabled_any=true
        done < <(grep -rlF "$url_key" /etc/apt/sources.list.d/ 2>/dev/null \
            | grep -Ev '\.disabled$' || true)
    done < <(grep -oE "The repository '[^']+' does not have a Release file" "$log_file" 2>/dev/null \
        | sed -E "s/^The repository '([^']+)'.*/\1/" || true)

    # Known stale PPAs that often break fresh 26.04 upgrades before upstream catches up.
    if [[ "${VERSION_CODENAME:-}" == "resolute" ]]; then
        while IFS= read -r source_file; do
            [[ -n "$source_file" ]] || continue
            warn "Disabling stale Gradle PPA (not needed for Ghidra): $source_file"
            sudo mv "$source_file" "${source_file}.disabled"
            disabled_any=true
        done < <(grep -rlE 'cwchien/gradle|ppa\.launchpadcontent\.net/cwchien/gradle' \
            /etc/apt/sources.list.d/ 2>/dev/null | grep -Ev '\.disabled$' || true)
    fi

    [[ "$disabled_any" == "true" ]]
}

apt_update_safe() {
    local log_file tries=0
    log_file="$(mktemp)"
    trap 'rm -f "$log_file"' RETURN

    while (( tries < 5 )); do
        if sudo apt-get update -qq 2>"$log_file"; then
            return 0
        fi

        if grep -q 'does not have a Release file' "$log_file"; then
            if disable_broken_apt_sources "$log_file"; then
                tries=$((tries + 1))
                continue
            fi
        fi

        cat "$log_file" >&2
        return 1
    done

    cat "$log_file" >&2
    return 1
}

# ----- Defaults -----
GHIDRA_VERSION=""
INSTALL_ROOT="${GHIDRA_INSTALL_ROOT:-$HOME/.local/share/ghidra}"
CACHE_DIR="${GHIDRA_CACHE_DIR:-$HOME/.cache/ghidra-installer}"
BIN_DIR="${GHIDRA_BIN_DIR:-$HOME/.local/bin}"
INSTALL_ONLY=false
RUN_ONLY=false
USE_XVFB=false
FORCE=false
SKIP_SHA256=false
GITHUB_API="https://api.github.com/repos/NationalSecurityAgency/ghidra"
CURL_UA="ghidra-install-script/1.0"

# ----- Argument parsing -----
while [[ $# -gt 0 ]]; do
    case "$1" in
        --install-only)  INSTALL_ONLY=true ;;
        --run-only)      RUN_ONLY=true; INSTALL_ONLY=false ;;
        --version)       GHIDRA_VERSION="$2"; shift ;;
        --install-dir)   INSTALL_ROOT="$2"; shift ;;
        --cache-dir)     CACHE_DIR="$2"; shift ;;
        --bin-dir)       BIN_DIR="$2"; shift ;;
        --xvfb)          USE_XVFB=true ;;
        --force)         FORCE=true ;;
        --skip-sha256)   SKIP_SHA256=true ;;
        -h|--help)
            awk '/^#!/ {next} /^# / {sub(/^# ?/, ""); print; next} /^#$/ {print ""; next} {exit}' "$0"
            exit 0
            ;;
        --)
            shift
            break
            ;;
        -*)
            fail "Unknown argument: $1 (try --help)"
            ;;
        *)
            break
            ;;
    esac
    shift
done
GHIDRA_ARGS=("$@")

if [[ "$RUN_ONLY" == "true" && "$FORCE" == "true" ]]; then
    fail "--run-only and --force cannot be used together"
fi

# ----- Top banner -----
echo
printf "${BOLD}${CYAN}╔═══════════════════════════════════════════════════════════════╗${RESET}\n"
printf "${BOLD}${CYAN}║     Ghidra installer v1.1.1 // Ubuntu 26.04 LTS              ║${RESET}\n"
printf "${BOLD}${CYAN}╚═══════════════════════════════════════════════════════════════╝${RESET}\n"

# ====================================================================
# STAGE 0 — Pre-flight
# ====================================================================
banner "0. Pre-flight"

if [[ ! -r /etc/os-release ]]; then
    fail "/etc/os-release not found — is this Linux?"
fi
# shellcheck disable=SC1091
. /etc/os-release
if [[ "${ID:-}" != "ubuntu" && "${ID_LIKE:-}" != *ubuntu* ]]; then
    warn "This script targets Ubuntu — you're on ${ID:-unknown}. Proceeding anyway."
else
    ok "Ubuntu ${VERSION_ID:-unknown} (${VERSION_CODENAME:-unknown}) detected"
    if [[ "${VERSION_ID:-}" != "26.04" ]]; then
        warn "Tuned for Ubuntu 26.04 LTS (Resolute Raccoon) — you're on ${VERSION_ID:-unknown}."
        warn "It should still work on 24.04/22.04 if OpenJDK 21 is available."
    fi
fi

ARCH="$(uname -m)"
if [[ "$ARCH" != "x86_64" && "$ARCH" != "amd64" ]]; then
    fail "Unsupported CPU architecture: $ARCH (Ghidra public Linux builds require x86_64)"
fi
ok "Architecture: $ARCH"

if ! command -v sudo &>/dev/null; then
    fail "sudo is required to install system packages"
fi
if sudo -n true 2>/dev/null; then
    ok "sudo available"
else
    info "sudo will prompt for your password when needed"
fi

mkdir -p "$INSTALL_ROOT" "$CACHE_DIR" "$BIN_DIR"

# ====================================================================
# STAGE 1 — System packages
# ====================================================================
if [[ "$RUN_ONLY" == "false" ]]; then
    banner "1. System packages (apt)"

    info "Updating apt package lists..."
    apt_update_safe

    info "Installing OpenJDK 21, archive tools, and GUI runtime libraries..."
    ASOUND_PKG="libasound2"
    if apt-cache show libasound2t64 &>/dev/null; then
        ASOUND_PKG="libasound2t64"
    fi
    sudo apt-get install -y -qq \
        openjdk-21-jdk \
        ca-certificates curl wget unzip \
        libx11-6 libxext6 libxrender1 libxtst6 libxi6 libxrandr2 \
        libgtk-3-0 "$ASOUND_PKG" \
        python3 python3-pip \
        >/dev/null

    if [[ "$USE_XVFB" == "true" ]]; then
        sudo apt-get install -y -qq xvfb >/dev/null
    fi

    ok "System packages installed"

    if ! command -v java &>/dev/null; then
        fail "java not found after installing openjdk-21-jdk"
    fi
    JAVA_VER="$(java -version 2>&1 | head -1)"
    ok "Java available: $JAVA_VER"

    JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")"
    export JAVA_HOME
    info "JAVA_HOME=$JAVA_HOME"
fi

# ====================================================================
# Resolve release metadata
# ====================================================================
resolve_release() {
    local api_url release_json tag_name asset_name download_url sha256

    if [[ -n "$GHIDRA_VERSION" ]]; then
        GHIDRA_VERSION="${GHIDRA_VERSION#Ghidra_}"
        GHIDRA_VERSION="${GHIDRA_VERSION%_build}"
        GHIDRA_VERSION="${GHIDRA_VERSION#ghidra_}"
        tag_name="Ghidra_${GHIDRA_VERSION}_build"
        api_url="${GITHUB_API}/releases/tags/${tag_name}"
    else
        api_url="${GITHUB_API}/releases/latest"
    fi

    step "Querying GitHub release metadata: $api_url"
    release_json="$(curl -fsSL -H "User-Agent: ${CURL_UA}" "$api_url")"
    release_meta="$(RELEASE_JSON="$release_json" python3 - <<'PY'
import json, os, re, sys

release = json.loads(os.environ["RELEASE_JSON"])
body = release.get("body", "")
match = re.search(r"SHA-256:\s*`([0-9a-f]+)`", body, re.I)
sha256 = match.group(1).lower() if match else ""
assets = [
    a for a in release.get("assets", [])
    if a.get("name", "").endswith(".zip") and "PUBLIC" in a.get("name", "")
]
if not assets:
    sys.exit("No PUBLIC release zip found in GitHub assets")
asset = assets[0]
print(release["tag_name"])
print(asset["name"])
print(asset["browser_download_url"])
print(sha256)
PY
)"

    GHIDRA_TAG="$(sed -n '1p' <<<"$release_meta")"
    GHIDRA_ZIP="$(sed -n '2p' <<<"$release_meta")"
    GHIDRA_URL="$(sed -n '3p' <<<"$release_meta")"
    GHIDRA_SHA256="$(sed -n '4p' <<<"$release_meta")"
}

find_install_dir() {
    local current_link="$INSTALL_ROOT/current"
    if [[ -L "$current_link" && -x "$current_link/ghidraRun" ]]; then
        readlink -f "$current_link"
        return 0
    fi
    local candidate
    for candidate in "$INSTALL_ROOT"/ghidra_*; do
        if [[ -d "$candidate" && -x "$candidate/ghidraRun" ]]; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done
    return 1
}

install_ghidra() {
    local zip_path="$CACHE_DIR/$GHIDRA_ZIP"
    local extract_root="$INSTALL_ROOT"
    local install_dir=""

    banner "2. Download Ghidra ${GHIDRA_TAG}"

    if [[ -f "$zip_path" && "$FORCE" == "false" ]]; then
        ok "Using cached archive: $zip_path"
    else
        info "Downloading $GHIDRA_ZIP (~550 MB) — this can take a few minutes..."
        curl -fL --retry 3 --retry-delay 5 \
            -H "User-Agent: ${CURL_UA}" \
            -o "$zip_path.part" \
            "$GHIDRA_URL"
        mv "$zip_path.part" "$zip_path"
        ok "Download complete: $zip_path"
    fi

    if [[ "$SKIP_SHA256" == "false" && -n "$GHIDRA_SHA256" ]]; then
        step "Verifying SHA-256 checksum"
        actual_sha256="$(sha256sum "$zip_path" | awk '{print $1}')"
        if [[ "$actual_sha256" != "$GHIDRA_SHA256" ]]; then
            fail "Checksum mismatch for $GHIDRA_ZIP\n         expected: $GHIDRA_SHA256\n         got:      $actual_sha256"
        fi
        ok "SHA-256 verified"
    elif [[ -z "$GHIDRA_SHA256" ]]; then
        warn "Release notes did not include SHA-256; skipping checksum verification"
    fi

    banner "3. Install Ghidra"

    if [[ "$FORCE" == "true" ]]; then
        rm -rf "$INSTALL_ROOT/current"
        rm -rf "$INSTALL_ROOT"/ghidra_*
    fi

    if install_dir="$(find_install_dir)" && [[ "$FORCE" == "false" ]]; then
        ok "Ghidra already installed at $install_dir"
    else
        info "Extracting to $extract_root ..."
        unzip -q -o "$zip_path" -d "$extract_root"
        install_dir="$(find_install_dir)" || fail "Extraction succeeded but ghidraRun was not found under $extract_root"
        ok "Extracted to $install_dir"
    fi

    ln -sfn "$install_dir" "$INSTALL_ROOT/current"

    cat > "$BIN_DIR/ghidra" <<EOF
#!/usr/bin/env bash
set -euo pipefail
export JAVA_HOME="${JAVA_HOME}"
export PATH="\${JAVA_HOME}/bin:\${PATH}"
exec "${install_dir}/ghidraRun" "\$@"
EOF
    chmod +x "$BIN_DIR/ghidra"

    ln -sfn "$BIN_DIR/ghidra" "$BIN_DIR/ghidraRun"

    mkdir -p "$HOME/.local/share/applications"
    cat > "$HOME/.local/share/applications/ghidra.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Ghidra
Comment=Software reverse engineering framework
Exec=${BIN_DIR}/ghidra
Icon=${install_dir}/Ghidra/images/GhidraIcon128.png
Terminal=false
Categories=Development;
StartupWMClass=ghidra-Ghidra
EOF

    ok "Launchers installed:"
    info "  CLI:     $BIN_DIR/ghidra"
    info "  Desktop: ~/.local/share/applications/ghidra.desktop"
    info "  Install: $install_dir"
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        warn "$BIN_DIR is not on your PATH — add this to ~/.bashrc:"
        warn "  export PATH=\"$BIN_DIR:\$PATH\""
    fi

    GHIDRA_INSTALL_DIR="$install_dir"
}

launch_ghidra() {
    local install_dir="${GHIDRA_INSTALL_DIR:-}"
    if [[ -z "$install_dir" ]]; then
        install_dir="$(find_install_dir)" || fail "Ghidra is not installed. Run without --run-only first."
    fi

    banner "4. Launch Ghidra"

    export JAVA_HOME="${JAVA_HOME:-$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")}"
    export PATH="${JAVA_HOME}/bin:${PATH}"

    if [[ "$USE_XVFB" == "true" ]]; then
        if ! command -v xvfb-run &>/dev/null; then
            info "Installing xvfb..."
            apt_update_safe
            sudo apt-get install -y -qq xvfb >/dev/null
        fi
        ok "Launching under Xvfb (virtual display)"
        exec xvfb-run -a "$install_dir/ghidraRun" "${GHIDRA_ARGS[@]}"
    fi

    if [[ -z "${DISPLAY:-}" ]]; then
        warn "DISPLAY is not set — Ghidra's GUI needs an X11/Wayland session."
        warn "Options:"
        warn "  • Run this on a desktop session, or"
        warn "  • Re-run with --xvfb for a headless virtual display, or"
        warn "  • Use headless mode: $install_dir/support/analyzeHeadless"
        fail "No display available for GUI launch"
    fi

    ok "Starting Ghidra from $install_dir"
    exec "$install_dir/ghidraRun" "${GHIDRA_ARGS[@]}"
}

# ====================================================================
# Main flow
# ====================================================================
if [[ "$RUN_ONLY" == "true" ]]; then
    if command -v java &>/dev/null; then
        JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")"
        export JAVA_HOME
    fi
    launch_ghidra
fi

resolve_release
install_ghidra

if [[ "$INSTALL_ONLY" == "true" ]]; then
    echo
    printf "${BOLD}${GREEN}╔═══════════════════════════════════════════════════════════════╗${RESET}\n"
    printf "${BOLD}${GREEN}║                     INSTALL COMPLETE                          ║${RESET}\n"
    printf "${BOLD}${GREEN}╚═══════════════════════════════════════════════════════════════╝${RESET}\n"
    echo
    printf "  Launch Ghidra:\n"
    printf "    ${CYAN}$BIN_DIR/ghidra${RESET}\n\n"
    exit 0
fi

launch_ghidra

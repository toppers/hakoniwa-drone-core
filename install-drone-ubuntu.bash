#!/usr/bin/env bash
# pyenv + Python 3.12.3 + (optional) Hakoniwa bits
# OS: apt-based Linux (Ubuntu/WSL)
set -euo pipefail
IFS=$'\n\t'

# ===== User options =====
PYTHON_VERSION="${PYTHON_VERSION:-3.12.3}"    # change via env var if needed
PYENV_DIR="${PYENV_DIR:-$HOME/.pyenv}"
PROFILE_FILE="${PROFILE_FILE:-$HOME/.bashrc}" # change to ~/.zshrc for zsh
INSTALL_HAKONIWA="${INSTALL_HAKONIWA:-1}"     # set 0 to skip Hakoniwa section
HAKO_APT_FILE="/etc/apt/sources.list.d/hakoniwa.list"
HAKO_APT_LINE='deb [trusted=yes] https://hakoniwalab.github.io/apt stable main'

# ===== UI helpers =====
C_B="\033[1;34m"; C_G="\033[1;32m"; C_Y="\033[1;33m"; C_R="\033[1;31m"; C_0="\033[0m"
STEP_IDX=0; PHASES=(); PHASE_START=0
say()  { printf "${C_B}==> %s${C_0}\n" "$*"; }
ok()   { printf "${C_G}✔ %s${C_0}\n" "$*"; }
warn() { printf "${C_Y}⚠ %s${C_0}\n" "$*"; }
err()  { printf "${C_R}✖ %s${C_0}\n" "$*"; }
begin_phase() { STEP_IDX=$((STEP_IDX+1)); local t="$1"; PHASES+=("$t"); PHASE_START=$(date +%s); printf "\n${C_B}[ %d/%d ] %s${C_0}\n" "$STEP_IDX" "${#PHASES[@]}" "$t"; }
end_phase()   { local end=$(date +%s); printf "${C_G}   done in %ss${C_0}\n" "$((end-PHASE_START))"; }

# ===== small utils =====
command_exists() { command -v "$1" >/dev/null 2>&1; }
ensure_line() { local line="$1" file="$2"; grep -Fqx "$line" "$file" 2>/dev/null || echo "$line" >> "$file"; }
require_apt_pkgs() { sudo apt-get install -y "$@"; }
fetch_and_unpack() {
  local name="$1" url="$2"
  local tmpzip
  tmpzip="$(mktemp "/tmp/${name}.XXXXXX.zip")"
  say "Downloading ${name}..."
  curl -fsSL -o "$tmpzip" "$url"
  unzip -o "$tmpzip" -d .
  rm -f "$tmpzip"
  ok "${name} unpacked"
}

# ===== Phase 0: Preconditions =====
begin_phase "Preflight checks (apt environment & build deps)"
if ! command_exists apt-get; then err "This script expects an apt-based OS. Abort."; exit 1; fi
sudo apt-get update -y
require_apt_pkgs make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
  libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev \
  liblzma-dev python3-openssl git unzip ca-certificates
ok "Build dependencies installed/verified"
end_phase

# ===== Phase 1: Install/Update pyenv =====
begin_phase "Install/Update pyenv"
if [ ! -d "$PYENV_DIR" ]; then
  say "Cloning pyenv to $PYENV_DIR"
  git clone https://github.com/pyenv/pyenv.git "$PYENV_DIR"
else
  say "pyenv exists → updating"
  git -C "$PYENV_DIR" pull --ff-only || warn "Could not update pyenv (skipped)"
fi
ok "pyenv files ready"
end_phase

# ===== Phase 2: Shell init (idempotent) =====
begin_phase "Configure shell init for pyenv (${PROFILE_FILE})"
ensure_line 'export PYENV_ROOT="$HOME/.pyenv"' "$PROFILE_FILE"
ensure_line 'export PATH="$PYENV_ROOT/bin:$PATH"' "$PROFILE_FILE"
ensure_line 'eval "$(pyenv init --path)"' "$PROFILE_FILE"
ensure_line 'eval "$(pyenv init -)"' "$PROFILE_FILE"
export PYENV_ROOT="$PYENV_DIR"; export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"; eval "$(pyenv init -)"
command_exists pyenv || { err "pyenv not on PATH after init"; exit 1; }
ok "pyenv available: $(pyenv --version)"
end_phase

# ===== Phase 3: Install Python version =====
begin_phase "Install Python ${PYTHON_VERSION} via pyenv"
pyenv install -s "$PYTHON_VERSION"
CURRENT_GLOBAL="$(pyenv global || true)"
if [ -z "${CURRENT_GLOBAL}" ] || [ "${CURRENT_GLOBAL}" = "system" ]; then
  say "Setting pyenv global to ${PYTHON_VERSION}"
  pyenv global "$PYTHON_VERSION"
else
  say "Keeping existing pyenv global: ${CURRENT_GLOBAL}"
fi
pyenv rehash
PY_BIN="$(pyenv root)/versions/${PYTHON_VERSION}/bin/python"
PIP_BIN="$(pyenv root)/versions/${PYTHON_VERSION}/bin/pip"
[ -x "$PY_BIN" ] || { err "python not found at $PY_BIN"; exit 1; }
[ -x "$PIP_BIN" ] || { err "pip not found at $PIP_BIN"; exit 1; }
ok "Python OK: $("$PY_BIN" -V)"
end_phase

# ===== Phase 4: Hakoniwa (optional) =====
if [ "$INSTALL_HAKONIWA" = "1" ]; then
  # 4.0 Add/verify Hakoniwa APT repo
  begin_phase "Hakoniwa: add APT repository & update"
  if [ -f "$HAKO_APT_FILE" ] && grep -Fqx "$HAKO_APT_LINE" "$HAKO_APT_FILE"; then
    ok "APT repo already present: $HAKO_APT_FILE"
  else
    echo "$HAKO_APT_LINE" | sudo tee "$HAKO_APT_FILE" >/dev/null
    ok "Added repo line to $HAKO_APT_FILE"
  fi
  sudo apt-get update -y
  end_phase

  # 4.1 Download & unpack lnx.zip
  begin_phase "Hakoniwa: download & unpack lnx.zip"
  fetch_and_unpack "lnx.zip" "https://github.com/toppers/hakoniwa-drone-core/releases/latest/download/lnx.zip"
  chmod +x lnx/linux-* || true
  end_phase

  # 4.2 Download & unpack WebAvatar.zip
  begin_phase "Hakoniwa: download & unpack WebAvatar.zip"
  fetch_and_unpack "WebAvatar.zip" "https://github.com/toppers/hakoniwa-drone-core/releases/latest/download/WebAvatar.zip"
  end_phase

  # 4.3 Install hakoniwa-core-full from repo
  begin_phase "Hakoniwa: apt install hakoniwa-core-full"
  if sudo apt-get install -y hakoniwa-core-full; then
    ok "hakoniwa-core-full installed"
  else
    warn "hakoniwa-core-full not installed (check repo availability)"
  fi
  end_phase

  # 4.4 pip install hakoniwa-pdu into the selected Python
  begin_phase "Hakoniwa: pip install hakoniwa-pdu into ${PYTHON_VERSION}"
  "$PIP_BIN" install -U pip
  "$PIP_BIN" install -U hakoniwa-pdu
  "$PIP_BIN" install -U \
    "scipy" \
    "aiohttp>=3.10.0" \
    "aiohttp-cors>=0.7.0" \
    "websockets==13.1"
  ok "hakoniwa-pdu installed for ${PYTHON_VERSION}"
  end_phase
else
  warn "Hakoniwa section skipped (INSTALL_HAKONIWA=0)"
fi

function install_mustache()
{
  curl -fsSL -o mo https://raw.githubusercontent.com/tests-always-included/mo/master/mo
  chmod +x mo
  mkdir -p scripts && mv mo scripts/
  bash render-launch.bash
}

install_mustache

printf "\n${C_G}All done!${C_0} Current Python: $("$PY_BIN" -V)\n"
echo "Tip: open a new shell so your ${PROFILE_FILE} changes take effect there too."

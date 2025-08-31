#!/usr/bin/env bash
# Uninstall Hakoniwa bits from the setup script.
# Default: remove Hakoniwa packages/files, keep pyenv & its Pythons.
# OS: apt-based Linux (Ubuntu/WSL)
set -euo pipefail
IFS=$'\n\t'

# ===== User options =====
PROFILE_FILE="${PROFILE_FILE:-$HOME/.bashrc}"   # change to ~/.zshrc for zsh
REMOVE_HAKONIWA="${REMOVE_HAKONIWA:-1}"         # 1=remove hakoniwa-core-full, lnx/, WebAvatar/, hakoniwa-pdu
REMOVE_HAKO_APT="${REMOVE_HAKO_APT:-0}"         # 1=remove hakoniwa APT source list & apt update
REMOVE_PYENV_LINES="${REMOVE_PYENV_LINES:-1}"   # 1=remove pyenv init lines from profile
REMOVE_PYENV_DIR="${REMOVE_PYENV_DIR:-0}"       # 1=remove ~/.pyenv directory (backup by default)
PYENV_BACKUP_DELETE="${PYENV_BACKUP_DELETE:-0}" # 1=rm -rf (no backup); default=backup then remove

PYENV_DIR="${PYENV_DIR:-$HOME/.pyenv}"
HAKO_APT_FILE="/etc/apt/sources.list.d/hakoniwa.list"
HAKO_APT_LINE='deb [trusted=yes] https://hakoniwalab.github.io/apt stable main'

# ===== UI helpers =====
C_B="\033[1;34m"; C_G="\033[1;32m"; C_Y="\033[1;33m"; C_R="\033[1;31m"; C_0="\033[0m"
STEP=0; PHASE_START=0
say()  { printf "${C_B}==> %s${C_0}\n" "$*"; }
ok()   { printf "${C_G}✔ %s${C_0}\n" "$*"; }
warn() { printf "${C_Y}⚠ %s${C_0}\n" "$*"; }
err()  { printf "${C_R}✖ %s${C_0}\n" "$*"; }
begin(){ STEP=$((STEP+1)); PHASE_START=$(date +%s); printf "\n${C_B}[ %d ] %s${C_0}\n" "$STEP" "$1"; }
end()  { local d=$(( $(date +%s) - PHASE_START )); printf "${C_G}   done in %ss${C_0}\n" "$d"; }

command_exists() { command -v "$1" >/dev/null 2>&1; }

# remove an exact line from a file (idempotent)
remove_line() {
  local line="$1" file="$2"
  [ -f "$file" ] || return 0
  awk -v tgt="$line" '($0==tgt){next} {print $0}' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
}

# ===== Phase 1: Preflight =====
begin "Preflight checks"
if ! command_exists apt-get; then
  err "This uninstaller expects an apt-based OS."
  exit 1
fi
ok "apt environment detected"
end

# ===== Phase 2: Remove Hakoniwa bits (optional) =====
if [ "$REMOVE_HAKONIWA" = "1" ]; then
  begin "Remove hakoniwa-core-full (apt) and unpacked artifacts"
  if dpkg -s hakoniwa-core-full >/dev/null 2>&1; then
    sudo apt-get purge -y hakoniwa-core-full || warn "Failed to purge hakoniwa-core-full"
    sudo apt-get autoremove -y || true
    ok "hakoniwa-core-full purged"
  else
    warn "hakoniwa-core-full not installed; skipping"
  fi

  if [ -d "./lnx" ]; then
    rm -rf ./lnx && ok "Removed ./lnx directory"
  else
    warn "./lnx not found; skipping"
  fi

  if [ -d "./WebAvatar" ]; then
    rm -rf ./WebAvatar && ok "Removed ./WebAvatar directory"
  elif [ -d "./webavatar" ]; then
    rm -rf ./webavatar && ok "Removed ./webavatar directory"
  else
    warn "WebAvatar directory not found; skipping"
  fi

  rm -f ./lnx.zip ./WebAvatar.zip 2>/dev/null || true
  end

  # ===== Phase 2b: Uninstall hakoniwa-pdu from pyenv-managed Pythons (safe) =====
  begin "Uninstall hakoniwa-pdu from pyenv-managed Pythons (best-effort)"
  if [ -d "$PYENV_DIR/versions" ]; then
    removed_any=0
    # 1) pyenv-installed interpreters (e.g., 3.12.3)
    while IFS= read -r -d '' pybin; do
      if "$pybin" -m pip show hakoniwa-pdu >/dev/null 2>&1; then
        "$pybin" -m pip uninstall -y hakoniwa-pdu >/dev/null 2>&1 && removed_any=1 || true
        ok "Removed hakoniwa-pdu from $(dirname "$pybin")"
      fi
    done < <(find "$PYENV_DIR/versions" -maxdepth 2 -type f -name python -print0 2>/dev/null || true)

    # 2) pyenv-virtualenv environments
    while IFS= read -r -d '' vpy; do
      if "$vpy" -m pip show hakoniwa-pdu >/dev/null 2>&1; then
        "$vpy" -m pip uninstall -y hakoniwa-pdu >/dev/null 2>&1 && removed_any=1 || true
        ok "Removed hakoniwa-pdu from virtualenv $(dirname "$vpy")"
      fi
    done < <(find "$PYENV_DIR/versions" -type f -path "*/envs/*/bin/python" -print0 2>/dev/null || true)

    [ "$removed_any" = "1" ] || warn "No hakoniwa-pdu found under pyenv"
  else
    warn "pyenv directory not found; skipping hakoniwa-pdu removal"
  fi
  end
fi  # ← Phase 2/2b をここで閉じる

# ===== Phase 3: Remove Hakoniwa APT repo (optional) =====
if [ "$REMOVE_HAKO_APT" = "1" ]; then
  begin "Remove Hakoniwa APT source list & update"
  if [ -f "$HAKO_APT_FILE" ]; then
    if [ "$(wc -l < "$HAKO_APT_FILE")" -eq 1 ] && grep -Fqx "$HAKO_APT_LINE" "$HAKO_APT_FILE"; then
      sudo rm -f "$HAKO_APT_FILE"
      ok "Deleted $HAKO_APT_FILE"
    else
      sudo awk -v tgt="$HAKO_APT_LINE" '($0==tgt){next} {print $0}' "$HAKO_APT_FILE" | sudo tee "$HAKO_APT_FILE" >/dev/null
      ok "Removed Hakoniwa line from $HAKO_APT_FILE"
    fi
    sudo apt-get update -y || true
  else
    warn "$HAKO_APT_FILE not found; skipping"
  fi
  end
else
  warn "Keeping Hakoniwa APT repo (REMOVE_HAKO_APT=0)"
fi

# ===== Phase 4: Remove pyenv init lines from shell profile (optional) =====
if [ "$REMOVE_PYENV_LINES" = "1" ]; then
  begin "Remove pyenv init lines from ${PROFILE_FILE}"
  BACKUP="${PROFILE_FILE}.bak.$(date +%Y%m%d-%H%M%S)"
  if [ -f "$PROFILE_FILE" ]; then
    cp -a "$PROFILE_FILE" "$BACKUP"
    remove_line 'export PYENV_ROOT="$HOME/.pyenv"' "$PROFILE_FILE"
    remove_line 'export PATH="$PYENV_ROOT/bin:$PATH"' "$PROFILE_FILE"
    remove_line 'eval "$(pyenv init --path)"' "$PROFILE_FILE"
    remove_line 'eval "$(pyenv init -)"' "$PROFILE_FILE"
    ok "Edited ${PROFILE_FILE} (backup: ${BACKUP})"
  else
    warn "${PROFILE_FILE} not found; skipping"
  fi
  end
else
  warn "Keeping pyenv init lines (REMOVE_PYENV_LINES=0)"
fi

# ===== Phase 5: Remove pyenv directory (optional, careful) =====
if [ "$REMOVE_PYENV_DIR" = "1" ]; then
  begin "Remove pyenv directory: ${PYENV_DIR}"
  if [ -d "$PYENV_DIR" ]; then
    if [ "$PYENV_BACKUP_DELETE" = "1" ]; then
      rm -rf "$PYENV_DIR"
      ok "Deleted ${PYENV_DIR}"
    else
      DEST="${PYENV_DIR}.bak.$(date +%Y%m%d-%H%M%S)"
      mv "$PYENV_DIR" "$DEST"
      ok "Moved ${PYENV_DIR} -> ${DEST}"
    fi
  else
    warn "pyenv directory not found; skipping"
  fi
  end
else
  warn "Keeping pyenv directory (REMOVE_PYENV_DIR=0)"
fi

printf "\n${C_G}All clean!${C_0} System Python remains untouched.\n"

cat <<EOF
Flags:
  REMOVE_HAKONIWA=${REMOVE_HAKONIWA}
  REMOVE_HAKO_APT=${REMOVE_HAKO_APT}
  REMOVE_PYENV_LINES=${REMOVE_PYENV_LINES}
  REMOVE_PYENV_DIR=${REMOVE_PYENV_DIR}
  PYENV_BACKUP_DELETE=${PYENV_BACKUP_DELETE}
Tip: open a new shell so ${PROFILE_FILE} changes (if any) take effect.
EOF

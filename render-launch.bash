#!/usr/bin/env bash
set -euo pipefail

# 1) 変数解決
REPO_ROOT="$(pwd)"

# system の dist-packages（Linux前提）
SYS_DIST="$(/usr/bin/python3 - <<'PY'
import sysconfig; print(sysconfig.get_paths().get("platlib",""))
PY
)"

# 現在の python の site-packages（pyenv 3.12.3 を選んでおくと吉）
PYENV_SITE="$(python - <<'PY' 2>/dev/null || true
import site
cands=[]
for p in (getattr(site,"getsitepackages",lambda:[])() or []):
    if "site-packages" in p: cands.append(p)
us = getattr(site,"getusersitepackages",lambda:"")() or ""
if us: cands.append(us)
print(next(iter(cands),""))
PY
)"

PYTHON_EXEC=$(which python)

# 2) レンダリング（mo に環境変数で渡す）
export REPO_ROOT SYS_DIST PYENV_SITE PYTHON_EXEC
scripts/mo config/launcher/drone-api-ubuntu.launch_json.mo > config/launcher/drone-api-ubuntu.launch.json
scripts/mo config/launcher/gemini-mcpserver_json.mo > config/launcher/gemini-mcpserver.json

# 任意：JSON 検証
command -v jq >/dev/null 2>&1 && jq . config/launcher/drone-api.launch.json >/dev/null

echo "generated: config/launcher/drone-api.launch.json"

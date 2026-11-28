#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE_DIR="${ROOT_DIR}/harness/pstack/antigravity"

WORKSPACE=""
USE_SYMLINK=false
USE_CLI=false

usage() {
  cat <<'EOF'
Install the Antigravity pstack plugin.

Usage:
  ./scripts/install-antigravity.sh [--workspace <dir>] [--symlink] [--cli]

Options:
  --workspace <dir>  Install into <dir>/.agents/plugins/pstack instead of global ~/.gemini/config/plugins/pstack
  --symlink          Symlink instead of copying (useful when developing locally)
  --cli              Install via `agy plugin install` instead of copying files directly
  -h, --help         Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace)
      [[ $# -ge 2 ]] || { echo "Error: --workspace requires a directory path" >&2; exit 1; }
      WORKSPACE="$2"
      shift 2
      ;;
    --symlink)
      USE_SYMLINK=true
      shift
      ;;
    --cli)
      USE_CLI=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ ! -d "${SOURCE_DIR}" ]]; then
  echo "Error: ${SOURCE_DIR} not found. Run \`node scripts/sync-pstack.mjs\` first." >&2
  exit 1
fi

if [[ "${USE_CLI}" == "true" ]]; then
  if ! command -v agy >/dev/null 2>&1; then
    echo "Error: \`agy\` CLI not found on PATH." >&2
    exit 1
  fi
  agy plugin install "${SOURCE_DIR}"
  exit 0
fi

if [[ -n "${WORKSPACE}" ]]; then
  TARGET_BASE="${WORKSPACE}/.agents/plugins"
else
  TARGET_BASE="${HOME}/.gemini/config/plugins"
fi

TARGET_DIR="${TARGET_BASE}/pstack"
mkdir -p "${TARGET_BASE}"

if [[ "${USE_SYMLINK}" == "true" ]]; then
  rm -rf "${TARGET_DIR}"
  ln -s "${SOURCE_DIR}" "${TARGET_DIR}"
  echo "Symlinked pstack plugin to ${TARGET_DIR}"
else
  rm -rf "${TARGET_DIR}"
  cp -R "${SOURCE_DIR}" "${TARGET_DIR}"
  echo "Installed pstack plugin to ${TARGET_DIR}"
fi

echo "Start a new Antigravity session and run /setup-pstack or /poteto-mode."

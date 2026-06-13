#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
ADMIN_DIR="$ROOT_DIR/admin-frontend"

ADMIN_HOST="${ADMIN_HOST:-127.0.0.1}"
ADMIN_PORT="${ADMIN_PORT:-5174}"
VITE_ADMIN_API_URL="${VITE_ADMIN_API_URL:-http://127.0.0.1:8001}"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required but was not found." >&2
  exit 1
fi

cd "$ADMIN_DIR"
if [ ! -d node_modules ]; then
  npm install
fi

VITE_ADMIN_API_URL="$VITE_ADMIN_API_URL" \
  npm run dev -- --host "$ADMIN_HOST" --port "$ADMIN_PORT" --strictPort

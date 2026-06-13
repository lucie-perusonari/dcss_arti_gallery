#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
FRONTEND_DIR="$ROOT_DIR/frontend"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-5173}"
export VITE_ARTIFACT_API_URL="${VITE_ARTIFACT_API_URL:-http://127.0.0.1:8000}"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required but was not found." >&2
  exit 1
fi

cd "$FRONTEND_DIR"

if [ ! -d node_modules ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

echo "Starting DCSS Artifact Gallery at http://$HOST:$PORT/"
echo "Using Gallery API at $VITE_ARTIFACT_API_URL"
exec npm run dev -- --host "$HOST" --port "$PORT"

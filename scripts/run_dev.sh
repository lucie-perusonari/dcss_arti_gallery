#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
FRONTEND_DIR="$ROOT_DIR/frontend"

API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${API_PORT:-8000}"
FRONTEND_HOST="${FRONTEND_HOST:-127.0.0.1}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
VITE_ARTIFACT_API_URL="${VITE_ARTIFACT_API_URL:-http://127.0.0.1:${API_PORT}}"
API_READY_URL="${API_READY_URL:-${VITE_ARTIFACT_API_URL}/filters}"
API_READY_TIMEOUT_SECONDS="${API_READY_TIMEOUT_SECONDS:-30}"

api_pid=""
crawl_worker_pid=""
frontend_pid=""

cleanup() {
  if [ -n "$frontend_pid" ] && kill -0 "$frontend_pid" 2>/dev/null; then
    kill "$frontend_pid" 2>/dev/null || true
  fi
  if [ -n "$api_pid" ] && kill -0 "$api_pid" 2>/dev/null; then
    kill "$api_pid" 2>/dev/null || true
  fi
  if [ -n "$crawl_worker_pid" ] && kill -0 "$crawl_worker_pid" 2>/dev/null; then
    kill "$crawl_worker_pid" 2>/dev/null || true
  fi
  if [ -n "$frontend_pid" ]; then
    wait "$frontend_pid" 2>/dev/null || true
  fi
  if [ -n "$api_pid" ]; then
    wait "$api_pid" 2>/dev/null || true
  fi
  if [ -n "$crawl_worker_pid" ]; then
    wait "$crawl_worker_pid" 2>/dev/null || true
  fi
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "$1 is required but was not found." >&2
    exit 1
  fi
}

require_port_free() {
  local host="$1"
  local port="$2"
  local label="$3"

  if ! python3 - "$host" "$port" >/dev/null 2>&1 <<'PY'
import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
PY
  then
    echo "$label port is already in use: $host:$port" >&2
    exit 1
  fi
}

wait_for_api() {
  local url="$1"
  local pid="$2"
  local label="$3"
  local elapsed=0

  until python3 - "$url" >/dev/null 2>&1 <<'PY'
import sys
from urllib.request import urlopen

with urlopen(sys.argv[1], timeout=1) as response:
    if response.status >= 400:
        raise SystemExit(1)
PY
  do
    if ! kill -0 "$pid" 2>/dev/null; then
      echo "$label server exited before it became ready." >&2
      exit 1
    fi
    if [ "$elapsed" -ge "$API_READY_TIMEOUT_SECONDS" ]; then
      echo "Timed out waiting for $label at $url" >&2
      exit 1
    fi
    sleep 1
    elapsed=$((elapsed + 1))
  done
}

trap cleanup EXIT INT TERM

require_command docker
require_command python3
require_command npm
require_port_free "$API_HOST" "$API_PORT" "API"
require_port_free "$FRONTEND_HOST" "$FRONTEND_PORT" "Frontend"

echo "Starting MongoDB..."
eval "$("$ROOT_DIR/infra/mongo/mongo_up.sh")"

echo "Starting crawl worker ..."
cd "$ROOT_DIR"
python3 -m crawl_service.worker &
crawl_worker_pid=$!

echo "Starting API at http://$API_HOST:$API_PORT ..."
cd "$ROOT_DIR"
python3 -m uvicorn api.app:app --host "$API_HOST" --port "$API_PORT" &
api_pid=$!

echo "Waiting for API at $API_READY_URL ..."
wait_for_api "$API_READY_URL" "$api_pid" "API"

cd "$FRONTEND_DIR"
if [ ! -d node_modules ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

echo "Starting frontend at http://$FRONTEND_HOST:$FRONTEND_PORT ..."
VITE_ARTIFACT_API_URL="$VITE_ARTIFACT_API_URL" \
  npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT" --strictPort &
frontend_pid=$!

echo
echo "DCSS Artifact Gallery is running:"
echo "  API:      $VITE_ARTIFACT_API_URL"
echo "  Crawl:    background worker"
echo "  Frontend: http://$FRONTEND_HOST:$FRONTEND_PORT"
echo
echo "Press Ctrl-C to stop the API, crawl worker, and frontend. MongoDB remains running; stop it with infra/mongo/mongo_down.sh."

while kill -0 "$api_pid" 2>/dev/null && kill -0 "$crawl_worker_pid" 2>/dev/null && kill -0 "$frontend_pid" 2>/dev/null; do
  sleep 1
done

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

LOG_DIR="${LOG_DIR:-$ROOT_DIR/.logs}"
PID_FILE="${PID_FILE:-$LOG_DIR/crawl_raw_only_prod.pid}"
LOG_FILE="${LOG_FILE:-$LOG_DIR/crawl_raw_only_prod.log}"
DETACH="${DETACH:-0}"

if [ -z "${MONGODB_URI:-}" ]; then
  echo "MONGODB_URI is required for prod raw crawler." >&2
  exit 2
fi

export MONGODB_DATABASE="${MONGODB_DATABASE:-dcss_arti_gallery}"
export MONGODB_CRAWL_FILES_COLLECTION="${MONGODB_CRAWL_FILES_COLLECTION:-crawl_files}"
export MONGODB_CRAWL_USERS_COLLECTION="${MONGODB_CRAWL_USERS_COLLECTION:-crawl_users}"
export MONGODB_RAW_FILES_COLLECTION="${MONGODB_RAW_FILES_COLLECTION:-raw_morgue_files}"
export CRAWL_USER_SKIP_MODE="${CRAWL_USER_SKIP_MODE:-modified_at}"

cd "$ROOT_DIR"

if [ "$DETACH" = "1" ]; then
  mkdir -p "$LOG_DIR"
  if [ -f "$PID_FILE" ]; then
    existing_pid=$(cat "$PID_FILE")
    if [ -n "$existing_pid" ] && kill -0 "$existing_pid" 2>/dev/null; then
      echo "Prod raw morgue crawler is already running."
      echo "  PID: $existing_pid"
      exit 0
    fi
  fi
  setsid python3 -u -m crawl_service.worker > "$LOG_FILE" 2>&1 < /dev/null &
  worker_pid=$!
  printf '%s\n' "$worker_pid" > "$PID_FILE"
  echo "Prod raw morgue crawler started in background."
  echo "  PID:  $worker_pid"
  echo "  Log:  $LOG_FILE"
  echo "  Mode: raw ingest only"
  exit 0
fi

echo "Starting prod raw morgue crawler."
echo "  MongoDB: $MONGODB_URI / $MONGODB_DATABASE"
echo "  Raw collection: $MONGODB_RAW_FILES_COLLECTION"
echo "  User skip mode: $CRAWL_USER_SKIP_MODE"
echo "  Mode: raw ingest only"
echo "Press Ctrl-C to stop."

exec python3 -u -m crawl_service.worker

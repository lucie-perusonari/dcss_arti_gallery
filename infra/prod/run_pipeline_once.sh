#!/usr/bin/env bash
set -euo pipefail

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH:-}"

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
LOG_DIR="${LOG_DIR:-$ROOT_DIR/.logs}"
LOCK_FILE="${LOCK_FILE:-$LOG_DIR/pipeline_once.lock}"
COMPOSE_FILE="${COMPOSE_FILE:-infra/prod/docker-compose.yml}"

mkdir -p "$LOG_DIR"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "$(date -Is) Pipeline is already running."
  exit 0
fi

cd "$ROOT_DIR"

echo "$(date -Is) Pipeline started."
docker compose -f "$COMPOSE_FILE" run --rm crawl-service
docker compose -f "$COMPOSE_FILE" run --rm arti-parser
echo "$(date -Is) Pipeline completed."

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
COMPOSE_FILE="${COMPOSE_FILE:-infra/prod/docker-compose.yml}"

cd "$ROOT_DIR"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage: infra/prod/run_player_casing_migration.sh [--apply] [migration options]

Runs infra/prod/migrate_player_casing.py inside the prod compose MongoDB network.
Without --apply, the migration only audits and prints the expected changes.

Common commands:
  infra/prod/run_player_casing_migration.sh
  infra/prod/run_player_casing_migration.sh --apply
  infra/prod/run_player_casing_migration.sh --apply --backup-confirmed

See infra/prod/migrate_player_casing.py for all migration options.
EOF
  exit 0
fi

docker compose -f "$COMPOSE_FILE" up -d mongo

MONGO_CONTAINER=$(docker compose -f "$COMPOSE_FILE" ps -q mongo)
if [[ -z "$MONGO_CONTAINER" ]]; then
  echo "mongo container is not running" >&2
  exit 1
fi

NETWORK_NAME=$(
  docker inspect \
    --format '{{range $name, $_ := .NetworkSettings.Networks}}{{println $name}}{{end}}' \
    "$MONGO_CONTAINER" \
    | head -n 1
)
if [[ -z "$NETWORK_NAME" ]]; then
  echo "failed to resolve mongo container network" >&2
  exit 1
fi

docker run --rm \
  --network "$NETWORK_NAME" \
  -v "$ROOT_DIR:/workspace" \
  -w /workspace \
  -e MONGODB_URI="${MONGODB_URI:-mongodb://mongo:27017}" \
  -e MONGODB_DATABASE="${MONGODB_DATABASE:-dcss_arti_gallery}" \
  -e MONGODB_RAW_FILES_COLLECTION="${MONGODB_RAW_FILES_COLLECTION:-raw_morgue_files}" \
  -e MONGODB_COLLECTION="${MONGODB_COLLECTION:-artifacts}" \
  -e MONGODB_ARTIFACT_PROCESSING_COLLECTION="${MONGODB_ARTIFACT_PROCESSING_COLLECTION:-artifact_processing_files}" \
  python:3.12-slim \
  sh -c "python -m pip install --no-cache-dir 'pymongo>=4.10' >/dev/null && python infra/prod/migrate_player_casing.py \"\$@\"" \
  migrate_player_casing \
  "$@"

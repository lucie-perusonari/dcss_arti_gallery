#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

ADMIN_API_HOST="${ADMIN_API_HOST:-0.0.0.0}"
ADMIN_API_PORT="${ADMIN_API_PORT:-8001}"
export MONGODB_URI="${MONGODB_URI:-mongodb://localhost:27018}"
export MONGODB_DATABASE="${MONGODB_DATABASE:-dcss_arti_gallery}"
export MONGODB_ARTIFACT_PROCESSING_COLLECTION="${MONGODB_ARTIFACT_PROCESSING_COLLECTION:-artifact_processing_files}"

cd "$ROOT_DIR"
python3 -m uvicorn admin_api.app:app --host "$ADMIN_API_HOST" --port "$ADMIN_API_PORT"

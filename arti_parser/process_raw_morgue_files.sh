#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

export MONGODB_URI="${MONGODB_URI:-mongodb://localhost:27018}"
export MONGODB_DATABASE="${MONGODB_DATABASE:-dcss_arti_gallery}"
export MONGODB_RAW_FILES_COLLECTION="${MONGODB_RAW_FILES_COLLECTION:-raw_morgue_files}"
export MONGODB_COLLECTION="${MONGODB_COLLECTION:-artifacts}"
export MONGODB_ARTIFACT_PROCESSING_COLLECTION="${MONGODB_ARTIFACT_PROCESSING_COLLECTION:-artifact_processing_files}"

exec python3 -m arti_parser.batch "$@"

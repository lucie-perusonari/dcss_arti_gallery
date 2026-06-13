#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
. "$SCRIPT_DIR/mongo_env.sh"

if ! command -v docker >/dev/null 2>&1; then
    echo "docker command not found" >&2
    exit 1
fi

container_id=$(docker ps -aq --filter "name=^/${MONGO_CONTAINER_NAME}$")
if [ -z "$container_id" ]; then
    echo "missing"
    exit 0
fi

running_id=$(docker ps -q --filter "name=^/${MONGO_CONTAINER_NAME}$")
if [ -n "$running_id" ]; then
    echo "running"
else
    echo "stopped"
fi

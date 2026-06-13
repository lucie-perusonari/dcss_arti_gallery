#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
. "$SCRIPT_DIR/mongo_env.sh"

if [ "${CONFIRM_PROD:-0}" != "1" ]; then
    echo "Refusing to stop production MongoDB without CONFIRM_PROD=1." >&2
    exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
    echo "docker command not found" >&2
    exit 1
fi

container_id=$(docker ps -aq --filter "name=^/${MONGO_CONTAINER_NAME}$")
if [ -z "$container_id" ]; then
    echo "MongoDB container does not exist: ${MONGO_CONTAINER_NAME}"
    exit 0
fi

running_id=$(docker ps -q --filter "name=^/${MONGO_CONTAINER_NAME}$")
if [ -z "$running_id" ]; then
    echo "MongoDB container is already stopped: ${MONGO_CONTAINER_NAME}"
    exit 0
fi

docker stop "$MONGO_CONTAINER_NAME" >/dev/null
echo "MongoDB container stopped: ${MONGO_CONTAINER_NAME}"

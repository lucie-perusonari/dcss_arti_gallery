#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
. "$SCRIPT_DIR/mongo_env.sh"

if ! command -v docker >/dev/null 2>&1; then
    echo "docker command not found" >&2
    exit 1
fi

container_id=$(docker ps -aq --filter "name=^/${MONGO_CONTAINER_NAME}$")
if [ -n "$container_id" ]; then
    running_id=$(docker ps -q --filter "name=^/${MONGO_CONTAINER_NAME}$")
    if [ -n "$running_id" ]; then
        echo "MongoDB container is already running: ${MONGO_CONTAINER_NAME}" >&2
    else
        docker start "$MONGO_CONTAINER_NAME" >/dev/null
        echo "MongoDB container started: ${MONGO_CONTAINER_NAME}" >&2
    fi
else
    docker run \
        --detach \
        --name "$MONGO_CONTAINER_NAME" \
        --restart unless-stopped \
        --publish "${MONGO_PORT}:27017" \
        --volume "${MONGO_VOLUME}:/data/db" \
        "$MONGO_IMAGE" >/dev/null
    echo "MongoDB container created: ${MONGO_CONTAINER_NAME}" >&2
fi

python3 "$SCRIPT_DIR/../ensure_mongo_indexes.py" >&2

echo "export MONGODB_URI=${MONGODB_URI}"
echo "export MONGODB_DATABASE=${MONGODB_DATABASE}"
echo "export MONGODB_COLLECTION=${MONGODB_COLLECTION}"
echo "export MONGODB_CRAWL_FILES_COLLECTION=${MONGODB_CRAWL_FILES_COLLECTION}"
echo "export MONGODB_CRAWL_USERS_COLLECTION=${MONGODB_CRAWL_USERS_COLLECTION}"
echo "export MONGODB_RAW_FILES_COLLECTION=${MONGODB_RAW_FILES_COLLECTION}"
echo "export MONGODB_ARTIFACT_PROCESSING_COLLECTION=${MONGODB_ARTIFACT_PROCESSING_COLLECTION}"

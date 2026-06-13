#!/bin/sh

# Production MongoDB settings. Use explicit confirmation for lifecycle scripts.

: "${MONGO_IMAGE:=mongo:7.0}"
: "${MONGO_CONTAINER_NAME:=dcss-arti-gallery-mongo-prod}"
: "${MONGO_PORT:=27017}"
: "${MONGO_VOLUME:=$HOME/.local/var/dcss-arti-gallery/mongodb-prod}"
: "${MONGODB_URI:=mongodb://localhost:${MONGO_PORT}}"
: "${MONGODB_DATABASE:=dcss_arti_gallery}"
: "${MONGODB_COLLECTION:=artifacts}"
: "${MONGODB_CRAWL_FILES_COLLECTION:=crawl_files}"
: "${MONGODB_CRAWL_USERS_COLLECTION:=crawl_users}"
: "${MONGODB_RAW_FILES_COLLECTION:=raw_morgue_files}"
: "${MONGODB_ARTIFACT_PROCESSING_COLLECTION:=artifact_processing_files}"

export MONGODB_URI
export MONGODB_DATABASE
export MONGODB_COLLECTION
export MONGODB_CRAWL_FILES_COLLECTION
export MONGODB_CRAWL_USERS_COLLECTION
export MONGODB_RAW_FILES_COLLECTION
export MONGODB_ARTIFACT_PROCESSING_COLLECTION

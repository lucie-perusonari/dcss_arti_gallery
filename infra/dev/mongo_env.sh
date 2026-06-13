#!/bin/sh

# Development MongoDB settings for local Docker scripts and app environment.

: "${MONGO_IMAGE:=mongo:7.0}"

if [ "${ALLOW_DEV_MONGO_ENV_OVERRIDE:-0}" = "1" ]; then
    : "${MONGO_CONTAINER_NAME:=dcss-arti-gallery-mongo-dev}"
    : "${MONGO_PORT:=27018}"
    : "${MONGO_VOLUME:=$HOME/.local/var/dcss-arti-gallery/mongodb-dev}"
    : "${MONGODB_URI:=mongodb://localhost:${MONGO_PORT}}"
    : "${MONGODB_DATABASE:=dcss_arti_gallery_dev}"
    : "${MONGODB_COLLECTION:=artifacts}"
    : "${MONGODB_CRAWL_FILES_COLLECTION:=crawl_files}"
    : "${MONGODB_CRAWL_USERS_COLLECTION:=crawl_users}"
    : "${MONGODB_RAW_FILES_COLLECTION:=raw_morgue_files}"
    : "${MONGODB_ARTIFACT_PROCESSING_COLLECTION:=artifact_processing_files}"
else
    MONGO_CONTAINER_NAME="dcss-arti-gallery-mongo-dev"
    MONGO_PORT="27018"
    MONGO_VOLUME="$HOME/.local/var/dcss-arti-gallery/mongodb-dev"
    MONGODB_URI="mongodb://localhost:${MONGO_PORT}"
    MONGODB_DATABASE="dcss_arti_gallery_dev"
    MONGODB_COLLECTION="artifacts"
    MONGODB_CRAWL_FILES_COLLECTION="crawl_files"
    MONGODB_CRAWL_USERS_COLLECTION="crawl_users"
    MONGODB_RAW_FILES_COLLECTION="raw_morgue_files"
    MONGODB_ARTIFACT_PROCESSING_COLLECTION="artifact_processing_files"
fi

export MONGODB_URI
export MONGODB_DATABASE
export MONGODB_COLLECTION
export MONGODB_CRAWL_FILES_COLLECTION
export MONGODB_CRAWL_USERS_COLLECTION
export MONGODB_RAW_FILES_COLLECTION
export MONGODB_ARTIFACT_PROCESSING_COLLECTION

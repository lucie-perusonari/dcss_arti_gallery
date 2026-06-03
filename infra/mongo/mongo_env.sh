#!/bin/sh

# Shared MongoDB settings for local Docker scripts and app environment.

: "${MONGO_IMAGE:=mongo:7.0}"
: "${MONGO_CONTAINER_NAME:=dcss-arti-gallery-mongo}"
: "${MONGO_PORT:=27017}"
: "${MONGO_VOLUME:=dcss_arti_gallery_mongo_data}"
: "${MONGODB_URI:=mongodb://localhost:${MONGO_PORT}}"
: "${MONGODB_DATABASE:=dcss_arti_gallery}"
: "${MONGODB_COLLECTION:=artifacts}"
: "${MONGODB_CRAWL_FILES_COLLECTION:=crawl_files}"
: "${MONGODB_CRAWL_USERS_COLLECTION:=crawl_users}"

export MONGODB_URI
export MONGODB_DATABASE
export MONGODB_COLLECTION
export MONGODB_CRAWL_FILES_COLLECTION
export MONGODB_CRAWL_USERS_COLLECTION

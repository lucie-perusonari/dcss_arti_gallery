#!/bin/sh

# Compatibility path for local development. New scripts should use infra/dev.

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
. "$SCRIPT_DIR/../dev/mongo_env.sh"

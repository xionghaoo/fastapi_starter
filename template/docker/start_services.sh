#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Ensure compose sees the project root .env for variable substitution
ENV_FILE_OPT=""
if [[ -f "../.env" ]]; then
  ENV_FILE_OPT="--env-file ../.env"
fi

docker compose ${ENV_FILE_OPT} up -d



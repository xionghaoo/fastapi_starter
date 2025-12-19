#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

ENV_FILE_OPT=""
if [[ -f "../.env" ]]; then
  ENV_FILE_OPT="--env-file ../.env"
fi

# Stop infra; keep volumes by default to preserve data
if [[ "${1-}" == "--purge" ]]; then
  docker compose -f docker-compose.infra.yml ${ENV_FILE_OPT} down -v
else
  docker compose -f docker-compose.infra.yml ${ENV_FILE_OPT} down
fi



#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Ensure compose sees the project root .env for variable substitution
ENV_FILE_OPT=""
if [[ -f "../.env" ]]; then
  ENV_FILE_OPT="--env-file ../.env"
fi

# Build deps image first to avoid web/worker trying to pull it
deps_service="$(docker compose ${ENV_FILE_OPT} config --services | grep -E '(-deps)$' || true)"
if [[ -n "${deps_service}" ]]; then
  echo "Building deps image via service: ${deps_service}"
  docker compose ${ENV_FILE_OPT} build "${deps_service}"
fi

# Build web/worker next
app_services="$(docker compose ${ENV_FILE_OPT} config --services | grep -E '(-web|-worker)$' || true)"
if [[ -n "${app_services}" ]]; then
  echo "Building app services: ${app_services}"
  # shellcheck disable=SC2086
  docker compose ${ENV_FILE_OPT} build ${app_services}
fi

# Bring up app services and common deps (mysql/redis); avoid starting the deps image as a container
to_up_services="$(printf "%s\n" ${app_services} mysql redis | xargs -n1 | sort -u | xargs || true)"
if [[ -z "${to_up_services}" ]]; then
  echo "No services to start."
  exit 0
fi
echo "Starting services: ${to_up_services}"
# shellcheck disable=SC2086
docker compose ${ENV_FILE_OPT} up -d ${to_up_services}



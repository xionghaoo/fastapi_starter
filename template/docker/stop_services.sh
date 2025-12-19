#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
#
# Usage:
#   ./stop_services.sh           # stop only app services (web/worker)
#   ./stop_services.sh --stop-deps  # stop all services including mysql/redis
#

if [[ "${1-}" == "--help" || "${1-}" == "-h" ]]; then
  echo "Usage: $0 [--stop-deps]"
  exit 0
fi

ENV_FILE_OPT=""
if [[ -f "../.env" ]]; then
  ENV_FILE_OPT="--env-file ../.env"
fi

if [[ "${1-}" == "--stop-deps" ]]; then
  echo "Stopping ALL services (including mysql/redis)..."
  docker compose ${ENV_FILE_OPT} down
  exit 0
fi

# Stop only app services (web/worker); keep mysql/redis running if they are shared.
services_to_stop="$(docker compose ${ENV_FILE_OPT} config --services | grep -E '(-web|-worker)$' || true)"
if [[ -z "${services_to_stop}" ]]; then
  echo "No app services (web/worker) found. Doing nothing."
  exit 0
fi

echo "Stopping app services: ${services_to_stop}"
docker compose ${ENV_FILE_OPT} stop ${services_to_stop}
echo "Removing app services containers: ${services_to_stop}"
docker compose ${ENV_FILE_OPT} rm -f ${services_to_stop}



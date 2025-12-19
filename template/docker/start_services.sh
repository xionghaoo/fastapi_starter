#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Ensure compose sees the project root .env for variable substitution
ENV_FILE_OPT=""
if [[ -f "../.env" ]]; then
  ENV_FILE_OPT="--env-file ../.env"
fi

# Best-effort: ensure app DB/user exist on existing MySQL (external container)
ensure_mysql_user() {
  # Load .env into current shell if present
  if [[ -f "../.env" ]]; then
    # shellcheck disable=SC1091
    set -o allexport
    source ../.env || true
    set +o allexport
  fi
  local mysql_url="${MYSQL_URL:-}"
  local root_pw="${MYSQL_ROOT_PASSWORD:-}"
  local mysql_container="${MYSQL_CONTAINER_NAME:-mysql}"
  if [[ -z "${mysql_url}" || -z "${root_pw}" ]]; then
    echo "Skip MySQL init: MYSQL_URL or MYSQL_ROOT_PASSWORD not set."
    return 0
  fi
  # Parse MYSQL_URL: mysql+pymysql://user:pass@host:port/db
  local rest="${mysql_url#*://}"     # drop scheme
  local creds="${rest%%@*}"          # user:pass
  local user="${creds%%:*}"
  local pass="${creds#*:}"
  local after_at="${rest#*@}"        # host:port/db
  local db="${after_at#*/}"          # db[?query]
  db="${db%%\?*}"

  echo "Ensuring MySQL user/database exist: user=${user}, db=${db} (container=${mysql_container})"
  # Wait for container and mysql ready (up to ~30s)
  for i in {1..15}; do
    if docker exec "${mysql_container}" mysqladmin ping -h 127.0.0.1 -uroot -p"${root_pw}" --silent >/dev/null 2>&1; then
      break
    fi
    if [[ "${i}" -eq 15 ]]; then
      echo "MySQL not ready in container ${mysql_container}, continue without initializing."
      return 0
    fi
    sleep 2
  done
  docker exec -i "${mysql_container}" mysql -uroot -p"${root_pw}" -e "\
    CREATE DATABASE IF NOT EXISTS \`${db}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; \
    CREATE USER IF NOT EXISTS '${user}'@'%' IDENTIFIED BY '${pass}'; \
    GRANT ALL PRIVILEGES ON \`${db}\`.* TO '${user}'@'%'; \
    FLUSH PRIVILEGES; \
  " || true
}

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

# Attempt to ensure MySQL user/database on external MySQL before app starts
ensure_mysql_user

# Bring up app services; include mysql/redis only if defined in this compose
defined_extra="$(docker compose ${ENV_FILE_OPT} config --services | grep -E '^(mysql|redis)$' || true)"
to_up_services="$(printf "%s\n%s\n" "${app_services}" "${defined_extra}" | xargs -n1 | sort -u | xargs || true)"
if [[ -z "${to_up_services}" ]]; then
  echo "No services to start."
  exit 0
fi
echo "Starting services: ${to_up_services}"
# shellcheck disable=SC2086
docker compose ${ENV_FILE_OPT} up -d ${to_up_services}



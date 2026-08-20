#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$script_dir/../.." && pwd)"
cd "$repo_dir"

if [[ ! -f .env ]]; then
  echo "ERROR: $repo_dir/.env does not exist" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

domain="${ONDA_DOMAIN:?ONDA_DOMAIN must be set}"
base_url="${ONDA_HEALTHCHECK_URL:-https://$domain}"

running_services="$(docker compose ps --status running --services)"
for service in db web caddy; do
  if ! grep -qx "$service" <<<"$running_services"; then
    echo "ERROR: Compose service is not running: $service" >&2
    docker compose ps >&2
    exit 1
  fi
done

headers="$(mktemp)"
trap 'rm -f "$headers"' EXIT INT TERM
curl --fail --silent --show-error --location \
  --connect-timeout 10 --max-time 30 \
  --dump-header "$headers" --output /dev/null \
  "$base_url/api/cities/"

if ! grep -Eiq '^x-robots-tag:[[:space:]]*noindex([[:space:]]|$)' "$headers"; then
  echo "ERROR: public health response is missing X-Robots-Tag: noindex" >&2
  exit 1
fi

echo "Production health check passed: db, web, caddy, and $base_url/api/cities/"

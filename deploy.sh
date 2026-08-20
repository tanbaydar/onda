#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$repo_dir"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: refusing to deploy from a dirty checkout" >&2
  git status --short >&2
  exit 1
fi

echo "Creating and verifying the required pre-deploy backup"
"$repo_dir/backup.sh"

git pull --ff-only
docker compose build
docker compose up -d db
docker compose run --rm web python manage.py migrate --noinput
docker compose up -d

docker compose ps

healthcheck_passed=false
for _ in $(seq 1 12); do
  if "$repo_dir/production-healthcheck.sh"; then
    healthcheck_passed=true
    break
  fi
  sleep 5
done

if [[ "$healthcheck_passed" != true ]]; then
  echo "ERROR: post-deploy production health check failed" >&2
  exit 1
fi

docker image prune -f

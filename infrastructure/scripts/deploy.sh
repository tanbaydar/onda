#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$script_dir/../.." && pwd)"
cd "$repo_dir"

if [[ "$#" -gt 1 ]]; then
  echo "Usage: $0 [40-character-main-commit]" >&2
  exit 2
fi

requested_revision="${1:-}"
if [[ -n "$requested_revision" && ! "$requested_revision" =~ ^[0-9a-f]{40}$ ]]; then
  echo "ERROR: deployment revision must be a full lowercase 40-character commit SHA" >&2
  exit 2
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: refusing to deploy from a dirty checkout" >&2
  git status --short >&2
  exit 1
fi

if [[ -n "$requested_revision" ]]; then
  git fetch --prune origin +refs/heads/main:refs/remotes/origin/main
  remote_revision="$(git rev-parse --verify 'refs/remotes/origin/main^{commit}')"

  if [[ "$requested_revision" != "$remote_revision" ]]; then
    echo "Skipping stale deployment request for $requested_revision; origin/main is $remote_revision"
    exit 0
  fi
fi

echo "Creating and verifying the required pre-deploy backup"
"$script_dir/backup.sh"

if [[ -n "$requested_revision" ]]; then
  git merge --ff-only "$requested_revision"
else
  git pull --ff-only
fi
docker compose build
docker compose up -d db
docker compose run --rm web python manage.py check --deploy --fail-level WARNING
docker compose run --rm web python manage.py migrate --noinput
docker compose up -d

docker compose ps

healthcheck_passed=false
for _ in $(seq 1 12); do
  if "$script_dir/production-healthcheck.sh"; then
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

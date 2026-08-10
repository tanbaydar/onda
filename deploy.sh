#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$repo_dir"

git pull --ff-only
docker compose build
docker compose up -d
docker compose exec -T web python manage.py migrate --noinput
docker image prune -f

docker compose ps

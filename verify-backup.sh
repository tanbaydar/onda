#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
backup_dir="${BACKUP_DIR:-$repo_dir/backups}"
backup_file="${1:-}"

if [[ -z "$backup_file" ]]; then
  backup_file="$(find "$backup_dir" -maxdepth 1 -type f -name 'danced-*.sql.gz' -print 2>/dev/null | sort | tail -1)"
fi

if [[ -z "$backup_file" || ! -f "$backup_file" ]]; then
  echo "ERROR: pass a .sql.gz backup path or place a backup in $backup_dir" >&2
  exit 1
fi

gzip -t "$backup_file"

mysql_image="${RESTORE_MYSQL_IMAGE:-mysql:8.4}"
container_name="danced-restore-check-$(date -u +%Y%m%d%H%M%S)-$$"
restore_database="danced_restore"
restore_password="$(openssl rand -hex 24)"

cleanup() {
  docker rm -f "$container_name" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

echo "Starting isolated restore target ($mysql_image)"
docker run --detach --name "$container_name" \
  --env MYSQL_ROOT_PASSWORD="$restore_password" \
  --env MYSQL_DATABASE="$restore_database" \
  "$mysql_image" >/dev/null

ready=false
for _ in $(seq 1 60); do
  if docker exec "$container_name" mysqladmin ping \
    --host=127.0.0.1 --user=root --password="$restore_password" --silent; then
    ready=true
    break
  fi
  sleep 2
done

if [[ "$ready" != true ]]; then
  echo "ERROR: isolated MySQL did not become ready" >&2
  docker logs "$container_name" >&2
  exit 1
fi

echo "Restoring $(basename "$backup_file") into isolated MySQL"
gzip -dc "$backup_file" | docker exec -i "$container_name" \
  mysql --user=root --password="$restore_password" "$restore_database"

table_count="$(docker exec "$container_name" mysql \
  --batch --skip-column-names --user=root --password="$restore_password" \
  --execute="SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$restore_database';")"

if [[ ! "$table_count" =~ ^[0-9]+$ || "$table_count" -eq 0 ]]; then
  echo "ERROR: restore completed without any tables" >&2
  exit 1
fi

docker exec "$container_name" mysqlcheck \
  --user=root --password="$restore_password" "$restore_database" >/dev/null

echo "Restore verification passed: $table_count tables checked in an isolated container"

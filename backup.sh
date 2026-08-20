#!/usr/bin/env bash
set -euo pipefail

# Database dumps can contain user data. Apply a private creation mask before
# creating either the backup directory or the dump itself.
umask 077

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$repo_dir"

if [[ ! -f .env ]]; then
  echo "ERROR: $repo_dir/.env does not exist" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_dir="${BACKUP_DIR:-$repo_dir/backups}"
backup_file="$backup_dir/danced-$timestamp.sql.gz"
mkdir -p "$backup_dir"

echo "Creating $backup_file"
if ! docker compose exec -T db sh -c \
  'MYSQL_PWD="$MYSQL_PASSWORD" exec mysqldump --single-transaction --routines --triggers --no-tablespaces --set-gtid-purged=OFF -u"$MYSQL_USER" "$MYSQL_DATABASE"' \
  | gzip -9 > "$backup_file"; then
  echo "ERROR: database dump failed" >&2
  rm -f "$backup_file"
  exit 1
fi

gzip -t "$backup_file"
chmod 0600 "$backup_file"

if [[ -n "${BACKUP_BUCKET:-}" ]]; then
  destination="${BACKUP_BUCKET%/}/$(basename "$backup_file")"
  echo "Uploading $backup_file to $destination"
  aws s3 cp "$backup_file" "$destination" --region "${AWS_REGION:?AWS_REGION must be set when BACKUP_BUCKET is set}"
else
  echo "BACKUP_BUCKET is empty; verified local dump retained at $backup_file"
fi

echo "Backup completed: $backup_file"

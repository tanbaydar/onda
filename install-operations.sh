#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
logs_dir="$repo_dir/logs"
lock_dir="/var/lock/danced"

health_entry="*/5 * * * * /usr/bin/flock -n $lock_dir/healthcheck.lock $repo_dir/production-healthcheck.sh >> $logs_dir/healthcheck.log 2>&1"
restore_entry="30 4 1 * * /usr/bin/flock -n $lock_dir/restore-check.lock $repo_dir/verify-backup.sh >> $logs_dir/restore-check.log 2>&1"

mkdir -p "$logs_dir"
sudo install -d -o "$(id -un)" -g "$(id -gn)" "$lock_dir"

current_crontab="$(mktemp)"
updated_crontab="$(mktemp)"
logrotate_config="$(mktemp)"
cleanup() {
  rm -f "$current_crontab" "$updated_crontab" "$logrotate_config"
}
trap cleanup EXIT INT TERM

crontab -l >"$current_crontab" 2>/dev/null || true
cp "$current_crontab" "$updated_crontab"

for entry in "$health_entry" "$restore_entry"; do
  if ! grep -Fqx "$entry" "$updated_crontab"; then
    printf '%s\n' "$entry" >>"$updated_crontab"
  fi
done

crontab "$updated_crontab"

sed "s|__LOGS_DIR__|$logs_dir|g; s|__LOG_OWNER__|$(id -un)|g; s|__LOG_GROUP__|$(id -gn)|g" \
  "$repo_dir/ops/danced.logrotate" >"$logrotate_config"
sudo install -m 0644 "$logrotate_config" /etc/logrotate.d/danced
sudo logrotate --debug /etc/logrotate.d/danced >/dev/null

echo "Installed health and restore schedules without replacing existing cron entries."
echo "Installed host log rotation at /etc/logrotate.d/danced."

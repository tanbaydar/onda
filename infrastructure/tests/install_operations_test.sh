#!/usr/bin/env bash
set -euo pipefail

test_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$test_dir/../.." && pwd)"
# The installer writes its own absolute paths into each schedule. Take the
# fixture path in the form that "pwd" gives, so the expected lines can match.
fixture_dir="$(cd "$(mktemp -d)" && pwd)"
trap 'rm -rf "$fixture_dir"' EXIT INT TERM

mkdir -p "$fixture_dir/infrastructure/scripts" "$fixture_dir/infrastructure/operations" \
  "$fixture_dir/bin"
cp "$repo_dir/infrastructure/scripts/install-operations.sh" \
  "$fixture_dir/infrastructure/scripts/install-operations.sh"
cp "$repo_dir/infrastructure/operations/onda.logrotate" \
  "$fixture_dir/infrastructure/operations/onda.logrotate"
cp "$test_dir/fixtures/bin/crontab" "$fixture_dir/bin/crontab"
cp "$test_dir/fixtures/bin/sudo" "$fixture_dir/bin/sudo"
chmod +x "$fixture_dir/infrastructure/scripts/"*.sh "$fixture_dir/bin/"*

export PATH="$fixture_dir/bin:$PATH"
export ONDA_TEST_LOG="$fixture_dir/commands.log"
export ONDA_TEST_CRONTAB="$fixture_dir/crontab"

scripts="$fixture_dir/infrastructure/scripts"
logs="$fixture_dir/logs"
locks="/var/lock/onda"

health_entry="*/5 * * * * /usr/bin/flock -n $locks/healthcheck.lock $scripts/production-healthcheck.sh >> $logs/healthcheck.log 2>&1"
restore_entry="30 4 1 * * /usr/bin/flock -n $locks/restore-check.lock $scripts/verify-backup.sh >> $logs/restore-check.log 2>&1"
# Lines that the host owner wrote. The installer must not change them.
mail_setting='MAILTO=""'
other_entry="0 6 * * 1 /usr/local/bin/weekly-report"

run_install() {
  : >"$ONDA_TEST_LOG"
  set +e
  install_output="$("$scripts/install-operations.sh" 2>&1)"
  install_status=$?
  set -e
}

require_status() {
  local expected="$1"
  if [[ "$install_status" -ne "$expected" ]]; then
    echo "Expected status $expected, received $install_status" >&2
    printf '%s\n' "$install_output" >&2
    exit 1
  fi
}

write_crontab() {
  printf '%s\n' "$@" >"$ONDA_TEST_CRONTAB"
}

# The table must have these lines in this sequence, and no other line.
require_crontab() {
  if ! diff -u <(printf '%s\n' "$@") "$ONDA_TEST_CRONTAB" >&2; then
    echo "The crontab is not the expected table" >&2
    exit 1
  fi
}

require_log_line() {
  local expected="$1"
  if ! grep -Fqx "$expected" "$ONDA_TEST_LOG"; then
    echo "Missing command log line: $expected" >&2
    cat "$ONDA_TEST_LOG" >&2
    exit 1
  fi
}

# A new host has no table. The installer adds each schedule, and it creates
# the two directories that the schedules write to.
rm -f "$ONDA_TEST_CRONTAB"
run_install
require_status 0
require_crontab "$health_entry" "$restore_entry"
if [[ ! -d "$logs" ]]; then
  echo "Missing logs directory: $logs" >&2
  exit 1
fi
require_log_line "sudo install -d -o $(id -un) -g $(id -gn) $locks"
require_log_line "sudo logrotate --debug /etc/logrotate.d/onda"

# A second run changes nothing.
run_install
require_status 0
require_crontab "$health_entry" "$restore_entry"

# A host that has each schedule among its own lines stays as it is.
write_crontab "$mail_setting" "$restore_entry" "$other_entry" "$health_entry"
run_install
require_status 0
require_crontab "$mail_setting" "$restore_entry" "$other_entry" "$health_entry"

# A host that has one schedule gets only the other one, after its own lines.
write_crontab "$other_entry" "$restore_entry"
run_install
require_status 0
require_crontab "$other_entry" "$restore_entry" "$health_entry"

echo "Schedule installation tests passed"

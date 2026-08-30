#!/usr/bin/env bash
set -euo pipefail

test_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$test_dir/../.." && pwd)"
fixture_dir="$(mktemp -d)"
trap 'rm -rf "$fixture_dir"' EXIT INT TERM

mkdir -p "$fixture_dir/infrastructure/scripts" "$fixture_dir/bin"
cp "$repo_dir/infrastructure/scripts/deploy.sh" "$fixture_dir/infrastructure/scripts/deploy.sh"
cp "$test_dir/fixtures/scripts/backup.sh" "$fixture_dir/infrastructure/scripts/backup.sh"
cp "$test_dir/fixtures/scripts/production-healthcheck.sh" \
  "$fixture_dir/infrastructure/scripts/production-healthcheck.sh"
cp "$test_dir/fixtures/bin/git" "$fixture_dir/bin/git"
cp "$test_dir/fixtures/bin/docker" "$fixture_dir/bin/docker"
chmod +x "$fixture_dir/infrastructure/scripts/"*.sh "$fixture_dir/bin/"*

export PATH="$fixture_dir/bin:$PATH"
export ONDA_TEST_LOG="$fixture_dir/commands.log"

run_deploy() {
  : >"$ONDA_TEST_LOG"
  set +e
  deploy_output="$("$fixture_dir/infrastructure/scripts/deploy.sh" "$@" 2>&1)"
  deploy_status=$?
  set -e
}

require_status() {
  local expected="$1"
  if [[ "$deploy_status" -ne "$expected" ]]; then
    echo "Expected status $expected, received $deploy_status" >&2
    printf '%s\n' "$deploy_output" >&2
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

reject_log_line() {
  local rejected="$1"
  if grep -Fqx "$rejected" "$ONDA_TEST_LOG"; then
    echo "Unexpected command log line: $rejected" >&2
    cat "$ONDA_TEST_LOG" >&2
    exit 1
  fi
}

tested_revision="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
newer_revision="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

export ONDA_TEST_REMOTE_SHA="$tested_revision"
run_deploy invalid-revision
require_status 2
[[ "$deploy_output" == *"must be a full lowercase 40-character commit SHA"* ]]
[[ ! -s "$ONDA_TEST_LOG" ]]

export ONDA_TEST_REMOTE_SHA="$newer_revision"
run_deploy "$tested_revision"
require_status 0
[[ "$deploy_output" == *"Skipping stale deployment request"* ]]
require_log_line "git fetch --prune origin +refs/heads/main:refs/remotes/origin/main"
reject_log_line "backup"
reject_log_line "git merge --ff-only $tested_revision"

export ONDA_TEST_REMOTE_SHA="$tested_revision"
run_deploy "$tested_revision"
require_status 0
require_log_line "backup"
require_log_line "git merge --ff-only $tested_revision"
reject_log_line "git pull --ff-only"
require_log_line "docker compose build"
require_log_line "healthcheck"

run_deploy
require_status 0
require_log_line "backup"
require_log_line "git pull --ff-only"
reject_log_line "git fetch --prune origin +refs/heads/main:refs/remotes/origin/main"

echo "Guarded deployment tests passed"

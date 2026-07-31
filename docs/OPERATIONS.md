# Danced ingestion operations

## Nightly synchronization

Run the production nightly planner with no window arguments:

```sh
cd /path/to/danced_app
.venv/bin/python manage.py sync_ra
```

The bare command fetches both active seeds from the current date through 30 days
ahead. `--window-start` and `--window-end` override that planner for a supervised
manual run; `--backfill` marks a bounded historical execution and never changes the
window by itself.

Requests are sequential, with a fixed 1.5-second delay between pages. Retry attempts
share the same 1,000-attempt ceiling as ordinary page requests.

## Operator alarm

The command logs at `ERROR` level, writes a clear diagnostic to stderr, and exits
nonzero when:

- the run crashes;
- one or more seeds fail; or
- the run completes with zero admitted event observations.

This project deliberately has no email or external alerting dependency. Cron can mail
the command's nonzero stderr output when local mail delivery is configured. A launchd
job records the same signal in its configured stderr log.

## Cron example

Tan installs the schedule manually. This example runs every day at 03:15 in the
machine's local timezone:

```cron
15 3 * * * cd /path/to/danced_app && .venv/bin/python manage.py sync_ra
```

Do not redirect stderr to `/dev/null`; doing so discards the operator alarm. Cron mail
also requires a functioning local mail transport, which should be verified on the
host after installation.

## macOS launchd example

Save the following as
`~/Library/LaunchAgents/com.danced.sync-ra.plist`, replacing every `/path/to` value
with an absolute local path. Create the log directory before loading the job.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.danced.sync-ra</string>

  <key>ProgramArguments</key>
  <array>
    <string>/path/to/danced_app/.venv/bin/python</string>
    <string>/path/to/danced_app/manage.py</string>
    <string>sync_ra</string>
  </array>

  <key>WorkingDirectory</key>
  <string>/path/to/danced_app</string>

  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>3</integer>
    <key>Minute</key>
    <integer>15</integer>
  </dict>

  <key>StandardOutPath</key>
  <string>/path/to/danced_app/logs/sync-ra.out.log</string>
  <key>StandardErrorPath</key>
  <string>/path/to/danced_app/logs/sync-ra.err.log</string>
</dict>
</plist>
```

Load or reload it manually after reviewing the resolved paths:

```sh
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.danced.sync-ra.plist
```

## Manual bounded sync

Use explicit dates for supervised investigation:

```sh
.venv/bin/python manage.py sync_ra \
  --window-start 2026-07-31 \
  --window-end 2026-08-07 \
  --page-size 20
```

Use `--backfill` only for a deliberately approved historical window:

```sh
.venv/bin/python manage.py sync_ra --backfill \
  --window-start YYYY-MM-DD \
  --window-end YYYY-MM-DD \
  --page-size 20
```

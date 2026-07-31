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

## Local guest frontend

The guest React shell runs through Vite and proxies `/api` requests to Django.
Run the backend and frontend in two terminals from the repository.

Terminal 1:

```sh
cd /path/to/danced_app
.venv/bin/python manage.py runserver
```

Terminal 2:

```sh
cd /path/to/danced_app/frontend
npm install
npm run dev
```

Open the local URL printed by Vite. The proxy target is
`http://127.0.0.1:8000`, so Django must use its default local address and port.
No Django CORS configuration is needed for this development workflow. In debug
mode Django explicitly trusts the two documented Vite origins,
`http://127.0.0.1:5173` and `http://localhost:5173`, for CSRF origin checking.
This is a development-only convenience; a deployed same-origin frontend must not
need a trusted-origin exception for its own requests.

When verifying an unsafe browser request such as registration, login, logout, or a
Been mutation outside the browser, include the browser-equivalent `Origin` header.
A cookie-and-CSRF-header check without `Origin` does not exercise Django's origin
validation and can pass while every real browser request receives a 403.

Create a production frontend bundle with:

```sh
cd /path/to/danced_app/frontend
npm run build
```

## Favorite-cap browser click-through

For event and artist favorites, verify the business-rule rejection through the
browser rather than only calling the API:

1. Sign in with a disposable account and add three favorites of the same type.
2. Open a fourth detail page and select **Add favorite**.
3. Confirm the control remains unselected and its field-keyed three-favorite limit
   message appears beside the control; the page must not silently refetch it away.
4. Remove an existing favorite, retry the fourth, and confirm it becomes selected.
5. Remove it again and confirm the control returns to **Add favorite** without an
   error. Repeat for both event and artist favorites.

## Standing local product-test data

The local development database includes the public account
`review.public.test`, created for the Phase C written-review browser pipeline. It is
standing test data, not disposable cleanup. Its public Been entry and review may be
used to verify guest review visibility and signed-in review controls. Do not use or
alter the founder's `tan` account when a public review fixture is needed, and do not
place test-account credentials in the repository.

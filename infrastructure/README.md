[Onda](../README.md) / [Documentation](../docs/README.md) / Operations

# Operations: deploy, back up, restore

> **For** the person who operates the production host. **Use** the procedures when you do a task.

Onda runs on one host with Docker Compose.
One GitHub Actions workflow tests each change and deploys the commit that passed all checks.

## In brief

- A push to `main` starts 5 checks. A deploy starts only if all 5 pass.
- The host deploys the exact commit that the checks tested.
- The deploy script makes a backup before it changes the database.
- A health check must pass after each deploy. A schedule repeats it each 5 minutes.
- A monthly job restores a backup into an empty database to prove that the backup is good.

## What runs where

![One host runs Caddy, Django and MySQL in containers. Host schedules start the nightly sync, the daily backup and a health probe. GitHub Actions deploys the commit that passed all checks.](../docs/assets/figures/deployment.svg)

| Part | Details |
|---|---|
| `caddy` | The only public container. Ports 80 and 443. TLS, static files, security headers, a 3 MB limit for an API body |
| `web` | Django with Gunicorn, 2 workers. It is not public |
| `db` | MySQL 8.4 on an internal network. No published port |
| Volumes | `mysql_data`, `media_data`, `django_static`, `caddy_data`, `caddy_config` |

Each service container has a read-only file system, a user that is not root, and no capability that it does not use.
Each image and each CI action uses a fixed digest.

## The delivery pipeline

![A push to main starts 5 checks. If one check fails, there is no deploy. If all pass, a job on the production runner starts the deploy script through SSH. The script makes a backup, builds, migrates and does a health check. If the health check fails, the job fails and the backup stays.](../docs/assets/figures/delivery-pipeline.svg)

| Check | What it does |
|---|---|
| `backend` | Django tests on MySQL, and the production settings check |
| `frontend` | Tests, production build, `npm audit` |
| `security` | Bandit on the source, pip-audit on the packages |
| `container-security` | Trivy on the repository and on the three production images |
| `delivery-safety` | ShellCheck, a test of the deploy script, a test of the schedule installer, and a check of the Compose file |

- A pull request and a manual run do the checks. They do not deploy.
- Deploys go one at a time. A new push does not cancel a deploy in the middle.
- The production job runs on the runner `onda-production`. Its account cannot read the `.env` file and cannot use Docker.
- The job connects through SSH on the loopback interface. The SSH key can run the deploy command only.

## What the deploy script does

[`scripts/deploy.sh`](scripts/deploy.sh) does these steps in sequence. A failure stops the script.

1. It refuses a checkout that has local changes.
2. It gets `origin/main`. If a newer commit is there, it skips this request.
3. It makes a backup and tests the compressed file.
4. It moves the checkout to the tested commit with a fast-forward.
5. It builds the images.
6. It runs the production settings check and applies the migrations.
7. It starts all containers.
8. It runs the health check a maximum of 12 times, with 5 seconds between.

## Procedures

### How to deploy by hand

Use this procedure only if the workflow is not available.

1. Log in to the host with the deploy account.
2. Go to the production checkout.
3. Make sure that the checkout has no local changes.

   ```bash
   git status --short
   ```

4. Run the deploy script with no argument.

   ```bash
   ./infrastructure/scripts/deploy.sh
   ```

5. Make sure that the last line of the output is the health check result.

### How to make a backup

1. Go to the production checkout.
2. Run the backup script.

   ```bash
   ./infrastructure/scripts/backup.sh
   ```

3. Make sure that the output ends with `Backup completed`.

The script makes a dump in one transaction, so writes continue during the backup.
It compresses the file, tests the compressed file, and sets the file mode to `0600`.
If `BACKUP_BUCKET` is set, it uploads the file to S3 with server-side encryption.

### How to prove that a backup is good

1. Go to the production checkout.
2. Run the script with no argument to test the newest backup.

   ```bash
   ./infrastructure/scripts/verify-backup.sh
   ```

3. Make sure that the output ends with `Restore verification passed`.

The script starts an empty MySQL container with no network link to production.
It restores the backup, counts the tables, and runs `CHECK TABLE` on each table.
Then it removes the container.

### How to run the health check

```bash
./infrastructure/scripts/production-healthcheck.sh
```

The check passes only if all of these are true:

- The containers `db`, `web` and `caddy` run.
- `https://<domain>/api/cities/` returns a success status in less than 30 seconds.
- The response has the six security headers: `Cache-Control: no-store`, a content security policy, HSTS for one year, `nosniff`, `X-Frame-Options: DENY` and `X-Robots-Tag: noindex`.

### How to run the nightly sync by hand

```bash
docker compose exec -T web python manage.py sync_ra
```

| Exit code | Meaning |
|---|---|
| 0 | The run is complete |
| 1 | A seed failed, or the run admitted no listing. Read the output |
| 2 | A different run has the lock. Do nothing |

### How to install the schedules

```bash
./infrastructure/scripts/install-operations.sh
```

The script adds two schedules and does not change other schedules:

| Schedule | Time | Log |
|---|---|---|
| Health check | Each 5 minutes | `logs/healthcheck.log` |
| Restore test | 04:30 on day 1 of each month | `logs/restore-check.log` |

It also installs a log rotation of 14 days.

> [!NOTE]
> The schedules for the nightly sync and for the daily backup are on the production host.
> The script does not install these two schedules.

## How to recover

| Problem | Action |
|---|---|
| The health check fails after a deploy | The deploy job fails. Revert the change on `main`. The revert goes through the same checks and deploys |
| A migration damaged data | Restore the backup that the deploy made. Do this only after a review of the migration and of the data |
| The host is lost | Start a new host. Install Docker. Restore the newest backup from S3. Run the deploy script |

An automatic rollback to an older commit is not available, on purpose.
A migration is not always reversible, so an older commit can meet a newer schema.

## One-time configuration in GitHub

Create a GitHub Actions environment with the name `production`.

| Variable | Value |
|---|---|
| `ONDA_DEPLOY_HOST` | The SSH host that the runner can get to. `127.0.0.1` for one host |
| `ONDA_DEPLOY_PORT` | The SSH port. The default is `22` |
| `ONDA_DEPLOY_USER` | The deploy account |
| `ONDA_DEPLOY_PATH` | The absolute path of the production checkout |
| `ONDA_PRODUCTION_URL` | The public HTTPS URL for the deployment record |

| Secret | Value |
|---|---|
| `ONDA_DEPLOY_SSH_PRIVATE_KEY` | The private key of the deploy account |
| `ONDA_DEPLOY_SSH_KNOWN_HOSTS` | A `known_hosts` line for the host and the port |

> [!WARNING]
> Get the host key through a second channel before you save it.
> A key from `ssh-keyscan` alone can be the key of an attacker.

- The deploy account owns the checkout. It has the Docker, GitHub and AWS permissions that the scripts use.
- The application secrets stay in the `.env` file on the host. They are not in GitHub.
- Protect `main` with the five checks before you start to use the deploy job.
- To get a manual approval before each deploy, add a reviewer to the `production` environment.

## Evidence

- On 2026-11-27 the public API answered on HTTPS with all six security headers.
- On 2026-08-20 eight nightly runs in sequence and eight daily backups were complete. The backups were in a private S3 bucket with encryption and a 30-day expiry.
- The first scheduled restore test was not complete on 2026-08-20.

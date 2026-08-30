# Production delivery

Onda uses one GitHub Actions workflow for continuous integration and guarded
continuous deployment to the existing single-host Docker Compose environment.

## Pipeline

Pull requests and pushes to `main` run the `CI/CD` workflow. It verifies the Django
suite against MySQL, the frontend tests and production build, dependency and
source security scans, all production images, deployment shell behavior, and the
resolved Compose configuration.

The production job is eligible to run only after every check succeeds for a push
to `main`, or after those same checks pass in an operator-started run.
Production deployments are serialized and never canceled while in progress. The
workflow connects with a dedicated SSH key, verifies the server host key, and
asks the host to deploy the exact commit verified by that workflow run.

The host-side deployment keeps the existing safety sequence:

1. refuse a dirty production checkout;
2. reject a stale automation event if a newer commit is already at
   `origin/main`;
3. create and verify the required pre-deploy database backup;
4. fast-forward to the exact tested commit;
5. rebuild the images, check production settings, and apply migrations;
6. start the full Compose project and require the public production health
   check to pass.

Manual host deployments remain available by running
`infrastructure/scripts/deploy.sh` without a commit argument.

## One-time GitHub configuration

Create a GitHub Actions environment named `production`. Add these environment
variables:

| Name | Value |
|---|---|
| `ONDA_DEPLOY_HOST` | Production DNS name or IPv4 address, without a scheme |
| `ONDA_DEPLOY_PORT` | SSH port; omit it to use `22` |
| `ONDA_DEPLOY_USER` | Dedicated production deployment account |
| `ONDA_DEPLOY_PATH` | Absolute path to the production checkout |
| `ONDA_PRODUCTION_URL` | Public HTTPS URL shown in GitHub deployment records |

Add these environment secrets:

| Name | Value |
|---|---|
| `ONDA_DEPLOY_SSH_PRIVATE_KEY` | Private key for the dedicated deployment account |
| `ONDA_DEPLOY_SSH_KNOWN_HOSTS` | Pre-verified OpenSSH `known_hosts` entry for the configured host and port |

Verify the host key through an independent channel before saving it. Do not use
an unverified `ssh-keyscan` result as the trust decision. The deployment account
must own the clean production checkout and already have the Docker, GitHub, and
AWS permissions used by `deploy.sh` and `backup.sh`; production application
secrets remain only in the host's `.env` file.

Environment protection rules can require an operator approval when continuous
delivery is preferred over automatic deployment. For automatic deployment, keep
the environment unreviewed. In either mode, protect `main` with the five CI job
checks (`backend`, `frontend`, `security`, `container-security`, and
`delivery-safety`) before enabling CD.

## Recovery

Failed health checks fail the deployment and preserve the pre-deploy backup for
operator recovery. Because database migrations may not be reversible, rollback
is deliberately not an automated checkout of an older commit. Revert the faulty
change on `main`, let CI verify the revert, and deploy that new commit; use the
documented backup restore procedure only when the migration and data impact have
been reviewed.

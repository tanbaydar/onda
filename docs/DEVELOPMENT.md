[Onda](../README.md) / [Documentation](README.md) / Development

# Development: run, test, change

> **For** engineers who run the code or change it. **Time** 15 minutes to a local server.

## In brief

- Python 3.12, Node 22 and MySQL 8 are necessary.
- The backend reads its settings from environment variables.
- The command `migrate` creates the two cities. It creates no events.
- Four checks must pass before a change goes to `main`: backend tests, frontend tests, the frontend build, and the docs check.

## Repository layout

```text
backend/
  config/        settings, routes, the list of sources
  ingestion/     the nightly path: client, runner, transformer, reconciler
  catalog/       catalog models, read views, search
  users/         accounts, services, the Home query, product views
frontend/        the React app (Vite)
infrastructure/  Caddy, Dockerfiles, deploy, backup and health scripts
benchmarks/      the Home feed benchmark
docs/            these pages, the figures and the tools that check them
compose.yaml     the three production containers
```

## How to run the backend

I tested the commands on Ubuntu 24.04 with Python 3.13 and MySQL 8.0. CI uses Python 3.12 and MySQL 8.4.

1. Create a database.

   ```bash
   mysql -uroot -p -e "CREATE DATABASE onda CHARACTER SET utf8mb4;"
   ```

2. Create a virtual environment and install the packages.

   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r backend/requirements.txt
   ```

3. Set the environment variables.

   ```bash
   export DJANGO_SECRET_KEY=<50 characters or more>
   export DJANGO_DEBUG=true
   export ONDA_DB_NAME=onda ONDA_DB_USER=<user> ONDA_DB_PASSWORD=<password>
   ```

4. Apply the migrations.

   ```bash
   .venv/bin/python backend/manage.py migrate
   ```

5. Start the server.

   ```bash
   .venv/bin/python backend/manage.py runserver 127.0.0.1:8000
   ```

6. Make sure that the server answers. The response has the two cities.

   ```bash
   curl http://127.0.0.1:8000/api/cities/
   ```

| Variable | Necessary | Default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Yes. Without it, each command stops | None |
| `DJANGO_DEBUG` | `true` for `runserver` | `false` |
| `ONDA_DB_NAME`, `ONDA_DB_USER`, `ONDA_DB_PASSWORD` | No | `onda`, `root`, empty |
| `ONDA_DB_HOST`, `ONDA_DB_PORT` | No | `127.0.0.1`, `3306` |
| `EMAIL_VERIFICATION_ENFORCED` | No | `false` in development, `true` in production |

- A file with the name `.env` in the repository root can contain the same names. Git ignores that file.
- Django connects through TCP with a password. If the `root` account of MySQL has no password, create a second account.
- In development, email goes to the terminal. A verification code shows there.
- The page `/admin/` is available only when `DJANGO_DEBUG` is `true`.

## How to run the frontend

1. Install the packages.

   ```bash
   cd frontend && npm ci
   ```

2. Start the development server.

   ```bash
   npm run dev
   ```

3. Open `http://localhost:5173`. The server sends `/api` and `/media` to `127.0.0.1:8000`.

## How to get events into a local catalog

A new database has no events.

1. Create an admin account.

   ```bash
   .venv/bin/python backend/manage.py createsuperuser
   ```

2. Open `http://127.0.0.1:8000/admin/`.
3. Add a venue, an artist and an event.
4. Add one lineup row that connects the artist to the event.

> [!CAUTION]
> Do not run `manage.py sync_ra` again and again on a local machine.
> Each run sends real requests to a website that Onda does not own.

## How to run the checks

| Check | Directory | Command | Result on 2026-11-27 |
|---|---|---|---|
| Backend tests | `backend/` | `python manage.py test` | 278 tests pass |
| Frontend tests | `frontend/` | `npm test` | 158 tests pass |
| Frontend build | `frontend/` | `npm run build` | 95 modules |
| Docs | Root | `python3 docs/tools/check_docs.py` | 0 errors |
| Deploy script | Root | `infrastructure/tests/deploy_test.sh` | Runs in CI |

- The backend tests create the database `test_<name>`. The MySQL account must have the permission to create it.
- CI runs the same commands. It adds Bandit, pip-audit, `npm audit`, Trivy scans and a production settings check.

## Where code goes

| You add | Put it in | Rule |
|---|---|---|
| A route | `urls.py` and a view | The view validates the shape, calls one service function, and maps a conflict to `409` |
| A change of state | `users/services.py` | One function with `@transaction.atomic`. Take the lock first. Raise a named exception for a conflict |
| A rule that one row can prove | A constraint in `models.py`, and a migration | Give the constraint a name that starts with `ck_` or `uq_` |
| A read that changes with the viewer | A queryset method, for example `visible_to` | Do not write a privacy filter in a view |
| A relation that a user owns | A migration that sets `ON DELETE CASCADE` | Add a test that deletes with direct SQL |

## How to add a route

1. Write a test for each status code in `backend/users/tests/`.
2. Add the service function if the route changes state.
3. Add the view. Use `_authentication_required` if the route must have a session.
4. Add the path to `been_urls.py`.
5. Run the backend tests.
6. Add the route to [`API.md`](API.md).

## How to change the schema

1. Change the model.
2. Create the migration.

   ```bash
   python backend/manage.py makemigrations
   ```

3. Add a migration for the delete action if a user owns the new rows. Use `users/migrations/0004_enforce_diary_user_cascade.py` as the pattern.
4. Add a test that proves the constraint with a direct write to the database.
5. Update [`DATABASE.md`](DATABASE.md).

## How to change these pages

1. Read the [writing standard](STYLE.md).
2. Change the page.
3. Run the docs check, and correct each error.

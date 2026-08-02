# Danced

Danced is **Letterboxd for the dancefloor**: a social event diary for discovering dance music events, marking plans, recording attendance and ratings, writing reviews, and following the taste of people you trust. It combines a city-led event ledger with public or private profiles, social activity, favorites, and venue-local event state.

## Stack

- **Backend:** Python, Django 6, MySQL
- **Frontend:** React 19, React Router, Vite, hand-authored CSS
- **Data:** Resident Advisor public event listings through a bounded, rate-disciplined GraphQL ingestion adapter
- **Media:** Django local media storage with validated, server-processed avatar uploads
- **Testing:** Django test suite and Node's built-in test runner

## Architecture

Danced is a modular monolith. Django owns authentication, privacy boundaries, product invariants, ingestion, and JSON APIs; the React application consumes those APIs through Vite's local proxy. Domain code is separated into `catalog`, `users`, and `ingestion` modules rather than split into premature services.

The ingestion pipeline fetches public RA listing pages sequentially, archives observations, normalizes source records, reconciles stable entities, and admits events into the product catalog. Request budgets, retry behavior, provenance, and operator-visible failures are explicit.

Frontend work follows a markdown-only design-handoff workflow. Product laws and tokens live in `frontend/DESIGN_BRIEF.md` and `frontend/design-tokens.css`; ratified surface specifications live in `frontend/design-handoffs/`. The implementation uses self-hosted fonts, shared primitives, and scoped responsive CSS without a framework.

## Local setup

Prerequisites: Python 3.12+, Node.js 22+, and a running MySQL 8 server.

1. Create the database:

   ```sql
   CREATE DATABASE danced CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. Create the Python environment and install dependencies:

   ```sh
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

3. Configure local environment variables:

   ```sh
   cp .env.example .env
   ```

   Replace `DJANGO_SECRET_KEY` and adjust the `DANCED_DB_*` values for your MySQL installation. Keep `EMAIL_VERIFICATION_ENFORCED=false` for the current local demo behavior.

4. Prepare Django:

   ```sh
   .venv/bin/python manage.py migrate
   .venv/bin/python manage.py runserver 127.0.0.1:8000
   ```

5. In a second terminal, start the frontend:

   ```sh
   cd frontend
   npm install
   npm run dev -- --host 127.0.0.1
   ```

6. Open [http://127.0.0.1:5173](http://127.0.0.1:5173).

Run verification with:

```sh
.venv/bin/python manage.py test
cd frontend && npm test && npm run build
```

The ingestion command is intentionally operator-driven. See `docs/OPERATIONS.md` before running `manage.py sync_ra`.

## Status

**Milestone 4 is complete.** The product system, responsive design integration, primary social surfaces, artwork pipeline, and verification prerequisites are implemented and tested. Danced is currently a gated demo: email-verification enforcement remains disabled until the deployment email backend and launch flow are explicitly enabled.

No license is granted at this time; all rights are reserved.

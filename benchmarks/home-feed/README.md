# Home feed benchmark

This directory measures the response time of `GET /api/me/home/` on a seeded database.
[`docs/HOME_FEED.md`](../../docs/HOME_FEED.md) explains the query and the results.

## Records

| File | Query | Machine |
|---|---|---|
| [`results.yaml`](results.yaml) | Six branches, an earlier version (2026-08-17) | Apple M4 Pro, MySQL 9.6 |
| [`results-2026-11-27.yaml`](results-2026-11-27.yaml) | Five branches, the current version | Cloud machine, 4 virtual CPUs, MySQL 8.0.46 |

## How to run the benchmark

The script refuses a database name that does not contain `benchmark`.
It also refuses a database that contains application data.

1. Create an empty database and an account that is not `root`.

   ```bash
   mysql -uroot -p -e "CREATE DATABASE onda_feed_benchmark CHARACTER SET utf8mb4;
     CREATE USER 'onda_bench'@'localhost' IDENTIFIED BY '<16 characters or more>';
     GRANT ALL ON onda_feed_benchmark.* TO 'onda_bench'@'localhost';"
   ```

2. Set the production settings for a local run.

   ```bash
   export DJANGO_SETTINGS_MODULE=config.settings_production
   export DJANGO_SECRET_KEY=<50 characters or more>
   export ONDA_DOMAIN=bench.example.com
   export ONDA_DB_HOST=127.0.0.1 ONDA_DB_NAME=onda_feed_benchmark
   export ONDA_DB_USER=onda_bench ONDA_DB_PASSWORD=<the password>
   export DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   export DJANGO_DEFAULT_FROM_EMAIL=noreply@example.com DJANGO_EMAIL_HOST=smtp.example.com
   export DJANGO_EMAIL_HOST_USER=bench DJANGO_EMAIL_HOST_PASSWORD=bench DJANGO_EMAIL_USE_TLS=true
   ```

3. Apply the migrations.

   ```bash
   python backend/manage.py migrate --noinput
   ```

4. Seed 100,000 rows.

   ```bash
   python benchmarks/home-feed/benchmark.py seed
   ```

5. Run the measurement three times, and record the median.

   ```bash
   python benchmarks/home-feed/benchmark.py benchmark
   ```

A run that starts immediately after the seed can be much slower.
Do not use that run.

## What the benchmark measures

- 220 requests for page 1 and 220 requests for page 50. The script discards the first 20 of each.
- The p95 of the other 200, with the nearest-rank method.
- The requests go one at a time through the Django test client and the production middleware.

The benchmark does not measure the network, Gunicorn, or requests at the same time.
It is not a capacity test.

FROM python:3.14-alpine@sha256:05b2b8b732ecd268fee8727a369f936f022d1321b59befd13c30ede22769dcdc AS builder

WORKDIR /build

RUN apk upgrade --no-cache \
    && apk add --no-cache gcc mariadb-connector-c-dev musl-dev pkgconf

COPY backend/requirements.txt ./
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.14-alpine@sha256:05b2b8b732ecd268fee8727a369f936f022d1321b59befd13c30ede22769dcdc

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk upgrade --no-cache \
    && apk add --no-cache mariadb-connector-c tzdata \
    && addgroup -S -g 10001 onda \
    && adduser -S -D -H -u 10001 -G onda onda

COPY backend/requirements.txt ./
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

COPY --chown=onda:onda backend/ ./
RUN DJANGO_SECRET_KEY=collectstatic-build-only python manage.py collectstatic --noinput

RUN mkdir -p /app/media \
    && chown -R onda:onda /app

USER onda

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-"]

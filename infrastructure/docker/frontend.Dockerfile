FROM node:26-slim@sha256:4ebb5ace66f15a24c14c492e01a8beeed4fddf970a856109f5126e703e5fe503 AS frontend-build

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM golang:1.26.6-alpine@sha256:3889b425f035be855a72fb4755265311293b6d414521f0a519d819df32222d83 AS caddy-build

ENV GOTOOLCHAIN=local
WORKDIR /build

# Caddy 2.11.4 is the latest stable release. Rebuild that release with patched
# Go and networking modules until the official image incorporates the fixes.
RUN go mod init onda.local/caddy-build \
    && go get github.com/caddyserver/caddy/v2/cmd/caddy@v2.11.4 \
    && go get golang.org/x/net@v0.56.0 \
        golang.org/x/text@v0.39.0 \
        google.golang.org/grpc@v1.82.1 \
    && CGO_ENABLED=0 go build -trimpath \
        -ldflags="-s -w -X github.com/caddyserver/caddy/v2.CustomVersion=v2.11.4-onda.1" \
        -o /out/caddy github.com/caddyserver/caddy/v2/cmd/caddy

FROM caddy:2.11-alpine@sha256:5f5c8640aae01df9654968d946d8f1a56c497f1dd5c5cda4cf95ab7c14d58648

RUN apk upgrade --no-cache \
    && addgroup -S -g 10001 onda \
    && adduser -S -D -H -u 10001 -G onda onda \
    && chown -R onda:onda /config /data /srv

COPY --from=caddy-build /out/caddy /usr/bin/caddy
RUN setcap cap_net_bind_service=+ep /usr/bin/caddy \
    && caddy version

COPY infrastructure/caddy/Caddyfile /etc/caddy/Caddyfile
COPY --chown=onda:onda --from=frontend-build /frontend/dist /srv/frontend

USER onda

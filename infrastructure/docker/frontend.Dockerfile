FROM node:22-slim@sha256:d649c27dae7ba0137b3cef5dd75baa422c08dc3d9e3fc0c23dfb172dc3cc6436 AS frontend-build

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM golang:1.26.10-alpine@sha256:87c65a688975c0b1d4585d204874c45ca78354670e3a5f11368c5a492303d696 AS caddy-build

ENV GOTOOLCHAIN=local
WORKDIR /build

# Rebuild Caddy 2.11.4 with a patched Go release and patched modules.
# golang.org/x/net 0.62.0 also brings x/text 0.43.0 and x/crypto 0.58.0.
# Caddy 2.11.9 is newer. It answers a request body over the limit in a
# different way and it adds a Vary header, so that update needs its own review.
RUN go mod init onda.local/caddy-build \
    && go get github.com/caddyserver/caddy/v2/cmd/caddy@v2.11.4 \
    && go get golang.org/x/net@v0.62.0 \
        google.golang.org/grpc@v1.83.2 \
        github.com/klauspost/compress@v1.18.7 \
        github.com/go-jose/go-jose/v4@v4.1.6 \
    && CGO_ENABLED=0 go build -trimpath \
        -ldflags="-s -w -X github.com/caddyserver/caddy/v2.CustomVersion=v2.11.4-onda.2" \
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

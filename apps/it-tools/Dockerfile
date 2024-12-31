ARG VERSION
FROM node:lts-alpine AS build

ARG VERSION
ARG CHANNEL
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL internal.flatops.image.target_platform=$TARGETPLATFORM
LABEL internal.flatops.image.target_architecture=$TARGETARCH
LABEL internal.flatops.image.target_os=$TARGETOS
LABEL internal.flatops.image.forked_from="https://github.com/joryirving/containers"
LABEL org.opencontainers.image.source="https://github.com/CorentinTh/it-tools"

RUN \
  apk add --no-cache curl git jq \
  && git clone -b v$VERSION --single-branch https://github.com/CorentinTh/it-tools.git /app \
  && cd /app \
  && corepack enable  \
  && corepack prepare pnpm@latest --activate \
  && pnpm install --prefer-offline \
  && pnpm build

  FROM ghcr.io/jfroy/caddy-scratch:2.9.0
  COPY --chown=1000:1000 --from=build /app/dist/ /app
  CMD ["file-server", "--root", "/app", "--listen", ":8080"]

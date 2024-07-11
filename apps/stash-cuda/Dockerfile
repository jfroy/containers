FROM docker.io/library/alpine:3.20 as source

ARG TARGETPLATFORM
ARG VERSION
ARG CHANNEL

ENV UMASK="0002" \
    TZ="Etc/UTC"

USER root

RUN \
    apk add --no-cache curl git patch \
    && git clone --depth 1 --branch "v${VERSION}" https://github.com/stashapp/stash /src \
    && curl -sLO https://github.com/jellyfin/jellyfin-ffmpeg/releases/download/v6.0.1-7/jellyfin-ffmpeg6_6.0.1-7-jammy_amd64.deb
COPY ./apps/stash-cuda/jellyfin-cuda.patch /src/
WORKDIR /src
RUN patch -p1 < jellyfin-cuda.patch

# Frontend
FROM node:alpine as frontend
RUN apk add --no-cache make git
## cache node_modules separately
COPY --from=source /src/ui/v2.5/package.json /src/ui/v2.5/yarn.lock /stash/ui/v2.5/
COPY --from=source /src/Makefile /stash/
COPY --from=source /src/graphql /stash/graphql/
COPY --from=source /src/ui /stash/ui/
WORKDIR /stash
RUN make pre-ui
RUN make generate-ui
RUN BUILD_DATE=$(date +"%Y-%m-%d %H:%M:%S") STASH_VERSION=${VERSION} make ui

# Backend
FROM golang:1.22-bookworm as backend
RUN apt update && apt install -y build-essential golang
WORKDIR /stash
COPY --from=source /src/go* /src/*.go /src/Makefile /src/gqlgen.yml /src/.gqlgenc.yml /stash/
COPY --from=source /src/scripts /stash/scripts/
COPY --from=source /src/pkg /stash/pkg/
COPY --from=source /src/cmd /stash/cmd
COPY --from=source /src/internal /stash/internal
COPY --from=frontend /stash /stash/
RUN \
    make generate-backend \
    && make flags-release flags-pie stash

# Runtime
FROM nvidia/cuda:12.5.0-runtime-ubuntu22.04
ENV \
    DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    NVIDIA_DRIVER_CAPABILITIES=compute,video,utility \
    PATH="$PATH:/usr/lib/jellyfin-ffmpeg" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    STASH_CONFIG_FILE=/config/config.yml
COPY --from=backend /stash/stash /usr/bin/
COPY --from=source /jellyfin-ffmpeg6_6.0.1-7-jammy_amd64.deb /run/jellyfin-ffmpeg6_6.0.1-7-jammy_amd64.deb
COPY ./apps/stash-cuda/config.yaml /config/config.yaml
RUN \
    (dpkg -i /run/jellyfin-ffmpeg6_6.0.1-7-jammy_amd64.deb || true) \
    && apt-get update \
    && apt-get -y install --fix-broken \
    && apt-get -y install python3 python3-pip python-is-python3 \
    && rm -rf /var/lib/apt/lists/* /var/cache/* /run/jellyfin-ffmpeg6_6.0.1-7-jammy_amd64.deb \
    && pip install uv \
    && uv pip install --system stashapp-tools \
    && groupadd -g 1000 ubuntu \
    && useradd -g 1000 -u 1000 ubuntu \
    && touch /.dockerenv
EXPOSE 9999
ENTRYPOINT ["/usr/bin/stash"]

LABEL org.opencontainers.image.source="https://github.com/stashapp/stash"

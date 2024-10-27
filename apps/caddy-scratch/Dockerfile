ARG VERSION
FROM public.ecr.aws/docker/library/caddy:${VERSION}-builder AS build

ARG VERSION
ARG CHANNEL
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL internal.flatops.image.target_platform=$TARGETPLATFORM
LABEL internal.flatops.image.target_architecture=$TARGETARCH
LABEL internal.flatops.image.target_os=$TARGETOS
LABEL internal.flatops.image.forked_from="https://github.com/joryirving/containers"
LABEL org.opencontainers.image.source="https://github.com/caddyserver/caddy"

RUN \
  xcaddy build \
  && setcap -r /usr/bin/caddy
FROM scratch
COPY --chown=1000:1000 --chmod=555 --from=caddy /usr/bin/caddy /caddy
ENV XDG_CONFIG_HOME=/config/rendered
ENV XDG_DATA_HOME=/config/data
USER 1000:1000
WORKDIR /config/rendered
WORKDIR /config/data
WORKDIR /config
ENTRYPOINT ["/caddy"]

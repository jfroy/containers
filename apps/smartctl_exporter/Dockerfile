FROM docker.io/library/alpine:3.21

ARG VERSION
ARG CHANNEL
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL internal.flatops.image.target_platform=$TARGETPLATFORM
LABEL internal.flatops.image.target_architecture=$TARGETARCH
LABEL internal.flatops.image.target_os=$TARGETOS
LABEL internal.flatops.image.forked_from="https://github.com/joryirving/containers"
LABEL org.opencontainers.image.source="https://github.com/prometheus-community/smartctl_exporter"

RUN apk add smartmontools
RUN wget "https://github.com/prometheus-community/smartctl_exporter/releases/download/v$VERSION/smartctl_exporter-$VERSION.$TARGETOS-$TARGETARCH.tar.gz" \
  && tar xvzf smartctl_exporter-$VERSION.$TARGETOS-$TARGETARCH.tar.gz \
  && ls -l smartctl_exporter-$VERSION.$TARGETOS-$TARGETARCH.tar.gz \
  && mv smartctl_exporter-$VERSION.$TARGETOS-$TARGETARCH/smartctl_exporter /bin/smartctl_exporter \
  && chmod +x /bin/smartctl_exporter \
  && rm -rf smartctl_exporter*

EXPOSE      9633
USER        nobody
ENTRYPOINT  [ "/bin/smartctl_exporter" ]

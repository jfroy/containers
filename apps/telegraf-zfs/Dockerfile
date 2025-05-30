FROM docker.io/library/alpine:3.22

ARG VERSION
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL internal.flatops.image.target_platform=$TARGETPLATFORM
LABEL internal.flatops.image.target_architecture=$TARGETARCH
LABEL internal.flatops.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/influxdata/telegraf"

RUN apk add zfs
RUN wget "https://dl.influxdata.com/telegraf/releases/telegraf-${VERSION}_linux_${TARGETARCH}.tar.gz" \
    && tar xvzf telegraf-${VERSION}_linux_${TARGETARCH}.tar.gz \
    && mv telegraf-${VERSION}/usr/bin/telegraf /usr/bin/telegraf \
    && chmod +x /usr/bin/telegraf \
    && rm -rf telegraf-*

USER root
ENTRYPOINT ["/usr/bin/telegraf"]

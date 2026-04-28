FROM ubuntu:26.04 AS builder

ARG TARGETARCH
ARG VERSION

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    meson \
    pkg-config \
    wget

WORKDIR /build
RUN wget -q https://github.com/bus1/dbus-broker/releases/download/v${VERSION}/dbus-broker-${VERSION}.tar.xz \
    && tar xf dbus-broker-${VERSION}.tar.xz

WORKDIR /build/dbus-broker-${VERSION}
RUN meson setup -Dlauncher=false --prefix /usr build \
    && meson compile -C build \
    && meson install -C build --destdir /out

FROM ubuntu:26.04
WORKDIR /
COPY --from=builder /out/usr /usr

ENTRYPOINT ["/usr/bin/dbus-broker"]
CMD [""]

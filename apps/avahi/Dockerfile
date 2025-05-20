FROM ubuntu:25.10 AS builder

ARG TARGETARCH
ARG VERSION

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    libdaemon-dev \
    libdbus-1-dev \
    libexpat1-dev \
    pkg-config \
    wget

WORKDIR /build
RUN wget -q https://github.com/avahi/avahi/releases/download/v${VERSION}/avahi-${VERSION}.tar.gz \
    && tar xf avahi-${VERSION}.tar.gz

WORKDIR /build/avahi-${VERSION}
RUN ./configure \
        --prefix=/usr --sysconfdir=/etc --localstatedir=/var \
        --disable-glib \
        --disable-gobject \
        --disable-libevent \
        --disable-qt4 \
        --disable-qt5 \
        --disable-gtk \
        --disable-gtk3 \
        --disable-gdbm \
        --disable-libsystemd \
        --disable-python \
        --disable-mono \
        --disable-monodoc \
        --disable-autoipd \
        --disable-manpages \
        --with-avahi-user=nobody \
        --with-avahi-group=nogroup \
        --with-distro=none \
    && make -j$(nproc) \
    && make DESTDIR=/out install

FROM ubuntu:25.10
WORKDIR /

RUN apt-get update && apt-get install -y --no-install-recommends \
        libdbus-1-3 \
        libdaemon0 \
        libexpat1 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /out/usr /usr
COPY ./defaults/avahi-daemon.conf /etc/avahi/avahi-daemon.conf

USER nobody:nogroup

ENTRYPOINT ["/usr/sbin/avahi-daemon"]
CMD ["--no-rlimits", "--no-drop-root", "--no-chroot", "--no-proc-title"]

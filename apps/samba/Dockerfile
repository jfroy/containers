FROM alpine:latest AS builder

ARG TARGETARCH
ARG VERSION
ARG CHANNEL

RUN apk add --no-cache \
    acl-dev \
    attr-dev \
    avahi-dev \
    bash \
    bison \
    build-base \
    cmake \
    dbus-dev \
    flex \
    git \
    gnutls-dev \
    icu-dev \
    jansson-dev \
    krb5-dev \
    libtirpc-dev \
    liburing-dev \
    linux-headers \
    perl-parse-yapp \
    popt-dev \
    readline-dev \
    talloc-dev \
    tevent-dev \
    util-linux-dev \
    wget \
    zlib-dev

WORKDIR /build
RUN wget -q https://download.samba.org/pub/samba/stable/samba-${VERSION}.tar.gz \
    && tar xzf samba-${VERSION}.tar.gz

WORKDIR /build/samba-${VERSION}
RUN ./configure \
        --prefix=/usr --sysconfdir=/etc --localstatedir=/var \
        --disable-cephfs \
        --disable-cups \
        --disable-fault-handling \
        --disable-glusterfs \
        --disable-iprint \
        --disable-python \
        --enable-fhs \
        --enable-spotlight \
        --nonshared-binary=smbtorture,smbd/smbd \
        --with-static-modules=ALL \
        --without-ad-dc \
        --without-ads \
        --without-gettext \
        --without-kernel-keyring \
        --without-ldap \
        --without-ldb-lmdb \
        --without-libarchive \
        --without-pam \
        --without-regedit \
        --without-systemd \
        --without-winexe \
    && make -j$(nproc) \
    && make DESTDIR=/out install

FROM alpine:latest
WORKDIR /
RUN apk add --no-cache acl-libs avahi-libs dbus gnutls icu-libs jansson liburing popt zlib
COPY --from=builder /out/usr /usr
EXPOSE 445 139
CMD ["smbd", "-F", "--no-process-group"]

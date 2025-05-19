FROM ubuntu:25.10 AS builder

ARG TARGETARCH
ARG VERSION

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    bison \
    build-essential \
    ca-certificates \
    cmake \
    flex \
    git \
    libacl1-dev \
    libavahi-client-dev \
    libdbus-1-dev \
    libgnutls28-dev \
    libicu-dev \
    libjansson-dev \
    libparse-yapp-perl \
    libpopt-dev \
    libreadline-dev \
    libtalloc-dev \
    libtevent-dev \
    libtirpc-dev \
    liburing-dev \
    python3-dev \
    wget \
    zlib1g-dev

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

FROM ubuntu:25.10
WORKDIR /

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        libavahi-client3 \
        libgnutls30t64 \
        libicu76 \
        libjansson4 \
        libpopt0 \
        libpython3.13 \
        libtirpc3t64 \
        liburing2 \
        python3-pip \
        python3-yaml \
        wget \
    && rm -rf /var/lib/apt/lists/*
RUN wget -q https://github.com/samba-in-kubernetes/sambacc/releases/download/v0.6/sambacc-0.6-py3-none-any.whl \
    && pip3 install --break-system-packages sambacc-0.6-py3-none-any.whl \
    && rm sambacc-0.6-py3-none-any.whl
COPY --from=builder /out/usr /usr
COPY ./smb.conf /etc/samba/smb.conf

EXPOSE 445
ENTRYPOINT ["samba-container"]
CMD ["run", "smbd"]

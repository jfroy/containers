FROM debian:13.1-slim AS builder

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
    libtasn1-bin \
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
# NOTE: Need to set PYTHONDIR and PYTHONARCHDIR because the logic in WAF to autoconfigure the path
# is broken for DESTDIR (i.e. prefix) installs.
ENV PYTHONDIR=/usr/local/lib/python3.13/dist-packages \
    PYTHONARCHDIR=/usr/local/lib/python3.13/dist-packages
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
        --without-quotas \
        --without-regedit \
        --without-systemd \
        --without-winexe \
    && make -j$(nproc) \
    && make DESTDIR=/out install

FROM debian:13.1-slim
WORKDIR /

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        libavahi-client3 \
        libgnutls30t64 \
        libicu76 \
        libjansson4 \
        libpopt0 \
        libpython3.13 \
        libtalloc2 \
        libtirpc3t64 \
        liburing2 \
        python3-pip \
        python3-yaml \
        wget \
    && rm -rf /var/lib/apt/lists/*
RUN wget -q https://github.com/samba-in-kubernetes/sambacc/releases/download/v0.7/sambacc-0.7-py3-none-any.whl \
    && pip3 install --break-system-packages sambacc-0.7-py3-none-any.whl \
    && rm sambacc-0.7-py3-none-any.whl
COPY --from=builder /out/usr /usr
COPY ./defaults/smb.conf /etc/samba/smb.conf

EXPOSE 445
ENTRYPOINT ["samba-container"]
CMD ["run", "smbd"]

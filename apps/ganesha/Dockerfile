FROM docker.io/debian:bookworm-slim AS build

ARG DEBIAN_FRONTEND=noninteractive
USER root
WORKDIR /
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    bison \
    build-essential \
    ca-certificates \
    cmake \
    curl \
    flex \
    git \
    libacl1-dev \
    libblkid-dev \
    libcap-dev \
    libjemalloc-dev \
    libnfsidmap-dev \
    libnsl-dev \
    libsqlite3-dev \
    libunwind-dev \
    liburcu-dev \
    ninja-build \
    pkg-config \
    uuid-dev \
    xfslibs-dev

ARG VERSION
RUN git clone --branch "V${VERSION}" --depth 1 --recursive https://github.com/nfs-ganesha/nfs-ganesha.git /app
WORKDIR /app/src
RUN cmake -G Ninja -B ./build/ \
    -D CMAKE_BUILD_TYPE=Release \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D RUNTIMEDIR=/run \
    -D SYSCONFDIR=/etc \
    -D SYSSTATEDIR=/var \
    -D ALLOCATOR=jemalloc \
    -D ENABLE_VFS_POSIX_ACL=ON \
    -D RPCBIND=OFF \
    -D USE_9P=OFF \
    -D USE_ACL_MAPPING=ON \
    -D USE_ADMIN_TOOLS=OFF \
    -D USE_CAPS=ON \
    -D USE_DBUS=OFF \
    -D USE_FSAL_CEPH=OFF \
    -D USE_FSAL_GLUSTER=OFF \
    -D USE_FSAL_GPFS=OFF \
    -D USE_FSAL_KVSFS=OFF \
    -D USE_FSAL_LIZARDFS=OFF \
    -D USE_FSAL_LUSTRE=OFF \
    -D USE_FSAL_MEM=ON \
    -D USE_FSAL_NULL=ON \
    -D USE_FSAL_PROXY_V3=OFF \
    -D USE_FSAL_PROXY_V4=ON \
    -D USE_FSAL_RGW=OFF \
    -D USE_FSAL_SAUNAFS=OFF \
    -D USE_FSAL_VFS=ON \
    -D USE_FSAL_XFS=ON \
    -D USE_GSS=OFF \
    -D USE_GUI_ADMIN_TOOLS=OFF \
    -D USE_MAN_PAGE=OFF \
    -D USE_MONITORING=ON \
    -D USE_NFS3=ON \
    -D USE_NFSIDMAP=ON \
    -D USE_RADOS_RECOV=OFF \
    -D USE_RQUOTA=OFF
RUN ninja -C ./build/ install

FROM docker.io/debian:bookworm-slim AS runtime

ARG DEBIAN_FRONTEND=noninteractive

USER root
WORKDIR /
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        catatonit \
        libacl1 \
        libblkid1 \
        libcap2 \
        libjemalloc2 \
        libnfsidmap1 \
        libnsl2 \
        libsqlite3-0 \
        libtirpc-common \
        libunwind8 \
        liburcu8 \
        libuuid1 \
        tzdata \
        xfsprogs \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /proc/mounts /etc/mtab
COPY --from=build --chown=root:root /usr/local/ /usr/local/

ENTRYPOINT ["/usr/bin/catatonit", "--", "/usr/local/bin/ganesha.nfsd"]
CMD ["-F", "-x", "-L", "STDOUT", "-f", "/config/ganesha.conf"]
ENV LD_LIBRARY_PATH=/usr/local/lib

LABEL org.opencontainers.image.source="https://github.com/nfs-ganesha/nfs-ganesha"

ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION

USER 0

RUN apt-get update && \
    apt-get install -y --no-install-recommends wget gpg && \
    wget -qO /tmp/timescaledb.gpg https://packagecloud.io/timescale/timescaledb/gpgkey && \
    gpg --dearmor < /tmp/timescaledb.gpg > /usr/share/keyrings/timescaledb-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/timescaledb-archive-keyring.gpg] https://packagecloud.io/timescale/timescaledb/debian/ trixie main" > /etc/apt/sources.list.d/timescaledb.list && \
    apt-get update && \
	apt-get install -y --no-install-recommends "timescaledb-2-postgresql-${PG_MAJOR}=${EXT_VERSION}*"

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /usr/share/doc/timescaledb-2-postgresql-${PG_MAJOR}/copyright /licenses/timescaledb-2-postgresql-${PG_MAJOR}/
COPY --from=builder /usr/share/doc/timescaledb-2-loader-postgresql-${PG_MAJOR}/copyright /licenses/timescaledb-2-loader-postgresql-${PG_MAJOR}/

# Libraries
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/timescaledb* /lib/

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/timescaledb* /share/extension/

USER 65532:65532

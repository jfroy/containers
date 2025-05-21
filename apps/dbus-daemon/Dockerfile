FROM ubuntu:25.10

WORKDIR /
RUN apt-get update && apt-get install -y --no-install-recommends \
        dbus-daemon \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/usr/bin/dbus-daemon"]
CMD ["--nopidfile", "--nofork"]

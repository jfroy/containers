FROM docker.io/library/alpine:3.21
ARG VERSION
ARG TARGETARCH

RUN apk add --no-cache bash \
    && wget -O /usr/local/bin/kubectl "https://dl.k8s.io/release/v$VERSION/bin/linux/$TARGETARCH/kubectl" \
    && chmod +x  /usr/local/bin/kubectl

USER nobody
ENTRYPOINT ["/usr/local/bin/kubectl"]
CMD ["--help"]

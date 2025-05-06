FROM docker.io/library/alpine:3.21
ARG VERSION
ARG TARGETOS
ARG TARGETARCH
ARG TARGETPLATFORM

RUN apk add --no-cache bash \
    && wget "https://dl.k8s.io/release/v$VERSION/bin/linux/$TARGETARCH/kubectl" \
    && chmod +x kubectl

USER nobody
ENTRYPOINT ["/kubectl"]
CMD ["--help"]

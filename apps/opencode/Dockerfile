# syntax=docker/dockerfile:1

ARG VERSION

# Fetch and verify the pinned CLI tools on the build platform: this stage only
# downloads, checksums and unpacks, so it never runs a target-arch binary.
FROM --platform=$BUILDPLATFORM docker.io/library/alpine:3.24 AS tools

ARG TARGETARCH
ARG AGE_VERSION
ARG FLATE_VERSION
ARG FLUX_VERSION
ARG GH_VERSION
ARG HELM_VERSION
ARG JQ_VERSION
ARG KUBECONFORM_VERSION
ARG KUBECTL_VERSION
ARG KUSTOMIZE_VERSION
ARG SOPS_VERSION
ARG TALHELPER_VERSION
ARG TALOSCTL_VERSION
ARG TASK_VERSION
ARG YQ_VERSION

RUN apk add --no-cache ca-certificates python3

COPY scripts/install-tools.py /install-tools.py

RUN python3 /install-tools.py --arch "${TARGETARCH}" --dest /out/usr/local/bin

FROM ghcr.io/anomalyco/opencode:${VERSION}

# opencode ships a minimal Alpine with only libgcc, libstdc++ and ripgrep;
# these are what the flatops workflow needs on top of the pinned tools.
RUN apk add --no-cache \
        bash \
        ca-certificates \
        curl \
        git \
        openssh-client

COPY --from=tools /out/ /

LABEL org.opencontainers.image.description="opencode with the flatops toolchain"

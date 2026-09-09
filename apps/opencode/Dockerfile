# syntax=docker/dockerfile:1

# Fetch and verify the pinned tools on the build platform: this stage only
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
ARG OPENCODE_VERSION
ARG SOPS_VERSION
ARG TALHELPER_VERSION
ARG TALOSCTL_VERSION
ARG TASK_VERSION
ARG YQ_VERSION

RUN apk add --no-cache ca-certificates python3

COPY scripts/install-tools.py /install-tools.py

RUN python3 /install-tools.py --arch "${TARGETARCH}" --dest /out/usr/local/bin

FROM docker.io/library/alpine:3.24

# opencode2 is a Bun single-file executable linked against musl, libstdc++ and
# libgcc, and it shells out to ripgrep for search. The rest is what the flatops
# workflow needs alongside the pinned tools. opencode does not publish a v2
# image during the beta, so this starts from Alpine rather than deriving.
RUN apk add --no-cache \
        bash \
        ca-certificates \
        curl \
        git \
        libgcc \
        libstdc++ \
        openssh-client \
        ripgrep

COPY --from=tools /out/ /

ENTRYPOINT ["/usr/local/bin/opencode2"]

LABEL org.opencontainers.image.description="opencode2 beta with the flatops toolchain"

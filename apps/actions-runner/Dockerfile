ARG VERSION
FROM --platform=amd64 ghcr.io/actions/actions-runner:${VERSION}

ENV HOMEBREW_NO_ANALYTICS=1 \
    HOMEBREW_NO_ENV_HINTS=1 \
    HOMEBREW_NO_INSTALL_CLEANUP=1 \
    DEBCONF_NONINTERACTIVE_SEEN=true \
    DEBIAN_FRONTEND="noninteractive" \
    APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=DontWarn

USER root

RUN \
    apt-get update \
    && \
    apt-get install -y --no-install-recommends --no-install-suggests \
        ca-certificates \
        gcc \
        jo \
        moreutils \
        wget \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/fluxcd/flux-cli:v2.4.0 /usr/local/bin/flux /usr/local/bin/flux
COPY --from=registry.k8s.io/kubectl:v1.31.1 /bin/kubectl /usr/local/bin/kubectl
COPY --from=docker.io/mikefarah/yq:4.44.3 /usr/bin/yq /usr/local/bin/yq

USER runner

RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

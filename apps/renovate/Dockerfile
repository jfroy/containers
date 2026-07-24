ARG VERSION=43.280.3
FROM ghcr.io/renovatebot/renovate:${VERSION}

ARG HELM_DOCS_VERSION
ARG HELM_SCHEMA_VERSION
ARG TARGETARCH

USER root

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN set -eux; \
    case "${TARGETARCH}" in \
        amd64) asset_arch="x86_64" ;; \
        arm64) asset_arch="arm64" ;; \
        *) echo "unsupported architecture: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    tmp_dir="$(mktemp -d)"; \
    cd "${tmp_dir}"; \
    helm_docs_asset="helm-docs_${HELM_DOCS_VERSION#v}_Linux_${asset_arch}.tar.gz"; \
    curl -fsSLO "https://github.com/norwoodj/helm-docs/releases/download/${HELM_DOCS_VERSION}/checksums.txt"; \
    curl -fsSLO "https://github.com/norwoodj/helm-docs/releases/download/${HELM_DOCS_VERSION}/${helm_docs_asset}"; \
    grep " ${helm_docs_asset}$" checksums.txt | sha256sum -c -; \
    tar -xzf "${helm_docs_asset}" -C /usr/local/bin helm-docs; \
    rm -f checksums.txt; \
    helm_schema_asset="helm-schema_${HELM_SCHEMA_VERSION}_Linux_${asset_arch}.tar.gz"; \
    curl -fsSLO "https://github.com/dadav/helm-schema/releases/download/${HELM_SCHEMA_VERSION}/checksums.txt"; \
    curl -fsSLO "https://github.com/dadav/helm-schema/releases/download/${HELM_SCHEMA_VERSION}/${helm_schema_asset}"; \
    grep " ${helm_schema_asset}$" checksums.txt | sha256sum -c -; \
    tar -xzf "${helm_schema_asset}" -C /usr/local/bin helm-schema; \
    chmod +x /usr/local/bin/helm-docs /usr/local/bin/helm-schema; \
    rm -rf "${tmp_dir}"

USER ubuntu

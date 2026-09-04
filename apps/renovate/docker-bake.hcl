target "docker-metadata-action" {}

variable "APP" {
  default = "renovate"
}

variable "VERSION" {
  // renovate: datasource=docker depName=ghcr.io/renovatebot/renovate
  default = "44.62.1"
}

variable "HELM_DOCS_VERSION" {
  // renovate: datasource=github-releases depName=norwoodj/helm-docs
  default = "v1.14.2"
}

variable "HELM_SCHEMA_VERSION" {
  // renovate: datasource=github-releases depName=dadav/helm-schema
  default = "0.23.5"
}

variable "SOURCE" {
  default = "https://github.com/renovatebot/renovate"
}

group "default" {
  targets = ["image-local"]
}

target "image" {
  inherits = ["docker-metadata-action"]
  args = {
    VERSION             = "${VERSION}"
    HELM_DOCS_VERSION  = "${HELM_DOCS_VERSION}"
    HELM_SCHEMA_VERSION = "${HELM_SCHEMA_VERSION}"
  }
  labels = {
    "org.opencontainers.image.source" = "${SOURCE}"
  }
}

target "image-local" {
  inherits = ["image"]
  output = ["type=docker"]
  tags = ["${APP}:${VERSION}"]
}

target "image-all" {
  inherits = ["image"]
  platforms = [
    "linux/amd64",
    "linux/arm64"
  ]
}

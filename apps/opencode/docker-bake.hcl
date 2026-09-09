target "docker-metadata-action" {}

variable "APP" {
  default = "opencode"
}

variable "VERSION" {
  // renovate: datasource=docker depName=ghcr.io/anomalyco/opencode
  default = "1.18.30"
}

variable "AGE_VERSION" {
  // renovate: datasource=github-releases depName=FiloSottile/age
  default = "v1.3.2"
}

variable "FLATE_VERSION" {
  // renovate: datasource=github-releases depName=home-operations/flate
  default = "v0.6.5"
}

variable "FLUX_VERSION" {
  // renovate: datasource=github-releases depName=fluxcd/flux2
  default = "v2.9.5"
}

variable "GH_VERSION" {
  // renovate: datasource=github-releases depName=cli/cli
  default = "v2.100.0"
}

variable "HELM_VERSION" {
  // renovate: datasource=github-releases depName=helm/helm
  default = "v4.2.4"
}

variable "JQ_VERSION" {
  // renovate: datasource=github-releases depName=jqlang/jq
  default = "1.8.2"
}

variable "KUBECONFORM_VERSION" {
  // renovate: datasource=github-releases depName=yannh/kubeconform
  default = "v0.8.0"
}

variable "KUBECTL_VERSION" {
  // renovate: datasource=github-releases depName=kubernetes/kubernetes
  default = "1.37.0"
}

variable "KUSTOMIZE_VERSION" {
  // renovate: datasource=github-releases depName=kubernetes-sigs/kustomize
  default = "5.8.1"
}

variable "SOPS_VERSION" {
  // renovate: datasource=github-releases depName=getsops/sops
  default = "v3.13.3"
}

variable "TALHELPER_VERSION" {
  // renovate: datasource=github-releases depName=budimanjojo/talhelper
  default = "v3.1.17"
}

variable "TALOSCTL_VERSION" {
  // renovate: datasource=github-releases depName=siderolabs/talos
  default = "v1.14.0"
}

variable "TASK_VERSION" {
  // renovate: datasource=github-releases depName=go-task/task
  default = "v3.53.1"
}

variable "YQ_VERSION" {
  // renovate: datasource=github-releases depName=mikefarah/yq
  default = "v4.53.6"
}

variable "SOURCE" {
  default = "https://github.com/anomalyco/opencode"
}

group "default" {
  targets = ["image-local"]
}

target "image" {
  inherits = ["docker-metadata-action"]
  args = {
    VERSION             = "${VERSION}"
    AGE_VERSION         = "${AGE_VERSION}"
    FLATE_VERSION       = "${FLATE_VERSION}"
    FLUX_VERSION        = "${FLUX_VERSION}"
    GH_VERSION          = "${GH_VERSION}"
    HELM_VERSION        = "${HELM_VERSION}"
    JQ_VERSION          = "${JQ_VERSION}"
    KUBECONFORM_VERSION = "${KUBECONFORM_VERSION}"
    KUBECTL_VERSION     = "${KUBECTL_VERSION}"
    KUSTOMIZE_VERSION   = "${KUSTOMIZE_VERSION}"
    SOPS_VERSION        = "${SOPS_VERSION}"
    TALHELPER_VERSION   = "${TALHELPER_VERSION}"
    TALOSCTL_VERSION    = "${TALOSCTL_VERSION}"
    TASK_VERSION        = "${TASK_VERSION}"
    YQ_VERSION          = "${YQ_VERSION}"
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

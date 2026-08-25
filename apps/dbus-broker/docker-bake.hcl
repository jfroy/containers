target "docker-metadata-action" {}

variable "APP" {
  default = "dbus-broker"
}

variable "VERSION" {
  // renovate: datasource=github-releases depName=bus1/dbus-broker
  default = "36"
}

variable "SOURCE" {
  default = "https://github.com/bus1/dbus-broker"
}

group "default" {
  targets = ["image-local"]
}

target "image" {
  inherits = ["docker-metadata-action"]
  args = {
    VERSION = "${VERSION}"
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

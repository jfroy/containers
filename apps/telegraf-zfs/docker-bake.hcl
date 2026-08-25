target "docker-metadata-action" {}

variable "APP" {
  default = "telegraf-zfs"
}

variable "VERSION" {
  // renovate: datasource=github-releases depName=influxdata/telegraf
  default = "1.39.3"
}

variable "SOURCE" {
  default = "https://github.com/influxdata/telegraf"
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

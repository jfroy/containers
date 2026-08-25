target "docker-metadata-action" {}

variable "APP" {
  default = "dbus-daemon"
}

variable "VERSION" {
  default = "1.16.2"
}

variable "SOURCE" {
  default = "https://www.freedesktop.org/wiki/Software/dbus/"
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

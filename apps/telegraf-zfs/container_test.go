package main

import (
	"testing"

	helpers "github.com/jfroy/containers/tests"
)

func Test(t *testing.T) {
	image := helpers.GetTestImage("ghcr.io/jfroy/telegraf-zfs:rolling")
	helpers.RequireFileExists(t, image, "/usr/bin/telegraf")
	helpers.RequireFileExists(t, image, "/usr/sbin/zfs")
	helpers.RequireFileExists(t, image, "/usr/sbin/zpool")
}

package main

import (
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/jfroy/telegraf-zfs:rolling")
	testhelpers.RequireFileExists(t, image, "/usr/bin/telegraf")
	testhelpers.RequireFileExists(t, image, "/usr/sbin/zfs")
	testhelpers.RequireFileExists(t, image, "/usr/sbin/zpool")
}

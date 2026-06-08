package main

import (
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/jfroy/telegraf-zfs:rolling")
	testhelpers.TestFileExists(t, image, "/usr/bin/telegraf", nil)
	testhelpers.TestFileExists(t, image, "/usr/sbin/zfs", nil)
	testhelpers.TestFileExists(t, image, "/usr/sbin/zpool", nil)
}

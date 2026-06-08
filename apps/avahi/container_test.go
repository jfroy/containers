package main

import (
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/jfroy/avahi:rolling")
	testhelpers.TestFileExists(t, image, "/usr/sbin/avahi-daemon", nil)
}

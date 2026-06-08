package main

import (
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/jfroy/dbus-broker:rolling")
	testhelpers.TestFileExists(t, image, "/usr/bin/dbus-broker", nil)
}

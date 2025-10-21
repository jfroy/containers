package main

import (
	"context"
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/jfroy/dbus-daemon:rolling")
	testhelpers.TestFileExists(t, ctx, image, "/usr/bin/dbus-daemon", nil)
}

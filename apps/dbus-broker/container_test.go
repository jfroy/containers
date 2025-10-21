package main

import (
	"context"
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/jfroy/dbus-broker:rolling")
	testhelpers.TestFileExists(t, ctx, image, "/usr/bin/dbus-broker", nil)
}

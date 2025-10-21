package main

import (
	"context"
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/jfroy/avahi:rolling")
	testhelpers.TestFileExists(t, ctx, image, "/usr/sbin/avahi-daemon", nil)
}

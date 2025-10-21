package main

import (
	"context"
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/jfroy/telegraf-zfs:rolling")
	testhelpers.TestFileExists(t, ctx, image, "/usr/bin/telegraf", nil)
	testhelpers.TestFileExists(t, ctx, image, "/usr/sbin/zfs", nil)
	testhelpers.TestFileExists(t, ctx, image, "/usr/sbin/zpool", nil)
}

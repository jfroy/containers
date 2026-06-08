package main

import (
	"context"
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/jfroy/timescaledb-extension-18:rolling")
	testhelpers.TestFileExists(t, ctx, image, "/lib/timescaledb.so", nil)
	testhelpers.TestFileExists(t, ctx, image, "/share/extension/timescaledb.control", nil)
}

package main

import (
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/jfroy/timescaledb-extension-18:rolling")
	testhelpers.TestFileExists(t, image, "/lib/timescaledb.so", nil)
	testhelpers.TestFileExists(t, image, "/share/extension/timescaledb.control", nil)
}

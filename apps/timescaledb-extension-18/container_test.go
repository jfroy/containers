package main

import (
	"testing"

	helpers "github.com/jfroy/containers/tests"
)

func Test(t *testing.T) {
	image := helpers.GetTestImage("ghcr.io/jfroy/timescaledb-extension-18:rolling")
	helpers.RequireFileExists(t, image, "/lib/timescaledb.so")
	helpers.RequireFileExists(t, image, "/share/extension/timescaledb.control")
}

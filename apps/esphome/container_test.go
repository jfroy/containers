package main

import (
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/jfroy/esphome:rolling")
	testhelpers.TestFileExists(t, image, "/usr/local/bin/esphome", nil)
}

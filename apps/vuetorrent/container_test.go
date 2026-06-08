package main

import (
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/jfroy/vuetorrent:rolling")
	testhelpers.TestFileExists(t, image, "/vuetorrent/public/index.html", nil)
}

package main

import (
	"testing"

	helpers "github.com/jfroy/containers/tests"
)

func Test(t *testing.T) {
	image := helpers.GetTestImage("ghcr.io/jfroy/vuetorrent:rolling")
	helpers.RequireFileExists(t, image, "/vuetorrent/public/index.html")
}

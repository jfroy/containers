package main

import (
	"testing"

	helpers "github.com/jfroy/containers/tests"
)

func Test(t *testing.T) {
	image := helpers.GetTestImage("ghcr.io/jfroy/samba:rolling")
	helpers.RequireFileExists(t, image, "/usr/local/bin/samba-container")
	helpers.RequireFileExists(t, image, "/usr/sbin/smbd")
}

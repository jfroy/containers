package main

import (
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/jfroy/samba:rolling")
	testhelpers.RequireFileExists(t, image, "/usr/local/bin/samba-container")
	testhelpers.RequireFileExists(t, image, "/usr/sbin/smbd")
}

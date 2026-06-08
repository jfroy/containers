package main

import (
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/jfroy/samba:rolling")
	testhelpers.TestFileExists(t, image, "/usr/local/bin/samba-container", nil)
	testhelpers.TestFileExists(t, image, "/usr/sbin/smbd", nil)
}

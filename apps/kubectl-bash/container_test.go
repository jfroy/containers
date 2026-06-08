package main

import (
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/jfroy/kubectl-bash:rolling")
	testhelpers.TestFileExists(t, image, "/bin/bash", nil)
	testhelpers.TestFileExists(t, image, "/usr/local/bin/kubectl", nil)
}

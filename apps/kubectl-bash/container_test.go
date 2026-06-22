package main

import (
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/jfroy/kubectl-bash:rolling")
	testhelpers.RequireFileExists(t, image, "/bin/bash")
	testhelpers.RequireFileExists(t, image, "/usr/local/bin/kubectl")
}

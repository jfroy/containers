package main

import (
	"testing"

	helpers "github.com/jfroy/containers/tests"
)

func Test(t *testing.T) {
	image := helpers.GetTestImage("ghcr.io/jfroy/kubectl-bash:rolling")
	helpers.RequireFileExists(t, image, "/bin/bash")
	helpers.RequireFileExists(t, image, "/usr/local/bin/kubectl")
}

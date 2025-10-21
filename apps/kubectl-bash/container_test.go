package main

import (
	"context"
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/jfroy/kubectl-bash:rolling")
	testhelpers.TestFileExists(t, ctx, image, "/bin/bash", nil)
	testhelpers.TestFileExists(t, ctx, image, "/usr/local/bin/kubectl", nil)
}

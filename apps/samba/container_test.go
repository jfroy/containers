package main

import (
	"context"
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/jfroy/samba:rolling")
	testhelpers.TestFileExists(t, ctx, image, "/usr/local/bin/samba-container", nil)
	testhelpers.TestFileExists(t, ctx, image, "/usr/sbin/smbd", nil)
}

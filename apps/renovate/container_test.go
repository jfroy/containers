package main

import (
	"testing"

	"github.com/jfroy/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/jfroy/renovate:rolling")
	testhelpers.RequireFileExists(t, image, "/usr/local/sbin/renovate")
	testhelpers.RequireFileExists(t, image, "/usr/local/bin/helm-docs")
	testhelpers.RequireFileExists(t, image, "/usr/local/bin/helm-schema")
}

package main

import (
	"testing"

	helpers "github.com/jfroy/containers/tests"
)

func Test(t *testing.T) {
	image := helpers.GetTestImage("ghcr.io/jfroy/renovate:rolling")
	helpers.RequireFileExists(t, image, "/usr/local/sbin/renovate")
	helpers.RequireFileExists(t, image, "/usr/local/bin/helm-docs")
	helpers.RequireFileExists(t, image, "/usr/local/bin/helm-schema")
}

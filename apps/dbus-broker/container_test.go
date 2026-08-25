package main

import (
	"testing"

	helpers "github.com/jfroy/containers/tests"
)

func Test(t *testing.T) {
	image := helpers.GetTestImage("ghcr.io/jfroy/dbus-broker:rolling")
	helpers.RequireFileExists(t, image, "/usr/bin/dbus-broker")
}

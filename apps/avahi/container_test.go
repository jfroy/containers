package main

import (
	"testing"
	"time"

	helpers "github.com/jfroy/containers/tests"
)

func Test(t *testing.T) {
	image := helpers.GetTestImage("ghcr.io/jfroy/avahi:rolling")
	helpers.RequireFileExists(t, image, "/usr/sbin/avahi-daemon")
	t.Run("starts up with production flags", func(t *testing.T) {
		config := &helpers.ContainerConfig{
			Files: []helpers.FileToCopy{{
				HostPath:      "testdata/avahi-daemon.conf",
				ContainerPath: "/etc/avahi/avahi-daemon.conf",
				Mode:          0o644,
			}},
			Tmpfs: map[string]string{"/run": "rw,mode=1777"},
		}
		helpers.RequireDaemonStartsUp(t, image, helpers.DaemonStartupConfig{
			LogPattern: `Server startup complete\.`,
			Timeout:    30 * time.Second,
		}, config)
	})
}

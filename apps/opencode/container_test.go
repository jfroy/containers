package main

import (
	"maps"
	"slices"
	"strings"
	"testing"

	helpers "github.com/jfroy/containers/tests"
)

// binaries maps every executable the image is expected to provide to the
// invocation that proves it actually runs. The pinned tools are fetched on the
// build platform and dropped into a musl base, so running them is what catches
// a wrong-arch or dynamically linked download.
var binaries = map[string]string{
	"/usr/local/bin/opencode":    "opencode --version",
	"/usr/bin/git":               "git --version",
	"/usr/local/bin/gh":          "gh --version",
	"/usr/local/bin/kubectl":     "kubectl version --client",
	"/usr/local/bin/flux":        "flux --version",
	"/usr/local/bin/kustomize":   "kustomize version",
	"/usr/local/bin/helm":        "helm version",
	"/usr/local/bin/yq":          "yq --version",
	"/usr/local/bin/jq":          "jq --version",
	"/usr/local/bin/task":        "task --version",
	"/usr/local/bin/sops":        "sops --version --disable-version-check",
	"/usr/local/bin/age":         "age --version",
	"/usr/local/bin/age-keygen":  "age-keygen --version",
	"/usr/local/bin/talosctl":    "talosctl version --client",
	"/usr/local/bin/talhelper":   "talhelper --version",
	"/usr/local/bin/kubeconform": "kubeconform -v",
	"/usr/local/bin/flate":       "flate --version",
}

func Test(t *testing.T) {
	image := helpers.GetTestImage("ghcr.io/jfroy/opencode:rolling")

	t.Run("installed", func(t *testing.T) {
		for _, path := range slices.Sorted(maps.Keys(binaries)) {
			helpers.RequireFileExists(t, image, path)
		}
	})

	t.Run("runnable", func(t *testing.T) {
		commands := make([]string, 0, len(binaries))
		for _, command := range binaries {
			commands = append(commands, command)
		}
		slices.Sort(commands)
		script := "set -eux; " + strings.Join(commands, "; ")
		helpers.RequireCommandSucceeds(t, image, nil, "/bin/bash", "-c", script)
	})
}

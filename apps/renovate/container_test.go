package main

import (
	"maps"
	"slices"
	"strings"
	"testing"

	helpers "github.com/jfroy/containers/tests"
)

const (
	// appRoot is where the upstream image installs Renovate and its node_modules.
	appRoot = "/usr/local/renovate"
	// nodeBin is the symlink the upstream image makes for its bundled node.
	nodeBin = "/bin/node"
	// checkScript is where check-bundle-imports.mjs lands inside the container.
	checkScript = "/tmp/check-bundle-imports.mjs"
)

// binaries maps every executable the image is expected to provide to the
// invocation that proves it actually runs. helm-docs and helm-schema are release
// tarballs fetched for the build platform, so running them is what catches a
// wrong-arch or truncated download; file presence alone does not.
var binaries = map[string]string{
	"/usr/local/sbin/renovate":   "renovate --version",
	"/usr/local/bin/helm-docs":   "helm-docs --version",
	"/usr/local/bin/helm-schema": "helm-schema --version",
}

func Test(t *testing.T) {
	image := helpers.GetTestImage("ghcr.io/jfroy/renovate:rolling")

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

	// "runnable" is not enough on its own. Renovate is ESM, so a package missing
	// from the image only surfaces as ERR_MODULE_NOT_FOUND when Node links the
	// module that imports it: 44.78.0 crashed every repository run in
	// dist/workers/repository/update/pr/index.js while `renovate --version` --
	// the upstream image's own build-time check -- still exited 0. Resolve every
	// package the bundle statically imports instead.
	t.Run("imports resolve", func(t *testing.T) {
		config := &helpers.ContainerConfig{
			Files: []helpers.FileToCopy{{
				HostPath:      "testdata/check-bundle-imports.mjs",
				ContainerPath: checkScript,
				Mode:          0o644,
			}},
		}
		helpers.RequireCommandSucceeds(t, image, config, nodeBin, checkScript, appRoot)
	})
}

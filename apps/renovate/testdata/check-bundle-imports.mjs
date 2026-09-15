// Verifies that every package Renovate's compiled bundle statically imports is
// actually installed in the image.
//
// Renovate ships as ESM, so a package missing from the image is not a build
// failure. Node only reports it as ERR_MODULE_NOT_FOUND the first time it links
// the module that needs it. 44.78.0 shipped with `common-tags` demoted to a dev
// dependency and crashed every repository run inside
// dist/workers/repository/update/pr/index.js, while `renovate --version` -- the
// only runtime check the upstream image performs at build time -- kept exiting 0.
//
// Resolving the specifiers instead of importing them keeps this offline, fast
// and free of module side effects. Resolution is the exact step that failed.
//
// Usage: node check-bundle-imports.mjs <app-root>   (e.g. /usr/local/renovate)

import { existsSync } from "node:fs";
import { readFile, readdir } from "node:fs/promises";
import { builtinModules } from "node:module";
import path from "node:path";
import process from "node:process";

// The scan must never pass by finding nothing: a build change that rewrites
// external imports would otherwise silently turn this check into a no-op.
const minPackages = 20;

// Packages expected to be absent, e.g. an optional dependency the image
// deliberately does not install. Add entries with a reason, or to silence a
// specifier the patterns below picked up out of a string literal.
const ignored = new Set();

const builtins = new Set(builtinModules);

// `import ... from "x"` / `export ... from "x"`, and the bare `import "x"` form.
// Static specifiers only: those are the ones Node resolves eagerly while linking
// the module graph, which is how a missing package takes the process down.
const patterns = [/\bfrom\s*["']([^"']+)["']/g, /\bimport\s+["']([^"']+)["']/g];

function isExternal(specifier) {
  if (specifier === "" || specifier.startsWith(".") || specifier.startsWith("/")) {
    return false;
  }
  // "#" is a package-internal import, the others are not node_modules lookups.
  if (specifier.startsWith("#") || specifier.startsWith("node:") || specifier.startsWith("data:")) {
    return false;
  }
  return /^(?:@[^/]+\/)?[a-z0-9~][a-z0-9-._~]*(?:\/.*)?$/i.test(specifier);
}

function packageOf(specifier) {
  const parts = specifier.split("/");
  return specifier.startsWith("@") ? parts.slice(0, 2).join("/") : parts[0];
}

const lookups = new Map();

// Mirrors what Node does before it throws ERR_MODULE_NOT_FOUND: walk node_modules
// up from the importing file until the package's package.json turns up.
function isInstalled(fromDir, pkg) {
  const key = fromDir + "|" + pkg;
  const cached = lookups.get(key);
  if (cached !== undefined) {
    return cached;
  }

  let found = false;
  for (let dir = fromDir; ; dir = path.dirname(dir)) {
    if (
      path.basename(dir) !== "node_modules" &&
      existsSync(path.join(dir, "node_modules", pkg, "package.json"))
    ) {
      found = true;
      break;
    }
    if (path.dirname(dir) === dir) {
      break;
    }
  }

  lookups.set(key, found);
  return found;
}

async function* bundleFiles(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name !== "node_modules") {
        yield* bundleFiles(full);
      }
    } else if (entry.isFile() && /\.[cm]?js$/.test(entry.name)) {
      yield full;
    }
  }
}

const root = process.argv[2];
if (!root) {
  console.error("usage: check-bundle-imports.mjs <app-root>");
  process.exit(2);
}

const bundle = path.join(root, "dist");
if (!existsSync(bundle)) {
  console.error(`no bundle directory at ${bundle}`);
  process.exit(1);
}

const packages = new Set();
const missing = new Map();
let files = 0;

for await (const file of bundleFiles(bundle)) {
  files += 1;
  const source = await readFile(file, "utf8");
  const dir = path.dirname(file);

  for (const pattern of patterns) {
    for (const [, specifier] of source.matchAll(pattern)) {
      if (!isExternal(specifier)) {
        continue;
      }

      const pkg = packageOf(specifier);
      if (builtins.has(pkg) || ignored.has(pkg)) {
        continue;
      }

      packages.add(pkg);
      if (!missing.has(pkg) && !isInstalled(dir, pkg)) {
        missing.set(pkg, file);
      }
    }
  }
}

console.log(`scanned ${files} file(s) under ${bundle}, ${packages.size} external package(s) imported`);

if (missing.size > 0) {
  console.error(`${missing.size} package(s) imported by the bundle are not installed:`);
  for (const pkg of [...missing.keys()].sort()) {
    console.error(`  ${pkg} -- imported from ${missing.get(pkg)}`);
  }
  process.exit(1);
}

if (packages.size < minPackages) {
  console.error(`only ${packages.size} external package(s) found, expected at least ${minPackages}`);
  console.error("the bundle layout likely changed and this check is no longer looking at anything");
  process.exit(1);
}

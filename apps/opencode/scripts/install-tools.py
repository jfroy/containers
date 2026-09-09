#!/usr/bin/env python3
"""Download, verify and stage the CLI tools baked into the opencode image.

Every tool is fetched from its upstream release at the version pinned in
``docker-bake.hcl`` (passed in as a ``<NAME>_VERSION`` build arg, and therefore
visible here as an environment variable) and checked against the digest the
publisher ships alongside the asset. The one exception is documented on the
tool itself.

opencode2 is taken straight from its per-platform npm package rather than
through ``@opencode/cli``: that launcher package picks a platform build by
probing the *build* machine (``os.arch()``, ``/etc/alpine-release``, and AVX2
from ``/proc/cpuinfo``) and then runs the binary to verify it, which would bake
the CI runner's CPU into the image and force cross-arch stages under emulation.
The per-platform packages carry no install scripts, just the binary.

Nothing downloaded here is executed: this stage runs on the *build* platform
while the binaries are for ``--arch``, so they may not even be runnable.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import io
import json
import os
import re
import sys
import tarfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ARCHES = ("amd64", "arm64")
NPM_REGISTRY = "https://registry.npmjs.org"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
USER_AGENT = "jfroy-containers-opencode-build"


@dataclass(frozen=True)
class Checksum:
    """Where to find the expected SHA-256 for an asset.

    ``url`` points at a file holding either a bare hash or ``sha256  filename``
    lines; ``key`` is the asset filename to look up when the file lists several.
    """

    url: str
    key: str | None = None


@dataclass(frozen=True)
class Digest:
    """An expected hash that is already known, rather than fetched from a file."""

    algorithm: str
    value: str  # lowercase hex


@dataclass(frozen=True)
class Tool:
    """One binary (or set of binaries) to install."""

    name: str
    version: str
    url: str
    binaries: tuple[str, ...] = ()
    checksum: Checksum | None = None
    digest: Digest | None = None
    # Set when upstream publishes no checksum we can consume; explains why.
    unverified_reason: str | None = None

    @property
    def wanted(self) -> tuple[str, ...]:
        return self.binaries or (self.name,)

    @property
    def is_archive(self) -> bool:
        return self.url.endswith((".tar.gz", ".tgz"))


def version(name: str) -> str:
    """Read a pinned version from the build environment."""
    value = os.environ.get(f"{name}_VERSION", "").strip()
    if not value:
        raise SystemExit(f"build arg {name}_VERSION is missing or empty")
    return value


def bare(v: str) -> str:
    """Strip the leading ``v`` some projects carry in their git tag."""
    return v[1:] if v.startswith("v") else v


def npm_release(package: str, wanted: str) -> tuple[str, Digest]:
    """Resolve an npm package version to its tarball URL and published digest.

    ``dist.integrity`` is a Subresource Integrity string (``<algorithm>-<base64
    digest>``) and is the strongest thing the registry publishes per version.
    """
    url = f"{NPM_REGISTRY}/{urllib.parse.quote(package, safe='')}/{wanted}"
    try:
        metadata = json.loads(fetch(url))
        dist = metadata["dist"]
        algorithm, _, encoded = str(dist["integrity"]).partition("-")
        return dist["tarball"], Digest(algorithm, base64.b64decode(encoded).hex())
    except (KeyError, ValueError, binascii.Error) as err:
        raise SystemExit(f"{package}@{wanted}: unusable registry metadata: {err}") from err


def tools(arch: str) -> list[Tool]:
    """Build the install table.

    This reaches the network once, for the npm registry lookup opencode2 needs
    to turn a version into a tarball URL and digest.
    """
    opencode = version("OPENCODE")
    gh = version("GH")
    kubectl = version("KUBECTL")
    flux = version("FLUX")
    kustomize = version("KUSTOMIZE")
    helm = version("HELM")
    yq = version("YQ")
    jq = version("JQ")
    task = version("TASK")
    sops = version("SOPS")
    age = version("AGE")
    talosctl = version("TALOSCTL")
    talhelper = version("TALHELPER")
    kubeconform = version("KUBECONFORM")
    flate = version("FLATE")

    gh_asset = f"gh_{bare(gh)}_linux_{arch}.tar.gz"
    flux_asset = f"flux_{bare(flux)}_linux_{arch}.tar.gz"
    kustomize_asset = f"kustomize_v{bare(kustomize)}_linux_{arch}.tar.gz"
    helm_asset = f"helm-{helm}-linux-{arch}.tar.gz"
    jq_asset = f"jq-linux-{arch}"
    task_asset = f"task_linux_{arch}.tar.gz"
    sops_asset = f"sops-{sops}.linux.{arch}"
    talosctl_asset = f"talosctl-linux-{arch}"
    talhelper_asset = f"talhelper_linux_{arch}.tar.gz"
    kubeconform_asset = f"kubeconform-linux-{arch}.tar.gz"
    flate_asset = f"flate_{bare(flate)}_linux_{arch}.tar.gz"

    gh_base = f"https://github.com/cli/cli/releases/download/{gh}"
    flux_base = f"https://github.com/fluxcd/flux2/releases/download/{flux}"
    # The kustomize tag is "kustomize/vX.Y.Z"; the slash has to be encoded.
    kustomize_base = (
        "https://github.com/kubernetes-sigs/kustomize/releases/download"
        f"/kustomize%2Fv{bare(kustomize)}"
    )
    jq_base = f"https://github.com/jqlang/jq/releases/download/jq-{bare(jq)}"
    task_base = f"https://github.com/go-task/task/releases/download/{task}"
    sops_base = f"https://github.com/getsops/sops/releases/download/{sops}"
    talos_base = f"https://github.com/siderolabs/talos/releases/download/{talosctl}"
    talhelper_base = (
        f"https://github.com/budimanjojo/talhelper/releases/download/{talhelper}"
    )
    kubeconform_base = (
        f"https://github.com/yannh/kubeconform/releases/download/{kubeconform}"
    )
    flate_base = f"https://github.com/home-operations/flate/releases/download/{flate}"
    kubectl_url = f"https://dl.k8s.io/release/v{bare(kubectl)}/bin/linux/{arch}/kubectl"
    yq_url = f"https://github.com/mikefarah/yq/releases/download/{yq}/yq_linux_{arch}"

    # The x64 build requires AVX2; "-baseline-musl" is the fallback for older CPUs.
    opencode_package = f"@opencode/cli-linux-{'x64' if arch == 'amd64' else 'arm64'}-musl"
    opencode_url, opencode_digest = npm_release(opencode_package, opencode)

    return [
        Tool(
            name="opencode2",
            version=opencode,
            url=opencode_url,
            binaries=("opencode2",),
            digest=opencode_digest,
        ),
        Tool(
            name="gh",
            version=gh,
            url=f"{gh_base}/{gh_asset}",
            checksum=Checksum(f"{gh_base}/gh_{bare(gh)}_checksums.txt", gh_asset),
        ),
        Tool(
            name="kubectl",
            version=kubectl,
            url=kubectl_url,
            checksum=Checksum(f"{kubectl_url}.sha256"),
        ),
        Tool(
            name="flux",
            version=flux,
            url=f"{flux_base}/{flux_asset}",
            checksum=Checksum(
                f"{flux_base}/flux_{bare(flux)}_checksums.txt", flux_asset
            ),
        ),
        Tool(
            name="kustomize",
            version=kustomize,
            url=f"{kustomize_base}/{kustomize_asset}",
            checksum=Checksum(f"{kustomize_base}/checksums.txt", kustomize_asset),
        ),
        Tool(
            name="helm",
            version=helm,
            url=f"https://get.helm.sh/{helm_asset}",
            checksum=Checksum(f"https://get.helm.sh/{helm_asset}.sha256sum", helm_asset),
        ),
        Tool(
            name="yq",
            version=yq,
            url=yq_url,
            checksum=Checksum(
                f"https://github.com/mikefarah/yq/releases/download/{yq}/checksums",
                f"yq_linux_{arch}",
            ),
        ),
        Tool(
            name="jq",
            version=jq,
            url=f"{jq_base}/{jq_asset}",
            checksum=Checksum(f"{jq_base}/sha256sum.txt", jq_asset),
        ),
        Tool(
            name="task",
            version=task,
            url=f"{task_base}/{task_asset}",
            checksum=Checksum(f"{task_base}/task_checksums.txt", task_asset),
        ),
        Tool(
            name="sops",
            version=sops,
            url=f"{sops_base}/{sops_asset}",
            checksum=Checksum(f"{sops_base}/sops-{sops}.checksums.txt", sops_asset),
        ),
        Tool(
            name="age",
            version=age,
            url=f"https://github.com/FiloSottile/age/releases/download/{age}"
            f"/age-{age}-linux-{arch}.tar.gz",
            binaries=("age", "age-keygen"),
            # age signs its releases with sigsum proofs only; there is no
            # checksum file to compare against without pulling in sigsum-verify.
            unverified_reason="upstream publishes sigsum proofs, not checksums",
        ),
        Tool(
            name="talosctl",
            version=talosctl,
            url=f"{talos_base}/{talosctl_asset}",
            checksum=Checksum(f"{talos_base}/sha256sum.txt", talosctl_asset),
        ),
        Tool(
            name="talhelper",
            version=talhelper,
            url=f"{talhelper_base}/{talhelper_asset}",
            checksum=Checksum(f"{talhelper_base}/checksums.txt", talhelper_asset),
        ),
        Tool(
            name="kubeconform",
            version=kubeconform,
            url=f"{kubeconform_base}/{kubeconform_asset}",
            checksum=Checksum(f"{kubeconform_base}/CHECKSUMS", kubeconform_asset),
        ),
        Tool(
            name="flate",
            version=flate,
            url=f"{flate_base}/{flate_asset}",
            checksum=Checksum(f"{flate_base}/{flate_asset}.sha256"),
        ),
    ]


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.read()
    except urllib.error.HTTPError as err:
        raise SystemExit(f"GET {url} failed: HTTP {err.code} {err.reason}") from err
    except urllib.error.URLError as err:
        raise SystemExit(f"GET {url} failed: {err.reason}") from err


def parse_sha256(text: str, key: str | None) -> str:
    """Pull the expected hash out of a checksum file.

    Handles both a bare ``<hash>`` file and the usual ``<hash>  <filename>``
    listing, including the ``*name`` and ``./name`` spellings ``sha256sum``
    emits.
    """
    entries: dict[str, str] = {}
    lone: str | None = None

    for line in text.splitlines():
        fields = line.split()
        if not fields or not SHA256_RE.match(fields[0]):
            continue
        if len(fields) == 1:
            lone = fields[0]
            continue
        name = fields[-1]
        name = name[1:] if name.startswith("*") else name
        entries[name.removeprefix("./")] = fields[0]

    if key is not None and key in entries:
        return entries[key]
    if lone is not None:
        return lone
    if key is None and len(entries) == 1:
        return next(iter(entries.values()))
    raise SystemExit(f"no SHA-256 for {key!r} in checksum file")


def parse_yq_sha256(checksums: str, order: str, key: str) -> str:
    """yq publishes one row per asset with a dozen digests side by side.

    ``checksums_hashes_order`` names the column each digest sits in.
    """
    columns = [line.strip() for line in order.splitlines() if line.strip()]
    try:
        column = columns.index("SHA-256")
    except ValueError as err:
        raise SystemExit("yq checksums_hashes_order has no SHA-256 column") from err

    for line in checksums.splitlines():
        fields = line.split()
        if not fields or fields[0] != key:
            continue
        digests = fields[1:]
        if column >= len(digests):
            raise SystemExit(f"yq checksum row for {key} is missing column {column}")
        digest = digests[column]
        if not SHA256_RE.match(digest):
            raise SystemExit(f"yq SHA-256 column for {key} is not a digest: {digest}")
        return digest
    raise SystemExit(f"no row for {key!r} in yq checksums")


def expected_digest(tool: Tool) -> Digest | None:
    if tool.digest is not None:
        return tool.digest
    if tool.checksum is None:
        return None
    if tool.name == "yq":
        order_url = tool.checksum.url + "_hashes_order"
        return Digest(
            "sha256",
            parse_yq_sha256(
                fetch(tool.checksum.url).decode(),
                fetch(order_url).decode(),
                tool.checksum.key or "",
            ),
        )
    return Digest("sha256", parse_sha256(fetch(tool.checksum.url).decode(), tool.checksum.key))


def extract(tool: Tool, payload: bytes) -> dict[str, bytes]:
    """Return ``{binary name: contents}`` for everything the tool installs."""
    if not tool.is_archive:
        return {tool.name: payload}

    found: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            name = Path(member.name).name
            if name not in tool.wanted:
                continue
            if name in found:
                raise SystemExit(f"{tool.name}: {name} appears twice in the archive")
            handle = archive.extractfile(member)
            if handle is None:
                raise SystemExit(f"{tool.name}: cannot read {member.name}")
            found[name] = handle.read()

    missing = [name for name in tool.wanted if name not in found]
    if missing:
        raise SystemExit(f"{tool.name}: {', '.join(missing)} not found in the archive")
    return found


def install(tool: Tool, dest: Path) -> None:
    print(f"==> {tool.name} {tool.version}", flush=True)
    print(f"    {tool.url}", flush=True)

    payload = fetch(tool.url)
    wanted = expected_digest(tool)
    algorithm = wanted.algorithm if wanted else "sha256"
    actual = hashlib.new(algorithm, payload).hexdigest()

    if wanted is None:
        print(
            f"    {algorithm} {actual} (unverified: {tool.unverified_reason})",
            flush=True,
        )
    elif actual != wanted.value:
        raise SystemExit(
            f"{tool.name}: {algorithm} mismatch\n"
            f"  expected {wanted.value}\n"
            f"  got      {actual}"
        )
    else:
        print(f"    {algorithm} {actual} ok", flush=True)

    for name, contents in extract(tool, payload).items():
        path = dest / name
        path.write_bytes(contents)
        path.chmod(0o755)
        print(f"    installed {path}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arch", required=True, choices=ARCHES, help="TARGETARCH")
    parser.add_argument(
        "--dest", required=True, type=Path, help="directory to stage binaries into"
    )
    args = parser.parse_args()

    args.dest.mkdir(parents=True, exist_ok=True)
    for tool in tools(args.arch):
        install(tool, args.dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())

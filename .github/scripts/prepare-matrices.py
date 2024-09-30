"""Build a GHA matrix for building container images."""

#!/usr/bin/env python3

import importlib.util
import json
import os
import sys
from os.path import isfile
from subprocess import check_output

import requests
import yaml

repo_owner = os.environ.get("REPO_OWNER", os.environ.get("GITHUB_REPOSITORY_OWNER"))

TESTABLE_PLATFORMS = ["linux/amd64"]


def load_metadata_file_yaml(file_path):
    """Load app metadata from a YAML file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_metadata_file_json(file_path):
    """Load app metadata from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_latest_version_py(latest_py_path, channel_name):
    """Get the latest version of a container image using a Python script."""
    spec = importlib.util.spec_from_file_location("latest", latest_py_path)
    latest = importlib.util.module_from_spec(spec)
    sys.modules["latest"] = latest
    spec.loader.exec_module(latest)
    return latest.get_latest(channel_name)


def get_latest_version_sh(latest_sh_path, channel_name):
    """Get the latest version of a container image using a shell script."""
    out = check_output([latest_sh_path, channel_name])
    return out.decode("utf-8").strip()


def get_latest_version(subdir, channel_name):
    """Get the latest version of a container image."""
    ci_dir = os.path.join(subdir, "ci")
    if os.path.isfile(os.path.join(ci_dir, "latest.py")):
        return get_latest_version_py(os.path.join(ci_dir, "latest.py"), channel_name)
    elif os.path.isfile(os.path.join(ci_dir, "latest.sh")):
        return get_latest_version_sh(os.path.join(ci_dir, "latest.sh"), channel_name)
    elif os.path.isfile(os.path.join(subdir, channel_name, "latest.py")):
        return get_latest_version_py(
            os.path.join(subdir, channel_name, "latest.py"), channel_name
        )
    elif os.path.isfile(os.path.join(subdir, channel_name, "latest.sh")):
        return get_latest_version_sh(
            os.path.join(subdir, channel_name, "latest.sh"), channel_name
        )
    return None


def get_published_version(image_name):
    """Get the latest published version of a container image."""
    r = requests.get(
        f"https://api.github.com/users/{repo_owner}/packages/container/{image_name}/versions",
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "token " + os.environ["TOKEN"],
        },
        timeout=10,
    )

    if r.status_code != 200:
        return None

    data = json.loads(r.text)
    for image in data:
        tags = image["metadata"]["container"]["tags"]
        if "rolling" in tags:
            tags.remove("rolling")
            # Assume the longest string is the complete version number
            return max(tags, key=len)


def get_image_builds(subdir, meta, for_release=False, force=False, channels=None):
    """Returns the image builds for a given app."""
    image_builds = {"images": [], "imagePlatforms": []}

    if channels is None:
        channels = meta["channels"]
    else:
        channels = [
            channel for channel in meta["channels"] if channel["name"] in channels
        ]

    for channel in channels:
        version = get_latest_version(subdir, channel["name"])
        if version is None:
            continue

        # Image Name
        build_spec = {}
        if channel.get("stable", False):
            build_spec["name"] = meta["app"]
        else:
            build_spec["name"] = "-".join([meta["app"], channel["name"]])

        # Skip if latest version already published
        if not force:
            published = get_published_version(build_spec["name"])
            if published is not None and published == version:
                continue
            build_spec["published_version"] = published

        build_spec["version"] = version

        # Image Tags
        build_spec["tags"] = ["rolling", version]
        if meta.get("semver", False):
            parts = version.split(".")[:-1]
            while len(parts) > 0:
                build_spec["tags"].append(".".join(parts))
                parts = parts[:-1]

        # Platform Metadata
        for platform in channel["platforms"]:

            if platform not in TESTABLE_PLATFORMS and not for_release:
                continue

            build_spec.setdefault("platforms", []).append(platform)

            target_os = platform.split("/")[0]
            target_arch = platform.split("/")[1]

            platform_build = {}
            platform_build["name"] = build_spec["name"]
            platform_build["platform"] = platform
            platform_build["target_os"] = target_os
            platform_build["target_arch"] = target_arch
            platform_build["version"] = version
            platform_build["channel"] = channel["name"]
            platform_build["label_type"] = "org.opencontainers.image"

            if isfile(os.path.join(subdir, channel["name"], "Dockerfile")):
                platform_build["dockerfile"] = os.path.join(
                    subdir, channel["name"], "Dockerfile"
                )
                platform_build["context"] = os.path.join(subdir, channel["name"])
                platform_build["goss_config"] = os.path.join(
                    subdir, channel["name"], "goss.yaml"
                )
            else:
                platform_build["dockerfile"] = os.path.join(subdir, "Dockerfile")
                platform_build["context"] = subdir
                platform_build["goss_config"] = os.path.join(subdir, "ci", "goss.yaml")

            platform_build["goss_args"] = (
                "tail -f /dev/null"
                if channel["tests"].get("type", "web") == "cli"
                else ""
            )

            platform_build["tests_enabled"] = (
                channel["tests"]["enabled"] and platform in TESTABLE_PLATFORMS
            )

            image_builds["imagePlatforms"].append(platform_build)
        image_builds["images"].append(build_spec)
    return image_builds


def main():
    """main"""
    apps = sys.argv[1]
    for_release = sys.argv[2] == "true"
    force = sys.argv[3] == "true"
    image_builds = {"images": [], "imagePlatforms": []}

    if apps != "all":
        channels = None
        apps = apps.split(",")
        if len(sys.argv) == 5:
            channels = sys.argv[4].split(",")

        for app in apps:
            if not os.path.exists(os.path.join("./apps", app)):
                print(f'App "{app}" not found')
                exit(1)

            meta = None
            if os.path.isfile(os.path.join("./apps", app, "metadata.yaml")):
                meta = load_metadata_file_yaml(
                    os.path.join("./apps", app, "metadata.yaml")
                )
            elif os.path.isfile(os.path.join("./apps", app, "metadata.json")):
                meta = load_metadata_file_json(
                    os.path.join("./apps", app, "metadata.json")
                )

            app_image_builds = get_image_builds(
                os.path.join("./apps", app),
                meta,
                for_release,
                force=force,
                channels=channels,
            )
            if app_image_builds is not None:
                image_builds["images"].extend(app_image_builds["images"])
                image_builds["imagePlatforms"].extend(
                    app_image_builds["imagePlatforms"]
                )
    else:
        for subdir, _, files in os.walk("./apps"):
            for file in files:
                meta = None
                if file == "metadata.yaml":
                    meta = load_metadata_file_yaml(os.path.join(subdir, file))
                elif file == "metadata.json":
                    meta = load_metadata_file_json(os.path.join(subdir, file))
                else:
                    continue
                if meta is not None:
                    app_image_builds = get_image_builds(
                        subdir, meta, for_release, force=force
                    )
                    if app_image_builds is not None:
                        image_builds["images"].extend(app_image_builds["images"])
                        image_builds["imagePlatforms"].extend(
                            app_image_builds["imagePlatforms"]
                        )
    print(json.dumps(image_builds))


if __name__ == "__main__":
    main()

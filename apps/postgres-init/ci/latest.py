"""Fetch the latest version of an Alpine package."""

import io
import re
import sys
import tarfile

import requests


def get_latest_version(
    package_name: str, repo: str = "v3.19/main", arch: str = "x86_64"
) -> str | None:
    """
    Fetches the latest version of a package from the specified Alpine repository.

    Args:
    - package_name (str): Name of the package to search.
    - repo (str): Alpine repository (e.g., v3.19/main). Defaults to v3.19/main.
    - arch (str): Architecture of the package. Defaults to x86_64.

    Returns:
    - str: Latest version of the package, or None if not found.
    """
    # URL of the APKINDEX file for the specified repository
    url = f"https://dl-cdn.alpinelinux.org/alpine/{repo}/{arch}/APKINDEX.tar.gz"

    try:
        # Fetch the APKINDEX file
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching APKINDEX: {e}", file=sys.stderr)
        return None

    # Extract the tar.gz file in memory
    tar_bytes = io.BytesIO(response.content)

    try:
        with tarfile.open(fileobj=tar_bytes, mode="r:gz") as tar:
            apkindex_data = None
            # Iterate over files in the tar archive
            for member in tar.getmembers():
                if member.name == "APKINDEX":
                    apkindex_file = tar.extractfile(member)
                    if apkindex_file is None:
                        print("Error extracting APKINDEX file.", file=sys.stderr)
                        return None
                    apkindex_data = apkindex_file.read().decode("utf-8")
                    break
            if apkindex_data is None:
                print("APKINDEX file not found in the tar archive.", file=sys.stderr)
                return None
    except tarfile.TarError as e:
        print(f"Error extracting APKINDEX: {e}", file=sys.stderr)
        return None

    # Use regular expression to find the package version
    package_info_pattern = rf"P:{package_name}\nV:([^-\n]+)"
    match = re.search(package_info_pattern, apkindex_data)

    if match:
        return match.group(1)  # The version is captured in group 1
    else:
        return None


def get_latest(_: str) -> str | None:
    """Get the latest version of the PostgreSQL client."""
    return get_latest_version("postgresql16-client")


if __name__ == "__main__":
    version = get_latest("stable")
    print(f"{version}")

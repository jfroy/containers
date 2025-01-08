import sys
import os

sys.path.append(os.path.abspath("scripts"))

from apksearch import apksearch


def get_latest(_: str) -> str | None:
    return apksearch("postgresql16-client", repo="v3.21/main")


if __name__ == "__main__":
    version = get_latest("stable")
    print(f"{version}")

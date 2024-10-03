#!/usr/bin/env bash
version=$(curl -sX GET "https://api.github.com/repos/nfs-ganesha/nfs-ganesha/releases/latest" | jq --raw-output '.tag_name')
version="${version#*V}"
version="${version#*release-}"
printf "%s" "${version}"

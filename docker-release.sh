#!/usr/bin/env sh
# Build and upload the release to PyPI from a clean Python container, so it
# doesn't depend on the Python install on this machine. Runs build.sh and
# release.sh as they are. PyPI credentials come from ~/.pypirc or the
# TWINE_USERNAME and TWINE_PASSWORD environment variables.
set -eu

cd "$(dirname "$0")"

if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    echo "You have uncommitted changes. Commit or stash them before releasing." >&2
    exit 1
fi

set -- --rm -v "$PWD:/src:ro" -e TWINE_USERNAME -e TWINE_PASSWORD
if [ -f "$HOME/.pypirc" ]; then
    set -- "$@" -v "$HOME/.pypirc:/root/.pypirc:ro"
fi
# twine asks for credentials when it finds none, which needs a terminal.
if [ -t 0 ]; then
    set -- "$@" -it
fi

# The source is mounted read-only and copied, so the build runs on a clean
# copy and leaves nothing owned by root in the checkout.
docker run "$@" python:3.12-slim sh -euc '
    cp -R /src /build
    cd /build
    rm -rf build dist
    pip install --quiet --root-user-action=ignore "build>=1.0" "twine>=5.0"
    ./build.sh
    ./release.sh
'

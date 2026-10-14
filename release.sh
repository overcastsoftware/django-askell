#!/usr/bin/env sh
set -eu

VERSION="0.1.26"

python3 -m twine check "dist/django_askell-${VERSION}"*
python3 -m twine upload "dist/django_askell-${VERSION}"*

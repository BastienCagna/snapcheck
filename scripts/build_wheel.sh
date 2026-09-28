#!/bin/bash
# Build the wheel (pip / uv) of snapcheck in ./output/wheels, including the built frontend.
#
# Usage: scripts/build_wheel.sh FORGE
# FORGE (or $LEPTON_FORGE) is a local conda channel providing the lepton-app package: the frontend
# is built against its @lepton/core library, in a copy of the sources.
set -euo pipefail

PIXI="${PIXI_EXE:-pixi}"

if [ "${1:-}" = "--in-env" ]; then
    # In the build environment, from the copy of the sources
    cd "$(dirname "$0")/.."
    OUT="$2"
    export PYTHONDONTWRITEBYTECODE=1

    npm pkg set "dependencies.@lepton/core=file:$CONDA_PREFIX/share/lepton/core"
    npm install
    PYTHONPATH=python python -m lepton.build_api python/snapserve/__main__.py:app .
    npm run build

    cp -r dist python/snapclient/frontend
    uv build --wheel -o "$OUT"
    exit 0
fi

FORGE="${1:-${LEPTON_FORGE:-}}"
if [ -z "$FORGE" ]; then
    echo "Usage: $0 FORGE (or set LEPTON_FORGE): local conda channel providing lepton-app" >&2
    exit 1
fi
FORGE="$(realpath -m "$FORGE")"
if [ ! -f "$FORGE/noarch/repodata.json" ]; then
    echo "Error: $FORGE is not a conda channel (no noarch/repodata.json)" >&2
    exit 1
fi

cd "$(dirname "$0")/.."
OUT="$PWD/output/wheels"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# Copy the sources, without the local builds and dependencies
tar -c --exclude=./.git --exclude=./.pixi --exclude=./node_modules --exclude=./dist \
    --exclude=./build --exclude=./output --exclude='*.egg-info' \
    --exclude=./python/snapclient/frontend . | tar -x -C "$WORK"

rm -rf "$OUT"
mkdir -p "$OUT"
# Build environment: lepton-app (@lepton/core and the API generator), node and the python
# dependencies needed to load the backend app when generating its API client
"$PIXI" exec -c "file://$FORGE" -c https://prefix.dev/conda-forge \
    --spec lepton-app --spec nodejs --spec uv \
    --spec beautifulsoup4 --spec pypdf --spec "xhtml2pdf>=0.2.16,<0.2.17" \
    -- bash "$WORK/scripts/build_wheel.sh" --in-env "$OUT"
ls "$OUT"

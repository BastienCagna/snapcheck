#!/bin/bash
# Build the conda packages of this project (recipe/recipe.yaml) in ./output,
# and publish them in a local forge (conda channel).
#
# Usage: scripts/conda.sh build [FORGE]
#        scripts/conda.sh publish FORGE    (build then publish)
# FORGE (or $LEPTON_FORGE) is the local conda channel. It also provides the dependencies which
# are not on conda-forge (lepton-common, lepton-app...) when building.
set -euo pipefail

usage() {
    echo "Usage: $0 build [FORGE] | publish FORGE  (FORGE can also be set with LEPTON_FORGE)" >&2
    exit 1
}

CMD="${1:-}"
FORGE="${2:-${LEPTON_FORGE:-}}"
[ -n "$FORGE" ] && FORGE="$(realpath -m "$FORGE")"
cd "$(dirname "$0")/.."

PIXI="${PIXI_EXE:-pixi}"

build() {
    local channels=()
    if [ -f "$FORGE/noarch/repodata.json" ]; then
        channels+=(-c "file://$FORGE")
    elif [ -n "$FORGE" ] && [ "$CMD" = build ]; then
        echo "Error: $FORGE is not a conda channel (no noarch/repodata.json)" >&2
        exit 1
    fi
    channels+=(-c https://prefix.dev/conda-forge)
    rm -rf output/noarch
    "$PIXI" exec --spec "rattler-build>=0.72" -- \
        rattler-build build -r recipe --output-dir output "${channels[@]}"
}

publish() {
    mkdir -p "$FORGE/noarch"
    # A published package must never change (its index entry and the caches would be stale)
    for pkg in output/noarch/*.conda; do
        dest="$FORGE/noarch/$(basename "$pkg")"
        if [ -e "$dest" ] && ! cmp -s "$pkg" "$dest"; then
            echo "Error: $(basename "$pkg") is already published with a different content." >&2
            echo "Increase build.number (or the version) in recipe/recipe.yaml and rebuild." >&2
            exit 1
        fi
    done
    cp -n output/noarch/*.conda "$FORGE/noarch/"
    "$PIXI" exec --spec rattler-index -- rattler-index fs "$FORGE"
    echo "Published in $FORGE: $(cd output/noarch && ls *.conda | tr '\n' ' ')"
}

case "$CMD" in
    build)
        build
        ;;
    publish)
        [ -n "$FORGE" ] || usage
        build
        publish
        ;;
    *)
        usage
        ;;
esac

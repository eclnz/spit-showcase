#!/bin/sh
# Download elevation tiles from the Terrain Tiles open dataset on AWS into
# data/tiles/: 2 × 2 tiles at zoom 11 around three mountains.
# https://registry.opendata.aws/terrain-tiles/, attribution in its README.
set -eu
base=https://s3.amazonaws.com/elevation-tiles-prod/geotiff/11
cd "$(dirname "$0")"
# region, then the tile at its top left
for spec in rainier:331:721 fuji:1813:808 matterhorn:1067:728; do
    region=${spec%%:*}; rest=${spec#*:}; x0=${rest%%:*}; y0=${rest#*:}
    mkdir -p "data/tiles/$region"
    for x in $x0 $((x0 + 1)); do
        for y in $y0 $((y0 + 1)); do
            curl -sSfL -o "data/tiles/$region/${x}_${y}.tif" "$base/$x/$y.tif"
        done
    done
done
ls -R data

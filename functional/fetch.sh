#!/bin/sh
# Download the first run of the task scan of the first SUBJECTS subjects of
# OpenNeuro ds000001 into data/: 3 by default, 16 at most, about 47 MB each.
# https://openneuro.org/datasets/ds000001, CC0.
set -eu
subjects=${SUBJECTS:-3}
base=https://s3.amazonaws.com/openneuro.org/ds000001
cd "$(dirname "$0")"
n=1
while [ "$n" -le "$subjects" ]; do
    sub=$(printf '%02d' "$n")
    name=sub-${sub}_task-balloonanalogrisktask_run-01_bold.nii.gz
    mkdir -p "data/sub-$sub/func"
    [ -s "data/sub-$sub/func/$name" ] || curl -sSfL -o "data/sub-$sub/func/$name" "$base/sub-$sub/func/$name"
    n=$((n + 1))
done
ls data

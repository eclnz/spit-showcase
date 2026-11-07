#!/bin/sh
# Download the T1-weighted image of the first SUBJECTS subjects of OpenNeuro
# ds000001 into data/: 4 by default, 16 at most, about 5 MB each.
# https://openneuro.org/datasets/ds000001, CC0.
set -eu
subjects=${SUBJECTS:-4}
base=https://s3.amazonaws.com/openneuro.org/ds000001
cd "$(dirname "$0")"
n=1
while [ "$n" -le "$subjects" ]; do
    sub=$(printf '%02d' "$n")
    mkdir -p "data/sub-$sub/anat"
    [ -s "data/sub-$sub/anat/sub-${sub}_T1w.nii.gz" ] ||
        curl -sSfL -o "data/sub-$sub/anat/sub-${sub}_T1w.nii.gz" "$base/sub-$sub/anat/sub-${sub}_T1w.nii.gz"
    n=$((n + 1))
done
ls data

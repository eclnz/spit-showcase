#!/bin/sh
# Download the T1 and the first task run of the first SUBJECTS subjects of
# OpenNeuro ds000001 into data/: 6 by default, 16 at most, about 53 MB each.
# https://openneuro.org/datasets/ds000001, CC0.
set -eu
subjects=${SUBJECTS:-6}
base=https://s3.amazonaws.com/openneuro.org/ds000001
cd "$(dirname "$0")"
get() {
    [ -s "data/$1" ] || { mkdir -p "$(dirname "data/$1")"; curl -sSfL -o "data/$1" "$base/$1"; }
}
n=1
while [ "$n" -le "$subjects" ]; do
    sub=$(printf '%02d' "$n")
    get "sub-$sub/anat/sub-$sub""_T1w.nii.gz"
    get "sub-$sub/func/sub-$sub""_task-balloonanalogrisktask_run-01_bold.nii.gz"
    n=$((n + 1))
done
# What FSL supplies: the MNI152 template and its mask, and the FIX classifier
# trained on the Whitehall II standard-sequence data.
: "${FSLDIR:?FSLDIR is not set: install FSL 6.0.7 or later}"
mkdir -p data/standard
cp "$FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz" "$FSLDIR/data/standard/MNI152_T1_2mm_brain_mask.nii.gz" data/standard/
cp "$(find "$FSLDIR/lib" -name Standard.pyfix_model | head -n 1)" data/standard/
# The number of components of each group ICA, as the paper's two. The files are
# empty: their names carry the number.
mkdir -p data/dims
: > data/dims/d-30.txt
: > data/dims/d-100.txt
ls data

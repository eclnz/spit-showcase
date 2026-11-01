"""Write a few facts about a T1-weighted image as JSON: its grid, its voxel size
and a signal-to-noise ratio.

    summarise.py T1.nii.gz summary.json

The signal is the mean of the voxels above Otsu's threshold, and the noise is
the standard deviation of the eight corners of the volume, which hold air. An
image whose corners are exactly zero, as in one that has had its background
removed, has no noise to measure, and its ratio is null.
"""

import json
import sys

import nibabel as nib
import numpy as np
from dipy.segment.threshold import otsu

CORNER = 8


def main(t1: str, summary: str) -> None:
    image = nib.load(t1)
    data = image.get_fdata(dtype=np.float32)
    signal = data[data > otsu(data)].mean()
    corners = [
        data[x : x + CORNER, y : y + CORNER, z : z + CORNER]
        for x in (0, data.shape[0] - CORNER)
        for y in (0, data.shape[1] - CORNER)
        for z in (0, data.shape[2] - CORNER)
    ]
    noise = np.concatenate([corner.ravel() for corner in corners]).std()
    voxel = image.header.get_zooms()[:3]
    facts = {
        "voxels": "x".join(str(n) for n in data.shape),
        "voxel_mm": round(float(np.prod(voxel)) ** (1 / 3), 2),
        "orientation": "".join(nib.aff2axcodes(image.affine)),
        "snr": round(float(signal / noise), 1) if noise > 0 else None,
        "zero_percent": round(float((data == 0).mean()) * 100),
    }
    with open(summary, "w") as out:
        json.dump(facts, out)


if __name__ == "__main__":
    main(*sys.argv[1:])

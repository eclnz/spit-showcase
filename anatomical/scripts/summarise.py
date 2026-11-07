"""Write a few facts about a T1-weighted image as JSON: its grid, its voxel size
and a signal-to-noise ratio.

    summarise.py T1.nii.gz summary.json

The signal is the mean of the voxels above Otsu's threshold, and the noise is
the standard deviation of the air: the voxels between zero and a quarter of
that threshold. An image with air in fewer than 1% of its voxels, as one whose
background has been removed, has no noise to measure, and its ratio is null.
"""

import json
import sys

import nibabel as nib
import numpy as np
from dipy.segment.threshold import otsu

AIR_SHARE = 0.01


def main(t1: str, summary: str) -> None:
    image = nib.load(t1)
    data = image.get_fdata(dtype=np.float32)
    threshold = otsu(data)
    signal = data[data > threshold].mean()
    air = data[(data > 0) & (data < threshold / 4)]
    voxel = image.header.get_zooms()[:3]
    facts = {
        "voxels": "x".join(str(n) for n in data.shape),
        "voxel_mm": round(float(np.prod(voxel)) ** (1 / 3), 2),
        "orientation": "".join(nib.aff2axcodes(image.affine)),
        "snr": round(float(signal / air.std()), 1) if air.size >= AIR_SHARE * data.size else None,
        "zero_percent": round(float((data == 0).mean()) * 100),
    }
    with open(summary, "w") as out:
        json.dump(facts, out)


if __name__ == "__main__":
    main(*sys.argv[1:])

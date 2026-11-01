"""Mask the voxels whose mean signal is above a quarter of the way from zero to
the image's 98th percentile, which keeps the head and drops the air.

    mask.py mean.nii.gz mask.nii.gz
"""

import sys

import nibabel as nib
import numpy as np


def main(mean: str, mask: str) -> None:
    image = nib.load(mean)
    data = image.get_fdata(dtype=np.float32)
    inside = data > np.percentile(data, 98) / 4
    nib.save(nib.Nifti1Image(inside.astype(np.uint8), image.affine), mask)


if __name__ == "__main__":
    main(*sys.argv[1:])

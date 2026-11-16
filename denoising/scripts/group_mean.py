"""Write the mean over runs of their dual-regression maps, component by component.

    group_mean.py mean.nii.gz maps1.nii.gz maps2.nii.gz ...
"""

import sys

import nibabel as nib
import numpy as np


def main(out: str, *maps: str) -> None:
    images = [nib.load(path) for path in maps]
    mean = np.mean([image.get_fdata(dtype=np.float32) for image in images], axis=0)
    nib.save(nib.Nifti1Image(mean, images[0].affine, images[0].header), out)


if __name__ == "__main__":
    main(*sys.argv[1:])

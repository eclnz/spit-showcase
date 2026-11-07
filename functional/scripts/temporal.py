"""Write the mean image of a BOLD run over time, and its temporal SNR: each
voxel's mean over its standard deviation.

    temporal.py bold.nii.gz mean.nii.gz tsnr.nii.gz
"""

import sys

import nibabel as nib
import numpy as np


def main(bold: str, mean: str, tsnr: str) -> None:
    image = nib.load(bold)
    data = image.get_fdata(dtype=np.float32)
    average = data.mean(axis=-1)
    spread = data.std(axis=-1)
    ratio = np.divide(average, spread, out=np.zeros_like(average), where=spread > 0)
    for path, volume in ((mean, average), (tsnr, ratio)):
        nib.save(nib.Nifti1Image(volume, image.affine), path)


if __name__ == "__main__":
    main(*sys.argv[1:])

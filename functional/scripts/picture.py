"""Draw a temporal SNR map at three heights, with the outline of a mask.

    picture.py tsnr.nii.gz mask.nii.gz picture.png
"""

import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np


def main(tsnr: str, mask: str, picture: str) -> None:
    data = nib.load(tsnr).get_fdata()
    inside = nib.load(mask).get_fdata() > 0
    top = np.percentile(data[inside], 99)
    figure, axes = plt.subplots(1, 3, figsize=(9, 3.2))
    for z, ax in zip((data.shape[2] // 4, data.shape[2] // 2, 3 * data.shape[2] // 4), axes):
        shown = ax.imshow(np.rot90(data[:, :, z]), cmap="viridis", vmin=0, vmax=top)
        ax.contour(np.rot90(inside[:, :, z]), levels=[0.5], colors="white", linewidths=0.6)
        ax.axis("off")
    figure.colorbar(shown, ax=axes, shrink=0.8, label="temporal SNR")
    figure.savefig(picture, dpi=100)


if __name__ == "__main__":
    main(*sys.argv[1:])

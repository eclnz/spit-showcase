"""Draw the middle slice of each axis of an image.

    mosaic.py T1.nii.gz mosaic.png
"""

import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np


def main(t1: str, picture: str) -> None:
    data = nib.load(t1).get_fdata()
    top = np.percentile(data, 99.5)
    figure, axes = plt.subplots(1, 3, figsize=(9, 3.2))
    for axis, ax in enumerate(axes):
        middle = data.shape[axis] // 2
        ax.imshow(np.rot90(np.take(data, middle, axis=axis)), cmap="gray", vmax=top)
        ax.axis("off")
    figure.tight_layout()
    figure.savefig(picture, dpi=100)


if __name__ == "__main__":
    main(*sys.argv[1:])

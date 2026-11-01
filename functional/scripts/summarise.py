"""Write the median temporal SNR inside a mask, and the mask's size, as JSON.

    summarise.py tsnr.nii.gz mask.nii.gz summary.json
"""

import json
import sys

import nibabel as nib
import numpy as np


def main(tsnr: str, mask: str, summary: str) -> None:
    inside = nib.load(mask).get_fdata() > 0
    values = nib.load(tsnr).get_fdata()[inside]
    facts = {"mask_voxels": int(inside.sum()), "median_tsnr": round(float(np.median(values)), 1)}
    with open(summary, "w") as out:
        json.dump(facts, out)


if __name__ == "__main__":
    main(*sys.argv[1:])

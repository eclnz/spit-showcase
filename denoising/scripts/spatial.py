"""Correlate each component's group-mean dual-regression map with its template.

    spatial.py group.gica none.nii.gz soft.nii.gz aggressive.nii.gz out.tsv
"""

import sys

import nibabel as nib
import numpy as np


def main(group: str, none: str, soft: str, aggressive: str, out: str) -> None:
    inside = nib.load(f"{group}/mask.nii.gz").get_fdata() > 0
    template = nib.load(f"{group}/melodic_IC.nii.gz").get_fdata()[inside]
    maps = [nib.load(path).get_fdata()[inside] for path in (none, soft, aggressive)]
    with open(out, "w") as table:
        table.write("component\tnone\tsoft\taggressive\n")
        for c in range(template.shape[1]):
            r = [np.corrcoef(template[:, c], m[:, c])[0, 1] for m in maps]
            table.write(f"{c + 1}\t" + "\t".join(f"{x:.3f}" for x in r) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:])

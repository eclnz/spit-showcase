"""Summarise one run's dual-regression time series before and after cleaning.

    analyse.py none.txt soft.txt aggressive.txt out.npz

Each input holds one column per group component. The output holds, for the soft
and aggressive cleanings, each component's amplitude relative to the uncleaned
run, and for all three the mean power spectrum, scaled by the uncleaned
amplitude, and the full and regularised partial correlation matrices as
z-scores.
"""

import sys

import numpy as np

TR = 2.0
RIDGE = 0.1


def spectrum(series: np.ndarray, scale: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    scaled = (series - series.mean(axis=0)) / scale
    power = np.abs(np.fft.rfft(scaled, axis=0)) ** 2 / len(scaled)
    return np.fft.rfftfreq(len(scaled), TR), np.median(power, axis=1)


def netmats(series: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    full = np.corrcoef(series, rowvar=False)
    partial = np.linalg.inv(full + RIDGE * np.eye(len(full)))
    partial = -partial / np.sqrt(np.outer(np.diag(partial), np.diag(partial)))
    np.fill_diagonal(partial, 0)
    np.fill_diagonal(full, 0)
    return np.arctanh(np.clip(full, -0.999, 0.999)), np.arctanh(np.clip(partial, -0.999, 0.999))


def main(none: str, soft: str, aggressive: str, out: str) -> None:
    runs = [np.loadtxt(path, ndmin=2) for path in (none, soft, aggressive)]
    base = runs[0].std(axis=0)
    spectra = [spectrum(run, base) for run in runs]
    mats = [netmats(run) for run in runs]
    np.savez_compressed(
        out,
        amplitude=np.stack([run.std(axis=0) / base for run in runs[1:]]),
        freq=spectra[0][0],
        spectra=np.stack([power for _, power in spectra]),
        full=np.stack([full for full, _ in mats]),
        partial=np.stack([partial for _, partial in mats]),
    )


if __name__ == "__main__":
    main(*sys.argv[1:])

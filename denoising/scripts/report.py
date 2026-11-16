"""Compare the cleanings across runs: amplitude, power spectra and networks.

    report.py report.png summary.tsv run1.npz run2.npz ...

The figure shows each component's amplitude after cleaning, relative to the
uncleaned run, and the mean power spectra, with and without scaling by the
power at the highest frequencies, where thermal noise dominates. The table
gives the numbers behind it, and how closely the cleanings' group-mean network
matrices agree.
"""

import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

NAMES = ["none", "soft", "aggressive"]
COLOURS = ["#c0392b", "#27ae60", "#2c3e50"]


def upper(matrix: np.ndarray) -> np.ndarray:
    return matrix[np.triu_indices_from(matrix, k=1)]


def main(figure: str, table: str, *paths: str) -> None:
    runs = [np.load(path) for path in paths]
    freq = runs[0]["freq"]
    amplitude = np.mean([run["amplitude"] for run in runs], axis=0)
    spectra = np.mean([run["spectra"] for run in runs], axis=0)
    thermal = spectra[:, -max(1, len(freq) // 12):].mean(axis=1, keepdims=True)
    rows = [("runs", len(runs)), ("components", amplitude.shape[1])]
    for name, values in zip(NAMES[1:], amplitude):
        rows.append((f"median_amplitude_{name}", round(float(np.median(values)), 3)))
    for name, power, floor in zip(NAMES, spectra, thermal):
        rows.append((f"contrast_to_noise_{name}", round(float(power[freq < 0.1].mean() / floor[0]), 2)))
    for kind in ("full", "partial"):
        group = [np.mean([run[kind][i] for run in runs], axis=0) for i in range(3)]
        for i, j in ((0, 1), (0, 2), (1, 2)):
            r = np.corrcoef(upper(group[i]), upper(group[j]))[0, 1]
            rows.append((f"{kind}_netmat_r_{NAMES[i]}_vs_{NAMES[j]}", round(float(r), 3)))
    with open(table, "w") as out:
        out.write("metric\tvalue\n")
        out.writelines(f"{name}\t{value}\n" for name, value in rows)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    axes[0].boxplot(list(amplitude), tick_labels=NAMES[1:])
    axes[0].set(title="Time series amplitude", ylabel="relative to uncleaned")
    for name, colour, power, floor in zip(NAMES, COLOURS, spectra, thermal):
        axes[1].semilogy(freq, power, color=colour, label=name)
        axes[2].semilogy(freq, power / floor, color=colour, label=name)
    axes[1].set(title="Power spectra", xlabel="Hz", ylabel="power")
    axes[2].set(title="Scaled by high-frequency power", xlabel="Hz")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(figure, dpi=110)


if __name__ == "__main__":
    main(*sys.argv[1:])

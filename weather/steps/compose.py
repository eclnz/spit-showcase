"""Lay the six panels out as one figure, pixel for pixel, and letter them."""

import argparse

import matplotlib.image
import matplotlib.pyplot as plt

from plot_style import DPI, HEIGHT, INK, WIDTH, place, save

LETTERS = "abcdef"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", dest="out", required=True)
    parser.add_argument("panels", nargs=6, help="panels a to f, in order")
    args = parser.parse_args()

    fig = plt.figure(figsize=(WIDTH, HEIGHT), dpi=DPI)
    for letter, path in zip(LETTERS, args.panels):
        image = matplotlib.image.imread(path)
        left, top = place(letter)
        height = image.shape[0] / DPI
        fig.figimage(image, xo=round(left * DPI), yo=round((HEIGHT - top - height) * DPI), origin="upper")
        fig.text((left + 0.02) / WIDTH, 1 - (top + 0.02) / HEIGHT, letter, fontsize=9, fontweight="bold",
                 ha="left", va="top", color=INK)
    save(fig, args.out)


if __name__ == "__main__":
    main()

"""Panel d: how far each site's day is from its own region's that day."""

import argparse

import matplotlib.pyplot as plt
import numpy as np

from plot_style import INK, MISSING, day_axis, panel, region_strip, save, site_grid, site_order, summaries_args

# Keep in step with panel_alerts.py and panel_drift.py, which share this row.
BOTTOM, TOP = 0.62, 0.3


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    summaries_args(parser)
    args = parser.parse_args()

    order = site_order(args.sites, args.regions)
    days, grid = site_grid(args.summaries, order)
    limit = 3.0
    cmap = plt.get_cmap("RdBu_r").copy()
    cmap.set_bad(MISSING)

    fig, ax = panel("d", left=0.55, bottom=BOTTOM, top=TOP, right=0.05)
    image = ax.imshow(np.ma.masked_invalid(grid), aspect="auto", cmap=cmap, vmin=-limit, vmax=limit, interpolation="nearest")
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([args.sites[i] for i in order], fontsize=5.5)
    ax.tick_params(axis="y", length=0, pad=7)
    for spine in ax.spines.values():
        spine.set_visible(False)
    region_strip(ax, order, args.regions)
    day_axis(ax, days)
    cax = ax.inset_axes([0.0, -0.13, 0.28, 0.025])
    bar = fig.colorbar(image, cax=cax, orientation="horizontal")
    bar.set_ticks([-limit, 0, limit])
    bar.set_ticklabels([f"−{limit:g}", "0", f"+{limit:g}"])
    bar.ax.tick_params(labelsize=5.5, width=0.5, length=2)
    bar.outline.set_linewidth(0.5)
    cax.text(1.04, 0.5, "anomaly (°C)", transform=cax.transAxes, fontsize=6, va="center", ha="left", color=INK)
    save(fig, args.out)


if __name__ == "__main__":
    main()

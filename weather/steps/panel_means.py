"""Panel c: each region's daily mean, and every site's."""

import argparse
from collections import defaultdict

import matplotlib.dates as mdates

from plot_style import INK, date, panel, region_colours, rows, save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regions", required=True, help="the regional table")
    parser.add_argument("--days", required=True, help="the network's table")
    parser.add_argument("-o", dest="out", required=True)
    args = parser.parse_args()

    by_region = defaultdict(list)
    for r in rows(args.regions):
        by_region[r["region"]].append((date(r["day"]), float(r["mean"])))

    fig, ax = panel("c", left=0.42, bottom=0.4, right=0.08)
    palette = region_colours(by_region)
    for region in sorted(by_region):
        points = sorted(by_region[region])
        ax.plot([p[0] for p in points], [p[1] for p in points], color=palette[region], linewidth=0.8, label=region)
    network = sorted((date(r["day"]), float(r["mean"])) for r in rows(args.days))
    ax.plot([p[0] for p in network], [p[1] for p in network], color=INK, linewidth=1.5, label="all sites")
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 4, 7, 10)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.set_ylabel("temperature (°C)")
    low, high = ax.get_ylim()
    ax.set_ylim(low, high + 0.3 * (high - low))
    ax.legend(loc="upper left", fontsize=5.5, ncol=2, columnspacing=0.9, handlelength=1.2)
    save(fig, args.out)


if __name__ == "__main__":
    main()

"""Panel a: the land, and where each site stands on it, coloured by region."""

import argparse
import json

import numpy as np

from plot_style import INK, panel, region_colours, rows, save

SEA = "#d6e6f2"


def place_labels(ax, points):
    """Name each point on whichever side of it overlaps nothing named before it."""
    renderer = ax.figure.canvas.get_renderer()
    taken = [(cx - 4, cy - 4, cx + 4, cy + 4) for cx, cy in (ax.transData.transform((x, y)) for x, y, _ in points)]
    sides = [((4, 0), "left", "center"), ((-4, 0), "right", "center"), ((0, 4), "center", "bottom"),
             ((0, -4), "center", "top")]
    for x, y, name in points:
        best = None
        for offset, ha, va in sides:
            label = ax.annotate(name, (x, y), xytext=offset, textcoords="offset points", ha=ha, va=va,
                                fontsize=4.8, color=INK, zorder=4)
            box = label.get_window_extent(renderer)
            clash = sum(not (box.x1 < a or box.x0 > c or box.y1 < b or box.y0 > d) for a, b, c, d in taken)
            if best is None or clash < best[0]:
                if best:
                    best[1].remove()
                best = (clash, label, box)
            else:
                label.remove()
            if clash == 0:
                break
        taken.append((best[2].x0, best[2].y0, best[2].x1, best[2].y1))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terrain", required=True)
    parser.add_argument("--regions", nargs="+", required=True)
    parser.add_argument("--sites", nargs="+", required=True)
    parser.add_argument("-o", dest="out", required=True)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    grid = rows(args.terrain)
    xs = sorted({float(r["x_km"]) for r in grid})
    ys = sorted({float(r["y_km"]) for r in grid})
    height = np.full((len(ys), len(xs)), np.nan)
    for r in grid:
        height[ys.index(float(r["y_km"])), xs.index(float(r["x_km"]))] = float(r["elevation_m"])
    land = np.ma.masked_less(height, 0)

    fig, ax = panel("a", left=0.4, bottom=0.32, right=0.12)
    ax.set_facecolor(SEA)
    ax.contourf(xs, ys, land, levels=np.arange(0, land.max() + 100, 100), cmap="Greys", vmin=-600, vmax=1400)
    lines = ax.contour(xs, ys, land, levels=np.arange(200, land.max(), 200), colors="#777777", linewidths=0.3)
    ax.clabel(lines, fontsize=4, fmt="%d m", inline_spacing=1)

    palette = region_colours(args.regions)
    points = []
    for region, site, path in zip(args.regions, args.sites, args.files, strict=True):
        with open(path) as f:
            spot = json.load(f)
        ax.scatter(spot["x_km"], spot["y_km"], s=14, color=palette[region], edgecolor="white", linewidth=0.5, zorder=3)
        points.append((spot["x_km"], spot["y_km"], site))
    place_labels(ax, points)
    for region, colour in palette.items():
        ax.scatter([], [], s=14, color=colour, label=region)
    # In the corner with the fewest sites, so the legend hides none.
    corners = {"lower left": (min(xs), min(ys)), "lower right": (max(xs), min(ys)),
               "upper left": (min(xs), max(ys)), "upper right": (max(xs), max(ys))}
    corner = min(corners, key=lambda c: sum(1 for x, y, _ in points
                                           if abs(x - corners[c][0]) < 35 and abs(y - corners[c][1]) < 30))
    ax.legend(loc=corner, fontsize=5, handletextpad=0.1, borderaxespad=0.3, framealpha=0.85,
              frameon=True, edgecolor="none")

    ax.set_xlim(min(xs), max(xs))
    ax.set_ylim(min(ys), max(ys))
    ax.set_aspect("equal")
    ax.set_xlabel("km")
    ax.set_ylabel("km")
    save(fig, args.out)


if __name__ == "__main__":
    main()

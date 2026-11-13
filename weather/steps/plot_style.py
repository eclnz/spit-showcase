"""What every panel of the figure shares: its size and place, colours, fonts, and the order of the sites."""

import csv
import datetime

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DPI = 300
WIDTH = 7.09  # 180 mm, a journal's two-column figure
GAP = 0.12  # between rows

# Each panel's size in inches, by row. Keep in step with `place` below, which
# lays the rows out, and with each panel's margins, so that panels in one row
# line their axes up.
ROWS = [
    {"a": (2.45, 2.55), "b": (2.15, 2.55), "c": (2.49, 2.55)},
    {"d": (3.70, 3.00), "e": (1.20, 3.00), "f": (2.19, 3.00)},
]
HEIGHT = sum(max(h for _, h in row.values()) for row in ROWS) + GAP * (len(ROWS) - 1)

# Okabe-Ito colours, which stay apart for readers with colour-blindness. Regions
# and alerts take them in name order, so a new one takes the next colour.
REGION_PALETTE = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#F0E442", "#56B4E9", "#D55E00"]
ALERT_PALETTE = ["#56B4E9", "#D55E00", "#F0E442", "#009E73", "#CC79A7"]
INK = "#222222"
MUTED = "#8a8a8a"
MISSING = "#d4d4d4"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7,
    "axes.linewidth": 0.6,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": INK,
    "ytick.color": INK,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "legend.frameon": False,
})


def size(name):
    for row in ROWS:
        if name in row:
            return row[name]
    raise KeyError(name)


def place(name):
    """A panel's top-left corner on the figure, in inches from the top-left."""
    top = 0.0
    for row in ROWS:
        left = 0.0
        for key, (w, h) in row.items():
            if key == name:
                return left, top
            left += w
        top += max(h for _, h in row.values()) + GAP
    raise KeyError(name)


def panel(name, left, bottom, right=0.08, top=0.22):
    """A figure the panel's size, with one axes inside the given margins, in inches."""
    w, h = size(name)
    fig = plt.figure(figsize=(w, h), dpi=DPI)
    ax = fig.add_axes([left / w, bottom / h, 1 - (left + right) / w, 1 - (bottom + top) / h])
    return fig, ax


def save(fig, path):
    fig.savefig(path, dpi=DPI, format="png", metadata={"Software": None})


def rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def date(text):
    return datetime.date.fromisoformat(text)


def colours(names, palette):
    """A colour for each name, given in name order and taken from the palette in turn."""
    return {name: palette[k % len(palette)] for k, name in enumerate(sorted(set(names)))}


def region_colours(regions):
    return colours(regions, REGION_PALETTE)


def alert_colours(alerts):
    return colours(alerts, ALERT_PALETTE)


def site_order(sites, regions):
    """Sites grouped by region, then by name, as every site-by-site panel lists them."""
    return sorted(range(len(sites)), key=lambda i: (regions[i], sites[i]))


def region_strip(ax, order, regions):
    """A bar of each site's region colour beside its row, and a white line between regions."""
    from matplotlib.patches import Rectangle

    palette = region_colours(regions)
    for row, i in enumerate(order):
        ax.add_patch(Rectangle((-0.014, row - 0.5), 0.009, 1, transform=ax.get_yaxis_transform(), clip_on=False,
                               facecolor=palette[regions[i]], edgecolor="none"))
        if row and regions[order[row - 1]] != regions[i]:
            ax.axhline(row - 0.5, color="white", linewidth=1.4)


def day_axis(ax, days):
    """A tick at the first column of each quarter."""
    ticks, seen = [], set()
    for k, d in enumerate(days):
        quarter = (d.year, (d.month - 1) // 3)
        if quarter not in seen and d.month in (1, 4, 7, 10):
            seen.add(quarter)
            ticks.append(k)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{days[k]:%b}" for k in ticks])


def site_grid(summaries, order):
    """Each site's daily anomaly, a row a site and a column a day, with NaN where it has no day.

    The columns run from the first day any site has to the last, at the spacing the
    days are kept at, so a kept day that no site has is an empty column rather
    than left out.
    """
    from collections import Counter

    import numpy as np

    tables = [rows(summaries[i]) for i in order]
    seen = sorted({date(r["day"]) for t in tables for r in t})
    gaps = Counter((b - a).days for a, b in zip(seen, seen[1:]))
    step = gaps.most_common(1)[0][0] if gaps else 1
    days = [seen[0] + datetime.timedelta(days=k) for k in range(0, (seen[-1] - seen[0]).days + 1, step)]
    index = {d: k for k, d in enumerate(days)}
    grid = np.full((len(order), len(days)), np.nan)
    for row, table in enumerate(tables):
        for r in table:
            grid[row, index[date(r["day"])]] = float(r["anomaly"])
    return days, grid


def summaries_args(parser):
    """The arguments of a panel drawn from every site's summary."""
    parser.add_argument("--regions", nargs="+", required=True)
    parser.add_argument("--sites", nargs="+", required=True)
    parser.add_argument("-o", dest="out", required=True)
    parser.add_argument("summaries", nargs="+")

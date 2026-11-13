"""Panel f: each site's mean anomaly against its drift, with the outliers named.

A site is an outlier when it lies more than 3.5 robust standard deviations from
the median of all sites, the cut-off Iglewicz and Hoaglin recommend. An outlier
in drift is a sensor going wrong, if it also drifts further than a sensor could
by chance; one in mean anomaly alone is a warm or cool place.
"""

import argparse
import statistics

from plot_style import INK, MUTED, panel, region_colours, rows, save
from panel_anomaly import BOTTOM, TOP

CUTOFF = 3.5
# How far, in °C a year, a sound sensor can wander. Sites drift together by less
# than this, so a drift can be unusual among them and still not be a fault.
TOLERANCE = 1.0


def robust_spread(values):
    """The median, and a standard deviation one or two extreme values can't inflate: 1.4826 × the median absolute deviation."""
    median = statistics.median(values)
    return median, 1.4826 * statistics.median([abs(v - median) for v in values]) or 1.0


def robust_z(values):
    """How far each value is from the median, in robust standard deviations."""
    median, spread = robust_spread(values)
    return [(v - median) / spread for v in values]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("league")
    parser.add_argument("-o", dest="out", required=True)
    args = parser.parse_args()

    league = rows(args.league)
    means = [float(r["anomaly"]) for r in league]
    drifts = [float(r["drift"]) for r in league]
    palette = region_colours([r["region"] for r in league])

    fig, ax = panel("f", left=0.5, bottom=BOTTOM, top=TOP, right=0.08)
    (x_median, x_spread), (y_median, y_spread) = robust_spread(means), robust_spread(drifts)
    # The band is where a site is not named: within the cut-off on both axes and, for
    # drift, within what a sound sensor can wander.
    x_band, y_band = CUTOFF * x_spread, max(CUTOFF * y_spread, TOLERANCE)

    # Fit both axes to the ordinary sites and the cut-off band; a site beyond them sits at the
    # edge, with an arrow and its value, so one extreme site doesn't squash the rest.
    ordinary = [k for k, (zm, zd) in enumerate(zip(robust_z(means), robust_z(drifts))) if not (abs(zd) > CUTOFF and abs(drifts[k]) > TOLERANCE)]
    xs = [means[k] for k in ordinary] + [x_median - x_band, x_median + x_band]
    ys = [drifts[k] for k in ordinary] + [y_median - y_band, y_median + y_band]
    x_lim = (min(xs) - 0.12 * (max(xs) - min(xs)), max(xs) + 0.12 * (max(xs) - min(xs)))
    y_lim = (min(ys) - 0.25 * (max(ys) - min(ys)), max(ys) + 0.45 * (max(ys) - min(ys)))
    ax.set_xlim(*x_lim)
    ax.set_ylim(*y_lim)
    ax.fill_between([x_median - x_band, x_median + x_band], y_median - y_band, y_median + y_band,
                    color=MUTED, alpha=0.15, linewidth=0, zorder=0)
    ax.axhline(0, color=MUTED, linewidth=0.5, zorder=1)
    ax.axvline(0, color=MUTED, linewidth=0.5, zorder=1)

    for r, mean, drift, z_mean, z_drift in zip(league, means, drifts, robust_z(means), robust_z(drifts)):
        colour = palette[r["region"]]
        x = min(max(mean, x_lim[0]), x_lim[1])
        if drift > y_lim[1] or drift < y_lim[0]:
            top = drift > y_lim[1]
            edge = y_lim[1] if top else y_lim[0]
            ax.annotate("", (x, edge), xytext=(0, -14 if top else 14), textcoords="offset points",
                        arrowprops=dict(arrowstyle="-|>", color=colour, linewidth=1, mutation_scale=7))
            name = f"{r['site']} (sensor drift, {drift:+.1f})" if abs(z_drift) > CUTOFF and abs(drift) > TOLERANCE else f"{r['site']} ({drift:+.1f})"
            ax.annotate(name.replace("-", "\u2212"), (x, edge), xytext=(-5, -9 if top else 9), textcoords="offset points",
                        fontsize=6, color=INK, ha="right", va="center")
            continue
        ax.scatter(mean, drift, s=18, color=colour, edgecolor="white", linewidth=0.5, zorder=3)
        if abs(z_drift) > CUTOFF and abs(drift) > TOLERANCE:
            note = f"{r['site']} (sensor drift)"
        elif abs(z_mean) > CUTOFF:
            note = f"{r['site']} ({'warm' if mean > 0 else 'cool'} site)"
        else:
            continue
        # Under its point, running in towards the middle, so it can't be read as another site's.
        right_half = mean > (x_lim[0] + x_lim[1]) / 2
        ax.annotate(note, (mean, drift), xytext=(4 if right_half else -4, -6), textcoords="offset points", fontsize=6,
                    color=INK, ha="right" if right_half else "left", va="top")
    ax.set_xlabel("mean anomaly (°C)")
    ax.set_ylabel("drift (°C per year)")
    save(fig, args.out)


if __name__ == "__main__":
    main()

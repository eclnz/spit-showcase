"""Panel b: one site's day as its sensor read it, once its calibration is undone, and once cleaned."""

import argparse
import json
from pathlib import Path

import numpy as np

from plot_style import INK, MUTED, date, panel, rows, save

CALIBRATED = "#0072B2"


def hourly(path, day=None):
    """A day's 24 temperatures, from a day's file or, given the day, from a series."""
    table = [r for r in rows(path) if day is None or r["day"] == day]
    return [float(r["temperature"]) for r in sorted(table, key=lambda r: int(r["hour"]))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True)
    parser.add_argument("--calibration", required=True)
    parser.add_argument("--clean", required=True, help="the site's cleaned series")
    parser.add_argument("-o", dest="out", required=True)
    args = parser.parse_args()

    region, site, day = Path(args.raw).with_suffix("").parts[-3:]
    raw = np.array(hourly(args.raw))
    clean = hourly(args.clean, day)
    hours = np.arange(24)
    good = raw > -900
    with open(args.calibration) as f:
        cal = json.load(f)
    calibrated = (raw - cal["offset"]) / cal["gain"]

    # Hours that cleaning replaced: dropouts, and readings it changed (the file keeps three decimals).
    clean = np.array(clean)
    spike = good & (np.abs(calibrated - clean) > 0.01)
    filled = ~good | spike

    fig, ax = panel("b", left=0.42, bottom=0.4)
    # The raw line breaks at a spike, which an arrow at the axis edge marks instead. The
    # cleaned day is whole: the calibrated readings, with the filled hours in their place.
    shown = good & ~spike
    ax.plot(hours, np.where(shown, raw, np.nan), color=MUTED, linewidth=0.8, marker="o", markersize=1.6, label="raw")
    ax.plot(hours, clean, color=CALIBRATED, linewidth=1.2, label="calibrated and cleaned")
    ax.plot(hours[filled], clean[filled], linestyle="none", marker="x", color=INK, markersize=4,
            markeredgewidth=1, label="filled in", zorder=4)

    # Fit the axis to the ordinary readings, so a spike doesn't flatten the rest.
    ordinary = np.concatenate([raw[good & ~spike], calibrated[good & ~spike], clean])
    low, high = ordinary.min(), ordinary.max()
    pad = 0.15 * (high - low)
    # Room below the lines for the legend.
    ax.set_ylim(low - 4 * pad, high + 2 * pad)
    bottom, top = ax.get_ylim()
    for h in hours[spike]:
        edge = bottom if calibrated[h] < bottom else top
        ax.annotate(f"spike, {raw[h]:.0f} °C".replace("-", "\u2212"), (h, edge), xytext=(0, 14 if edge == bottom else -14),
                    textcoords="offset points", fontsize=5.5, color=INK, ha="center",
                    va="bottom" if edge == bottom else "top",
                    arrowprops=dict(arrowstyle="->", color=MUTED, linewidth=0.6))
    for h in hours[~good]:
        ax.annotate("dropout", (h, clean[h]), xytext=(0, -7), textcoords="offset points",
                    fontsize=5.5, color=INK, ha="center", va="top")

    # The calibration's shift, drawn at the good hour furthest from any filled one, so its
    # label stays clear of theirs.
    distance = np.array([min((abs(h - f) for f in hours[filled]), default=24) for h in hours])
    hour = int(np.argmax(np.where(good, distance, -1)))
    ax.annotate("", (hour, calibrated[hour]), xytext=(hour, raw[hour]),
                arrowprops=dict(arrowstyle="->", color=CALIBRATED, linewidth=0.8, shrinkA=0, shrinkB=0))
    right = hour < 12
    ax.annotate(f"calibration\ngain {cal['gain']:g}\noffset {cal['offset']:+g}".replace("-", "\u2212"),
                (hour, (raw[hour] + calibrated[hour]) / 2), xytext=(5 if right else -5, 0), textcoords="offset points",
                fontsize=5.5, color=CALIBRATED, ha="left" if right else "right", va="center")
    ax.set_xlim(-0.5, 23.5)
    ax.set_xticks([0, 6, 12, 18, 23])
    ax.set_xlabel("hour")
    ax.set_ylabel("temperature (°C)")
    ax.text(1, 1, f"{site}, {date(day):%-d %b}", transform=ax.transAxes, ha="right", va="top", fontsize=6, color=MUTED)
    ax.legend(loc="lower center", fontsize=5.5, ncol=3, columnspacing=0.8, handlelength=1.4)
    save(fig, args.out)


if __name__ == "__main__":
    main()

"""Clean a site's days into one series: undo the sensor's calibration, and replace dropouts and spikes by interpolation."""

import argparse
import json

from table import read_hourly, write_series

# A reading this far from the median of its neighbours is a spike.
SPIKE = 8.0


def clean_day(raw, cal, name):
    """One day's 24 readings, calibrated, with bad hours interpolated from the good ones either side."""
    values = [None if r <= -900 else (r - cal["offset"]) / cal["gain"] for r in raw]

    for i, v in enumerate(values):
        if v is None:
            continue
        near = [values[j] for j in (i - 2, i - 1, i + 1, i + 2) if 0 <= j < len(values) and values[j] is not None]
        if near and abs(v - sorted(near)[len(near) // 2]) > SPIKE:
            values[i] = None

    good = [i for i, v in enumerate(values) if v is not None]
    if not good:
        raise SystemExit(f"{name}: no usable readings")
    filled = []
    for i, v in enumerate(values):
        if v is not None:
            filled.append(v)
            continue
        before = max((j for j in good if j < i), default=None)
        after = min((j for j in good if j > i), default=None)
        if before is None or after is None:
            filled.append(values[before if after is None else after])
        else:
            w = (i - before) / (after - before)
            filled.append(values[before] * (1 - w) + values[after] * w)
    return filled


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calibration", required=True)
    parser.add_argument("--days", nargs="+", required=True)
    parser.add_argument("-o", dest="out", required=True)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    with open(args.calibration) as f:
        cal = json.load(f)
    series = {day: clean_day(read_hourly(path, "temperature"), cal, path)
              for day, path in zip(args.days, args.files, strict=True)}
    write_series(args.out, series)


if __name__ == "__main__":
    main()

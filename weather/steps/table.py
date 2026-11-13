"""Shared reading and writing of the small CSV files the steps pass on.

A series is a site's or a region's temperatures over many days: a row for each
day and hour, with columns `day`, `hour` and `temperature`.
"""

import csv
from collections import defaultdict


def read_hourly(path, column):
    """The 24 values of one day's file, in hour order."""
    with open(path, newline="") as f:
        rows = sorted(csv.DictReader(f), key=lambda r: int(r["hour"]))
    return [float(r[column]) for r in rows]


def read_series(path):
    """A series, as {day: [24 temperatures in hour order]}."""
    days = defaultdict(dict)
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            days[r["day"]][int(r["hour"])] = float(r["temperature"])
    return {day: [hours[h] for h in sorted(hours)] for day, hours in sorted(days.items())}


def write_series(path, series):
    write_rows(path, ["day", "hour", "temperature"],
               [(day, h, fmt(t)) for day, hours in sorted(series.items()) for h, t in enumerate(hours)])


def write_rows(path, header, rows):
    with open(path, "w", newline="") as f:
        out = csv.writer(f, lineterminator="\n")
        out.writerow(header)
        out.writerows(rows)


def fmt(value):
    return f"{value:.3f}"

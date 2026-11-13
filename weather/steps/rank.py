"""Rank sites by how far they drift from their region over the days they have.

A site's drift is the slope of its daily anomaly, in degrees a year: a
sensor going wrong drifts, while a site that is simply warm or cool does not.
"""

import argparse
import csv
import datetime

from table import fmt, write_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regions", nargs="+", required=True)
    parser.add_argument("--sites", nargs="+", required=True)
    parser.add_argument("-o", dest="out", required=True)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    rows = []
    for region, site, path in zip(args.regions, args.sites, args.files, strict=True):
        with open(path, newline="") as f:
            table = list(csv.DictReader(f))
        days = [datetime.date.fromisoformat(r["day"]).toordinal() for r in table]
        values = [float(r["anomaly"]) for r in table]
        rows.append((abs(drift(days, values)), drift(days, values), sum(values) / len(values), region, site, len(values)))
    rows.sort(reverse=True)
    write_rows(args.out, ["rank", "region", "site", "drift", "anomaly", "days"],
               [(i + 1, region, site, fmt(d), fmt(mean), n) for i, (_, d, mean, region, site, n) in enumerate(rows)])


def drift(days, values):
    """The least-squares slope of values against days, in units a year."""
    n = len(days)
    mx, my = sum(days) / n, sum(values) / n
    sxx = sum((x - mx) ** 2 for x in days)
    if sxx == 0:
        return 0.0
    return 365 * sum((x - mx) * (y - my) for x, y in zip(days, values)) / sxx


if __name__ == "__main__":
    main()

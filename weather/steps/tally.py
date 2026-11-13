"""On how many of a site's days an alert went off, and for how many hours in all."""

import argparse
import json

from table import read_series, write_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--alert", required=True)
    parser.add_argument("--threshold", required=True)
    parser.add_argument("-o", dest="out", required=True)
    parser.add_argument("series")
    args = parser.parse_args()

    with open(args.threshold) as f:
        threshold = json.load(f)
    if "below" in threshold:
        hours = [sum(t < threshold["below"] for t in day) for day in read_series(args.series).values()]
    else:
        hours = [sum(t > threshold["above"] for t in day) for day in read_series(args.series).values()]
    write_rows(args.out, ["alert", "days", "hours", "of_days"], [(args.alert, sum(h > 0 for h in hours), sum(hours), len(hours))])


if __name__ == "__main__":
    main()

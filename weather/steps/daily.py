"""One row a day of a series' mean, low and high, for each region given, or for one series."""

import argparse

from table import fmt, read_series, write_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regions", nargs="+", help="each file's region, if they have one")
    parser.add_argument("-o", dest="out", required=True)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    regions = args.regions or [None] * len(args.files)
    header = (["region"] if args.regions else []) + ["day", "mean", "low", "high"]
    rows = []
    for region, path in zip(regions, args.files, strict=True):
        for day, hours in read_series(path).items():
            row = [day, fmt(sum(hours) / len(hours)), fmt(min(hours)), fmt(max(hours))]
            rows.append(([region] if args.regions else []) + row)
    write_rows(args.out, header, rows)


if __name__ == "__main__":
    main()

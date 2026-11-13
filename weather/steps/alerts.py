"""One row for each site and alert: on how many days it went off."""

import argparse
import csv

from table import write_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regions", nargs="+", required=True)
    parser.add_argument("--sites", nargs="+", required=True)
    parser.add_argument("--alerts", nargs="+", required=True)
    parser.add_argument("-o", dest="out", required=True)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    rows = []
    for region, site, alert, path in zip(args.regions, args.sites, args.alerts, args.files, strict=True):
        with open(path, newline="") as f:
            row = next(csv.DictReader(f))
        rows.append((region, site, alert, row["days"], row["of_days"]))
    write_rows(args.out, ["region", "site", "alert", "days", "of_days"], rows)


if __name__ == "__main__":
    main()

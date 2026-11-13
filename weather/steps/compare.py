"""How far a site is from its region each day: the mean over the day's hours of site minus region."""

import argparse

from table import fmt, read_series, write_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("readings")
    parser.add_argument("baseline")
    parser.add_argument("out")
    args = parser.parse_args()

    site, region = read_series(args.readings), read_series(args.baseline)
    rows = [(day, fmt(sum(s - r for s, r in zip(hours, region[day])) / 24)) for day, hours in site.items()]
    write_rows(args.out, ["day", "anomaly"], rows)


if __name__ == "__main__":
    main()

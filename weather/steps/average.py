"""Take the median of several series, hour by hour, over the sites each day has.

A median rather than a mean, so that one faulty sensor cannot move its region's
baseline, and every other site in the region is compared with what the region
actually did.
"""

import argparse
import statistics
from collections import defaultdict

from table import read_series, write_series


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-o", dest="out", required=True)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    days = defaultdict(list)
    for path in args.files:
        for day, hours in read_series(path).items():
            days[day].append(hours)
    write_series(args.out, {day: [statistics.median(hour) for hour in zip(*sites)] for day, sites in days.items()})


if __name__ == "__main__":
    main()

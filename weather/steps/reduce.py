"""Reduce a site's series to sea level: add 6.5 °C for each kilometre of the site's height.

Sites in one region stand at different heights, and height alone makes a site
colder. Reduced to sea level, they can be compared for what height doesn't
explain: a town, shade, or a hollow that pools cold air.
"""

import argparse
import json

from table import read_series, write_series

LAPSE = 6.5 / 1000  # °C a metre


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--location", required=True)
    parser.add_argument("-o", dest="out", required=True)
    parser.add_argument("series")
    args = parser.parse_args()

    with open(args.location) as f:
        metres = json.load(f)["elevation_m"]
    series = read_series(args.series)
    write_series(args.out, {day: [t + LAPSE * metres for t in hours] for day, hours in series.items()})


if __name__ == "__main__":
    main()

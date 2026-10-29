"""Print a tab-separated table of one number per file, with a column for each dimension.

SPIT gives each dimension's values, one per file, in the order it gives the
files, so row i is made of the i-th value of each:

    table.py --speaker george george --digit 3 4 --take 0 0 --seconds a.txt b.txt

prints a header, then `george  3  0  <a.txt's number>` and the row for b.txt.
"""

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    for column in ("speaker", "digit", "take"):
        parser.add_argument(f"--{column}", nargs="+", required=True)
    parser.add_argument("--seconds", nargs="+", required=True, metavar="FILE")
    args = parser.parse_args()
    columns = [args.speaker, args.digit, args.take]
    if any(len(values) != len(args.seconds) for values in columns):
        parser.error("each dimension needs one value per file")
    print("\t".join(["speaker", "digit", "take", "seconds"]))
    for *values, path in zip(*columns, args.seconds):
        print("\t".join([*values, Path(path).read_text().strip()]))


if __name__ == "__main__":
    main()

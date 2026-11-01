"""Print a tab-separated table with a row for each JSON file: its dimensions, then its fields.

SPIT gives each dimension's values, one per file, in the order it gives the
files, so row i is made of the i-th value of each:

    table.py --sub 01 02 --run 1 1 --summaries a.json b.json

prints a header, then `01  1` and the fields of a.json, and the row for b.json.
"""

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sub", nargs="+", required=True)
    parser.add_argument("--run", nargs="+", required=True)
    parser.add_argument("--summaries", nargs="+", required=True, metavar="FILE")
    args = parser.parse_args()
    if any(len(values) != len(args.summaries) for values in (args.sub, args.run)):
        parser.error("each dimension needs one value per file")
    rows = [json.loads(Path(path).read_text()) for path in args.summaries]
    fields = list(rows[0])
    print("\t".join(["sub", "run", *fields]))
    for sub, run, row in zip(args.sub, args.run, rows):
        print("\t".join([sub, run, *(str(row[field]) for field in fields)]))


if __name__ == "__main__":
    main()

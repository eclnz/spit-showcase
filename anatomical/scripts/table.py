"""Print a tab-separated table with a row for each JSON file: its subject, then its fields.

SPIT gives each dimension's values, one per file, in the order it gives the
files, so row i is made of the i-th value of each:

    table.py --sub 01 02 --summaries a.json b.json

prints a header, then `01` and the fields of a.json, and the row for b.json.
A field that is null is written `n/a`.
"""

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sub", nargs="+", required=True)
    parser.add_argument("--summaries", nargs="+", required=True, metavar="FILE")
    args = parser.parse_args()
    if len(args.sub) != len(args.summaries):
        parser.error("each dimension needs one value per file")
    rows = [json.loads(Path(path).read_text()) for path in args.summaries]
    fields = list(rows[0])
    print("\t".join(["sub", *fields]))
    for sub, row in zip(args.sub, rows):
        print("\t".join([sub, *("n/a" if row[field] is None else str(row[field]) for field in fields)]))


if __name__ == "__main__":
    main()

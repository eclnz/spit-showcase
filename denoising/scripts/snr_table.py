"""Print a tab-separated table of each run's median temporal SNR, before and after each cleaning.

SPIT gives each dimension's values, one per file, in the order it gives the
files, so row i is made of the i-th value of each:

    snr_table.py out.tsv --sub 01 02 --run 1 1 --none a b --soft c d --aggressive e f
"""

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out")
    parser.add_argument("--sub", nargs="+", required=True)
    parser.add_argument("--run", nargs="+", required=True)
    for cleaning in ("none", "soft", "aggressive"):
        parser.add_argument(f"--{cleaning}", nargs="+", required=True, metavar="FILE")
    args = parser.parse_args()
    columns = [args.sub, args.run, *(
        [f"{float(Path(path).read_text()):.1f}" for path in files]
        for files in (args.none, args.soft, args.aggressive)
    )]
    if any(len(column) != len(args.sub) for column in columns):
        parser.error("each option needs one value per run")
    with open(args.out, "w") as out:
        out.write("sub\trun\tnone\tsoft\taggressive\n")
        for row in zip(*columns):
            out.write("\t".join(row) + "\n")


if __name__ == "__main__":
    main()

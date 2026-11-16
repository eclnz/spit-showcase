"""Write how many ICA components FIX found in each run, and how many it called noise.

    components.py out.tsv --sub 01 02 --run 1 1 --labels a.txt b.txt

Each labels file is FIX's `fix4melview` list: a line for each component, and
last the list of the noise components.
"""

import argparse
import re
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out")
    parser.add_argument("--sub", nargs="+", required=True)
    parser.add_argument("--run", nargs="+", required=True)
    parser.add_argument("--labels", nargs="+", required=True, metavar="FILE")
    args = parser.parse_args()
    with open(args.out, "w") as out:
        out.write("sub\trun\tcomponents\tnoise\tnoise_fraction\n")
        for sub, run, path in zip(args.sub, args.run, args.labels):
            lines = Path(path).read_text().splitlines()
            components = sum(1 for line in lines if re.match(r"\d+,", line))
            noise = len(re.findall(r"\d+", lines[-1]))
            out.write(f"{sub}\t{run}\t{components}\t{noise}\t{noise / components:.2f}\n")


if __name__ == "__main__":
    main()

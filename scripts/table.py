"""Print a tab-separated table of one number per file, with a column for each entity in the files' names.

A file named `speaker=george_digit=3_take=0.txt` holding `0.41` gives the row
`george  3  0  0.41`. The names follow the pipeline's
`default entities: {@key}={@value} separated "_"`.
"""

import sys
from pathlib import Path


def entities(path: Path) -> dict[str, str]:
    return dict(part.split("=", 1) for part in path.name.split(".", 1)[0].split("_"))


def main(paths: list[str]) -> None:
    rows = [(entities(Path(p)), Path(p).read_text().strip()) for p in paths]
    keys = list(rows[0][0])
    print("\t".join([*keys, "value"]))
    for found, value in rows:
        print("\t".join([*(found[k] for k in keys), value]))


if __name__ == "__main__":
    main(sys.argv[1:])

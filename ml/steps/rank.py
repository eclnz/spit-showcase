"""Print scores as a table, best accuracy first: `rank.py COLUMN LABEL... -- SCORES...`
gives each score file's row the label in the same place."""
import json
import sys

import pandas as pd

column, rest = sys.argv[1], sys.argv[2:]
cut = rest.index("--")
rows = []
for label, path in zip(rest[:cut], rest[cut + 1 :]):
    with open(path) as f:
        rows.append({column: label, **json.load(f)})
frame = pd.DataFrame(rows).sort_values("accuracy", ascending=False)
frame.to_csv(sys.stdout, sep="\t", index=False, float_format="%.3f")

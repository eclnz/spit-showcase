#!/bin/sh
# Write scikit-learn's bundled datasets into data/datasets/ as CSV files, one
# per dataset, with the class in the last column. Nothing is downloaded.
set -eu
cd "$(dirname "$0")"
mkdir -p data/datasets
python3 - <<'PY'
from sklearn import datasets

for name in ("iris", "wine", "breast_cancer", "digits"):
    frame = getattr(datasets, f"load_{name}")(as_frame=True).frame
    frame.to_csv(f"data/datasets/{name.replace('_', '-')}.csv", index=False)
PY
ls data/datasets

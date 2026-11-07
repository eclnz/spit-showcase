"""Fit the model a spec describes to a training table, with the class in its
last column, and pickle it."""
import importlib
import json
import pickle
import sys

import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

MODULES = {
    "LogisticRegression": "sklearn.linear_model",
    "RandomForestClassifier": "sklearn.ensemble",
    "SVC": "sklearn.svm",
    "KNeighborsClassifier": "sklearn.neighbors",
    "DecisionTreeClassifier": "sklearn.tree",
}

cores, spec_path, train_path, output = sys.argv[1:]
with open(spec_path) as f:
    spec = json.load(f)
estimator = getattr(importlib.import_module(MODULES[spec["estimator"]]), spec["estimator"])
params = dict(spec["params"])
if "n_jobs" in estimator().get_params():
    params["n_jobs"] = int(cores)
steps = [StandardScaler()] if spec["scale"] else []
model = make_pipeline(*steps, estimator(**params))
train = pd.read_csv(train_path)
model.fit(train.iloc[:, :-1], train.iloc[:, -1])
with open(output, "wb") as f:
    pickle.dump(model, f)

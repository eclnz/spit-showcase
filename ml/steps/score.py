"""Print a fitted model's accuracy and macro F1 on a test table, as JSON."""
import json
import pickle
import sys

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score

fitted, test_path = sys.argv[1:]
with open(fitted, "rb") as f:
    model = pickle.load(f)
test = pd.read_csv(test_path)
truth, guess = test.iloc[:, -1], model.predict(test.iloc[:, :-1])
scores = {"accuracy": accuracy_score(truth, guess), "macro_f1": f1_score(truth, guess, average="macro")}
json.dump(scores, sys.stdout)

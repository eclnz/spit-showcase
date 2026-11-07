"""Split a dataset into a stratified training three quarters and a test quarter."""
import sys

import pandas as pd
from sklearn.model_selection import train_test_split

dataset, train_path, test_path = sys.argv[1:]
frame = pd.read_csv(dataset)
train, test = train_test_split(frame, test_size=0.25, stratify=frame[frame.columns[-1]], random_state=0)
train.to_csv(train_path, index=False)
test.to_csv(test_path, index=False)

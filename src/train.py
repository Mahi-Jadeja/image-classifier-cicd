import os
import json
import pickle
import numpy as np
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

with open("params.yaml") as f:
    params = yaml.safe_load(f)
proc_params = params["processing"]
train_params = params["train"]

processed_dir = proc_params["processed_dir"]
size = proc_params["image_size"]

# flatten images into vectors and scale pixels down to 0-1, random forest doesn't need raw images
X_train = np.load(os.path.join(processed_dir, "X_train.npy")).reshape(-1, size * size * 3) / 255.0
y_train = np.load(os.path.join(processed_dir, "y_train.npy"))
X_val = np.load(os.path.join(processed_dir, "X_val.npy")).reshape(-1, size * size * 3) / 255.0
y_val = np.load(os.path.join(processed_dir, "y_val.npy"))

model = RandomForestClassifier(
    n_estimators=train_params["n_estimators"],
    max_depth=train_params["max_depth"],
    random_state=train_params["random_state"],
)
model.fit(X_train, y_train)

acc = accuracy_score(y_val, model.predict(X_val))
print(f"Validation accuracy: {acc:.4f}")

os.makedirs(os.path.dirname(train_params["model_path"]), exist_ok=True)
with open(train_params["model_path"], "wb") as f:
    pickle.dump(model, f)

with open("data/metrics.json", "w") as f:
    json.dump({"accuracy": acc}, f)

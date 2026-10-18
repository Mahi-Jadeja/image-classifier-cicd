import os
import numpy as np
from PIL import Image
import yaml

with open("params.yaml") as f:
    params = yaml.safe_load(f)
data_params = params["data"]
proc_params = params["processing"]


def load_images():
    # loop through each class folder and resize everything to a fixed size for the model
    size = proc_params["image_size"]
    X, y = [], []
    for label, cls in enumerate(data_params["classes"]):
        cls_dir = os.path.join(data_params["raw_dir"], cls)
        for img_name in os.listdir(cls_dir):
            try:
                img = Image.open(os.path.join(cls_dir, img_name)).convert("RGB")
                img = img.resize((size, size))
                X.append(np.array(img))
                y.append(label)
            except Exception:
                # some images are corrupt/unreadable, just skip them instead of crashing
                continue
    return np.array(X), np.array(y)


def split_and_save(X, y):
    os.makedirs(proc_params["processed_dir"], exist_ok=True)
    idx = np.arange(len(X))
    np.random.shuffle(idx)
    X, y = X[idx], y[idx]

    split = int(len(X) * (1 - proc_params["validation_split"]))
    np.save(os.path.join(proc_params["processed_dir"], "X_train.npy"), X[:split])
    np.save(os.path.join(proc_params["processed_dir"], "y_train.npy"), y[:split])
    np.save(os.path.join(proc_params["processed_dir"], "X_val.npy"), X[split:])
    np.save(os.path.join(proc_params["processed_dir"], "y_val.npy"), y[split:])


if __name__ == "__main__":
    X, y = load_images()
    split_and_save(X, y)

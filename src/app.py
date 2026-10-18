import pickle
import numpy as np
from flask import Flask, jsonify

app = Flask(__name__)

# model is baked into the docker image at build time, loaded once at startup
with open("data/model/model.pkl", "rb") as f:
    model = pickle.load(f)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/predict")
def predict():
    # dummy random input just to prove the deployed model responds end to end
    dummy_input = np.random.rand(1, 64 * 64 * 3)
    pred = model.predict(dummy_input)[0]
    return jsonify({"prediction": int(pred)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

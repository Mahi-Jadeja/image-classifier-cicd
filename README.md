# Image Classification CI/CD Pipeline

An end-to-end MLOps project for training and serving a flower image classifier. The project uses DVC with Amazon S3 for data and model versioning, Flask for a prediction API, Docker for packaging, and GitHub Actions to build, publish, and deploy the container to an EC2 instance.

## Architecture

1. **Data and model versioning:** DVC defines the data collection, image processing, and model training stages. DVC artifacts are stored in the configured S3 remote.
2. **Model serving:** A Flask application loads the trained model when it starts and exposes health and prediction routes.
3. **Container build:** The Docker image includes the Flask application and `data/model/model.pkl`.
4. **Continuous deployment:** A push to `main` starts the GitHub Actions workflow. It retrieves the model from S3, builds and pushes the image to Docker Hub, then connects to EC2 over SSH to replace the running container.

## Project Structure

```text
.
├── .github/workflows/ci-cd.yaml  # Build, publish, and EC2 deployment workflow
├── src/
│   ├── app.py                    # Flask health and prediction API
│   ├── data_collection.py        # Downloads and selects flower images
│   ├── data_processing.py        # Resizes images and creates train/validation data
│   └── train.py                  # Trains and saves the classifier
├── data/
│   ├── model/model.pkl           # DVC-managed trained model
│   ├── processed/                # DVC-managed processed arrays
│   └── raw/                      # DVC-managed selected source images
├── Dockerfile
├── dvc.yaml                      # DVC pipeline stages
├── params.yaml                   # Dataset, processing, and training settings
└── requirements.txt
```

## API

The service listens on port `5000`.

| Route | Method | Description | Example response |
|---|---|---|---|
| `/health` | `GET` | Confirms that the API is responding. | `{"status":"ok"}` |
| `/predict` | `GET` | Returns a prediction from the loaded model. | `{"prediction":0}` |

Currently `/predict` uses a randomly generated input vector as a deployment smoke test; it does not accept an image upload. Prediction values are the classifier's integer class labels.

## Run Locally

Requirements: Python 3.10 or newer, Git, and AWS credentials with read access to the configured DVC S3 remote.

1. Clone the repository and enter the project directory:

   ```bash
   git clone https://github.com/Mahi-Jadeja/image-classifier-cicd.git
   cd image-classifier-cicd
   ```

2. Create an environment, install dependencies, and retrieve the model:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   dvc pull data/model/model.pkl
   ```

3. Start the API:

   ```bash
   python src/app.py
   ```

   Check the service with `curl http://localhost:5000/health` or `curl http://localhost:5000/predict`.

## Run with Docker

Docker builds the model file into the image, so retrieve it with DVC before building:

```bash
dvc pull data/model/model.pkl
docker build -t image-classifier .
docker run --rm -p 5000:5000 image-classifier
```

The API is then available at `http://localhost:5000`.

## DVC Pipeline

Run `dvc repro` to execute the stages defined in `dvc.yaml`:

1. `data_collection` downloads the flower photos dataset and selects the configured classes.
2. `data_processing` resizes images and creates training and validation arrays.
3. `train` trains the classifier, writes `data/model/model.pkl`, and records metrics in `data/metrics.json`.

The classes, image size, validation split, and training parameters are configured in `params.yaml`. The current configuration selects daisies, roses, and dandelions.

## GitHub Actions Deployment

The workflow in `.github/workflows/ci-cd.yaml` runs on pushes to `main`. Configure these repository secrets:

| Secret | Purpose |
|---|---|
| `AWS_ACCESS_KEY_ID` | Access the DVC S3 remote. |
| `AWS_SECRET_ACCESS_KEY` | Access the DVC S3 remote. |
| `DOCKER_USERNAME` | Authenticate to Docker Hub and name the image. |
| `DOCKER_PASSWORD` | Authenticate to Docker Hub. |
| `EC2_HOST` | Public hostname or IP address of the EC2 instance. |
| `EC2_SSH_KEY` | Private SSH key used to connect as `ubuntu`. |

The EC2 instance must have Docker installed, permit SSH from the GitHub Actions runner, and allow inbound traffic on port `5000` for external API access. The deployment runs the container as `classifier` and maps host port `5000` to container port `5000`.
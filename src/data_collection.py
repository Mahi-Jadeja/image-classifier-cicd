import os
import tarfile
import shutil
import requests
import yaml

with open("params.yaml") as f:
    params = yaml.safe_load(f)["data"]


def download_dataset():
    # skip re-downloading if the tar is already sitting here, saves time on repeat runs
    tar_path = "flower_photos.tgz"
    if not os.path.exists(tar_path):
        print("Downloading dataset...")
        r = requests.get(params["dataset_url"], stream=True)
        with open(tar_path, "wb") as f:
            shutil.copyfileobj(r.raw, f)
    with tarfile.open(tar_path) as tar:
        tar.extractall(".")


def organize_classes():
    # only keep the classes + image count we actually care about, keeps dataset small
    os.makedirs(params["raw_dir"], exist_ok=True)
    src_root = "flower_photos"
    for cls in params["classes"]:
        src_dir = os.path.join(src_root, cls)
        dst_dir = os.path.join(params["raw_dir"], cls)
        os.makedirs(dst_dir, exist_ok=True)
        images = os.listdir(src_dir)[: params["max_images_per_class"]]
        for img in images:
            shutil.copy(os.path.join(src_dir, img), os.path.join(dst_dir, img))


if __name__ == "__main__":
    download_dataset()
    organize_classes()

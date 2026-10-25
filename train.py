"""Assignment 2 training pipeline: PCB defect detection."""
import shutil
from pathlib import Path

import yaml
from roboflow import Roboflow
from ultralytics import YOLO

from api_key import load_api_key

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
WEIGHTS = ROOT / "weights" / "best.pt"

# Dataset on Roboflow Universe (recorded in REPORT.md)
WORKSPACE = "object-detection-dt-wzpc6"
PROJECT = "pcb-dataset-defect"
VERSION = 1

# Training settings
BASE_MODEL = "yolo11s.pt"  # pretrained COCO checkpoint we finetune from
IMGSZ = 1024               # larger than the default 640 because defects are tiny
EPOCHS = 100
PATIENCE = 20              # stop early if validation stops improving
BATCH = 8


def download_data() -> Path:
    """Download the dataset and point data.yaml at the right folders."""
    rf = Roboflow(api_key=load_api_key())
    rf.workspace(WORKSPACE).project(PROJECT).version(VERSION).download(
        "yolov11", location=str(DATA_DIR)
    )
    yaml_path = DATA_DIR / "data.yaml"
    cfg = yaml.safe_load(yaml_path.read_text())
    cfg.update(path=str(DATA_DIR), train="train/images",
               val="valid/images", test="test/images")
    yaml_path.write_text(yaml.safe_dump(cfg))
    return yaml_path


def train_model(data_yaml: Path) -> None:
    """Finetune YOLO from the pretrained checkpoint and save the best weights."""
    model = YOLO(BASE_MODEL)
    model.train(data=str(data_yaml), imgsz=IMGSZ, epochs=EPOCHS,
                patience=PATIENCE, batch=BATCH, seed=0,
                project=str(ROOT / "runs"), name="pcb", exist_ok=True)
    WEIGHTS.parent.mkdir(exist_ok=True)
    shutil.copy(model.trainer.best, WEIGHTS)
    print(f"Saved best weights to {WEIGHTS}")


def main() -> None:
    data_yaml = download_data()
    train_model(data_yaml)
    # Next: evaluation + baselines, cost sweep, saving results for the app


if __name__ == "__main__":
    main()
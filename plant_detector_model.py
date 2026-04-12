import os
import threading
from typing import Optional

_MODEL_LOCK = threading.Lock()
_MODEL = None


def load_plant_detector():
    """
    Download (once) and load a YOLOv8 plant leaf detector from HuggingFace.

    Repo: foduucom/plant-leaf-detection-and-classification
    File: best.pt
    Local path: models/plant_detector/best.pt
    """
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    with _MODEL_LOCK:
        if _MODEL is not None:
            return _MODEL

        try:
            from huggingface_hub import hf_hub_download
        except Exception as e:
            raise ImportError("huggingface_hub is required for plant detection. Install it with pip.") from e

        try:
            from ultralytics import YOLO
        except Exception as e:
            raise ImportError("ultralytics is required for plant detection. Install it with pip.") from e

        repo_id = "foduucom/plant-leaf-detection-and-classification"
        filename = "best.pt"

        models_dir = os.path.join(os.path.dirname(__file__), "models", "plant_detector")
        os.makedirs(models_dir, exist_ok=True)

        weights_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=models_dir,
            local_dir_use_symlinks=False,
        )

        _MODEL = YOLO(weights_path)
        return _MODEL

